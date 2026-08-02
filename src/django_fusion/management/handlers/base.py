"""
Base handler classes and middleware for django_fusion.

This module contains pure Django handler base classes and middleware
that can be used across projects without Wagtail dependencies.
"""

import logging

logger = logging.getLogger("django.request.errors")


class ErrorTrackerMiddleware:
    """
    Log 4xx and 5xx responses with request details.

    This middleware logs every HTTP error response so that error-report
    commands can pick them up from the standard Django logger.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        status = response.status_code
        if status >= 400:
            level = logging.CRITICAL if status >= 500 else logging.ERROR
            logger.log(
                level,
                "HTTP %s %s %s — user=%s ip=%s",
                status,
                request.method,
                request.get_full_path(),
                getattr(getattr(request, "user", None), "email", "anonymous"),
                self._get_ip(request),
                extra={
                    "status_code": status,
                    "request": request,
                },
            )

        return response

    @staticmethod
    def _get_ip(request):
        """Extract client IP address from request."""
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR", "—")
