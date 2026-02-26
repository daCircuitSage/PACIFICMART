#!/usr/bin/env python
import os
import django
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.factors_Ecom.settings')
django.setup()

from django.conf import settings
from decouple import config

def test_brevo_smtp():
    """Test Brevo SMTP connection directly"""
    print("Testing Brevo SMTP Configuration...")
    print(f"EMAIL_HOST: {config('EMAIL_HOST', default='Not set')}")
    print(f"EMAIL_PORT: {config('EMAIL_PORT', default='Not set')}")
    print(f"EMAIL_HOST_USER: {config('EMAIL_HOST_USER', default='Not set')}")
    print(f"EMAIL_HOST_PASSWORD: {'Set' if config('EMAIL_HOST_PASSWORD', default='') else 'Not set'}")
    print(f"EMAIL_USE_TLS: {config('EMAIL_USE_TLS', default=False, cast=bool)}")
    print(f"EMAIL_USE_SSL: {config('EMAIL_USE_SSL', default=False, cast=bool)}")
    
    try:
        # Create SMTP connection
        server = smtplib.SMTP(config('EMAIL_HOST'), config('EMAIL_PORT', default=587, cast=int))
        server.set_debuglevel(1)  # Enable debug output
        
        # Start TLS encryption
        if config('EMAIL_USE_TLS', default=False, cast=bool):
            print("Starting TLS...")
            server.starttls()
        
        # Login
        print("Attempting login...")
        server.login(
            config('EMAIL_HOST_USER'),
            config('EMAIL_HOST_PASSWORD')
        )
        print("✅ SMTP login successful!")
        
        # Test sending email
        msg = MIMEMultipart()
        msg['From'] = f"PacificMart <{config('DEFAULT_FROM_EMAIL')}>"
        msg['To'] = config('EMAIL_HOST_USER')  # Send to self for testing
        msg['Subject'] = "Test Email from PacificMart"
        
        body = """
        This is a test email from PacificMart to verify SMTP configuration.
        
        If you receive this email, the Brevo SMTP is working correctly.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        print("Sending test email...")
        server.send_message(msg)
        print("✅ Test email sent successfully!")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP Authentication Error: {e}")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"❌ SMTP Connection Error: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ General Error: {e}")
        return False

def test_django_email():
    """Test Django email backend"""
    print("\nTesting Django Email Backend...")
    
    try:
        from django.core.mail import send_mail, EmailMessage
        
        # Test simple send_mail
        result = send_mail(
            subject='Test from Django',
            message='This is a test email from Django.',
            from_email=f"PacificMart <{settings.DEFAULT_FROM_EMAIL}>",
            recipient_list=[config('EMAIL_HOST_USER')],
            fail_silently=False,
        )
        
        print(f"✅ Django send_mail result: {result}")
        
        # Test EmailMessage
        email = EmailMessage(
            subject='Test EmailMessage from Django',
            body='This is a test email using EmailMessage.',
            from_email=f"PacificMart <{settings.DEFAULT_FROM_EMAIL}>",
            to=[config('EMAIL_HOST_USER')],
        )
        email.content_subtype = "html"
        
        result2 = email.send(fail_silently=False)
        print(f"✅ Django EmailMessage result: {result2}")
        
        return True
        
    except Exception as e:
        print(f"❌ Django Email Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("BREVO EMAIL TESTING")
    print("=" * 60)
    
    # Test direct SMTP
    smtp_result = test_brevo_smtp()
    
    # Test Django backend
    django_result = test_django_email()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Direct SMTP Test: {'✅ PASSED' if smtp_result else '❌ FAILED'}")
    print(f"Django Email Test: {'✅ PASSED' if django_result else '❌ FAILED'}")
    print("=" * 60)
