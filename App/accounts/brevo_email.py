import requests
import logging
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.core.mail.backends.smtp import EmailBackend
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
import time

logger = logging.getLogger(__name__)

class BrevoEmailService:
    """Brevo API email service with retry logic and fallback"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'BREVO_API_KEY', None)
        self.sender_email = getattr(settings, 'BREVO_SENDER_EMAIL', None)
        self.sender_name = getattr(settings, 'BREVO_SENDER_NAME', 'PacificMart')
        self.api_url = 'https://api.brevo.com/v3/smtp/email'
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
    def send_email(self, to_email, subject, html_content, text_content=None):
        """Send email using Brevo API with retry logic"""
        
        if not all([self.api_key, self.sender_email]):
            logger.warning("Brevo credentials not configured, falling back to SMTP")
            return self._fallback_smtp(to_email, subject, html_content, text_content)
        
        payload = {
            'sender': {
                'name': self.sender_name,
                'email': self.sender_email
            },
            'to': [{'email': to_email}],
            'subject': subject,
            'htmlContent': html_content,
        }
        
        if text_content:
            payload['textContent'] = text_content
            
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'api-key': self.api_key
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=10  # 10-second timeout for faster failure detection
                )
                
                if response.status_code == 200:
                    logger.info(f"Email sent successfully via Brevo to {to_email}")
                    return True
                else:
                    logger.error(f"Brevo API error (attempt {attempt + 1}): {response.status_code} - {response.text}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Brevo request failed (attempt {attempt + 1}): {str(e)}")
                
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
        
        logger.warning(f"All Brevo attempts failed, falling back to SMTP for {to_email}")
        return self._fallback_smtp(to_email, subject, html_content, text_content)
    
    def _fallback_smtp(self, to_email, subject, html_content, text_content=None):
        """Fallback to Gmail SMTP with retry logic"""
        
        try:
            # Use Django's email backend with shorter timeout
            email = EmailMessage(
                subject=subject,
                body=text_content or html_content,
                from_email=getattr(settings, 'EMAIL_HOST_USER', self.sender_email),
                to=[to_email]
            )
            
            email.content_subtype = "html"
            email.send(fail_silently=False)
            
            logger.info(f"Email sent successfully via SMTP fallback to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"SMTP fallback also failed for {to_email}: {str(e)}")
            return False

# Global instance
brevo_service = BrevoEmailService()

def send_brevo_email(to_email, subject, html_content, text_content=None):
    """Convenience function to send email via Brevo with fallback"""
    return brevo_service.send_email(to_email, subject, html_content, text_content)

def send_verification_email_brevo(request, user):
    """Send verification email using Brevo API"""
    current_site = get_current_site(request)
    mail_subject = 'Please activate your account'
    
    message = render_to_string('accounts/account_verification_email.html', {
        'user': user,
        'domain': request.get_host(),
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user)
    })
    
    return send_brevo_email(user.email, mail_subject, message)

def send_password_reset_email_brevo(request, user):
    """Send password reset email using Brevo API"""
    current_site = get_current_site(request)
    mail_subject = 'Reset your password'
    
    message = render_to_string('accounts/reset_password_email.html', {
        'user': user,
        'domain': request.get_host(),
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user)
    })
    
    return send_brevo_email(user.email, mail_subject, message)
