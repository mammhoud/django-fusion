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
    """Log unhandled request exceptions and re-raise them through Django."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)

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
