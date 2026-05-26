"""
PrivacyConsentMiddleware

Re-exports PrivacyConsentMiddleware from django_rseal.
Canonical import: from django_rseal.http.middlewares import PrivacyConsentMiddleware

Configure via settings.PRIVACY_CONSENT_MIDDLEWARE:

    PRIVACY_CONSENT_MIDDLEWARE = {
        "PROTECTED_PATHS": ["/accounts/login/", "/accounts/signup/"],
        "PRIVACY_POLICY_MODEL": "accounts.PrivacyPolicy",
        "PRIVACY_CONSENT_MODEL": "accounts.PrivacyConsent",
        "TERMS_MODEL": "accounts.TermsOfService",
        "TERMS_CONSENT_MODEL": "accounts.TermsConsent",
        "CONSENT_TEMPLATE": "privacy/consent_required.html",
    }
"""

from django_rseal.http.middlewares import PrivacyConsentMiddleware

__all__ = ["PrivacyConsentMiddleware"]
