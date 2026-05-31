# ====================================
# 🔐 Security Configuration
# ====================================
from datetime import timedelta

from ..settings.setup import settings

SECURITY_BLOCK = "SECURITY"

# -------------------------------
# Core Settings
# -------------------------------
SECRET_KEY = settings.DJANGO_SECRET_KEY
DEBUG = settings.get("DEBUG", False, cast=bool)
SITE_URL = settings.get("SITE_URL", "http://localhost:8000")

# -------------------------------
# Django Security
# -------------------------------
ALLOWED_HOSTS = settings.get_list(
    "ALLOWED_HOSTS",
    [
        "localhost",
        "127.0.0.1",
        "vresume.structa.cloud",
        "docs.vresume.structa.cloud",
        "vresume-website",
        "docs",
    ],
    block=SECURITY_BLOCK,
    env="ALLOWED_HOSTS",
)

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = settings.get_bool(
    "CORS_ALLOW_ALL_ORIGINS", not settings.is_production, block=SECURITY_BLOCK
)
CORS_ALLOW_CREDENTIALS = settings.get_bool("CORS_ALLOW_CREDENTIALS", True, block=SECURITY_BLOCK)
CORS_ALLOWED_ORIGINS = settings.get_list(
    "CORS_ALLOWED_ORIGINS", [], block=SECURITY_BLOCK, env="CORS_ALLOWED_ORIGINS"
)
CORS_EXPOSE_HEADERS = settings.get_list("CORS_EXPOSE_HEADERS", [], block=SECURITY_BLOCK)

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = settings.get_list(
    "CSRF_TRUSTED_ORIGINS",
    ["http://localhost:8000", "https://vresume.structa.cloud"],
    block=SECURITY_BLOCK,
    env="CSRF_TRUSTED_ORIGINS",
)
CSRF_COOKIE_NAME = settings.get("CSRF_COOKIE_NAME", "csrftoken", block=SECURITY_BLOCK)
CSRF_HEADER_NAME = settings.get("CSRF_HEADER_NAME", "X-CSRFToken", block=SECURITY_BLOCK)
CSRF_COOKIE_HTTPONLY = settings.get_bool("CSRF_COOKIE_HTTPONLY", False, block=SECURITY_BLOCK)
CSRF_COOKIE_SECURE = settings.get_bool(
    "CSRF_COOKIE_SECURE",
    settings.is_production,
    block=SECURITY_BLOCK,
    env="CSRF_COOKIE_SECURE",
)
CSRF_COOKIE_SAMESITE = settings.get("CSRF_COOKIE_SAMESITE", "Lax", block=SECURITY_BLOCK)
CSRF_USE_SESSIONS = settings.get_bool("CSRF_USE_SESSIONS", False, block=SECURITY_BLOCK)

# Session Configuration
SESSION_COOKIE_NAME = settings.get("SESSION_COOKIE_NAME", "sessionid", block=SECURITY_BLOCK)
SESSION_COOKIE_AGE = settings.get_int("SESSION_COOKIE_AGE", 1209600, block=SECURITY_BLOCK)
SESSION_COOKIE_HTTPONLY = settings.get_bool("SESSION_COOKIE_HTTPONLY", True, block=SECURITY_BLOCK)
SESSION_COOKIE_SECURE = settings.get_bool(
    "SESSION_COOKIE_SECURE",
    settings.is_production,
    block=SECURITY_BLOCK,
    env="SESSION_COOKIE_SECURE",
)
SESSION_COOKIE_SAMESITE = settings.get("SESSION_COOKIE_SAMESITE", "Lax", block=SECURITY_BLOCK)
SESSION_ENGINE = settings.get(
    "SESSION_ENGINE", "django.contrib.sessions.backends.db", block=SECURITY_BLOCK
)

