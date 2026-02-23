# Brevo Email Integration Setup

This document explains the Brevo email integration for PacificMart e-commerce project.

## Overview

The project now uses Brevo HTTP API for email delivery, which works on Render Free tier (SMTP is blocked).

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Brevo Configuration
BREVO_API_KEY=your-brevo-api-key-here
BREVO_SENDER_EMAIL=your-sender-email@example.com
BREVO_SENDER_NAME=PacificMart
```

### Getting Brevo API Key

1. Go to [Brevo Dashboard](https://app.brevo.com/)
2. Navigate to Settings → API & SMTP → API Keys
3. Create a new Standard API key
4. Copy the key and add to `BREVO_API_KEY`

## Implementation

### Core Email Utility

Location: `factors_Ecom/utils.py`

Main functions:
- `send_brevo_email()` - Generic email sender
- `send_registration_email()` - User registration verification
- `send_password_reset_email()` - Password reset functionality
- `send_order_confirmation_email()` - Order confirmation

### Email Features Enabled

1. **User Registration Email** (`accounts/views.py`)
   - Sends account verification email
   - Uses template: `accounts/account_verification_email.html`

2. **Password Reset Email** (`accounts/views.py`)
   - Sends password reset link
   - Uses template: `accounts/reset_password_email.html`

3. **Order Confirmation Emails**
   - **bKash** (`bkash/views.py`)
   - **Nagad** (`nagad/views.py`)
   - **Cash on Delivery** (`cashOnDelevery/views.py`)
   - Uses template: `orders/order_recieved_email.html`

## Testing

Run the test script to verify configuration:

```bash
cd App
python test_email.py
```

Remember to update the test email in the script before running.

## Error Handling

- Email failures are logged but don't break user flows
- Users see appropriate success/warning messages
- All email calls include try-catch blocks

## Production Deployment

On Render Free tier:
1. Set environment variables in Render dashboard
2. The code automatically reads from environment variables
3. No SMTP configuration needed

## Security

- API keys are read from environment variables only
- No hardcoded secrets in the codebase
- `.env` file is in `.gitignore`

## Benefits

✅ Works on Render Free tier (no SMTP required)
✅ Reliable HTTP API delivery
✅ Easy configuration
✅ Production-ready error handling
✅ No Django SMTP backend dependency
