"""
Django settings for the CorrectWay project.

This project is a Python/Django rewrite of the original Node.js +
Express + MongoDB backend. Where the original used environment
variables (MONGO_URI, JWT_SECRET, PORT, CLIENT_ORIGIN — see
server/.env.example), this settings file reads the equivalent values
from a local .env file via python-decouple-style os.environ lookups,
falling back to sane development defaults.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env(key, default=None):
    return os.environ.get(key, default)


# SECURITY WARNING: keep the secret key used in production secret!
# Equivalent of the original JWT_SECRET in server/.env.example.
SECRET_KEY = env("DJANGO_SECRET_KEY", "django-insecure-correctway-dev-key-change-in-production")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DJANGO_DEBUG", "False") == "True"

allowed_hosts = [host.strip() for host in env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,.vercel.app").split(",") if host.strip()]
vercel_host = env("VERCEL_URL")
if vercel_host:
    allowed_hosts.append(vercel_host)
ALLOWED_HOSTS = allowed_hosts

CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in env("CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()]
if vercel_host:
    CSRF_TRUSTED_ORIGINS.append(f"https://{vercel_host}")

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "careers",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "correctway.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.csrf",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "careers.context_processors.site_languages",
            ],
        },
    },
]

WSGI_APPLICATION = "correctway.wsgi.application"

# Database
# The original project used MongoDB via Mongoose (server/config/db.js).
# Django's ORM here uses SQLite by default (zero-config, file-based),
# but any Django-supported database (PostgreSQL, MySQL, etc.) can be
# swapped in by changing this block — set DATABASE_URL-style env vars
# and update ENGINE/NAME/USER/PASSWORD/HOST/PORT accordingly.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 6},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Use signed-cookie sessions so the site can run without database-backed
# session tables like django_session when migrations are not yet applied.
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Auth / login redirects (session-based auth replaces the original JWT
# bearer-token auth from server/middleware/auth.js)
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "quiz"
LOGOUT_REDIRECT_URL = "home"

# CORS is not needed since the frontend is now served by Django itself
# rather than a separate Vite dev server (original CLIENT_ORIGIN setting
# is therefore no longer required).