# HTTPS/SSL Security
SECURE_SSL_REDIRECT = settings.get_bool(
    "SECURE_SSL_REDIRECT",
    settings.is_production,
    block=SECURITY_BLOCK,
    env="SECURE_SSL_REDIRECT",
)
SECURE_PROXY_SSL_HEADER = settings.get(
    "SECURE_PROXY_SSL_HEADER",
    ("HTTP_X_FORWARDED_PROTO", "https"),
    block=SECURITY_BLOCK,
)
USE_X_FORWARDED_HOST = True
SECURE_HSTS_SECONDS = settings.get_int(
    "SECURE_HSTS_SECONDS", 31536000 if settings.is_production else 0, block=SECURITY_BLOCK
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = settings.get_bool(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", True, block=SECURITY_BLOCK
)
SECURE_HSTS_PRELOAD = settings.get_bool(
    "SECURE_HSTS_PRELOAD", False, block=SECURITY_BLOCK, env="SECURE_HSTS_PRELOAD"
)
SECURE_REFERRER_POLICY = settings.get("SECURE_REFERRER_POLICY", "same-origin", block=SECURITY_BLOCK)

# Headers Security
X_FRAME_OPTIONS = settings.get("X_FRAME_OPTIONS", "DENY", block=SECURITY_BLOCK)
SECURE_CONTENT_TYPE_NOSNIFF = settings.get_bool(
    "SECURE_CONTENT_TYPE_NOSNIFF", True, block=SECURITY_BLOCK
)
SECURE_BROWSER_XSS_FILTER = settings.get_bool(
    "SECURE_BROWSER_XSS_FILTER", True, block=SECURITY_BLOCK
)

# -------------------------------
# Password Configuration
# -------------------------------
PASSWORD_HASHERS = settings.get(
    "PASSWORD_HASHERS",
    [
        "django.contrib.auth.hashers.PBKDF2PasswordHasher",
        "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
        "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    ],
    block=SECURITY_BLOCK,
)

AUTH_PASSWORD_VALIDATORS = []
if settings.is_production:
    AUTH_PASSWORD_VALIDATORS = [
        {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
            "OPTIONS": {"min_length": 8},
        },
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ]

# -------------------------------
# Rate Limiting
# -------------------------------
RATE_LIMIT_ENABLED = settings.get_bool("RATE_LIMIT_ENABLED", False, block=SECURITY_BLOCK)

# -------------------------------
# JWT Settings
# -------------------------------
JWT_AUTH = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        days=settings.get_int("JWT_ACCESS_TOKEN_LIFETIME_DAYS", 30, block=SECURITY_BLOCK)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=settings.get_int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", 365, block=SECURITY_BLOCK)
    ),
    "ALGORITHM": settings.get("JWT_ALGORITHM", "HS256", block=SECURITY_BLOCK),
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": tuple(
        settings.get_list("JWT_AUTH_HEADER_TYPES", ("Bearer",), block=SECURITY_BLOCK)
    ),
    "USER_ID_FIELD": settings.get("JWT_USER_ID_FIELD", "id", block=SECURITY_BLOCK),
    "USER_ID_CLAIM": settings.get("JWT_USER_ID_CLAIM", "user_id", block=SECURITY_BLOCK),
}

# -------------------------------
# Authentication URLs
# -------------------------------
LOGIN_URL = settings.get("LOGIN_URL", "/auth/sign-in/", block=SECURITY_BLOCK)
LOGIN_REDIRECT_URL = settings.get("LOGIN_REDIRECT_URL", "/", block=SECURITY_BLOCK)
LOGOUT_REDIRECT_URL = settings.get("LOGOUT_REDIRECT_URL", "/", block=SECURITY_BLOCK)

# -------------------------------
# File Upload Security
# -------------------------------
FILE_UPLOAD_MAX_MEMORY_SIZE = settings.get_int(
    "FILE_UPLOAD_MAX_MEMORY_SIZE", 26214400, block=SECURITY_BLOCK
)
DATA_UPLOAD_MAX_MEMORY_SIZE = settings.get_int(
    "DATA_UPLOAD_MAX_MEMORY_SIZE", 26214400, block=SECURITY_BLOCK
)

# -------------------------------
# Debugging Settings
# -------------------------------
INTERNAL_IPS = ["127.0.0.1", "localhost"]
