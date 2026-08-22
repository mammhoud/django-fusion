"""Authentication and privacy routes for the LMS accounts app."""

from django.urls import path

from .apps import AccountsConfig
from .site.views.auth import AllauthLoginView, AllauthSignupView
from .site.views import privacy
from .site.views.registration import CreatePasswordView, RegisterView, RegistrationSuccessView

app_name = AccountsConfig.label

urlpatterns = [
    path("auth/login/", AllauthLoginView.as_view(), name="allauth-login"),
    path("auth/signup/", AllauthSignupView.as_view(), name="allauth-signup"),
    # Custom registration view — the register_form.html/login_form.html and
    # token_error.html templates reverse `handlers:register-account`, and the
    # domain register service powers this flow. Registered after the
    # pages/urls.py `auth/register/` alias so `{% url ... %}` resolves here.
    path("auth/register/", RegisterView.as_view(), name="register-account"),
    # Registration → email-link flow: the confirmation email points here
    # (CreatePasswordView validates the token, sets the password, activates
    # the user, and logs them in). Registered under the legacy `handlers`
    # namespace too (see apps/handlers/legacy_urls.py) so the adapter's
    # `reverse("handlers:create-password")` resolves to /auth/create-password/.
    path(
        "auth/create-password/<str:token>/",
        CreatePasswordView.as_view(),
        name="create-password",
    ),
    path(
        "auth/registration/success/",
        RegistrationSuccessView.as_view(),
        name="registration-success",
    ),
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
