"""FusionSetupRedirectMiddleware — settings-driven setup/config redirects.

Redirects requests into a site/module/application that is not yet configured
to a designated setup or configuration view. The mapping is declarative and
lives in Django settings, so each consuming product can point its own
application names at its own setup flow without writing per-app middleware.

Configuration (*via Django settings*):::

    FUSION_SETUP_REDIRECTS = {
        "loop_crm": {
            # callable(request) -> bool, a dotted path, or a plain boolean.
            "predicate": "apps.core.setup.needs_setup",
            "url": "/setup/",
            # Paths that must never be redirected (e.g. the setup flow itself,
            # static/health routes). The redirect URL is auto-excluded.
            "exclude": ["/accounts/", "/admin/", "/api/"],
        },
    }

The middleware resolves the application name from the matched URL resolver's
metadata (django-fusion attaches ``viewset``/``app``/``module`` to the resolver
through ``_URLResolver.extra``), so the same settings map works for any
Module → Application → Viewset tree.
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.http.response import HttpResponseBase
from django.utils.module_loading import import_string

logger = logging.getLogger(__name__)

__all__ = ["FusionSetupRedirectMiddleware"]


class FusionSetupRedirectMiddleware:
    """Redirect requests to a setup view when the matched app is unconfigured.

    Add after ``AuthenticationMiddleware`` in ``MIDDLEWARE`` so ``request.user``
    is populated when a predicate inspects it.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        return self.get_response(request)

    # ------------------------------------------------------------------
    # Resolution helpers (extracted for testability)
    # ------------------------------------------------------------------

    def resolve_app_name(self, request: HttpRequest) -> str | None:
        """Return the application/module name for the matched route.

        django-fusion stores ``viewset``/``app``/``module`` on the resolver's
        ``url_name.extra``; this prefers the explicit app/module and falls back
        to Django's namespaced ``app_name``/``namespace``.
        """
        resolver = getattr(request, "resolver_match", None)
        if resolver is None:
            return None
        url_name = getattr(resolver, "url_name", None)
        extra = getattr(url_name, "extra", {}) or {}
        viewset = extra.get("app") or extra.get("module") or extra.get("viewset")
        name = getattr(viewset, "app_name", None)
        if name:
            return name
        return getattr(resolver, "app_name", None) or getattr(resolver, "namespace", None)

    def evaluate_predicate(self, predicate: Any, request: HttpRequest) -> bool:
        """Evaluate a redirect predicate (callable, dotted path, or boolean)."""
        if predicate is None:
            return False
        if callable(predicate):
            return bool(predicate(request))
        if isinstance(predicate, str):
            return bool(import_string(predicate)(request))
        return bool(predicate)

    def process_view(
        self,
        request: HttpRequest,
        view_func: Callable,
        view_args: list,
        view_kwargs: dict,
    ) -> HttpResponse | None:
        redirects = getattr(settings, "FUSION_SETUP_REDIRECTS", None) or {}
        if not redirects:
            return None

        app_name = self.resolve_app_name(request)
        if not app_name or app_name not in redirects:
            return None

        entry = redirects[app_name] or {}
        url = entry.get("url")
        if not url:
            return None

        # Never redirect the setup URL itself (loop guard) or excluded paths.
        if request.path.rstrip("/") == str(url).rstrip("/"):
            return None
        for excluded in entry.get("exclude") or []:
            if request.path.startswith(excluded):
                return None

        if not self.evaluate_predicate(entry.get("predicate"), request):
            return None

        logger.info("Redirecting %s to setup (%s)", request.path, url)
        return HttpResponseRedirect(url)
