"""
CRM allauth adapter.

Minimal adapter: no custom email templating, no HTMX fragment
wrapping required (the CRM uses standard Django views for auth).
Auth views are served by allauth directly; the CRM app shell
sits behind /crm/ which is login-required.
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpRequest


class CRMAccountAdapter(DefaultAccountAdapter):
    """Thin adapter — uses allauth defaults, no special email routing."""

    def get_login_redirect_url(self, request: HttpRequest) -> str:
        return "/crm/dashboard/"

    def get_logout_redirect_url(self, request: HttpRequest) -> str:
        return "/accounts/login/"


class CRMSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Default social adapter — social auth not required for CRM MVP."""

    def is_open_for_signup(self, request: HttpRequest, sociallogin) -> bool:  # type: ignore[override]
        return True
