"""Precis auth adapters — headless API + HTMX fragment parity.

``PrecisAuthAdapter`` extends the existing HTMX-aware RegistrationAdapter
(``apps.pages.accounts.adapters``) so the allauth headless JSON API and the
server-rendered fragment pages share the same account behaviour (email
confirmation routing, logout redirects, signup openness).

``PrecisSocialAccountAdapter`` mirrors precis-landing: signup openness
delegates to the account adapter so social + email flows agree.
"""

from __future__ import annotations

from django.http import HttpRequest

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from apps.pages.accounts.adapters import RegistrationAdapter


class PrecisAuthAdapter(RegistrationAdapter):
    """Precis account adapter — HTMX fragments + headless JSON, one behaviour."""

    def get_logout_redirect_url(self, request: HttpRequest) -> str:
        return "/"


class PrecisSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Precis social account adapter — signup openness matches the email flow."""

    def is_open_for_signup(self, request: HttpRequest, sociallogin) -> bool:
        return PrecisAuthAdapter(request).is_open_for_signup(request)
