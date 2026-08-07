"""CORS headers for public landing and fragment endpoints."""
from __future__ import annotations

import os

from django.http import HttpRequest, HttpResponse

DEFAULT_ALLOWED = "http://localhost:4321,http://localhost:3000"


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
            "/services/", "/products/", "/features/", "/blog/", "/pricing/",
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
