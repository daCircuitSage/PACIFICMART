#!/usr/bin/env python
"""
Test script for Brevo email functionality.
Run this script to verify email configuration is working.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'factors_Ecom.settings')
django.setup()

from factors_Ecom.utils import send_brevo_email
from django.conf import settings

def test_brevo_email():
    """Test the Brevo email functionality."""
    
    print("Testing Brevo Email Configuration...")
    print(f"BREVO_API_KEY configured: {bool(getattr(settings, 'BREVO_API_KEY', None))}")
    print(f"BREVO_SENDER_EMAIL configured: {bool(getattr(settings, 'BREVO_SENDER_EMAIL', None))}")
    
    # Test HTML content
    test_html = """
    <html>
        <body>
            <h2>Test Email from PacificMart</h2>
            <p>This is a test email to verify Brevo integration is working correctly.</p>
            <p>If you receive this email, the configuration is successful!</p>
            <br>
            <p>Best regards,<br>PacificMart Team</p>
        </body>
    </html>
    """
    
    # Send test email (use your email for testing)
    test_email = "shihabthebrowncrow@gmail.com"  # Replace with actual test email
    
    print(f"\nSending test email to: {test_email}")
    
    success = send_brevo_email(
        to_email=test_email,
        subject="PacificMart - Brevo Email Test",
        html_content=test_html
    )
    
    if success:
        print("✅ Email sent successfully!")
    else:
        print("❌ Failed to send email. Check configuration and logs.")
    
    return success

if __name__ == "__main__":
    test_brevo_email()
