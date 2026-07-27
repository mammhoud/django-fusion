# Privacy & Terms — wired via i18n_patterns(path("legal/", include("apps.core.handlers.urls", namespace="legal")))
# in www/urls.py.

from django.urls import path

from .views import privacy

app_name = "legal"


# ---------------------------------------------------------------------------
# Main URL patterns
# ---------------------------------------------------------------------------
urlpatterns = [
    # Privacy & Terms — wired as i18n_patterns(path("legal/", include("apps.core.handlers.urls", namespace="legal")))
    path("policy/", privacy.privacy_policy, name="policy"),
    path("terms/", privacy.terms_of_service, name="terms"),
    path("consent/", privacy.consent_required, name="consent_required"),
    path("policy/accept/", privacy.accept_privacy_policy, name="accept_policy"),
    path("terms/accept/", privacy.accept_terms, name="accept_terms"),
    path("consent/status/", privacy.consent_status, name="consent_status"),
]
