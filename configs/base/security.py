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
import ast

def _parse_hosts(raw):
    """Parse ALLOWED_HOSTS from various formats dynaconf may produce."""
    if raw is None:
        return ["localhost", "127.0.0.1"]
    if isinstance(raw, list):
        return [str(h).strip() for h in raw if str(h).strip()]
    if isinstance(raw, str):
        val = raw.strip()
        # Handle stringified Python list: "['a', 'b']"
        if val.startswith("[") and val.endswith("]"):
            try:
                parsed = ast.literal_eval(val)
                return [str(h).strip() for h in parsed if str(h).strip()]
            except (ValueError, SyntaxError):
                pass
        # Handle comma-separated string
        return [h.strip() for h in val.split(",") if h.strip()]
    return ["localhost", "127.0.0.1"]

# Basic security settings — check top-level first, then SECURITY block
_allowed_hosts_raw = getattr(settings, "ALLOWED_HOSTS", None) or getattr(
    security_settings, "ALLOWED_HOSTS", None
)
ALLOWED_HOSTS = _parse_hosts(_allowed_hosts_raw)

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = getattr(
    security_settings, "CORS_ALLOW_ALL_ORIGINS", not settings.is_production
)
CORS_ALLOW_CREDENTIALS = True
_cors_raw = getattr(security_settings, "CORS_ALLOWED_ORIGINS", [])
if isinstance(_cors_raw, str):
    CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_raw.split(",") if o.strip()]
else:
    CORS_ALLOWED_ORIGINS = list(_cors_raw)

# CSRF Configuration
_csrf_raw = getattr(security_settings, "CSRF_TRUSTED_ORIGINS", [])
if isinstance(_csrf_raw, str):
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_raw.split(",") if o.strip()]
else:
    CSRF_TRUSTED_ORIGINS = list(_csrf_raw)
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
# SSL redirect is handled by Traefik — disable in Django to avoid redirect loops
# and allow Traefik's internal health checks over plain HTTP
SECURE_SSL_REDIRECT = False
# Trust Traefik's X-Forwarded-Proto header so Django knows the request is HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
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
