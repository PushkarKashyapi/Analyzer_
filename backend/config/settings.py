"""
Django settings for Social Media Content Analyzer.

Production Ready
- Render + Docker
- React (Vite Frontend)
- WhiteNoise
- CORS Enabled
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# =============================================================================
# BASE DIRECTORY
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# LOAD ENV VARIABLES
# =============================================================================

load_dotenv(BASE_DIR / ".env")

# =============================================================================
# SECURITY
# =============================================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-dev-secret-key"
)

DEBUG = os.getenv("DEBUG", "False") == "True"

# Allow Render + Localhost
ALLOWED_HOSTS = ["*"]

# =============================================================================
# INSTALLED APPS
# =============================================================================

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third Party
    "rest_framework",
    "corsheaders",

    # Local
    "analyzer",
]

# =============================================================================
# MIDDLEWARE
# =============================================================================

MIDDLEWARE = [
    # CORS MUST BE FIRST
    "corsheaders.middleware.CorsMiddleware",

    # Security
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    # Django
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# =============================================================================
# URL CONFIGURATION
# =============================================================================

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

# =============================================================================
# TEMPLATES
# =============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# =============================================================================
# DATABASE (SQLite)
# =============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC FILES (WhiteNoise)
# =============================================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

# =============================================================================
# MEDIA FILES
# =============================================================================

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =============================================================================
# CORS CONFIGURATION
# =============================================================================

# Allow React locally and deployed frontend
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://analyzer-1-272f.onrender.com",
]

CORS_ALLOW_HEADERS = [
    "*",
]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# =============================================================================
# CSRF TRUSTED ORIGINS
# =============================================================================

CSRF_TRUSTED_ORIGINS = [
    "https://analyzer-1-272f.onrender.com",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# =============================================================================
# DJANGO REST FRAMEWORK
# =============================================================================

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
}

# =============================================================================
# GEMINI AI
# =============================================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# =============================================================================
# MONGODB (OPTIONAL)
# =============================================================================

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

# =============================================================================
# DEFAULT PRIMARY KEY
# =============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# RENDER / DOCKER SECURITY SETTINGS
# =============================================================================

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

USE_X_FORWARDED_HOST = True

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

SECURE_SSL_REDIRECT = False
