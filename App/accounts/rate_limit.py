"""
Rate limiting utilities for email verification resend functionality.
Uses cache-based rate limiting for Render free tier compatibility.
"""
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def can_resend_verification_email(user):
    """
    Check if user can resend verification email based on rate limit.
    Rate limit: 1 resend per 60 seconds per user.
    """
    cache_key = f"verification_email_resend_{user.pk}"
    
    # Check if user has resent email within last 60 seconds
    last_resend_time = cache.get(cache_key)
    
    if last_resend_time is not None:
        # User has resent email recently - calculate remaining time
        try:
            # Try to get TTL (time to live) - works in Django 3.2+
            remaining_time = cache.ttl(cache_key)
            if remaining_time is None or remaining_time <= 0:
                return True, 0
            return False, int(remaining_time)
        except AttributeError:
            # Fallback for older Django versions - assume 60 seconds
            return False, 60
    
    # User can resend email
    return True, 0


def mark_verification_email_sent(user):
    """
    Mark that verification email has been sent for rate limiting.
    Sets cache with 60-second TTL.
    """
    cache_key = f"verification_email_resend_{user.pk}"
    
    try:
        # Set cache with 60-second TTL
        cache.set(cache_key, True, timeout=60)
        logger.info(f"Rate limit set for user {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to set rate limit for user {user.email}: {str(e)}")
        # Don't fail the request if cache fails
        return False


def clear_verification_email_rate_limit(user):
    """
    Clear rate limit for user (useful for testing or admin override).
    """
    cache_key = f"verification_email_resend_{user.pk}"
    
    try:
        cache.delete(cache_key)
        logger.info(f"Rate limit cleared for user {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to clear rate limit for user {user.email}: {str(e)}")
        return False
