"""
Django settings for config project.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load `.env` if present (local dev). On the server, set the same variables in the host environment.
load_dotenv(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-&b0sm4$y3=4nkqm(#)np@b1atwcdc@u_$t_#-3&vw-kw$v2at$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'activities',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'config.context_processors.email_backend',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'teaching_activities',
        'USER': 'abhijnyakg',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Media files (activity materials stored on server)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Auth (TeachOrange)
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/activities/"
LOGOUT_REDIRECT_URL = "/"
# Email — same code path everywhere; only the *source* of env vars changes:
# - Local: put values in `.env` (see `.env.example`; file is gitignored).
# - Deployed: set the same DJANGO_* variables in your host (Render, Railway, systemd, etc.).
#
# If DJANGO_EMAIL_HOST and DJANGO_EMAIL_HOST_USER are set → real SMTP.
# Otherwise → console backend (terminal locally, or application/server logs when deployed).
DEFAULT_FROM_EMAIL = os.environ.get(
    "DJANGO_DEFAULT_FROM_EMAIL", "TeachOrange <noreply@teachorange.local>"
)
EMAIL_HOST = os.environ.get("DJANGO_EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("DJANGO_EMAIL_PORT", "587"))
_tls = os.environ.get("DJANGO_EMAIL_USE_TLS", "1").lower() not in ("0", "false", "no")
EMAIL_USE_TLS = _tls
EMAIL_USE_SSL = os.environ.get("DJANGO_EMAIL_USE_SSL", "0").lower() in ("1", "true", "yes")
# Port 465 often uses SSL, not STARTTLS — if USE_SSL is set, default TLS off unless explicitly set.
if EMAIL_USE_SSL and "DJANGO_EMAIL_USE_TLS" not in os.environ:
    EMAIL_USE_TLS = False
EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_HOST_PASSWORD", "")
if os.environ.get("DJANGO_EMAIL_BACKEND"):
    EMAIL_BACKEND = os.environ["DJANGO_EMAIL_BACKEND"]
elif EMAIL_HOST and EMAIL_HOST_USER:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# Sign-up: require email to end with one of these suffixes (lowercased)
ALLOWED_EMAIL_SUFFIXES = (".edu",)
