#!/usr/bin/env python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_brevo_smtp():
    """Test Brevo SMTP connection directly"""
    print("Testing Brevo SMTP Configuration...")
    print(f"EMAIL_HOST: {os.getenv('EMAIL_HOST', 'Not set')}")
    print(f"EMAIL_PORT: {os.getenv('EMAIL_PORT', 'Not set')}")
    print(f"EMAIL_HOST_USER: {os.getenv('EMAIL_HOST_USER', 'Not set')}")
    print(f"EMAIL_HOST_PASSWORD: {'Set' if os.getenv('EMAIL_HOST_PASSWORD') else 'Not set'}")
    print(f"EMAIL_USE_TLS: {os.getenv('EMAIL_USE_TLS', 'False')}")
    print(f"EMAIL_USE_SSL: {os.getenv('EMAIL_USE_SSL', 'False')}")
    
    try:
        # Create SMTP connection
        server = smtplib.SMTP(os.getenv('EMAIL_HOST'), int(os.getenv('EMAIL_PORT', 587)))
        server.set_debuglevel(1)  # Enable debug output
        
        # Start TLS encryption
        if os.getenv('EMAIL_USE_TLS', 'False').lower() == 'true':
            print("Starting TLS...")
            server.starttls()
        
        # Login
        print("Attempting login...")
        server.login(
            os.getenv('EMAIL_HOST_USER'),
            os.getenv('EMAIL_HOST_PASSWORD')
        )
        print("✅ SMTP login successful!")
        
        # Test sending email
        msg = MIMEMultipart()
        msg['From'] = f"PacificMart <{os.getenv('DEFAULT_FROM_EMAIL')}>"
        msg['To'] = os.getenv('EMAIL_HOST_USER')  # Send to self for testing
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
        print("This usually means:")
        print("1. Wrong SMTP key (check EMAIL_HOST_PASSWORD)")
        print("2. Sender email not verified in Brevo")
        print("3. Account limits exceeded")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"❌ SMTP Connection Error: {e}")
        print("This usually means:")
        print("1. Wrong SMTP server (check EMAIL_HOST)")
        print("2. Wrong port (check EMAIL_PORT)")
        print("3. Network/firewall issues")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ General Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("BREVO SMTP TESTING")
    print("=" * 60)
    
    # Test direct SMTP
    smtp_result = test_brevo_smtp()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Direct SMTP Test: {'✅ PASSED' if smtp_result else '❌ FAILED'}")
    print("=" * 60)
