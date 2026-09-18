"""Path-based course center middleware — resolves center from URL path.

django-tenants ships a host-based resolver (TenantMainMiddleware).  Precis-dev
uses **path-based** routing: ``/c/{center}/`` identifies the course center
scope, with all routes under that prefix resolved inside the center's schema.

When no center path is present (``/``, ``/register/``, ``/centers/``, …) the
request stays in the **public schema**."""

from __future__ import annotations

import re
from typing import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse

TENANCY_ENABLED: bool = getattr(settings, "TENANCY_ENABLED", False)
_CENTER_PATH_RE = re.compile(r"^/c/(?P<center>[a-z0-9][a-z0-9\-]{0,61})/")


class PathCenterMiddleware:
    """Resolve ``connection.tenant`` from request path (path-based routing).

    Inserted after SessionMiddleware / CommonMiddleware and before any
    tenant-dependent middleware. No-op when ``TENANCY_ENABLED`` is False.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not TENANCY_ENABLED:
            return self.get_response(request)

        center_slug = self._resolve_center_slug(request.path)
        if center_slug is not None:
            self._set_center(request, center_slug)

        return self.get_response(request)

    @staticmethod
    def _resolve_center_slug(path: str) -> str | None:
        if not path.startswith("/c/"):
            return None
        match = _CENTER_PATH_RE.match(path)
        if match is None:
            return None
        return match.group("center")

    @staticmethod
    def _set_center(request: HttpRequest, slug: str) -> None:
        try:
            from django.db import connection
            from django_tenants.utils import get_tenant_model
        except ImportError:  # pragma: no cover
            return

        TenantModel = get_tenant_model()
        try:
            center = TenantModel.objects.get(slug=slug, status="active")
        except TenantModel.DoesNotExist:
            return

        connection.set_tenant(center)
        request.center = center

    # ── URL generation helper ────────────────────────────────────────
    @staticmethod
    def center_path(center_slug: str, path: str = "") -> str:
        """Build a center-scoped path: ``/c/{slug}/{path}``."""
        path = path.lstrip("/")
        return f"/c/{center_slug}/{path}" if path else f"/c/{center_slug}/"


def get_current_center():
    """Return the CourseCenter for the current thread/connection, or None."""
    if not TENANCY_ENABLED:
        return None
    try:
        from django.db import connection

        return getattr(connection, "tenant", None)
    except Exception:
        return None