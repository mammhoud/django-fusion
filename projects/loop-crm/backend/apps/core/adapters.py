"""Loop-CRM allauth adapters — thin wrappers over allauth defaults.

Mirrors landing-fusion's ``apps.auth.adapters`` so the auth behavior stays
consistent across workspace products: logout returns to the landing root and
social signup (GitHub/Google) follows the same open-registration policy as
email signup.
"""
from __future__ import annotations

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpRequest


class LoopAuthAdapter(DefaultAccountAdapter):
    """Loop-CRM account adapter — uses allauth defaults."""

    def get_logout_redirect_url(self, request: HttpRequest) -> str:
        return "/"


class LoopSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Loop-CRM social account adapter — uses allauth defaults."""

    def is_open_for_signup(self, request: HttpRequest, sociallogin) -> bool:
        return LoopAuthAdapter(request).is_open_for_signup(request)
