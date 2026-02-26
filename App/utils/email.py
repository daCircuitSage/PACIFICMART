"""
Brevo API Email Backend
Uses Brevo's REST API instead of SMTP for sending emails
"""
import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage, EmailMultiAlternatives
from django.conf import settings
from decouple import config
import logging

logger = logging.getLogger(__name__)


class BrevoEmailBackend(BaseEmailBackend):
    """
    Email backend that uses Brevo's REST API instead of SMTP
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = config('BREVO_API_KEY', default='')
        self.api_url = 'https://api.brevo.com/v3/smtp/email'
    
    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects using Brevo API
        """
        if not email_messages:
            return 0
        
        sent_count = 0
        for message in email_messages:
            try:
                sent = self._send_message(message)
                if sent:
                    sent_count += 1
            except Exception as e:
                if not self.fail_silently:
                    raise
                logger.error(f"Failed to send email via Brevo API: {e}")
        
        return sent_count
    
    def _send_message(self, message):
        """
        Send a single email message using Brevo API
        """
        # Prepare email data for Brevo API
        # Extract email address from from_email (handle both "Name <email>" and plain email)
        from_email = message.from_email
        if '<' in from_email and '>' in from_email:
            # Extract email from "Name <email@domain.com>" format
            sender_email = from_email.split('<')[1].split('>')[0].strip()
            sender_name = from_email.split('<')[0].strip().strip('"')
        else:
            # Plain email address
            sender_email = from_email
            sender_name = getattr(settings, 'BREVO_SENDER_NAME', 'PacificMart')
        
        email_data = {
            'sender': {
                'name': sender_name,
                'email': sender_email
            },
            'to': [{'email': addr[1] if isinstance(addr, tuple) else addr} 
                   for addr in message.to],
            'subject': message.subject,
        }
        
        # Handle HTML and plain text content
        if isinstance(message, EmailMultiAlternatives):
            # Handle multipart messages
            if message.alternatives:
                # Use the first HTML alternative
                content, content_type = message.alternatives[0]
                if content_type == 'text/html':
                    email_data['htmlContent'] = content
                else:
                    email_data['textContent'] = content
            
            # Add plain text if available
            if message.body:
                email_data['textContent'] = message.body
                
        else:
            # Handle simple EmailMessage
            if message.content_subtype == 'html':
                email_data['htmlContent'] = message.body
            else:
                email_data['textContent'] = message.body
        
        # Add CC and BCC if present
        if message.cc:
            email_data['cc'] = [{'email': addr[1] if isinstance(addr, tuple) else addr} 
                               for addr in message.cc]
        
        if message.bcc:
            email_data['bcc'] = [{'email': addr[1] if isinstance(addr, tuple) else addr} 
                                for addr in message.bcc]
        
        # Add reply-to if present
        if message.reply_to:
            email_data['replyTo'] = message.reply_to[0]
        
        # Send via Brevo API
        headers = {
            'api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(self.api_url, headers=headers, json=email_data, timeout=30)
        
        if response.status_code == 201:
            logger.info(f"Email sent successfully via Brevo API. Message ID: {response.json().get('messageId')}")
            return True
        else:
            error_msg = f"Brevo API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)


def send_brevo_email(subject, body, to_email, from_email=None, html_content=None):
    """
    Helper function to send emails using Brevo API
    """
    from django.core.mail import EmailMessage
    
    if from_email is None:
        from_email = f"{getattr(settings, 'BREVO_SENDER_NAME', 'PacificMart')} <{settings.DEFAULT_FROM_EMAIL}>"
    
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=from_email,
        to=[to_email]
    )
    
    if html_content:
        email.content_subtype = "html"
        email.body = html_content
    
    # Use Brevo backend
    from django.core.mail import get_connection
    connection = get_connection('utils.email.BrevoEmailBackend')
    result = email.send(fail_silently=False, connection=connection)
    
    return result == 1
