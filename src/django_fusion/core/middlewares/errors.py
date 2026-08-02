"""Error logging middleware for django-fusion responses and components.

``ErrorTrackerMiddleware`` logs HTTP error responses. ``ComponentErrorLoggingMiddleware``
logs uncaught component exceptions with request metadata before re-raising them.
"""
from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import traceback

from django.conf import settings

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


def component_logger() -> logging.Logger:
    log_dir = Path(getattr(settings, "BASE_DIR", Path.cwd())) / "applications" / "logs" / "components"
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("django_fusion.fragments")
    if not logger.handlers:
        handler = TimedRotatingFileHandler(log_dir / "component_errors.log", when="midnight", backupCount=14)
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler); logger.setLevel(logging.INFO); logger.propagate = False
    return logger

class ComponentErrorLoggingMiddleware:
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as exc:
            meta = {k: v for k, v in request.META.items() if k in {"PATH_INFO", "REQUEST_METHOD", "REMOTE_ADDR", "HTTP_USER_AGENT"}}
            component_logger().error({"template": getattr(exc, "template_debug", None), "context": getattr(request, "component_context", {}), "metadata": meta, "traceback": traceback.format_exc()})
            raise
