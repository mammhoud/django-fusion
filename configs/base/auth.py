"""
Authentication & Account Configuration
--------------------------------------

This module defines all authentication, authorization, and account-related
settings for the project. It integrates Django Allauth, custom backends,
and Wagtail authentication seamlessly.

References:
- Django docs: https://docs.djangoproject.com/en/stable/ref/settings/#auth
- Allauth docs: https://docs.allauth.org/en/latest/
- Wagtail docs: https://docs.wagtail.org/
"""

from django.urls import reverse_lazy

from ..settings.conf import settings
from ..settings.conf import settings as tracker

# =============================================================================
# 🔐 AUTHENTICATION BACKENDS
# =============================================================================
# Define the authentication backends used for user authentication.
# Order matters: Django checks them sequentially.

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",  # Default Django auth
    "allauth.account.auth_backends.AuthenticationBackend",  # Allauth backend
    # "guardian.backends.ObjectPermissionBackend",  # Object-level permissions
)

# =============================================================================
# 👤 USER MODEL CONFIGURATION
# =============================================================================

# Custom user model (optional - uncomment if using custom user model)
# AUTH_USER_MODEL = "pipelines.User"

# Profile model (if separate from user)
PROFILE_MODEL = settings.get("AUTH_PROFILE_MODEL", "pipelines.Person")

# User model fields configuration
USER_MODEL_CONFIG = {
    "USERNAME_FIELD": settings.get("AUTH_USERNAME_FIELD", "email"),
    "EMAIL_FIELD": settings.get("AUTH_EMAIL_FIELD", "email"),
    "REQUIRED_FIELDS": settings.get(
        "AUTH_REQUIRED_FIELDS", ["first_name", "last_name"]
    ),
}

# =============================================================================
# 🔄 ACCOUNT ADAPTERS & FORMS
# =============================================================================
# Custom adapters allow fine-grained control over login/signup behavior.

ACCOUNT_ADAPTER = settings.get(
    "AUTH_ACCOUNT_ADAPTER", "django_osoul.adapters.AccountAdapter"
)
SOCIALACCOUNT_ADAPTER = settings.get(
    "AUTH_SOCIALACCOUNT_ADAPTER",
    "django_osoul.adapters.SocialAccountAdapter",
)

# Custom forms
# ACCOUNT_FORMS = settings.get("AUTH_ACCOUNT_FORMS", {
#     "signup": "apps.users.forms.UserSignupForm",
#     "login": "apps.users.forms.UserLoginForm",
#     "change_password": "apps.users.forms.ChangePasswordForm",
#     "reset_password": "apps.users.forms.ResetPasswordForm",
#     "reset_password_from_key": "apps.users.forms.ResetPasswordKeyForm",
# })

# SOCIALACCOUNT_FORMS = settings.get("AUTH_SOCIALACCOUNT_FORMS", {
#     "signup": "apps.users.forms.UserSocialSignupForm",
# })

# =============================================================================
# 📍 REDIRECTION SETTINGS
# =============================================================================

LOGIN_REDIRECT_URL = settings.get("AUTH_LOGIN_REDIRECT_URL", "/")
LOGOUT_REDIRECT_URL = settings.get("AUTH_LOGOUT_REDIRECT_URL", "/")
LOGIN_URL = settings.get("AUTH_LOGIN_URL", reverse_lazy("pipelines:login"))
LOGOUT_URL = settings.get("AUTH_LOGOUT_URL", reverse_lazy("pipelines:logout"))

# Allauth-specific redirects
ACCOUNT_LOGOUT_REDIRECT_URL = settings.get(
    "AUTH_ACCOUNT_LOGOUT_REDIRECT_URL", LOGOUT_REDIRECT_URL
)
ACCOUNT_LOGIN_REDIRECT_URL = settings.get(
    "AUTH_ACCOUNT_LOGIN_REDIRECT_URL", LOGIN_REDIRECT_URL
)
ACCOUNT_SIGNUP_REDIRECT_URL = settings.get(
    "AUTH_ACCOUNT_SIGNUP_REDIRECT_URL", LOGIN_REDIRECT_URL
)

