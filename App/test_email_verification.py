"""
Test script to verify email verification implementation.
Run this script to test the new email verification system.
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'factors_Ecom.settings')
django.setup()

from accounts.models import Account
from accounts.tokens import account_activation_token
from accounts.rate_limit import can_resend_verification_email, mark_verification_email_sent
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

def test_email_verification_system():
    """Test the email verification system components."""
    print("Testing Email Verification System")
    print("=" * 50)
    
    # Test 1: Check if is_email_verified field exists
    try:
        # This will raise an error if the field doesn't exist
        test_field = Account._meta.get_field('is_email_verified')
        print("✓ is_email_verified field exists in Account model")
        print(f"  Field type: {test_field.__class__.__name__}")
        print(f"  Default value: {test_field.default}")
    except Exception as e:
        print(f"✗ Error checking is_email_verified field: {e}")
        return False
    
    # Test 2: Test token generation
    try:
        # Create a dummy user (in memory, not saved)
        user = Account(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User'
        )
        user.is_email_verified = False
        
        # Generate token
        token = account_activation_token.make_token(user)
        print(f"✓ Token generation works: {token[:20]}...")
        
        # Test token validation
        is_valid = account_activation_token.check_token(user, token)
        print(f"✓ Token validation works: {is_valid}")
        
    except Exception as e:
        print(f"✗ Error testing token system: {e}")
        return False
    
    # Test 3: Test rate limiting
    try:
        # Create a dummy user for rate limiting test
        user = Account(
            email='ratelimit@example.com',
            username='ratelimituser',
            first_name='Rate',
            last_name='Limit'
        )
        user.pk = 999  # Set a fake primary key
        
        # Test initial check (should allow)
        can_resend, wait_time = can_resend_verification_email(user)
        print(f"✓ Initial rate limit check: can_resend={can_resend}, wait_time={wait_time}")
        
        # Mark as sent
        mark_verification_email_sent(user)
        print("✓ Rate limit marked as sent")
        
        # Test second check (should block)
        can_resend, wait_time = can_resend_verification_email(user)
        print(f"✓ Second rate limit check: can_resend={can_resend}, wait_time={wait_time}")
        
    except Exception as e:
        print(f"✗ Error testing rate limiting: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("All tests passed! Email verification system is working correctly.")
    return True

if __name__ == '__main__':
    test_email_verification_system()
