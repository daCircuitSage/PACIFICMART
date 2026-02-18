from pathlib import Path
from decouple import config
import dj_database_url
import cloudinary

# environment variables
import dotenv
dotenv.load_dotenv()


# ================= BASE =================
BASE_DIR = Path(__file__).resolve().parent.parent

# ================= SITE CONFIGURATION =================
SITE_ID = 1

# ================= SECURITY =================
SECRET_KEY = config('SECRET_KEY', default='unsafe-secret-key')
DEBUG = config('DEBUG', default=False, cast=bool)
# DEBUG = True

# ================= HOST & CSRF =================
ALLOWED_HOSTS = [host.strip() for host in config('ALLOWED_HOSTS', default='localhost,127.0.0.1,localhost:8001').split(',') if host.strip()]
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in config('CSRF_TRUSTED_ORIGINS', default='http://127.0.0.1:8001,http://localhost:8001').split(',') if origin.strip()]

# Add default trusted origins for production
# if not DEBUG and not CSRF_TRUSTED_ORIGINS:
#     CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = not DEBUG

# ================= APPS =================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required for get_current_site()

    # custom apps
    'category',
    'accounts',
    'product',
    'cart',
    'orders',
    'bkash',
    'nagad',
    'cashOnDelevery',

    # third party
    'widget_tweaks',
    'cloudinary',
    'cloudinary_storage',
]

# ================= MIDDLEWARE =================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ================= URLS =================
ROOT_URLCONF = 'factors_Ecom.urls'

# ================= TEMPLATES =================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'category.context_processors.menu_links',
                'cart.context_processors.counter',
                'accounts.context_processors.user_profile',
            ],
        },
    },
]

# ================= WSGI =================
WSGI_APPLICATION = 'factors_Ecom.wsgi.application'

# ================= DATABASE =================
DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL', default='sqlite:///' + str(BASE_DIR / 'db.sqlite3')),
        conn_max_age=600,
    )
}

# Additional database options for PostgreSQL
if 'postgresql' in config('DATABASE_URL', default=''):
    DATABASES['default'].update({
        'OPTIONS': {
            'sslmode': 'require',
        }
    })

# ================= AUTH =================
AUTH_USER_MODEL = 'accounts.Account'

# ================= PASSWORD VALIDATORS =================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ================= INTERNATIONAL =================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

# ================= STATIC =================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'factors_Ecom' / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Static file caching settings
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_MAX_AGE = 31536000  # 1 year for production
WHITENOISE_IMMUTABLE_FILE_TEST = r'\.[0-9a-f]{8,}\.'

# ================= MEDIA (Cloudinary) =================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  # Required for development fallback
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET'),
}

cloudinary.config(
    cloud_name=config('CLOUDINARY_CLOUD_NAME'),
    api_key=config('CLOUDINARY_API_KEY'),
    api_secret=config('CLOUDINARY_API_SECRET'),
)

# ================= CACHING =================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes default
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    }
}

# ================= SESSION =================
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_SAVE_EVERY_REQUEST = False

# ================= CSRF =================
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_AGE = 31449600
CSRF_COOKIE_SAMESITE = 'Lax'

# ================= EMAIL =================
# EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

EMAIL_BACKEND ='django.core.mail.backends.smtp.EmailBackend' # to mail
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # to console

# Use Gmail SMTP in both development and production
if not DEBUG:
    # Production settings - use Gmail SMTP
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
else:
    # Development settings - same Gmail SMTP
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# Email timeout settings for production
EMAIL_TIMEOUT = 30  # 30 seconds timeout
EMAIL_FAIL_SILENTLY = False  # Show errors for debugging

# Email fallback for development
if DEBUG and not EMAIL_HOST_USER:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ================= MESSAGE TAGS =================
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {messages.ERROR: "danger"}

# ================= DEFAULT =================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================= URL SLASH =================
APPEND_SLASH = True # fixed // problem

# couldn't login so added this
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# ================= END =================