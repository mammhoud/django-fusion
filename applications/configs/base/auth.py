"""
Authentication Configuration
-----------------------------

Django-only authentication settings for VResume.
Allauth and all social/MFA/headless settings have been removed.

References:
- Django auth: https://docs.djangoproject.com/en/stable/ref/settings/#auth
- Django sessions: https://docs.djangoproject.com/en/stable/ref/settings/#sessions
- Django CSRF: https://docs.djangoproject.com/en/stable/ref/csrf/
"""

from ..settings.conf import settings as conf_settings
from ..settings.setup import settings

# =============================================================================
# 🔐 AUTHENTICATION BACKENDS
# =============================================================================

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# =============================================================================
# 📍 REDIRECTION SETTINGS
# =============================================================================

LOGIN_REDIRECT_URL = settings.get("AUTH_LOGIN_REDIRECT_URL", "/")
LOGOUT_REDIRECT_URL = settings.get("AUTH_LOGOUT_REDIRECT_URL", "/")
# LOGIN_URL = settings.get("AUTH_LOGIN_URL", "/accounts/login/")
# LOGOUT_URL = settings.get("AUTH_LOGOUT_URL", "/accounts/logout/")

# # Wagtail integration
# WAGTAIL_FRONTEND_LOGIN_URL = settings.get("AUTH_WAGTAIL_LOGIN_URL", LOGIN_URL)
# WAGTAILADMIN_LOGIN_URL = settings.get("AUTH_WAGTAILADMIN_LOGIN_URL", LOGIN_URL)
WAGTAIL_LOGOUT_REDIRECT_URL = settings.get(
    "AUTH_WAGTAIL_LOGOUT_REDIRECT_URL", LOGOUT_REDIRECT_URL
)

# =============================================================================
# 🔐 PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "OPTIONS": {
            "max_similarity": settings.get("AUTH_PASSWORD_SIMILARITY_THRESHOLD", 0.7),
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": settings.get("AUTH_PASSWORD_MIN_LENGTH", 8),
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# =============================================================================
# 🛡️ SESSION SETTINGS
# =============================================================================

SESSION_COOKIE_AGE = settings.get("AUTH_SESSION_COOKIE_AGE", 60 * 60 * 24 * 7)  # 1 week
SESSION_EXPIRE_AT_BROWSER_CLOSE = settings.get(
    "AUTH_SESSION_EXPIRE_AT_BROWSER_CLOSE", False
)
SESSION_COOKIE_SECURE = settings.get(
    "AUTH_SESSION_COOKIE_SECURE", conf_settings.is_production
)
SESSION_COOKIE_HTTPONLY = settings.get("AUTH_SESSION_COOKIE_HTTPONLY", True)
SESSION_COOKIE_SAMESITE = settings.get("AUTH_SESSION_COOKIE_SAMESITE", "Lax")

# =============================================================================
# 🛡️ CSRF SETTINGS
# =============================================================================

CSRF_COOKIE_SECURE = settings.get("AUTH_CSRF_COOKIE_SECURE", conf_settings.is_production)
CSRF_COOKIE_HTTPONLY = settings.get("AUTH_CSRF_COOKIE_HTTPONLY", False)
CSRF_COOKIE_SAMESITE = settings.get("AUTH_CSRF_COOKIE_SAMESITE", "Lax")
CSRF_USE_SESSIONS = settings.get("AUTH_CSRF_USE_SESSIONS", False)
CSRF_FAILURE_VIEW = settings.get(
    "AUTH_CSRF_FAILURE_VIEW", "django.views.csrf.csrf_failure"
)
# Ensure the admin login form always gets a fresh CSRF token
CSRF_COOKIE_AGE = None  # Session-scoped (expires when browser closes)

# =============================================================================
# ✉️ ALLAUTH / HTMX AUTH FLOW
# =============================================================================
# The site URLconf exposes allauth login/signup/password routes and wraps selected
# views for HTMX fragments. Keep email verification mandatory enough to send set-
# password/invite messages, but avoid blocking local dry-run tests.
SITE_ID = int(settings.get("SITE_ID", 1))
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = settings.get("ACCOUNT_EMAIL_VERIFICATION", "optional")
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_ADAPTER = settings.get("ACCOUNT_ADAPTER", "plugins.accounts.adapters.RegistrationAdapter")
ACCOUNT_FORMS = settings.get("ACCOUNT_FORMS", {})

# =============================================================================
# 👤 PROFILE MODEL — required by django_rseal and django_osoul ForeignKey refs
# =============================================================================
# This must be set at the base config level so it is available when Django
# loads model classes from installed apps (before site settings are applied).
PROFILE_MODEL = settings.get("PROFILE_MODEL", "auth.User")
