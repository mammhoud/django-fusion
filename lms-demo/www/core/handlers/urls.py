# type: ignore NOQA
"""
Handlers URL configuration.

Includes:
  - Cart / checkout endpoints
  - Accounts plugin URLs
  - Privacy policy & terms of service (page + modal + consent API)
"""

from allauth.account.decorators import secure_admin_login
from django.contrib import admin
from django.urls import include, path

from .apps import AccountsConfig
from .site import *
from .views import privacy

app_name = AccountsConfig.label


# ---------------------------------------------------------------------------
# Privacy & Terms patterns (merged from urls_privacy.py)
# ---------------------------------------------------------------------------
privacy_patterns = (
    [
        # Full-page views (also serve as Unpoly overlay targets)
        path("policy/", privacy.privacy_policy, name="policy"),
        path("terms/", privacy.terms_of_service, name="terms"),
        # Consent gate page (redirect target from middleware)
        path("consent/", privacy.consent_required, name="consent_required"),
        # POST: record consent
        path("policy/accept/", privacy.accept_privacy_policy, name="accept_policy"),
        path("terms/accept/", privacy.accept_terms, name="accept_terms"),
        # JSON status API
        path("consent/status/", privacy.consent_status, name="consent_status"),
    ],
    "privacy",
)


# ---------------------------------------------------------------------------
# Main URL patterns
# ---------------------------------------------------------------------------
urlpatterns = [
    # Privacy & Terms (namespaced as "privacy")
    path("legal/", include(privacy_patterns)),

    # Accounts plugin
    path("", include("plugins.accounts.urls", namespace="accounts")),
]
