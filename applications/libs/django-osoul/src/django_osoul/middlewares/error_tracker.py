"""Request exception tracking middleware.

The middleware is intentionally lightweight: it lets Django continue to raise
exceptions while providing one reusable hook for projects to attach logging or
external error reporting.
"""

import logging
from collections.abc import Callable
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class ErrorTrackerMiddleware:
    """Log error responses (4xx/5xx) and unhandled request exceptions."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        status = response.status_code
        if status >= 500:
            logger.critical(
                "%s %s %s — %s",
                request.method,
                request.path,
                status,
                self._get_user_display(request),
                extra={"status_code": status, "request": request},
            )
        elif status >= 400:
            logger.error(
                "%s %s %s — %s",
                request.method,
                request.path,
                status,
                self._get_user_display(request),
                extra={"status_code": status, "request": request},
            )
        return response

    @staticmethod
    def _get_user_display(request: HttpRequest) -> str:
        user = getattr(request, "user", None)
        if user is None:
            return "anonymous"
        return getattr(user, "email", "anonymous")

    @staticmethod
    def _get_ip(request: HttpRequest) -> str:
        xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "\u2014")

    def process_exception(
        self, request: HttpRequest, exception: Exception
    ) -> None:
        """Record request context for an unhandled exception.

        Returning ``None`` keeps Django's normal exception handling behavior.
        """
        logger.exception(
            "Unhandled request exception",
            extra={"request_path": request.path, "exception_type": type(exception).__name__},
            exc_info=True,
        )
        return None
