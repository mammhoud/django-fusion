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

# Get security settings with site/domain defaults injected from sites.yml.
security_settings = settings.section("SECURITY")

# -------------------------------
# Django Security
# -------------------------------
def _as_list(value):
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    if isinstance(value, (tuple, set)):
        return list(value)
    return value or []


_security_map = settings.setting_map(
    {
        "ALLOWED_HOSTS": ("ALLOWED_HOSTS", ["localhost", "127.0.0.1"], list),
        "CORS_ALLOW_ALL_ORIGINS": ("CORS_ALLOW_ALL_ORIGINS", not settings.is_production, bool),
        "CORS_ALLOWED_ORIGINS": ("CORS_ALLOWED_ORIGINS", [], list),
        "CSRF_TRUSTED_ORIGINS": ("CSRF_TRUSTED_ORIGINS", [], list),
        "CSRF_COOKIE_SECURE": ("CSRF_COOKIE_SECURE", settings.is_production, bool),
    },
    block="SECURITY",
)
# Get ALLOWED_HOSTS from environment variable or settings
import os
_env_allowed_hosts = os.environ.get("ALLOWED_HOSTS", "")
if _env_allowed_hosts:
    ALLOWED_HOSTS = _as_list(_env_allowed_hosts)
else:
    ALLOWED_HOSTS = _as_list(_security_map["ALLOWED_HOSTS"])
CORS_ALLOW_ALL_ORIGINS = _security_map["CORS_ALLOW_ALL_ORIGINS"]
CORS_ALLOW_CREDENTIALS = not CORS_ALLOW_ALL_ORIGINS
CORS_ALLOWED_ORIGINS = _as_list(_security_map["CORS_ALLOWED_ORIGINS"])
CSRF_TRUSTED_ORIGINS = _as_list(_security_map["CSRF_TRUSTED_ORIGINS"])
CSRF_COOKIE_SECURE = _security_map["CSRF_COOKIE_SECURE"]
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript access
CSRF_COOKIE_NAME = "csrftoken"
CSRF_HEADER_NAME = "X-CSRFToken"

# Session Configuration
SESSION_COOKIE_SECURE = settings.get_bool("SESSION_COOKIE_SECURE", settings.is_production, block="SECURITY")
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_SAMESITE = "Lax"

# HTTPS/SSL
SECURE_SSL_REDIRECT = settings.get_bool("SECURE_SSL_REDIRECT", False, block="SECURITY")
SECURE_HSTS_SECONDS = 31536000 if settings.is_production else 0
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# Proxy SSL header — set when behind a reverse proxy (e.g. Traefik) that terminates TLS
_proxy_ssl_header = settings.get("SECURE_PROXY_SSL_HEADER", None, block="SECURITY")
if _proxy_ssl_header:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# -------------------------------
# Password Configuration
# -------------------------------
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

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
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# -------------------------------
# Authentication URLs
# -------------------------------
LOGIN_URL = "/accounts/login/"
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
