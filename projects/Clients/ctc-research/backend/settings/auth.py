"""Auth configuration for ctc-research (django-allauth headless API).

Precis-landing parity: the Alpine login modal (frontend + Django templates)
consumes the headless API at /api/auth/browser/v1/auth/*. Server-rendered
/accounts/* pages remain as fallback.
"""

from configs.default import *  # noqa: E402,F401,F403

__all__ = [
    "ACCOUNT_LOGIN_METHODS",
    "ACCOUNT_SIGNUP_FIELDS",
    "ACCOUNT_EMAIL_VERIFICATION",
    "ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION",
    "ACCOUNT_ADAPTER",
    "SOCIALACCOUNT_ADAPTER",
    "MFA_PASSKEY_LOGIN_ENABLED",
    "MFA_SUPPORTED_TYPES",
    "ACCOUNT_LOGIN_URL",
    "ACCOUNT_SIGNUP_URL",
    "ACCOUNT_EMAIL_URL",
]

if "allauth.headless" not in INSTALLED_APPS:
    INSTALLED_APPS.append("allauth.headless")
if "apps.auth.apps.PrecisAuthConfig" not in INSTALLED_APPS:
    INSTALLED_APPS.append("apps.auth.apps.PrecisAuthConfig")
if "apps.tasks" not in INSTALLED_APPS:
    INSTALLED_APPS.append("apps.tasks")

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = cfg("ACCOUNT_EMAIL_VERIFICATION", "optional")
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_ADAPTER = "apps.auth.adapters.PrecisAuthAdapter"
SOCIALACCOUNT_ADAPTER = "apps.auth.adapters.PrecisSocialAccountAdapter"
MFA_PASSKEY_LOGIN_ENABLED = cfg("MFA_PASSKEY_LOGIN_ENABLED", True)
MFA_SUPPORTED_TYPES = ["recovery_codes", "totp", "webauthn"]
ACCOUNT_LOGIN_URL = "/accounts/login/"
ACCOUNT_SIGNUP_URL = "/accounts/signup/"
ACCOUNT_EMAIL_URL = "/accounts/email/"