# Wagtail integration
WAGTAIL_FRONTEND_LOGIN_URL = settings.get("AUTH_WAGTAIL_LOGIN_URL", LOGIN_URL)
WAGTAILADMIN_LOGIN_URL = settings.get("AUTH_WAGTAILADMIN_LOGIN_URL", LOGIN_URL)
WAGTAIL_LOGOUT_REDIRECT_URL = settings.get(
    "AUTH_WAGTAIL_LOGOUT_REDIRECT_URL", LOGOUT_REDIRECT_URL
)

# =============================================================================
# 📝 ACCOUNT CONFIGURATION
# =============================================================================
# Email and username behavior, verification, and security controls.
ACCOUNT_RATE_LIMITS = {}
# Registration settings
ACCOUNT_ALLOW_REGISTRATION = settings.get(
    "AUTH_ACCOUNT_ALLOW_REGISTRATION", not tracker.is_production
)
ACCOUNT_ALLOW_SIGNUPS = settings.get(
    "AUTH_ACCOUNT_ALLOW_SIGNUPS", not tracker.is_production
)

# Email settings
ACCOUNT_UNIQUE_EMAIL = settings.get("AUTH_ACCOUNT_UNIQUE_EMAIL", True)
ACCOUNT_EMAIL_VERIFICATION = settings.get("AUTH_ACCOUNT_EMAIL_VERIFICATION", "mandatory")
# ACCOUNT_EMAIL_REQUIRED and ACCOUNT_USERNAME_REQUIRED are deprecated in allauth.
# Use ACCOUNT_SIGNUP_FIELDS instead (defined below).
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = settings.get(
    "AUTH_ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS", 3
)
ACCOUNT_EMAIL_CONFIRMATION_HMAC = settings.get(
    "AUTH_ACCOUNT_EMAIL_CONFIRMATION_HMAC", True
)
# ACCOUNT_EMAIL_RATE_LIMITS = settings.get("ACCOUNT_RATE_LIMITS", {})
ACCOUNT_EMAIL_SUBJECT_PREFIX = settings.get("AUTH_ACCOUNT_EMAIL_SUBJECT_PREFIX", "")
ACCOUNT_RATE_LIMITS["confirm_email"] = settings.get(
    "AUTH_ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN", "1/3m"
)
# Username settings
ACCOUNT_USERNAME_MIN_LENGTH = settings.get("AUTH_ACCOUNT_USERNAME_MIN_LENGTH", 4)
ACCOUNT_USERNAME_BLACKLIST = settings.get(
    "AUTH_ACCOUNT_USERNAME_BLACKLIST", ["admin", "root", "superuser"]
)
ACCOUNT_USERNAME_VALIDATORS = settings.get("AUTH_ACCOUNT_USERNAME_VALIDATORS", None)
ACCOUNT_RATE_LIMITS["login_failed"] = settings.get(
    "AUTH_ACCOUNT_LOGIN_ATTEMPTS_LIMIT", "5/5m"
)
# Login settings
ACCOUNT_LOGIN_METHODS = settings.get("AUTH_ACCOUNT_LOGIN_METHODS", ["email"])
# ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = settings.get("AUTH_ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT", 300)  # 5 minutes
ACCOUNT_SESSION_REMEMBER = settings.get("AUTH_ACCOUNT_SESSION_REMEMBER", True)
ACCOUNT_SESSION_COOKIE_AGE = settings.get(
    "AUTH_ACCOUNT_SESSION_COOKIE_AGE", 60 * 60 * 24 * 7
)  # 1 week
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = settings.get(
    "AUTH_ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE", True
)
ACCOUNT_LOGOUT_ON_GET = settings.get("AUTH_ACCOUNT_LOGOUT_ON_GET", False)

