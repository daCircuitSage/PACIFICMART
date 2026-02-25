import logging
from celery import shared_task
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import Account, EmailStatus
from .brevo_email import send_brevo_email

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email_async(self, user_id, domain, protocol='http'):
    """
    Send verification email asynchronously
    """
    try:
        user = Account.objects.get(id=user_id)
        
        # Create email content
        mail_subject = 'Please activate your account'
        message = render_to_string('accounts/account_verification_email.html', {
            'user': user,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
            'protocol': protocol
        })
        
        # Send email using Brevo
        email_sent = send_brevo_email(
            to_email=user.email,
            subject=mail_subject,
            html_content=message
        )
        
        # Update email status
        EmailStatus.objects.update_or_create(
            user=user,
            email_type='verification',
            defaults={
                'status': 'sent' if email_sent else 'failed',
                'sent_at': None if not email_sent else None,
                'error_message': None if email_sent else 'Brevo API failed',
                'retry_count': 0
            }
        )
        
        if email_sent:
            logger.info(f"Verification email sent successfully to {user.email}")
            return {'status': 'success', 'user_id': user_id}
        else:
            logger.error(f"Failed to send verification email to {user.email}")
            # Retry with exponential backoff
            raise self.retry(exc=Exception('Email sending failed'), countdown=60 * (2 ** self.request.retries))
            
    except Account.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        return {'status': 'error', 'message': 'User not found'}
    except Exception as exc:
        logger.error(f"Error sending verification email: {str(exc)}")
        
        # Update email status with error
        try:
            user = Account.objects.get(id=user_id)
            EmailStatus.objects.update_or_create(
                user=user,
                email_type='verification',
                defaults={
                    'status': 'failed',
                    'error_message': str(exc),
                    'retry_count': self.request.retries
                }
            )
        except:
            pass
        
        # Retry if we haven't exceeded max retries
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        
        return {'status': 'error', 'message': str(exc)}

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email_async(self, user_id, domain, protocol='http'):
    """
    Send password reset email asynchronously
    """
    try:
        user = Account.objects.get(id=user_id)
        
        # Create email content
        mail_subject = 'Reset your password'
        message = render_to_string('accounts/reset_password_email.html', {
            'user': user,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
            'protocol': protocol
        })
        
        # Send email using Brevo
        email_sent = send_brevo_email(
            to_email=user.email,
            subject=mail_subject,
            html_content=message
        )
        
        # Update email status
        EmailStatus.objects.update_or_create(
            user=user,
            email_type='password_reset',
            defaults={
                'status': 'sent' if email_sent else 'failed',
                'sent_at': None if not email_sent else None,
                'error_message': None if email_sent else 'Brevo API failed',
                'retry_count': 0
            }
        )
        
        if email_sent:
            logger.info(f"Password reset email sent successfully to {user.email}")
            return {'status': 'success', 'user_id': user_id}
        else:
            logger.error(f"Failed to send password reset email to {user.email}")
            raise self.retry(exc=Exception('Email sending failed'), countdown=60 * (2 ** self.request.retries))
            
    except Account.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        return {'status': 'error', 'message': 'User not found'}
    except Exception as exc:
        logger.error(f"Error sending password reset email: {str(exc)}")
        
        # Update email status with error
        try:
            user = Account.objects.get(id=user_id)
            EmailStatus.objects.update_or_create(
                user=user,
                email_type='password_reset',
                defaults={
                    'status': 'failed',
                    'error_message': str(exc),
                    'retry_count': self.request.retries
                }
            )
        except:
            pass
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        
        return {'status': 'error', 'message': str(exc)}
