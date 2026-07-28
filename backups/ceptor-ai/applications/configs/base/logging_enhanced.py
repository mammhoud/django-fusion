"""
Enhanced Logging Configuration
==============================
Structured logging with colorized console output using structlog + colorlog.

Features:
  - Color-coded log levels in terminal (DEBUG=cyan, INFO=green, WARNING=yellow, ERROR=red, CRITICAL=red+bold)
  - Structured JSON logging to files for machine parsing
  - Django request/response logging via django-structlog
  - Performance logging (slow queries, slow requests)
  - Trace ID correlation across requests
  - Async-compatible logging handlers

Usage in settings.py:

    from configs.base.logging_enhanced import LOGGING
    from configs.base.logging_enhanced import configure_structlog

    LOGGING = LOGGING  # Django logging dict
    configure_structlog()  # Sets up structlog processors with colors
"""

import logging
import os
import sys
from pathlib import Path

# ── Color formatter for console ──────────────────────────────────────────────
try:
    import colorlog

    class ColorFormatter(colorlog.ColoredFormatter):
        """Custom color formatter with structlog-compatible output."""

        def __init__(self):
            super().__init__(
                fmt=(
                    "%(cyan)s%(asctime)s%(reset)s "
                    "%(log_color)s%(levelname)-8s%(reset)s "
                    "%(blue)s%(name)s:%(lineno)d%(reset)s "
                    "%(message_log_color)s%(message)s%(reset)s"
                ),
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bold",
                },
                secondary_log_colors={
                    "message": {
                        "DEBUG": "cyan",
                        "INFO": "green",
                        "WARNING": "yellow",
                        "ERROR": "red",
                        "CRITICAL": "red,bold",
                    },
                },
                style="%",
            )

except ImportError:
    colorlog = None  # type: ignore[assignment]

    class ColorFormatter(logging.Formatter):  # type: ignore[no-redef]
        """Fallback formatter when colorlog is not installed."""

        def __init__(self):
            super().__init__(
                fmt="[%(asctime)s] %(levelname)-8s %(name)s:%(lineno)d  %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )


# ── JSON formatter for file output ───────────────────────────────────────────
try:
    from pythonjsonlogger import jsonlogger

    class JsonFormatter(jsonlogger.JsonFormatter):
        """JSON formatter for structured log files."""

        def __init__(self):
            super().__init__(
                fmt="%(asctime)s %(levelname)s %(name)s %(module)s %(funcName)s %(lineno)d %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )

except ImportError:

    class JsonFormatter(logging.Formatter):  # type: ignore[no-redef]
        """Fallback JSON-like formatter."""

        def __init__(self):
            super().__init__(
                fmt='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "module": "%(module)s", "line": %(lineno)d, "message": %(message)r}',
                datefmt="%Y-%m-%dT%H:%M:%S",
            )


# ── Log directories ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ── Django LOGGING dictionary ────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(levelname)s %(message)s",
        },
        "console": {
            "()": "configs.base.logging_enhanced.ColorFormatter",
        },
        "json": {
            "()": "configs.base.logging_enhanced.JsonFormatter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
            "level": "DEBUG",
            "stream": sys.stdout,
        },
        "console_stderr": {
            "class": "logging.StreamHandler",
            "formatter": "console",
            "level": "WARNING",
            "stream": sys.stderr,
        },
        "file_debug": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "debug.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "json",
            "level": "DEBUG",
            "filters": ["require_debug_true"],
        },
        "file_app": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "application.log",
            "maxBytes": 5 * 1024 * 1024,  # 5 MB
            "backupCount": 5,
            "formatter": "json",
            "level": "INFO",
        },
        "file_error": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "error.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 10,
            "formatter": "json",
            "level": "ERROR",
        },
        "file_structlog": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "structlog.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "json",
            "level": "INFO",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file_app", "file_error"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "console_stderr", "file_error"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console", "console_stderr", "file_error"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console", "file_debug"],
            "level": "DEBUG",
            "propagate": False,
            "filters": ["require_debug_true"],
        },
        "django_structlog": {
            "handlers": ["console", "file_structlog"],
            "level": "INFO",
            "propagate": False,
        },
        "structlog": {
            "handlers": ["console", "file_structlog"],
            "level": "INFO",
            "propagate": False,
        },
        "wagtail": {
            "handlers": ["console", "file_app"],
            "level": "INFO",
            "propagate": False,
        },
        "core": {
            "handlers": ["console", "file_app", "file_error"],
            "level": "DEBUG",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "file_app", "file_error"],
            "level": "INFO",
            "propagate": False,
        },
        "plugins": {
            "handlers": ["console", "file_app", "file_error"],
            "level": "INFO",
            "propagate": False,
        },
        "tests": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console", "console_stderr", "file_app", "file_error"],
        "level": "INFO",
    },
}


