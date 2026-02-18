# location: App/factors_Ecom/validators.py

import re
from django.core.exceptions import ValidationError






"""
This module contains custom validators for different purposes.

The custom validators are defined in this module to make the code more organized and reusable.
Validators are functions that validate the input data according to some rules.
They are used to validate the format, length, and content of input data.

The validators in this module are:
- validate_bangladeshi_phone_number: Validates Bangladeshi phone number format.
  It checks if the phone number starts with '01' and has exactly 11 digits.

The validate_bangladeshi_phone_number function takes a phone number as input and raises a ValidationError
if the phone number is not in the correct format.

"""


def validate_bangladeshi_phone_number(phone_number):
    """
    Validates Bangladeshi phone number format
    
    Args:
        phone_number (str): Phone number to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If phone number is invalid
    """
    phone_number = str(phone_number).strip()

    # Reject if any non-digit character exists
    if not phone_number.isdigit():
        raise ValidationError(
            'Phone number must contain only digits.'
        )

    # Check if it's exactly 11 digits and starts with valid BD mobile prefix
    if re.fullmatch(r'01[3-9]\d{8}', phone_number):
        return True
    
    raise ValidationError(
        'Please enter a valid Bangladeshi phone number (01XXXXXXXXX)'
    )

def is_valid_bangladeshi_phone(phone_number):
    """
    Simple boolean check for Bangladeshi phone number
    
    Args:
        phone_number (str): Phone number to validate
        
    Returns:
        bool: True if valid, False if invalid
    """
    try:
        validate_bangladeshi_phone_number(phone_number)
        return True
    except ValidationError:
        return False

# testcases
# print(is_valid_bangladeshi_phone('@01777046105'))  # False
# print(is_valid_bangladeshi_phone('01777046105'))  # True
