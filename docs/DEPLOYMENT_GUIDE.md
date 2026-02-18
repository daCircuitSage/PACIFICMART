# PACIFICMART - Deployment Guide for Render

## Pre-Deployment Checklist

### 1. Security & Credentials (**CRITICAL**)
- [ ] Remove `.env` file from git history: `git rm --cached .env && git commit -m "Remove .env from tracking"`
- [ ] Ensure `.env` is in `.gitignore`
- [ ] Generate new SECRET_KEY at https://djecrety.ir/
- [ ] Create new Cloudinary API credentials in dashboard
- [ ] Reset all passwords and API keys

### 2. Database Setup on Render
- [ ] Create PostgreSQL database on Render (free tier available)
- [ ] Copy connection string (DATABASE_URL)
- [ ] Verify database is created and accessible

### 3. Code Changes Applied ✓
- [x] Fixed `variation_category` CharField - added max_length=20
- [x] Changed monetary fields to DecimalField (order_total, tax, amount_paid, product_price)
- [x] Fixed INSTALLED_APPS to include bkash, nagad, cashOnDelevery
- [x] Added WhiteNoise middleware for static file serving
- [x] Fixed ALLOWED_HOSTS to use environment variable
- [x] Removed hardcoded ngrok URL from CSRF_TRUSTED_ORIGINS
- [x] Added STATICFILES_STORAGE configuration
- [x] Fixed render.yaml to use correct WSGI module (factors_Ecom)
- [x] Made static file serving conditional (development only)
- [x] Created migrations for all model changes
- [x] Fixed .gitignore merge conflict

## Step-by-Step Deployment

### Step 1: Apply Database Migrations Locally (Before Pushing)
```bash
python manage.py migrate
```

### Step 2: Collect Static Files Locally (for testing)
```bash
python manage.py collectstatic --no-input
```

### Step 3: Update Git and Push to Render
```bash
# Remove .env from history if committed
git rm --cached .env

# Verify changes
git status

# Commit all fixes
git add .
git commit -m "Fix: Django configuration for Render deployment, model field types, security settings"

# Push to main branch (triggers Render deployment)
git push origin main
```

### Step 4: Set Environment Variables on Render Dashboard
Go to your Render service dashboard:
1. Settings → Environment
2. Add all variables from `.env.example`:
   - SECRET_KEY (generate new)
   - DEBUG=False
   - ALLOWED_HOSTS=your-app.onrender.com
   - DATABASE_URL (from Render PostgreSQL dashboard)
   - CLOUDINARY_CLOUD_NAME
   - CLOUDINARY_API_KEY
   - CLOUDINARY_API_SECRET
   - EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS

### Step 5: Verify render.yaml Configuration
The following settings are already configured in `render.yaml`:
```yaml
buildCommand: './build.sh'
startCommand: 'python -m gunicorn factors_Ecom.asgi:application -k uvicorn.workers.UvicornWorker'
```

Note: `build.sh` will:
1. Install requirements
2. Collect static files (served by WhiteNoise)
3. Run migrations automatically

## Testing After Deployment

### Local Testing Before Deployment
```bash
# Set DEBUG=True in .env for testing
DEBUG=True

# Test with PostgreSQL locally if possible
python manage.py runserver
```

### Post-Deployment Testing
1. Visit https://your-app.onrender.com/admin/
2. Verify static files load (CSS, JS, images)
3. Test product image upload (should go to Cloudinary)
4. Test user profile picture upload
5. Add product and verify images display correctly

## Troubleshooting

### Issue: Static files not loading (404 errors)
**Solution:** Ensure WhiteNoise is configured in MIDDLEWARE and STATICFILES_STORAGE is set

### Issue: "Disallowed host" error
**Solution:** Add your Render domain to ALLOWED_HOSTS in environment variables
Example: `yourdomain-abc123.onrender.com`

### Issue: Image uploads failing
**Solution:** 
1. Verify CLOUDINARY credentials in environment variables
2. Check Cloudinary API key permissions
3. Ensure cloudinary and cloudinary_storage are in INSTALLED_APPS

### Issue: Database connection errors
**Solution:**
1. Verify DATABASE_URL is correct
2. Check PostgreSQL is running on Render
3. Run migrations: `python manage.py migrate`

### Issue: Email not sending
**Solution:**
1. Gmail: Use app-specific password instead of account password
2. Test SMTP credentials
3. For production, switch to SendGrid or AWS SES

## Performance Optimization

### WhiteNoise Configuration
The app now uses `CompressedManifestStaticFilesStorage` which:
- Gzips static files for faster delivery
- Adds content-hash to filenames for browser caching
- Reduces bandwidth significantly

### Cloudinary Integration
All image uploads use Cloudinary:
- Automatic image optimization
- CDN delivery worldwide
- Reduced storage cost
- Automatic format conversion

## Security Improvements Implemented

1. ✓ WhiteNoise middleware for secure static file serving
2. ✓ Removed hardcoded URLs from settings
3. ✓ All credentials use environment variables
4. ✓ .env file properly ignored in git
5. ✓ DEBUG=False for production
6. ✓ ALLOWED_HOSTS restricted to configured domains
7. ✓ CSRF_TRUSTED_ORIGINS configurable

## Future Enhancements

1. Add Django security headers (HSTS, CSP, X-Frame-Options)
2. Enable HTTPS redirect
3. Add database backups automation
4. Set up error tracking (Sentry)
5. Configure CDN for static files
6. Add rate limiting for API endpoints

## Common Issues After Migration

### Payment Calculations
Payment fields are now DecimalField. If you have code that treats them as strings, update:
```python
# OLD (will fail):
total = float(order.order_total)

# NEW (correct):
total = order.order_total  # Already a Decimal
```

### Variation Queries
Variation category queries still work the same:
```python
Variation.objects.filter(variation_category='color')
```

## Need Help?

1. Check Render logs: Dashboard → Logs
2. SSH into container: Dashboard → Connect Shell
3. Run migrations manually: `python manage.py migrate`
4. Check static files collected: `/opt/render/project/python3.11/lib/python3.11/site-packages/whitenoise/`

## Deployment Verification Checklist

- [ ] App loads without errors
- [ ] Admin panel accessible and styled correctly
- [ ] Product images display
- [ ] User profile pictures display
- [ ] Product upload works
- [ ] Orders can be placed
- [ ] Email notifications send (if configured)
- [ ] No 404 for static files (CSS, JS, fonts)