def configure_structlog(
    log_level: str = "INFO",
    json_format: bool = False,
    include_trace_id: bool = True,
) -> None:
    """
    Configure structlog with colorized console output and optional file JSON.

    Call this in your Django settings file after importing LOGGING:

        from configs.base.logging_enhanced import LOGGING, configure_structlog
        LOGGING = LOGGING
        configure_structlog()

    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: If True, use JSON output everywhere (including console)
        include_trace_id: If True, bind request ID to logs via django-structlog
    """
    try:
        import structlog

        # Build processor chain
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
        ]

        if json_format:
            # JSON output for production log aggregation
            processors.append(structlog.processors.JSONRenderer())
            console_log_level = logging.WARNING
        else:
            # ConsoleRenderer with colors
            processors.append(
                structlog.dev.ConsoleRenderer(
                    colors=True,
                    pad_level=True,
                    force_colors=True,
                )
            )
            console_log_level = getattr(logging, log_level.upper(), logging.INFO)

        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # Configure django-structlog middleware settings
        from django.conf import settings as django_settings

        django_settings.STRUCTLOG = getattr(django_settings, "STRUCTLOG", {})
        django_settings.STRUCTLOG.setdefault("LOG_LEVEL", log_level)
        django_settings.STRUCTLOG.setdefault("CONSOLE_LOG_LEVEL", console_log_level)
        django_settings.STRUCTLOG.setdefault("CELERY_ENABLED", True)
        django_settings.STRUCTLOG.setdefault("ENABLE_REQUEST_LOGGING", True)

        if include_trace_id:
            django_settings.STRUCTLOG.setdefault("REQUEST_ID_HEADER", "X-Request-ID")
            django_settings.STRUCTLOG.setdefault("CELERY_TIMING_LOG_LEVEL", log_level)

        # Ensure django_structlog is in INSTALLED_APPS if available
        if "django_structlog" not in django_settings.INSTALLED_APPS:
            try:
                import django_structlog  # noqa: F401
                django_settings.INSTALLED_APPS.append("django_structlog")
            except ImportError:
                pass

        # Bind extra request metadata if django_structlog signals are available
        try:
            from django_structlog.signals import bind_extra_request_metadata

            @bind_extra_request_metadata.connect
            def _bind_extra_meta(sender, request=None, logger=None, **kwargs):
                """Bind user info and session data to request logs."""
                if logger and request:
                    logger.bind(
                        user_id=getattr(request.user, "id", None),
                        user_username=getattr(request.user, "username", None),
                        session_key=getattr(request, "session", None)
                        and request.session.session_key,
                        method=request.method,
                        path=request.path,
                        ip=getattr(request, "META", {}).get("REMOTE_ADDR", ""),
                    )
        except Exception:
            pass

    except ImportError:
        # structlog not installed — fall back to standard logging with colors
        logger = logging.getLogger(__name__)
        logger.warning("structlog not available, falling back to standard logging")


# Convenience alias
def setup_logging(log_level: str = "INFO", json_format: bool = False) -> None:
    """Quick setup: configure logging dict and structlog in one call."""
    configure_structlog(log_level=log_level, json_format=json_format)


# Auto-configure structlog on import — settings files that do
# ``from configs.base import *`` or ``from configs.base.logging_enhanced import *``
# get structlog with colors automatically.
_auto_configured = False
if not _auto_configured:
    try:
        configure_structlog()
        _auto_configured = True
    except Exception:
        pass
