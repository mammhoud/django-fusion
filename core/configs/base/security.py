# ====================================
# 🔐 Security Configuration
# ====================================
from datetime import timedelta

from ..settings.conf import settings

# -------------------------------
# Core Settings
# -------------------------------
SECRET_KEY = settings.DJANGO_SECRET_KEY
DEBUG = getattr(settings, "DEBUG", False)

# Get security settings with proper fallbacks
security_settings = getattr(settings, "SECURITY", {})

# -------------------------------
# Django Security
# -------------------------------
# Basic security settings
ALLOWED_HOSTS = getattr(
    settings,
    "ALLOWED_HOSTS",
    getattr(security_settings, "ALLOWED_HOSTS", ["localhost", "127.0.0.1"]),
)

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = getattr(
    security_settings, "CORS_ALLOW_ALL_ORIGINS", not settings.is_production
)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = getattr(security_settings, "CORS_ALLOWED_ORIGINS", [])

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = getattr(security_settings, "CSRF_TRUSTED_ORIGINS", [])
CSRF_COOKIE_SECURE = settings.is_production
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript access
CSRF_COOKIE_NAME = "csrftoken"
CSRF_HEADER_NAME = "X-CSRFToken"

# Session Configuration
SESSION_COOKIE_SECURE = settings.is_production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_SAMESITE = "Lax"

# HTTPS/SSL
SECURE_SSL_REDIRECT = settings.get("SECURE_SSL_REDIRECT", settings.is_production, cast=bool)
SECURE_HSTS_SECONDS = 31536000 if settings.is_production else 0
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# -------------------------------
# Password Configuration
# -------------------------------
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# Password validators only in production
AUTH_PASSWORD_VALIDATORS = []
if settings.is_production:
    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
            "OPTIONS": {"min_length": 8},
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
    ]

# -------------------------------
# JWT Settings
# -------------------------------
JWT_AUTH = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=365),
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# -------------------------------
# Authentication URLs
# -------------------------------
LOGIN_URL = "/auth/sign-in/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# -------------------------------
# File Upload Security
# -------------------------------
FILE_UPLOAD_MAX_MEMORY_SIZE = 26214400  # 25MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400  # 25MB

# -------------------------------
# Debugging Settings
# -------------------------------
INTERNAL_IPS = ["127.0.0.1", "localhost"]
