"""
Landing-fusion auth adapters — thin wrappers over allauth defaults.

The headless API (/api/auth/browser/v1/auth/login) is the primary auth path
consumed by the LoginModal (Alpine.js). Server-rendered /accounts/* pages
fall back to allauth's built-in templates unless landing-specific overrides
are added to the app's templates directory.
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpRequest


class LandingAuthAdapter(DefaultAccountAdapter):
    """Landing-fusion account adapter — uses allauth defaults."""

    def get_logout_redirect_url(self, request: HttpRequest) -> str:
        return "/"


class LandingSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Landing-fusion social account adapter — uses allauth defaults."""

    def is_open_for_signup(self, request: HttpRequest, sociallogin) -> bool:
        return LandingAuthAdapter(request).is_open_for_signup(request)
