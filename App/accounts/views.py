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
import smtplib
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme



def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                phone_number = form.cleaned_data['phone_number']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                username = email.split("@")[0]

                # Create user account
                user = Account.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=username,
                    password=password
                )
                user.phone_number = phone_number
                user.is_active = True  # Auto-activate user (email verification disabled)
                user.is_email_verified = True  # Mark as verified
                user.save()

                # Create user profile
                profile = UserProfile(user=user)
                profile.save()

                # Skip email sending (disabled for now)
                messages.success(request, 'Registration successful! You can now login.')
                return redirect('login')
                
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Registration error: {str(e)}")
                messages.error(request, 'An error occurred during registration. Please try again.')
                return redirect('register')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def send_verification_email(request, user, email):
    """Send verification email using Brevo with proper error detection"""
    logger = logging.getLogger(__name__)
    
    try:
        # Validate email configuration first
        if not settings.DEFAULT_FROM_EMAIL:
            logger.error("DEFAULT_FROM_EMAIL not configured")
            return False
            
        # Get domain - prioritize request host for production
        if request:
            domain = request.get_host()
        else:
            current_site = get_current_site(request)
            domain = current_site.domain if current_site else 'thepacificmart.onrender.com'
        
        # Generate verification link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        # Render email template
        mail_subject = 'Activate your PacificMart Account'
        message = render_to_string('accounts/account_verification_email.html', {
            'user': user,
            'domain': domain,
            'uid': uid,
            'token': token
        })
        
        # Create email with proper configuration
        send_email = EmailMessage(
            subject=mail_subject,
            body=message,
            from_email=f"{settings.BREVO_SENDER_NAME} <{settings.DEFAULT_FROM_EMAIL}>",
            to=[email]
        )
        send_email.content_subtype = "html"
        
        # Send with timeout and explicit error handling
        result = send_email.send(fail_silently=False)
        
        # Check if email was actually sent (result = 1 means success)
        if result == 1:
            logger.info(f"Verification email sent successfully to {email}")
            return True
        else:
            logger.error(f"Email sending returned {result} for {email}")
            return False
            
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed for {email}: {str(e)}")
        return False
    except smtplib.SMTPConnectError as e:
        logger.error(f"SMTP connection failed for {email}: {str(e)}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error for {email}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending verification email to {email}: {str(e)}")
        return False

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = auth.authenticate(email=email, password=password)

            if user is not None:
                # Check if user is active
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
                    
                    messages.success(request, 'You are now logged in.')
                    return redirect(url)
                else:
                    messages.error(request, 'Please verify your email address before logging in.')
                    return redirect('login')
            else:
                messages.error(request, 'Invalid login credentials')
                return redirect('login')
                
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Login error: {str(e)}")
            messages.error(request, 'An error occurred during login. Please try again.')
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
        user.is_email_verified = True  # Mark email as verified
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('register')

def resend_verification_email(request):
    """Resend verification email for inactive users"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = Account.objects.get(email=email)
            
            if user.is_active:
                messages.info(request, 'This account is already activated. You can login.')
                return redirect('login')
                
            if user.is_email_verified:
                # This shouldn't happen but handle it gracefully
                user.is_active = True
                user.save()
                messages.info(request, 'Your account is already verified. You can login.')
                return redirect('login')
            
            # Resend verification email
            email_sent = send_verification_email(request, user, email)
            
            if email_sent:
                messages.success(request, 'Verification email has been resent. Please check your inbox.')
                return redirect('/accounts/login/?command=verification&email=' + email + '&email_sent=True')
            else:
                messages.error(request, 'Failed to send verification email. Please try again later or contact support.')
                return redirect('/accounts/login/?command=verification&email=' + email + '&email_sent=False')
                
        except Account.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
            return redirect('/accounts/login/?command=resend')
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Resend verification error: {str(e)}")
            messages.error(request, 'An error occurred. Please try again.')
            return redirect('/accounts/login/?command=resend')
    
    # GET request - show resend form
    return render(request, 'accounts/resend_verification.html')

def forgotpassword(request):
    if request.method == "POST":
        email = request.POST['email']
        try:
            if Account.objects.filter(email=email).exists():
                user = Account.objects.get(email=email)
                
                # Send password reset email
                email_sent = send_password_reset_email(request, user, email)
                
                if email_sent:
                    messages.success(request, 'Password reset email has been sent to your email.')
                else:
                    messages.warning(request, 'Unable to send reset email. Please try again later.')
                    
                return redirect('login')
            else:
                messages.error(request, 'Account does not exist.')
                return redirect('forgotpassword')
                
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Forgot password error: {str(e)}")
            messages.error(request, 'An error occurred. Please try again.')
            return redirect('forgotpassword')
            
    return render(request, 'accounts/forgotpassword.html')


def send_password_reset_email(request, user, email):
    """Send password reset email using Brevo"""
    try:
        # Get domain - prioritize request host for production
        if request:
            domain = request.get_host()
        else:
            current_site = get_current_site(request)
            domain = current_site.domain if current_site else 'thepacificmart.onrender.com'
        
        mail_subject = 'Reset Your PacificMart Password'
        message = render_to_string('accounts/reset_password_email.html', {
            'user': user,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user)
        })
        
        send_email = EmailMessage(
            mail_subject, 
            message, 
            from_email=f"{settings.BREVO_SENDER_NAME} <{settings.DEFAULT_FROM_EMAIL}>",
            to=[email]
        )
        send_email.content_subtype = "html"
        send_email.send(fail_silently=False)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Password reset email sent successfully to {email}")
        return True
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Password reset email failed for {email}: {str(e)}")
        return False

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
        
        try:
            if not uid:
                messages.error(request, 'Invalid password reset link. Please try again.')
                return redirect('forgotpassword')
                
            user = Account.objects.get(pk=uid)

            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, 'Password reset successful. You can now login with your new password.')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
                return redirect('resetpassword')
                
        except Account.DoesNotExist:
            messages.error(request, 'Invalid password reset link. Please try again.')
            return redirect('forgotpassword')
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Reset password error: {str(e)}")
            messages.error(request, 'An error occurred. Please try again.')
            return redirect('resetpassword')

    return render(request, 'accounts/resetpassword.html')
