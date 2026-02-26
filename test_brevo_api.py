#!/usr/bin/env python
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_brevo_api():
    """Test Brevo REST API directly"""
    print("Testing Brevo REST API...")
    print(f"API Key: {'Set' if os.getenv('BREVO_API_KEY') else 'Not set'}")
    print(f"Sender Email: {os.getenv('DEFAULT_FROM_EMAIL')}")
    print(f"Sender Name: {os.getenv('BREVO_SENDER_NAME')}")
    
    try:
        api_key = os.getenv('BREVO_API_KEY')
        if not api_key:
            print("❌ BREVO_API_KEY not found in environment variables")
            return False
        
        # Prepare email data
        email_data = {
            'sender': {
                'name': os.getenv('BREVO_SENDER_NAME', 'PacificMart'),
                'email': os.getenv('DEFAULT_FROM_EMAIL')
            },
            'to': [{'email': os.getenv('EMAIL_HOST_USER')}],  # Send to self for testing
            'subject': 'Test Email from PacificMart (API)',
            'htmlContent': '''
            <h2>Test Email from PacificMart</h2>
            <p>This is a test email sent using Brevo's REST API.</p>
            <p>If you receive this email, the Brevo API is working correctly.</p>
            <p><strong>Configuration:</strong></p>
            <ul>
                <li>API Key: ✅ Valid</li>
                <li>Sender Email: ✅ Valid</li>
                <li>API Endpoint: ✅ Working</li>
            </ul>
            <p>Best regards,<br>PacificMart Team</p>
            '''
        }
        
        # Send via Brevo API
        headers = {
            'api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        print("Sending test email via Brevo API...")
        response = requests.post(
            'https://api.brevo.com/v3/smtp/email',
            headers=headers,
            json=email_data,
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Email sent successfully! Message ID: {result.get('messageId')}")
            return True
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            
            # Common error explanations
            if response.status_code == 400:
                print("This usually means:")
                print("1. Invalid sender email (not verified in Brevo)")
                print("2. Invalid recipient email")
                print("3. Missing required fields")
            elif response.status_code == 401:
                print("This usually means:")
                print("1. Invalid API key")
                print("2. API key expired")
                print("3. API key doesn't have SMTP permissions")
            elif response.status_code == 403:
                print("This usually means:")
                print("1. Account suspended")
                print("2. API key doesn't have required permissions")
            elif response.status_code == 429:
                print("This usually means:")
                print("1. Rate limit exceeded")
                print("2. Too many requests")
            
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return False
    except Exception as e:
        print(f"❌ General Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("BREVO API TESTING")
    print("=" * 60)
    
    # Test Brevo API
    api_result = test_brevo_api()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Brevo API Test: {'✅ PASSED' if api_result else '❌ FAILED'}")
    print("=" * 60)
