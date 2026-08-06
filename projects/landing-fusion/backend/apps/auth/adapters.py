"""
Landing-fusion auth adapters — HTMX-aware allauth with Alpine modal support.

These adapters:
- Map allauth template names to landing-fusion styled templates
- Support fragment (HTMX) and full-page (direct) rendering
- Handle social auth with GitHub + Google OAuth
"""

from __future__ import annotations

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string


class LandingAuthAdapter(DefaultAccountAdapter):
    """Custom allauth adapter for landing-fusion — HTMX + Alpine ready."""

    # Template name mapping: allauth internal name → landing-fusion template
    TEMPLATE_MAP: dict[str, str] = {
        "account/login.html": "auth/login.html",
        "account/signup.html": "auth/register.html",
        "account/password_reset.html": "auth/password_reset.html",
        "account/password_reset_from_key.html": "auth/password_reset_from_key.html",
        "account/password_reset_from_key_done.html": "auth/password_reset_key_done.html",
        "account/password_reset_done.html": "auth/password_reset_done.html",
        "account/email_confirm.html": "auth/email_confirm.html",
        "account/verification_sent.html": "auth/verification_sent.html",
        "account/logout.html": "auth/logout.html",
        "socialaccount/signup.html": "auth/social_signup.html",
        "socialaccount/connections.html": "auth/social_connections.html",
    }

    def get_template_names(self, view_name: str) -> list[str]:
        """Return landing-fusion template paths for allauth views."""
        template_names = super().get_template_names(view_name)
        mapped = []
        for name in template_names:
            mapped.append(self.TEMPLATE_MAP.get(name, name))
        return mapped

    def render_response(
        self,
        request: HttpRequest,
        template_name: str,
        context: dict,
        status=None,
    ) -> HttpResponse:
        """Render auth fragment — bare for HTMX, wrapped for direct loads."""
        is_htmx = bool(request.headers.get("HX-Request"))
        fragment = render_to_string(template_name, context, request)
        if is_htmx:
            response = HttpResponse(fragment)
            if status:
                response.status_code = status
            return response
        # Full page load — wrap in landing-fusion shell
        wrapped = render_to_string(
            "auth/base.html",
            {"fragment": fragment, "request": request, **context},
            request,
        )
        response = HttpResponse(wrapped)
        if status:
            response.status_code = status
        return response

    def get_logout_redirect_url(self, request: HttpRequest) -> str:
        return "/"


class LandingSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter for landing-fusion."""

    def is_open_for_signup(self, request: HttpRequest, sociallogin) -> bool:
        return LandingAuthAdapter(request).is_open_for_signup(request)
