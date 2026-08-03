"""Authentication and privacy routes for the LMS accounts app."""

from django.urls import path

from .apps import AccountsConfig
from .site.views.auth import AllauthLoginView, AllauthSignupView
from .site.views import privacy

app_name = AccountsConfig.label

urlpatterns = [
    path("auth/login/", AllauthLoginView.as_view(), name="allauth-login"),
    path("auth/signup/", AllauthSignupView.as_view(), name="allauth-signup"),
    # Privacy Policy
    path(
        "policy/modal/",
        privacy.privacy_policy_modal,
        name="policy_modal",
    ),
    path(
        "policy/accept/",
        privacy.accept_privacy_policy,
        name="accept_policy",
    ),
    # Terms of Service
    path(
        "terms/modal/",
        privacy.terms_modal,
        name="terms_modal",
    ),
    path(
        "terms/accept/",
        privacy.accept_terms,
        name="accept_terms",
    ),
    # Consent Status
    path(
        "consent/status/",
        privacy.check_consent_status,
        name="consent_status",
    ),
]
