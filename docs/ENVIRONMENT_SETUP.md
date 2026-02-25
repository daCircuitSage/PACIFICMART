# Environment Setup Guide

This document contains all the environment variables needed to run the PacificMart application.

## Required Environment Variables

### 1. Basic Django Configuration
```bash
SECRET_KEY=your-secret-key-here
DEBUG=False  # Set to True for development
ALLOWED_HOSTS=yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

### 2. Database Configuration
```bash
DATABASE_URL=postgresql://username:password@host:port/database_name
```

### 3. Brevo Email Configuration
```bash
BREVO_API_KEY=your-brevo-api-key-here
BREVO_SENDER_EMAIL=your-sender-email@gmail.com
BREVO_SENDER_NAME=Your-App-Name
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
```

### 4. Cloudinary Configuration (for media files)
```bash
CLOUDINARY_CLOUD_NAME=your-cloudinary-cloud-name
CLOUDINARY_API_KEY=your-cloudinary-api-key
CLOUDINARY_API_SECRET=your-cloudinary-api-secret
```

## Render.com Setup Steps

1. **Go to your Render Dashboard**
2. **Select your Django service**
3. **Go to Environment tab**
4. **Add all the environment variables listed above**

## Testing Email Configuration

To test email configuration in development:

```python
from django.core.mail import EmailMessage
from django.conf import settings

def test_email():
    send_email = EmailMessage(
        subject='Test Email',
        body='This is a test email',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=['test@example.com']
    )
    result = send_email.send(fail_silently=False)
    return result == 1
```

## Security Notes

- Never commit actual API keys or secrets to version control
- Use environment variables for all sensitive data
- Rotate API keys regularly
- Use different credentials for development and production
