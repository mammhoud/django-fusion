"""Authentication and privacy routes — the single auth/accounts URL group.

Every auth route for the site lives here, mounted at ``/accounts/`` under the
``accounts`` namespace (apps/urls.py). The legacy ``/auth/...`` sub-paths are
kept as aliases *inside this group* because ``apps/handlers/legacy_urls.py``
re-registers these patterns at the site root under the ``handlers`` namespace
— registration confirmation emails and templates reverse
``handlers:create-password``, ``handlers:registration-success`` and
``handlers:register-account``, so those names/paths must stay live.
"""

from allauth.account.views import LogoutView
from django.urls import path

from apps.domain.site.auth.privacy import PrivacyModalView

from .apps import AccountsConfig
from .site.views.auth import (
    ActivationSentView,
    AllauthLoginView,
    AllauthPasswordResetFromKeyView,
    AllauthPasswordResetView,
    AllauthSignupView,
    VerificationSentView,
)
from .site.views import privacy
from .site.views.newsletter import NewsletterSubscribeView
from .site.views.registration import CreatePasswordView, RegisterView, RegistrationSuccessView

app_name = AccountsConfig.label

urlpatterns = [
    # ── Canonical auth routes (/accounts/...) ───────────────────────────
    path("login/", AllauthLoginView.as_view(), name="login"),
    path("signup/", AllauthSignupView.as_view(), name="signup"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # Custom registration view — the register_form.html/login_form.html and
    # token_error.html templates reverse `handlers:register-account` (legacy
    # /auth/register/ alias below) and the domain register service powers
    # this flow. `accounts:register` is the canonical /accounts/register/.
    path("register/", RegisterView.as_view(), name="register"),
    # Registration → email-link flow: the confirmation email points here.
    # Reversed as `handlers:create-password` (see legacy alias below).
    path(
        "create-password/<str:token>/",
        CreatePasswordView.as_view(),
        name="create-password-canonical",
    ),
    path(
        "registration/success/",
        RegistrationSuccessView.as_view(),
        name="registration-success-canonical",
    ),
    path("password/forgot/", AllauthPasswordResetView.as_view(), name="password_forgot"),
    path(
        "password/reset/<uidb36>/<key>/",
        AllauthPasswordResetFromKeyView.as_view(),
        name="password_reset_from_key",
    ),
    path("verify-email/", VerificationSentView.as_view(), name="verification_sent"),
    path("activation-sent/", ActivationSentView.as_view(), name="activation_sent"),
    # Privacy modal content — HTMX fragment rendered lazily via hx-get
    path("privacy-modal/", PrivacyModalView.as_view(), name="privacy_modal"),
    path(
        "newsletter/subscribe/",
        NewsletterSubscribeView.as_view(),
        name="subscribe_newsletter",
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
    # ── Legacy /auth/... aliases ────────────────────────────────────────
    # Kept for the `handlers` reverse-compat namespace (re-registered at the
    # site root by apps/handlers/legacy_urls.py) and any in-flight email
    # links. Original names preserved so reverse("handlers:create-password")
    # / "handlers:register-account" / "handlers:registration-success" keep
    # producing their existing /auth/... paths.
    path("auth/login/", AllauthLoginView.as_view(), name="allauth-login"),
    path("auth/signup/", AllauthSignupView.as_view(), name="allauth-signup"),
    path("auth/register/", RegisterView.as_view(), name="register-account"),
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
]
