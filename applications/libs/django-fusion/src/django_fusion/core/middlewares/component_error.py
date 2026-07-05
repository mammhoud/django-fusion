"""Component error logging middleware with daily file rotation."""
from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import traceback

from django.conf import settings


def component_logger() -> logging.Logger:
    log_dir = Path(getattr(settings, "BASE_DIR", Path.cwd())) / "applications" / "logs" / "components"
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("django_fusion.components")
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
