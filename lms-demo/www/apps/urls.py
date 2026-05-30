# type: ignore NOQA
"""
www.apps URL configuration — structa.cloud

Includes:
  - Privacy policy & terms of service (page + modal + consent API)
  - Accounts plugin URLs
"""

from django.urls import include, path

from .apps import AccountsConfig
from .views import privacy

app_name = AccountsConfig.label

# ---------------------------------------------------------------------------
# Privacy & Terms patterns (merged from urls_privacy.py)
# ---------------------------------------------------------------------------
privacy_patterns = (
    [
        path("policy/",         privacy.privacy_policy,        name="policy"),
        path("terms/",          privacy.terms_of_service,      name="terms"),
        path("consent/",        privacy.consent_required,      name="consent_required"),
        path("policy/accept/",  privacy.accept_privacy_policy, name="accept_policy"),
        path("terms/accept/",   privacy.accept_terms,          name="accept_terms"),
        path("consent/status/", privacy.consent_status,        name="consent_status"),
    ],
    "privacy",
)

urlpatterns = [
    path("legal/", include(privacy_patterns)),
    path("", include("plugins.accounts.urls", namespace="accounts")),
]
