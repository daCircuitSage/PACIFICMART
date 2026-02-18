from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from orders.models import Order, OrderProduct
from django.contrib import messages, auth
from cart.views import _cart_id, merge_carts
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
import requests
import logging
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme



def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            user.phone_number = phone_number
            user.save()

            profile = UserProfile(user=user)
            profile.save()

            # Verification email
            email_sent = False
            try:
                # current_site = get_current_site(request)
                mail_subject = 'Please activate your account'
                message = render_to_string('accounts/account_verification_email.html', {
                    'user': user,
                    # 'domain': current_site.domain,
                    'domain': request.get_host(),  #current_site This gives 127.0.0.1:8000 or your domain
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user)
                })
                
                # Create email with proper error handling
                send_email = EmailMessage(
                    mail_subject, 
                    message, 
                    to=[email],
                    # from_email=None
                    from_email=settings.EMAIL_HOST_USER
                )
                send_email.content_subtype = "html"
                # send_email.send(fail_silently=True)  # Changed to fail_silently=True
                send_email.send(fail_silently=False)  # false throws error
                email_sent = True
                
            except Exception as e:
                # Log error but don't fail registration
                logger = logging.getLogger(__name__)
                logger.error(f"Email sending failed for {email}: {str(e)}")
                email_sent = False

            # Always redirect, even if email fails
            # return redirect('/accounts/login/?command=verification&email=' + email + '&email_sent=' + str(email_sent))
            # SECURE: Only proceed if email was sent
            if email_sent:
                return redirect('/accounts/login/?command=verification&email=' + email + '&email_sent=True')
            else:
                messages.error(request, 'Registration failed. Please try again or contact support.')
                return redirect('register')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            # Check if user is active
            if user.is_active:
                session_key_before = _cart_id(request)
                auth.login(request, user)
                merge_carts(user, session_key_before)

                # Vulnerability found: Direct redirect without checking if URL is safe
                    # Malicious users could craft links like:
                        # ?next=http://evil.com/steal-data
                # url = request.GET.get('next') or 'dashboard'
                # messages.success(request, 'You are now logged in.')
                # return redirect(url)
                # SECURE CODE: resolve Only allows redirects to current host Defaults to 'dashboard' for invalid URLs
                next_url = request.GET.get('next')
                if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                    url = next_url
                else:
                    url = 'dashboard'
                return redirect(url)
            else:
                messages.error(request, 'Please verify your email address before logging in.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')

@login_required(login_url='login')
def dashboard(request):
    # Get all orders with optimized queries
    orders = Order.objects.filter(user=request.user, is_ordered=True)\
        .select_related('payment', 'user')\
        .prefetch_related('orderproduct_set__product', 'orderproduct_set__variations')\
        .order_by('-created_at')
    
    orders_count = orders.count()
    
    # Calculate order statistics
    shipped_orders_count = orders.filter(status__in=['Shipped', 'Delivered']).count()
    pending_orders_count = orders.filter(status='Verifying Payment').count()
    
    # Get recent orders (last 5)
    recent_orders = orders[:5]
    
    # Get cart count
    from cart.models import CartItems
    cart_count = CartItems.objects.filter(user=request.user, is_active=True).count()
    
    userprofile = get_object_or_404(UserProfile, user=request.user)
    
    return render(request, 'accounts/dashboard.html', {
        'orders_count': orders_count,
        'shipped_orders_count': shipped_orders_count,
        'pending_orders_count': pending_orders_count,
        'recent_orders': recent_orders,
        'cart_count': cart_count,
        'userprofile': userprofile
    })

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True)\
        .select_related('payment', 'user')\
        .prefetch_related('orderproduct_set__product', 'orderproduct_set__variations')\
        .order_by('-created_at')
    return render(request, 'accounts/my_orders.html', {'orders': orders})

@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
        else:
            # Add error messages when forms are invalid
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile
    })

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = request.user

        if new_password == confirm_password:
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Current password is incorrect.')
        else:
            messages.error(request, 'New password and confirm password do not match.')

    return render(request, 'accounts/change_password.html')

@login_required(login_url='login')
def order_detail(request, order_id):
    # order = get_object_or_404(Order, order_number=order_id) # VULNERABLE CODE: any user can access any order
    order = get_object_or_404(Order, order_number=order_id, user=request.user) # SECURE CODE: only the owner can access their order
    order_items = OrderProduct.objects.filter(order=order).select_related('product', 'order').prefetch_related('variations')
    subtotal = sum(item.product_price * item.quantity for item in order_items)
    return render(request, 'accounts/order_detail.html', {
        'order': order,
        'order_detail': order_items,
        'subtotal': subtotal
    })

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('register')

def forgotpassword(request):
    if request.method == "POST":
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email=email)
            # current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                # 'domain': current_site,
                'domain': request.get_host(), # fix: get the domain from the request
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            send_email = EmailMessage(mail_subject, message, to=[email])
            send_email.content_subtype = "html"
            send_email.send()
            messages.success(request, 'Password reset email has been sent to your email.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist.')
            return redirect('forgotpassword')
    return render(request, 'accounts/forgotpassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password.')
        return redirect('resetpassword')
    else:
        messages.error(request, 'This link is dead!')
        return redirect('login')

def resetpassword(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        uid = request.session.get('uid')
        user = Account.objects.get(pk=uid)

        if password == confirm_password:
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful.')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('resetpassword')

    return render(request, 'accounts/resetpassword.html')
