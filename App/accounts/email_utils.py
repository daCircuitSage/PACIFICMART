"""
Async email sending utilities for email verification.
Supports both Celery and thread-based fallback for Render free tier compatibility.
"""
import threading
import logging
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import account_activation_token


logger = logging.getLogger(__name__)


def send_verification_email_async(user, request):
    """
    Send verification email asynchronously without blocking the request thread.
    Uses threading fallback since Celery may not be available on Render free tier.
    """
    def send_email_thread():
        try:
            # Get domain properly - handle both development and production
            domain = request.get_host()
            if not domain or domain == 'testserver':
                # Fallback for testing or invalid domains
                domain = getattr(settings, 'SITE_DOMAIN', 'thepacificmart.onrender.com')
            
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user)
            })
            
            send_email = EmailMessage(
                mail_subject, 
                message, 
                to=[user.email],
                from_email=getattr(settings, 'EMAIL_HOST_USER', None)
            )
            send_email.content_subtype = "html"
            send_email.send(fail_silently=True)  # Production-safe: fail silently
            
            logger.info(f"Verification email sent successfully to {user.email}")
            
        except Exception as e:
            # Log error but don't fail the request
            logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
    
    # Start email sending in background thread
    thread = threading.Thread(target=send_email_thread, daemon=True)
    thread.start()
    
    # Return immediately - don't wait for email to be sent
    return True


def send_verification_email_sync(user, request):
    """
    Synchronous version of email sending for testing purposes.
    Not recommended for production due to blocking behavior.
    """
    try:
        current_site = get_current_site(request)
        mail_subject = 'Please activate your account'
        message = render_to_string('accounts/account_verification_email.html', {
            'user': user,
            'domain': request.get_host(),
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user)
        })
        
        send_email = EmailMessage(
            mail_subject, 
            message, 
            to=[user.email],
            from_email=getattr(settings, 'EMAIL_HOST_USER', None)
        )
        send_email.content_subtype = "html"
        send_email.send(fail_silently=True)
        
        logger.info(f"Verification email sent successfully to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False
