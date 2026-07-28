"""Accounts plugin URL patterns.

Routes:
- /accounts/login/ — Redirect to /auth/login/
- /accounts/signup/ — Redirect to /auth/register/
- /auth/login/, /auth/register/ — Main auth endpoints (defined in plugins/urls.py)
"""
from django.urls import path

from . import views
from .views.auth import AllauthLoginView, AllauthSignupView
from .apps import AccountsConfig

app_name = AccountsConfig.label

urlpatterns = [
    # Aliases for backwards compatibility
    path("login/", AllauthLoginView.as_view(), name="login"),
    path("signup/", AllauthSignupView.as_view(), name="signup"),
    path("register/", AllauthSignupView.as_view(), name="register"),
    # Privacy Policy
    path(
        "policy/modal/",
        views.privacy.privacy_policy_modal,
        name="policy_modal",
    ),
    path(
        "policy/accept/",
        views.privacy.accept_privacy_policy,
        name="accept_policy",
    ),
    # Terms of Service
    path(
        "terms/modal/",
        views.privacy.terms_modal,
        name="terms_modal",
    ),
    path(
        "terms/accept/",
        views.privacy.accept_terms,
        name="accept_terms",
    ),
    # Consent Status
    path(
        "consent/status/",
        views.privacy.check_consent_status,
        name="consent_status",
    ),
]
