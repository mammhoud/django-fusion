"""Request/response middleware for Django sites.

Modules
-------
access              Enforces group- and permission-based access control before views.
error_tracker       Captures unhandled exceptions and logs structured error reports.
language            Sets the active language from a cookie or Accept-Language header.
freeze              Blocks write operations during read-only maintenance windows.
service             Injects a per-request service registry into the request object.
site                Resolves the active Wagtail Site object for multi-site setups.
component_error     Returns HTMX-friendly error fragments on component render failure.

Usage::

    MIDDLEWARE += [
        "django_fusion.core.middlewares.access.RoleBasedAccessMiddleware",
        "django_fusion.core.middlewares.error_tracker.ErrorTrackerMiddleware",
        "django_fusion.core.middlewares.language.DefaultLanguageMiddleware",
    ]
"""
from __future__ import annotations


class FusionMiddleware:
    """Fusion middleware base."""
    pass


class PageHandlerMiddleware:
    """Page handler middleware."""
    pass


from .errors import ErrorTrackerMiddleware  # noqa: E402
from .access import RoleBasedAccessMiddleware  # noqa: E402

__all__ = [
    "ErrorTrackerMiddleware",
    "RoleBasedAccessMiddleware",
    "FusionMiddleware",
    "PageHandlerMiddleware",
]
