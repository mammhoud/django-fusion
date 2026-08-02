"""
PrivacyConsentMiddleware
========================
Configurable privacy consent middleware.

No hard-coded model imports — models are resolved lazily via
``django.apps.apps.get_model`` using dotted paths from settings.

Settings example::

    PRIVACY_CONSENT_MIDDLEWARE = {
        "PROTECTED_PATHS": ["/accounts/login/", "/accounts/signup/"],
        "PRIVACY_POLICY_MODEL": "accounts.PrivacyPolicy",
        "PRIVACY_CONSENT_MODEL": "accounts.PrivacyConsent",
        "TERMS_MODEL": "accounts.TermsOfService",
        "TERMS_CONSENT_MODEL": "accounts.TermsConsent",
    }
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.shortcuts import render

logger = logging.getLogger(__name__)


class PrivacyConsentMiddleware:
    """Check privacy consent on protected paths.

    Configuration is read from ``settings.PRIVACY_CONSENT_MIDDLEWARE``.
    If a model cannot be resolved the middleware logs a warning and passes
    the request through rather than raising a 500.
    """

    def __init__(self, get_response) -> None:
        self.get_response = get_response
        config = getattr(settings, "PRIVACY_CONSENT_MIDDLEWARE", {})
        self.protected_paths: list[str] = config.get("PROTECTED_PATHS", [])
        self._privacy_policy_model_path: str | None = config.get("PRIVACY_POLICY_MODEL")
        self._privacy_consent_model_path: str | None = config.get("PRIVACY_CONSENT_MODEL")
        self._terms_model_path: str | None = config.get("TERMS_MODEL")
        self._terms_consent_model_path: str | None = config.get("TERMS_CONSENT_MODEL")

    def __call__(self, request):
        if self._is_protected_path(request.path) and getattr(request, "user", None) and request.user.is_authenticated:
            policy_model = self._get_model(self._privacy_policy_model_path)
            consent_model = self._get_model(self._privacy_consent_model_path)
            terms_model = self._get_model(self._terms_model_path)
            terms_consent_model = self._get_model(self._terms_consent_model_path)

            policy = None
            terms = None
            privacy_consented = True
            terms_consented = True

            if policy_model and consent_model:
                try:
                    policy = policy_model.objects.filter(is_active=True).first()
                    if policy:
                        privacy_consented = consent_model.has_consented(request.user, policy)
                except Exception as e:
                    logger.warning("PrivacyConsentMiddleware: error checking privacy consent: %s", e)

            if terms_model and terms_consent_model:
                try:
                    terms = terms_model.objects.filter(is_active=True).first()
                    if terms:
                        terms_consented = terms_consent_model.has_consented(request.user, terms)
                except Exception as e:
                    logger.warning("PrivacyConsentMiddleware: error checking terms consent: %s", e)

            if not privacy_consented or not terms_consented:
                return render(
                    request,
                    "privacy/consent_required.html",
                    {
                        "policy": policy if not privacy_consented else None,
                        "terms": terms if not terms_consented else None,
                    },
                )

        return self.get_response(request)

    def _is_protected_path(self, path: str) -> bool:
        """Return ``True`` if *path* starts with any protected prefix."""
        return any(path.startswith(p) for p in self.protected_paths)

    def _get_model(self, dotted_path: str | None):
        """Lazily resolve a model from a dotted ``"app_label.ModelName"`` path.

        Returns ``None`` and logs a warning if the model cannot be found.
        """
        if not dotted_path:
            return None
        try:
            from django.apps import apps
            return apps.get_model(dotted_path)
        except (LookupError, ValueError) as e:
            logger.warning(
                "PrivacyConsentMiddleware: could not load model %r — %s", dotted_path, e
            )
            return None
