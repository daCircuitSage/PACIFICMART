import os
import requests
import logging
from django.conf import settings
from django.template.loader import render_to_string
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def send_brevo_email(
    to_email: str,
    subject: str,
    template_name: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    html_content: Optional[str] = None,
    sender_email: Optional[str] = None,
    sender_name: Optional[str] = None
) -> bool:
    """
    Send email using Brevo HTTP API.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        template_name: Django template name (optional)
        context: Template context variables (optional)
        html_content: Direct HTML content (optional, overrides template)
        sender_email: Sender email (optional, uses default from env)
        sender_name: Sender name (optional)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    api_key = getattr(settings, 'BREVO_API_KEY', None)
    if not api_key:
        logger.error("BREVO_API_KEY not configured")
        return False
    
    default_sender_email = getattr(settings, 'BREVO_SENDER_EMAIL', None)
    if not default_sender_email:
        logger.error("BREVO_SENDER_EMAIL not configured")
        return False
    
    # Use provided sender or default from environment
    from_email = sender_email or default_sender_email
    from_name = sender_name or getattr(settings, 'BREVO_SENDER_NAME', 'PacificMart')
    
    # Generate HTML content from template if provided
    if html_content is None and template_name:
        html_content = render_to_string(template_name, context or {})
    
    if not html_content:
        logger.error("No HTML content provided for email")
        return False
    
    url = "https://api.brevo.com/v3/smtp/email"
    
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }
    
    payload = {
        "sender": {
            "name": from_name,
            "email": from_email
        },
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Log successful email delivery
        logger.info(f"Email sent successfully to {to_email} via Brevo")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send email to {to_email} via Brevo: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Brevo API response: {e.response.text}")
        return False


def send_registration_email(user, domain: str) -> bool:
    """
    Send account verification email to new user.
    
    Args:
        user: User instance
        domain: Current domain for verification link
    
    Returns:
        bool: True if email sent successfully
    """
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode
    from django.contrib.auth.tokens import default_token_generator
    
    context = {
        'user': user,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user)
    }
    
    return send_brevo_email(
        to_email=user.email,
        subject='Please activate your account',
        template_name='accounts/account_verification_email.html',
        context=context
    )


def send_password_reset_email(user, domain: str) -> bool:
    """
    Send password reset email to user.
    
    Args:
        user: User instance
        domain: Current domain for reset link
    
    Returns:
        bool: True if email sent successfully
    """
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode
    from django.contrib.auth.tokens import default_token_generator
    
    context = {
        'user': user,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user)
    }
    
    return send_brevo_email(
        to_email=user.email,
        subject='Reset your password',
        template_name='accounts/reset_password_email.html',
        context=context
    )


def send_order_confirmation_email(user, order) -> bool:
    """
    Send order confirmation email to user.
    
    Args:
        user: User instance
        order: Order instance
    
    Returns:
        bool: True if email sent successfully
    """
    context = {
        'user': user,
        'order': order
    }
    
    return send_brevo_email(
        to_email=user.email,
        subject='Thank you for your order!',
        template_name='orders/order_recieved_email.html',
        context=context
    )
