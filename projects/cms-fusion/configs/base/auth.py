"""
Authentication Configuration
-----------------------------

Django + django-allauth authentication settings shared across all sites.
Includes allauth, social auth, MFA, and HTMX fragment auth flow settings.

References:
- Django auth: https://docs.djangoproject.com/en/stable/ref/settings/#auth
- Django sessions: https://docs.djangoproject.com/en/stable/ref/settings/#sessions
- Django CSRF: https://docs.djangoproject.com/en/stable/ref/csrf/
- django-allauth: https://docs.allauth.org/
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
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_ADAPTER = settings.get("ACCOUNT_ADAPTER", "apps.pages.accounts.adapters.RegistrationAdapter")
ACCOUNT_FORMS = settings.get("ACCOUNT_FORMS", {})

# =============================================================================
# 🔐 ALLAUTH ADVANCED OPTIONS
# =============================================================================
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_USERNAME_BLACKLIST = list(settings.get("ACCOUNT_USERNAME_BLACKLIST", ["admin", "root", "superuser"]))
ACCOUNT_MAX_EMAIL_ADDRESSES = settings.get("ACCOUNT_MAX_EMAIL_ADDRESSES", 1)
ACCOUNT_CHANGE_EMAIL = settings.get("ACCOUNT_CHANGE_EMAIL", False)
ACCOUNT_REAUTHENTICATION_REQUIRED = settings.get("ACCOUNT_REAUTHENTICATION_REQUIRED", False)
ACCOUNT_REAUTHENTICATION_TIMEOUT = settings.get("ACCOUNT_REAUTHENTICATION_TIMEOUT", 300)

# =============================================================================
# 🔗 SOCIAL AUTH OPTIONS
# =============================================================================
SOCIALACCOUNT_ADAPTER = settings.get(
    "SOCIALACCOUNT_ADAPTER", "apps.pages.accounts.adapters.AuthHTMXSocialAccountAdapter"
)
SOCIALACCOUNT_AUTO_SIGNUP = settings.get("SOCIALACCOUNT_AUTO_SIGNUP", True)
SOCIALACCOUNT_EMAIL_VERIFICATION = settings.get("SOCIALACCOUNT_EMAIL_VERIFICATION", "optional")
SOCIALACCOUNT_STORE_TOKENS = settings.get("SOCIALACCOUNT_STORE_TOKENS", False)
SOCIALACCOUNT_LOGIN_ON_GET = settings.get("SOCIALACCOUNT_LOGIN_ON_GET", False)
SOCIALACCOUNT_PROVIDERS = settings.get("SOCIALACCOUNT_PROVIDERS", {})

# =============================================================================
# 🛡️ MFA / 2FA OPTIONS (requires allauth.mfa in INSTALLED_APPS)
# =============================================================================
MFA_PASSKEY_LOGIN_ENABLED = settings.get("MFA_PASSKEY_LOGIN_ENABLED", True)
# Passkey signup requires ACCOUNT_EMAIL_VERIFICATION='mandatory' and
# ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED=True — keep False for password-first flow.
MFA_PASSKEY_SIGNUP_ENABLED = settings.get("MFA_PASSKEY_SIGNUP_ENABLED", False)
MFA_SUPPORTED_TYPES = settings.get(
    "MFA_SUPPORTED_TYPES", ["totp", "webauthn", "recovery_codes"]
)

# =============================================================================
# 📧 EMAIL OPTIONS
# =============================================================================
ACCOUNT_EMAIL_SUBJECT_PREFIX = settings.get("EMAIL_SUBJECT_PREFIX", "[Structa Cloud] ")
ACCOUNT_EMAIL_NOTIFICATIONS = settings.get("ACCOUNT_EMAIL_NOTIFICATIONS", True)
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = settings.get("ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS", 3)

# =============================================================================
# 👤 PROFILE MODEL — required by ceptor_ai and django_fusion ForeignKey refs
# =============================================================================
# This must be set at the base config level so it is available when Django
# loads model classes from installed apps (before site settings are applied).
PROFILE_MODEL = settings.get("PROFILE_MODEL", "auth.User")
