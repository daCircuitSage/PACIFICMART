# Django Production Deployment Checklist - Render Free Plan

## ✅ Pre-Deployment Requirements

### 1. Environment Variables Setup
- [ ] Copy `.env.example` to `.env` with production values
- [ ] Set `SECRET_KEY` to a secure generated value
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS` with your Render domain
- [ ] Set `CSRF_TRUSTED_ORIGINS` with your HTTPS domain
- [ ] Configure `DATABASE_URL` with Render PostgreSQL connection string
- [ ] Set up Cloudinary credentials (`CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`)
- [ ] Configure email settings (`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`)

### 2. Database Setup
- [ ] PostgreSQL database created on Render
- [ ] Database connection string copied to environment variables
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Test database connectivity

### 3. Static & Media Files
- [ ] Cloudinary account configured
- [ ] Static files collected: `python manage.py collectstatic --no-input`
- [ ] Whitenoise middleware properly configured
- [ ] Cloudinary storage working for media files

### 4. Security Configuration
- [ ] `DEBUG=False` in production
- [ ] `SECRET_KEY` is secure and unique
- [ ] `ALLOWED_HOSTS` includes your Render domain
- [ ] `CSRF_TRUSTED_ORIGINS` set for HTTPS
- [ ] SSL redirect enabled (`SECURE_SSL_REDIRECT=True`)
- [ ] Secure cookies enabled (`SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`)

### 5. Email Configuration
- [ ] SMTP server configured (Gmail/SendGrid/AWS SES)
- [ ] Email backend set correctly
- [ ] Test email sending functionality
- [ ] Email templates working for verification and password reset

### 6. Authentication & Sessions
- [ ] User registration working
- [ ] Email verification process functional
- [ ] Password reset working
- [ ] Login/logout functioning properly
- [ ] Session management configured

## 🚀 Deployment Steps

### 1. Render Configuration
- [ ] `render.yaml` file properly configured
- [ ] Database service created
- [ ] Web service configured with correct build/start commands
- [ ] Environment variables set in Render dashboard

### 2. Build Process
- [ ] `build.sh` script executable
- [ ] Dependencies install correctly
- [ ] Static files collection succeeds
- [ ] Migrations run successfully

### 3. Post-Deployment Testing
- [ ] Homepage loads correctly
- [ ] User registration works
- [ ] Email verification received
- [ ] Login/logout functional
- [ ] Admin panel accessible
- [ ] Static files loading
- [ ] Media uploads working
- [ ] All pages return 200 status

## 🔧 Common Issues & Solutions

### Email Issues
- **Problem**: 500 error during registration
- **Solution**: Check `EMAIL_BACKEND` and SMTP credentials
- **Fix**: Ensure all email environment variables are set

### CSRF Issues
- **Problem**: CSRF token missing or incorrect
- **Solution**: Add domain to `CSRF_TRUSTED_ORIGINS`
- **Fix**: Ensure HTTPS is properly configured

### Database Issues
- **Problem**: Connection refused
- **Solution**: Check `DATABASE_URL` format
- **Fix**: Ensure SSL is enabled for PostgreSQL

### Static Files Issues
- **Problem**: 404 errors for CSS/JS
- **Solution**: Run `collectstatic` command
- **Fix**: Check Whitenoise configuration

## 📊 Environment Variables Reference

### Required Variables
```
SECRET_KEY=your-secure-secret-key
DEBUG=False
ALLOWED_HOSTS=thepacificmart.onrender.com,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://thepacificmart.onrender.com
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### Optional Variables
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

## 🎯 Production Optimizations

### Performance
- [ ] Database connection pooling configured
- [ ] Static files compressed and cached
- [ ] CDN configured for media files (Cloudinary)
- [ ] Gunicorn workers optimized

### Monitoring
- [ ] Error logging configured
- [ ] Performance monitoring set up
- [ ] Database query optimization
- [ ] Memory usage monitoring

### Security
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] Rate limiting implemented
- [ ] Input validation enforced

## 🚨 Emergency Rollback Plan

### If Deployment Fails
1. Check Render build logs for errors
2. Verify environment variables are correct
3. Check database connectivity
4. Review static files collection
5. Test email configuration separately

### Quick Fixes
- **500 Errors**: Check missing environment variables
- **Static File 404s**: Run `collectstatic` again
- **Database Errors**: Verify connection string
- **Email Failures**: Test SMTP credentials

## 📞 Support Resources

### Render Documentation
- [Render Django Deployment Guide](https://render.com/docs/deploy-django)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Render PostgreSQL](https://render.com/docs/postgresql)

### Django Documentation
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Django Static Files](https://docs.djangoproject.com/en/stable/howto/static-files/deployment/)

---

## ✅ Final Verification

Before going live, ensure:
- [ ] All tests pass
- [ ] Admin panel accessible
- [ ] User registration works
- [ ] Email verification functional
- [ ] Payment gateways configured
- [ ] SSL certificate active
- [ ] Domain pointing correctly
- [ ] Monitoring enabled

Your Django application is now production-ready for Render free plan deployment!
