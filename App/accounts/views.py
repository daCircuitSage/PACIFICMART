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
from .tokens import account_activation_token
from .email_utils import send_verification_email_async
from .rate_limit import can_resend_verification_email, mark_verification_email_sent



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
            # User starts inactive until email verification
            user.is_active = False
            user.is_email_verified = False
            user.save()

            profile = UserProfile(user=user)
            profile.save()

            # Send verification email asynchronously
            email_sent = send_verification_email_async(user, request)
            
            return redirect('/accounts/login/?command=verification&email=' + email + '&email_sent=' + str(email_sent))
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # First check if user exists and email verification status
        try:
            user_obj = Account.objects.get(email=email)
            
            # Check email verification BEFORE authentication
            if not user_obj.is_email_verified:
                messages.error(request, 'Email not verified. Please check your inbox or resend verification email.')
                return redirect('login')
                
        except Account.DoesNotExist:
            # Don't reveal if user exists or not - use generic message
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
        
        # Now authenticate user
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            # Check if user is active (should always be true if email is verified)
            if user.is_active:
                session_key_before = _cart_id(request)
                auth.login(request, user)
                merge_carts(user, session_key_before)

                # Secure redirect handling
                next_url = request.GET.get('next')
                if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                    url = next_url
                else:
                    url = 'dashboard'
                return redirect(url)
            else:
                # This should not happen if email verification is working properly
                messages.error(request, 'Account is not active. Please contact support.')
                return redirect('login')
        else:
            # Invalid password
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

    if user is not None and account_activation_token.check_token(user, token):
        # Check if already verified to prevent duplicate activation
        if user.is_email_verified:
            messages.info(request, 'Your account is already activated.')
            return redirect('login')
            
        # Activate account
        user.is_active = True
        user.is_email_verified = True
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
            # EMAIL DISABLED TEMPORARILY (Render free plan issue)
            # Password reset email - DISABLED
            # send_email = EmailMessage(mail_subject, message, to=[email])
            # send_email.content_subtype = "html"
            # send_email.send()
            messages.success(request, 'Password reset email has been sent to your email.')  # Show dummy success message
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

def resend_verification_email(request):
    """
    Resend verification email endpoint with rate limiting.
    Accepts POST requests with email field.
    Rate limited to 1 resend per 60 seconds per user.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if not email:
            messages.error(request, 'Email address is required.')
            return redirect('login')
        
        try:
            user = Account.objects.get(email=email)
            
            # Check if user is already verified
            if user.is_email_verified:
                messages.info(request, 'Your account is already verified. You can log in.')
                return redirect('login')
            
            # Check rate limit
            can_resend, wait_time = can_resend_verification_email(user)
            
            if not can_resend:
                messages.error(request, f'Please wait {wait_time} seconds before requesting another verification email.')
                return redirect('login')
            
            # Send verification email asynchronously
            email_sent = send_verification_email_async(user, request)
            
            if email_sent:
                # Mark rate limit
                mark_verification_email_sent(user)
                messages.success(request, 'Verification email has been sent to your email address.')
            else:
                messages.error(request, 'Failed to send verification email. Please try again later.')
            
            return redirect('login')
            
        except Account.DoesNotExist:
            # Don't reveal if user exists or not for security
            messages.success(request, 'If an account with this email exists, a verification email will be sent.')
            return redirect('login')
            
    # For GET requests, redirect to login
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
