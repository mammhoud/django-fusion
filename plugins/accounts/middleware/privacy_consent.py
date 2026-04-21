"""
Privacy Consent Middleware

Checks if user has consented to privacy policy and terms of service
on authentication pages.
"""

from django.shortcuts import render

from www.apps.accounts.models.profiles.privacy_consent import (
    PrivacyConsent,
    PrivacyPolicy,
    TermsConsent,
    TermsOfService,
)


class PrivacyConsentMiddleware:
    """Middleware to check privacy consent on authentication pages."""

    # Pages that require privacy consent
    PROTECTED_PATHS = [
        "/accounts/login/",
        "/accounts/signup/",
        "/accounts/register/",
        "/auth/login/",
        "/auth/signup/",
        "/auth/register/",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is on a protected page
        if self._is_protected_path(request.path):
            # Check if user is authenticated
            if request.user.is_authenticated:
                # Check privacy consent
                policy = PrivacyPolicy.objects.filter(is_active=True).first()
                terms = TermsOfService.objects.filter(is_active=True).first()

                privacy_consented = (
                    PrivacyConsent.has_consented(request.user, policy)
                    if policy
                    else True
                )
                terms_consented = (
                    TermsConsent.has_consented(request.user, terms) if terms else True
                )

                # If user hasn't consented, show consent page
                if not privacy_consented or not terms_consented:
                    return render(
                        request,
                        "privacy/consent_required.html",
                        {
                            "policy": policy if not privacy_consented else None,
                            "terms": terms if not terms_consented else None,
                        },
                    )

        response = self.get_response(request)
        return response

    def _is_protected_path(self, path):
        """Check if path is protected."""
        for protected_path in self.PROTECTED_PATHS:
            if path.startswith(protected_path):
                return True
        return False