# Password settings
ACCOUNT_PASSWORD_MIN_LENGTH = settings.get("AUTH_ACCOUNT_PASSWORD_MIN_LENGTH", 8)
ACCOUNT_PASSWORD_REQUIRED = settings.get("AUTH_ACCOUNT_PASSWORD_REQUIRED", True)

# Signup settings
ACCOUNT_SIGNUP_FIELDS = settings.get(
    "AUTH_ACCOUNT_SIGNUP_FIELDS", ["email*", "password1*", "password2*"]
)
ACCOUNT_SIGNUP_FORM_CLASS = settings.get("AUTH_ACCOUNT_SIGNUP_FORM_CLASS", None)

# Security settings
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https" if tracker.is_production else "http"
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = settings.get(
    "AUTH_ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL", ACCOUNT_LOGIN_REDIRECT_URL
)
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = settings.get(
    "AUTH_ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL", None
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
# 🛡️ SECURITY SETTINGS
# =============================================================================

ADMIN_FORCE_ALLAUTH = settings.get("AUTH_ADMIN_FORCE_ALLAUTH", False)
ANONYMOUS_USER_NAME = settings.get("AUTH_ANONYMOUS_USER_NAME", "anonymous")

# Session configuration
SESSION_COOKIE_AGE = settings.get("AUTH_SESSION_COOKIE_AGE", 60 * 60 * 24 * 7 * 1)  # 1 week
SESSION_EXPIRE_AT_BROWSER_CLOSE = settings.get(
    "AUTH_SESSION_EXPIRE_AT_BROWSER_CLOSE", False
)
SESSION_COOKIE_SECURE = settings.get(
    "AUTH_SESSION_COOKIE_SECURE", tracker.is_production
)
SESSION_COOKIE_HTTPONLY = settings.get("AUTH_SESSION_COOKIE_HTTPONLY", True)
SESSION_COOKIE_SAMESITE = settings.get("AUTH_SESSION_COOKIE_SAMESITE", "Lax")

# CSRF configuration
CSRF_COOKIE_SECURE = settings.get(
    "AUTH_CSRF_COOKIE_SECURE", tracker.is_production
)
CSRF_COOKIE_HTTPONLY = settings.get("AUTH_CSRF_COOKIE_HTTPONLY", False)
CSRF_COOKIE_SAMESITE = settings.get("AUTH_CSRF_COOKIE_SAMESITE", "Lax")
CSRF_USE_SESSIONS = settings.get("AUTH_CSRF_USE_SESSIONS", False)
CSRF_FAILURE_VIEW = settings.get(
    "AUTH_CSRF_FAILURE_VIEW", "django.views.csrf.csrf_failure"
)

# =============================================================================
# 🔑 MULTI-FACTOR AUTHENTICATION (MFA)
# =============================================================================

MFA_ENABLED = settings.get("AUTH_MFA_ENABLED", tracker.is_production)
MFA_SUPPORTED_TYPES = settings.get(
    "AUTH_MFA_SUPPORTED_TYPES", ["totp", "webauthn", "recovery_codes"]
)
MFA_REQUIRED_FOR_ADMIN = settings.get(
    "AUTH_MFA_REQUIRED_FOR_ADMIN", tracker.is_production
)
MFA_REQUIRED_FOR_STAFF = settings.get("AUTH_MFA_REQUIRED_FOR_STAFF", False)

# TOTP settings
MFA_TOTP_ISSUER = settings.get("AUTH_MFA_TOTP_ISSUER", tracker.MODULE)
MFA_TOTP_DIGITS = settings.get("AUTH_MFA_TOTP_DIGITS", 6)
MFA_TOTP_PERIOD = settings.get("AUTH_MFA_TOTP_PERIOD", 30)
MFA_TOTP_WINDOW = settings.get("AUTH_MFA_TOTP_WINDOW", 1)

# WebAuthn settings
MFA_WEBAUTHN_RP_NAME = settings.get("AUTH_MFA_WEBAUTHN_RP_NAME", tracker.MODULE)
MFA_WEBAUTHN_RP_ID = settings.get("AUTH_MFA_WEBAUTHN_RP_ID", None)
MFA_WEBAUTHN_ORIGIN = settings.get("AUTH_MFA_WEBAUTHN_ORIGIN", None)
MFA_WEBAUTHN_TIMEOUT = settings.get("AUTH_MFA_WEBAUTHN_TIMEOUT", 60000)  # 1 minute

# Recovery codes
MFA_RECOVERY_CODES_COUNT = settings.get("AUTH_MFA_RECOVERY_CODES_COUNT", 10)
MFA_RECOVERY_CODES_LENGTH = settings.get("AUTH_MFA_RECOVERY_CODES_LENGTH", 8)

# =============================================================================
# 🌐 SOCIAL AUTHENTICATION PROVIDERS
# =============================================================================

SOCIALACCOUNT_ENABLED = settings.get("AUTH_SOCIALACCOUNT_ENABLED", False)
SOCIALACCOUNT_AUTO_SIGNUP = settings.get("AUTH_SOCIALACCOUNT_AUTO_SIGNUP", True)
SOCIALACCOUNT_EMAIL_REQUIRED = settings.get("AUTH_SOCIALACCOUNT_EMAIL_REQUIRED", True)
SOCIALACCOUNT_EMAIL_VERIFICATION = settings.get(
    "AUTH_SOCIALACCOUNT_EMAIL_VERIFICATION", "optional"
)
SOCIALACCOUNT_QUERY_EMAIL = settings.get("AUTH_SOCIALACCOUNT_QUERY_EMAIL", True)
SOCIALACCOUNT_STORE_TOKENS = settings.get("AUTH_SOCIALACCOUNT_STORE_TOKENS", True)

# Social providers configuration
SOCIALACCOUNT_PROVIDERS = settings.get(
    "AUTH_SOCIALACCOUNT_PROVIDERS",
    {
        "google": {
            "SCOPE": ["profile", "email"],
            "AUTH_PARAMS": {"access_type": "online"},
            "OAUTH_PKCE_ENABLED": True,
            "APP": {
                "client_id": settings.get("GOOGLE_OAUTH_CLIENT_ID", ""),
                "secret": settings.get("GOOGLE_OAUTH_SECRET", ""),
                "key": "",
            },
        },
        "github": {
            "SCOPE": ["user", "repo", "read:org"],
            "VERIFIED_EMAIL": True,
            "APP": {
                "client_id": settings.get("GITHUB_OAUTH_CLIENT_ID", ""),
                "secret": settings.get("GITHUB_OAUTH_SECRET", ""),
                "key": "",
            },
        },
        "facebook": {
            "METHOD": "oauth2",
            "SCOPE": ["email", "public_profile"],
            "AUTH_PARAMS": {"auth_type": "reauthenticate"},
            "INIT_PARAMS": {"cookie": True},
            "FIELDS": [
                "id",
                "email",
                "name",
                "first_name",
                "last_name",
                "verified",
                "locale",
                "timezone",
                "link",
                "gender",
                "updated_time",
            ],
            "EXCHANGE_TOKEN": True,
            "VERIFIED_EMAIL": False,
            "VERSION": "v13.0",
            "APP": {
                "client_id": settings.get("FACEBOOK_OAUTH_CLIENT_ID", ""),
                "secret": settings.get("FACEBOOK_OAUTH_SECRET", ""),
                "key": "",
            },
        },
    },
)

# =============================================================================
# 📱 FRONTEND / HEADLESS AUTH FLOW
# =============================================================================

HEADLESS_ONLY = settings.get("AUTH_HEADLESS_ONLY", False)
HEADLESS_FRONTEND_URLS = settings.get(
    "AUTH_HEADLESS_FRONTEND_URLS",
    {
        "account_confirm_email": "/auth/verify-email/{key}",
        "account_reset_password": "/auth/password/reset",
        "account_reset_password_from_key": "/auth/password/reset/key/{key}",
        "account_signup": "/auth/register",
        "account_login": "/auth/login",
        "account_logout": "/auth/logout",
        "account_profile": "/auth/profile",
    },
)

HEADLESS_TOKEN_CONFIG = {
    "ACCESS_TOKEN_LIFETIME": settings.get(
        "AUTH_ACCESS_TOKEN_LIFETIME", 60 * 15
    ),  # 15 minutes
    "REFRESH_TOKEN_LIFETIME": settings.get(
        "AUTH_REFRESH_TOKEN_LIFETIME", 60 * 60 * 24 * 7
    ),  # 1 week
    "ROTATE_REFRESH_TOKENS": settings.get("AUTH_ROTATE_REFRESH_TOKENS", True),
    "BLACKLIST_AFTER_ROTATION": settings.get("AUTH_BLACKLIST_AFTER_ROTATION", True),
    "ALGORITHM": settings.get("AUTH_TOKEN_ALGORITHM", "HS256"),
    "SIGNING_KEY": settings.DJANGO_SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
}

# =============================================================================
# 🎯 PERMISSIONS & AUTHORIZATION
# =============================================================================

# Django Guardian settings
GUARDIAN_GET_INIT_ANONYMOUS_USER = settings.get(
    "AUTH_GUARDIAN_GET_INIT_ANONYMOUS_USER", "guardian.models.AnonymousUser"
)
GUARDIAN_RAISE_403 = settings.get("AUTH_GUARDIAN_RAISE_403", True)
GUARDIAN_RENDER_403 = settings.get("AUTH_GUARDIAN_RENDER_403", False)
GUARDIAN_TEMPLATE_403 = settings.get("AUTH_GUARDIAN_TEMPLATE_403", "403.html")

# =============================================================================
# 📊 AUTHENTICATION LOGGING
# =============================================================================

AUTH_LOGGING = {
    "ENABLED": settings.get("AUTH_LOGGING_ENABLED", True),
    "LOG_FAILED_LOGINS": settings.get("AUTH_LOG_FAILED_LOGINS", True),
    "LOG_SUCCESSFUL_LOGINS": settings.get(
        "AUTH_LOG_SUCCESSFUL_LOGINS", tracker.is_production
    ),
    "LOG_PASSWORD_CHANGES": settings.get("AUTH_LOG_PASSWORD_CHANGES", True),
    "LOG_EMAIL_CHANGES": settings.get("AUTH_LOG_EMAIL_CHANGES", True),
    "LOG_PROFILE_UPDATES": settings.get("AUTH_LOG_PROFILE_UPDATES", False),
    "LOG_SOCIAL_LOGINS": settings.get("AUTH_LOG_SOCIAL_LOGINS", True),
}

# =============================================================================
# 🔄 ACCOUNT LIFECYCLE
# =============================================================================

ACCOUNT_LIFECYCLE = {
    "INACTIVE_AFTER_DAYS": settings.get("AUTH_INACTIVE_AFTER_DAYS", 90),
    "DEACTIVATE_AFTER_DAYS": settings.get("AUTH_DEACTIVATE_AFTER_DAYS", 365),
    "DELETE_AFTER_DEACTIVATION_DAYS": settings.get(
        "AUTH_DELETE_AFTER_DEACTIVATION_DAYS", 30
    ),
    "SEND_INACTIVITY_NOTICE_DAYS": settings.get(
        "AUTH_SEND_INACTIVITY_NOTICE_DAYS", [60, 30, 7]
    ),
}

# =============================================================================
# 🎨 AUTHENTICATION UI/UX
# =============================================================================

AUTH_UI = {
    "THEME": settings.get("AUTH_THEME", "default"),
    "SHOW_SOCIAL_LOGIN": settings.get("AUTH_SHOW_SOCIAL_LOGIN", True),
    "SHOW_REGISTRATION_LINK": settings.get(
        "AUTH_SHOW_REGISTRATION_LINK", ACCOUNT_ALLOW_REGISTRATION
    ),
    "SHOW_PASSWORD_RESET_LINK": settings.get("AUTH_SHOW_PASSWORD_RESET_LINK", True),
    "SHOW_REMEMBER_ME": settings.get("AUTH_SHOW_REMEMBER_ME", True),
    "SHOW_TERMS_CHECKBOX": settings.get("AUTH_SHOW_TERMS_CHECKBOX", True),
    "TERMS_URL": settings.get("AUTH_TERMS_URL", "/terms/"),
    "PRIVACY_URL": settings.get("AUTH_PRIVACY_URL", "/privacy/"),
    "CUSTOM_CSS": settings.get("AUTH_CUSTOM_CSS", None),
    "CUSTOM_JS": settings.get("AUTH_CUSTOM_JS", None),
}

# =============================================================================
# ⚡ PERFORMANCE OPTIMIZATIONS
# =============================================================================

AUTH_PERFORMANCE = {
    "CACHE_PERMISSIONS": settings.get("AUTH_CACHE_PERMISSIONS", True),
    "PERMISSION_CACHE_TIMEOUT": settings.get(
        "AUTH_PERMISSION_CACHE_TIMEOUT", 60 * 60
    ),  # 1 hour
    "CACHE_USER_SESSIONS": settings.get("AUTH_CACHE_USER_SESSIONS", True),
    "SESSION_CACHE_TIMEOUT": settings.get(
        "AUTH_SESSION_CACHE_TIMEOUT", 60 * 5
    ),  # 5 minutes
    "BATCH_PERMISSION_CHECKS": settings.get("AUTH_BATCH_PERMISSION_CHECKS", True),
    "BATCH_SIZE": settings.get("AUTH_BATCH_SIZE", 100),
}

# =============================================================================
# 🚀 WAGTAIL AUTH INTEGRATION
# =============================================================================

# WAGTAIL_AUTH = {
#     "ENABLE_REGISTRATION": settings.get(
#         "WAGTAIL_ENABLE_REGISTRATION", ACCOUNT_ALLOW_REGISTRATION
#     ),
#     "REQUIRE_APPROVAL": settings.get("WAGTAIL_REQUIRE_APPROVAL", False),
#     "APPROVAL_EMAIL": settings.get("WAGTAIL_APPROVAL_EMAIL", True),
#     "ADMIN_APPROVAL_EMAIL_SUBJECT": settings.get(
#         "WAGTAIL_ADMIN_APPROVAL_EMAIL_SUBJECT",
#         "New user registration requires approval",
#     ),
#     "APPROVED_EMAIL_SUBJECT": settings.get(
#         "WAGTAIL_APPROVED_EMAIL_SUBJECT", "Your account has been approved"
#     ),
#     "REGISTRATION_FORM": settings.get(
#         "WAGTAIL_REGISTRATION_FORM", "wagtail.users.forms.WagtailUserCreationForm"
#     ),
#     "EDIT_FORM": settings.get(
#         "WAGTAIL_EDIT_FORM", "wagtail.users.forms.WagtailUserEditForm"
#     ),
# }

# Wagtail user model (if different)
# WAGTAIL_USER_CREATION_FORM = WAGTAIL_AUTH["REGISTRATION_FORM"]
# WAGTAIL_USER_EDIT_FORM = WAGTAIL_AUTH["EDIT_FORM"]
# WAGTAIL_USER_CUSTOM_FIELDS = settings.get("WAGTAIL_USER_CUSTOM_FIELDS", [])

# =============================================================================
# 🎭 ANONYMOUS USER SETTINGS
# =============================================================================

ANONYMOUS_USER_CONFIG = {
    "ENABLED": settings.get("ANONYMOUS_USER_ENABLED", True),
    "USERNAME": settings.get("ANONYMOUS_USERNAME", "anonymous"),
    "EMAIL": settings.get("ANONYMOUS_EMAIL", "anonymous@example.com"),
    "PERMISSIONS": settings.get("ANONYMOUS_PERMISSIONS", []),
    "GROUPS": settings.get("ANONYMOUS_GROUPS", []),
}
