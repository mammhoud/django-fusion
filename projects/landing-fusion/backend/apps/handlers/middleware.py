"""
CORS for the landing fragment endpoints.

The Astro frontend (static build or dev server) fetches the Wagtail-rendered
component fragments via HTMX (see ``frontend/src/components/ui/LiveFragment``).
When the frontend and backend live on different origins (e.g. Astro on :4321
and Django on :8074), the browser blocks the response unless the backend sends
``Access-Control-Allow-Origin``. This middleware adds that header for the
public landing routes only, gated to the configured frontend origin(s).

Reads ``CORS_ALLOWED_ORIGINS`` (comma-separated). Defaults to
``http://localhost:4321,http://localhost:3000`` — the Astro dev/preview ports.
"""
from __future__ import annotations

import os

from django.http import HttpRequest, HttpResponse

DEFAULT_ALLOWED = "http://localhost:4321,http://localhost:3000"


class LandingCorsMiddleware:
    """Allow the Astro frontend to read HTMX fragment responses."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_origins = {
            origin.strip()
            for origin in os.environ.get("CORS_ALLOWED_ORIGINS", DEFAULT_ALLOWED).split(",")
            if origin.strip()
        }

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        # Only the public landing routes serve fragments; leave admin/Wagtail
        # responses untouched. The allauth headless API (/api/auth/*) is also
        # allowed so the Astro frontend can post login JSON cross-origin.
        cors_paths = (
            "/", "/about/", "/about/team/", "/services/", "/products/",
            "/features/", "/blog/", "/pricing/", "/contact/", "/faq/",
            "/privacy/", "/brand/",
        )
        if (
            request.path in cors_paths
            or request.path.startswith("/api/auth/")
            or request.path.startswith("/api/newsletter/")
        ):
            origin = request.headers.get("Origin")
            if origin and (origin in self.allowed_origins or "*" in self.allowed_origins):
                response["Access-Control-Allow-Origin"] = origin
                response["Access-Control-Allow-Credentials"] = "true"
                response["Access-Control-Allow-Headers"] = "HX-Request, HX-Target, HX-Current-URL, Content-Type"
                response["Vary"] = "Origin"
            if request.method == "OPTIONS":
                response.status_code = 200
                response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, DELETE"
        return response
