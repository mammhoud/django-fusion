"""
ErrorTrackerMiddleware
======================
Logs every 4xx / 5xx response with request details.

Canonical import: from django_fusion.middlewares.error_tracker import ErrorTrackerMiddleware

No website-specific configuration required.

Usage (add to ``MIDDLEWARE`` in settings)::

    MIDDLEWARE = [
        ...
        "django_fusion.middlewares.error_tracker.ErrorTrackerMiddleware",
    ]
"""

from __future__ import annotations

import logging

logger = logging.getLogger("django.request.errors")


class ErrorTrackerMiddleware:
    """Log 4xx and 5xx responses with method, path, status code, and user agent."""

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        status = response.status_code
        if status >= 400:
            self._log_error(request, response)
        return response

    def _log_error(self, request, response) -> None:
        """Log the error response details."""
        status = response.status_code
        level = logging.CRITICAL if status >= 500 else logging.ERROR
        logger.log(
            level,
            "HTTP %s %s %s — user=%s ua=%s ip=%s",
            status,
            request.method,
            request.get_full_path(),
            getattr(getattr(request, "user", None), "email", "anonymous"),
            request.META.get("HTTP_USER_AGENT", "—"),
            self._get_ip(request),
            extra={
                "status_code": status,
                "request": request,
            },
        )

    @staticmethod
    def _get_ip(request) -> str:
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR", "—")
