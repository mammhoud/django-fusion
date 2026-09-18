"""CORS headers + request-language locale activation for landing endpoints."""
from __future__ import annotations

import os

from django.http import HttpRequest, HttpResponse

DEFAULT_ALLOWED = "http://localhost:4321,http://localhost:3000"


class LandingLocaleMiddleware:
    """Activate the Django locale from the landing ``?lang=`` contract.

    ``django.middleware.locale.LocaleMiddleware`` only honours the
    ``django_language`` cookie or the Accept-Language header; the landing
    site also switches server-rendered pages via ``?lang=`` (the same
    resolver the content-overlay API uses), and the bilingual-parity
    refactor moved templates to ``{% translate %}`` tags. This middleware
    keeps the active locale aligned with the requested content language so
    both full documents and HTMX fragments render translated labels.

    Overriding only happens when ``?lang=`` is explicitly present: cookie
    and header signals are already handled by LocaleMiddleware (which runs
    just before this middleware), and forcing an override there could
    clobber its negotiation (e.g. Accept-Language q-value weighting).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if "lang" not in request.GET:
            return self.get_response(request)

        from django.utils import translation

        # Imported lazily: api.py imports this view module inside its
        # fragment handler, so a module-level import would be circular.
        from apps.pages.api import _requested_content_language

        language = _requested_content_language(request)
        with translation.override(language):
            return self.get_response(request)


class LandingCorsMiddleware:
    """Allow configured Astro origins to read Django-rendered fragments."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_origins = {
            origin.strip()
            for origin in os.environ.get("CORS_ALLOWED_ORIGINS", DEFAULT_ALLOWED).split(",")
            if origin.strip()
        }

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        public_paths = {
            "/", "/about/", "/about/team/", "/about/startup/", "/about/founder/",
            "/about/services/", "/services/", "/services/benefits/", "/products/", "/blog/", "/pricing/",
            "/contact/", "/faq/", "/privacy/", "/brand/",
        }
        is_allowed_path = (
            request.path in public_paths
            or request.path.startswith("/fragment/")
            or request.path.startswith("/api/auth/")
            or request.path.startswith("/api/newsletter/")
        )
        if not is_allowed_path:
            return response

        origin = request.headers.get("Origin")
        if origin and (origin in self.allowed_origins or "*" in self.allowed_origins):
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Allow-Headers"] = (
                "HX-Request, HX-Target, HX-Current-URL, Content-Type"
            )
            response["Vary"] = "Origin"
        if request.method == "OPTIONS":
            response.status_code = 200
            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, DELETE"
        return response
