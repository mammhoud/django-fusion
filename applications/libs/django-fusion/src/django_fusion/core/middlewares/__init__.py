"""Request/response middleware for Django sites.

Modules
-------
error_tracker       Captures unhandled exceptions and logs structured error reports.
privacy             Redirects unauthenticated users who have not accepted the policy.
language            Sets the active language from a cookie or Accept-Language header.
freeze              Blocks write operations during read-only maintenance windows.
service             Injects a per-request service registry into the request object.
site                Resolves the active Wagtail Site object for multi-site setups.
component_error     Returns HTMX-friendly error fragments on component render failure.

Usage::

    MIDDLEWARE += [
        "django_fusion.core.middlewares.error_tracker.ErrorTrackerMiddleware",
        "django_fusion.core.middlewares.language.LanguageMiddleware",
    ]
"""
from .error_tracker import ErrorTrackerMiddleware

__all__ = ["ErrorTrackerMiddleware"]
