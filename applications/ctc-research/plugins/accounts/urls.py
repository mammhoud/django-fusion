# type: ignore NOQA
from django.urls import path

from . import views
from .apps import AccountsConfig
from .views.allauth import AllauthLoginView, AllauthSignupView

app_name = AccountsConfig.label

urlpatterns = [
    path("auth/login/", AllauthLoginView.as_view(), name="allauth-login"),
    path("auth/signup/", AllauthSignupView.as_view(), name="allauth-signup"),
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
