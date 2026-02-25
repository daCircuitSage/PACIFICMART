"""
Email verification token system.
Uses Django's default token generator with custom hash for email verification.
"""
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Custom token generator for email verification.
    Uses user's email verification status and timestamp to create secure tokens.
    Tokens are automatically invalidated after email verification.
    """
    
    def _make_hash_value(self, user, timestamp):
        """
        Create hash for token generation.
        Includes user's primary key, timestamp, and email verification status.
        This ensures tokens become invalid after verification.
        """
        return str(user.pk) + str(timestamp) + str(user.is_email_verified)


account_activation_token = AccountActivationTokenGenerator()
