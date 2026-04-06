# ====================================
# 📝 Enhanced Structured Logging with Development Tools
# ====================================
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog
from colorlog import ColoredFormatter

# Import from your project structure
# from .apps import INSTALLED_APPS
# from .. import settings, tracker, BASE_DIR, Environment

# Temporary placeholders - replace with your actual imports
BASE_DIR = Path.cwd()
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# You'll need to define or import these in your actual project
# DEBUG_TOOLS_AVAILABLE = False  # Set based on your environment
# tracker = None  # Your environment tracker

# -------------------------------
# Context Injection Processor
# -------------------------------
def inject_contexts(_, __, event_dict):
    """
    Inject dynamic context into each log event.
    Combines both implementations.
    """
    # Add timestamp
    event_dict["timestamp"] = datetime.now().isoformat()

    # Add environment context if tracker is available
    try:
        from .. import tracker  # Your actual import
        event_dict.update({
            "environment": tracker.SERVER_ENV.value,
            "module": tracker.module,
            "runtime": tracker.runtime.value,
        })
    except (ImportError, AttributeError):
        pass

    # Add user context from both implementations
    event_dict.update({
        "user_id": event_dict.get("user_id"),
        "request_route": event_dict.get("request_route"),
        "trace_id": event_dict.get("trace_id"),
    })

    # Filter out None values
    return {k: v for k, v in event_dict.items() if v is not None}


# -------------------------------
# Enhanced Formatters
# -------------------------------
class EnhancedColoredFormatter(ColoredFormatter):
    """
    Enhanced formatter with beautiful multi-line formatting.
    Combines PrettyLineFormatter and EnhancedColoredFormatter features.
    """

    def format(self, record):
        msg = record.msg
        base = super().format(record)

        # Handle structlog dictionary messages
        if isinstance(msg, dict):
            event = msg.get("event", "")
            extra_data = {k: v for k, v in msg.items() if k != "event"}

            if event:
                if isinstance(event, str) and "\n" in event:
                    # Multiline string event
                    lines = "\n".join(f"│   {line}" for line in event.splitlines())
                    return f"\n╭─ Event:\n{lines}\n╰──────────────────────────────"
                elif extra_data:
                    # Flat dict data
                    lines = "\n".join(f"│   {k:<15}: {v}" for k, v in extra_data.items())
                    return f"\n╭─ Event Data:\n│   {event}\n{lines}\n╰──────────────────────────────"
                else:
                    return event
            elif extra_data:
                # Empty dict or no event key
                lines = "\n".join(f"│   {k:<15}: {v}" for k, v in extra_data.items())
                return f"\n╭─ Data:\n{lines}\n╰──────────────────────────────"

        # Handle multi-line messages
        elif isinstance(msg, str) and "\n" in msg:
            lines = "\n".join(f"│   {line}" for line in msg.splitlines())
            return f"\n╭─\n{lines}\n╰─"

        return base


# -------------------------------
# Django Logging Configuration
# -------------------------------
def get_logging_config(debug: bool = True) -> dict[str, Any]:
    """
    Get logging configuration based on environment.
    """
    # Base handlers based on environment
    if debug:
        console_level = "DEBUG"
        file_level = "DEBUG"
        formatter = "colored_console"
    else:
        console_level = "INFO"
        file_level = "INFO"
        formatter = "json"

    return {
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
                "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
            },
            "simple": {"format": "%(levelname)s %(message)s"},
            "colored_console": {
                "()": EnhancedColoredFormatter,
                "format": (
                    "%(log_color)s[%(asctime)s] "
                    "- %(levelname)-8s "
                    "- %(name)s:%(lineno)d "
                    "- %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "log_colors": {
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                },
            },
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
                "foreign_pre_chain": [
                    structlog.contextvars.merge_contextvars,
                    structlog.processors.TimeStamper(fmt="iso", utc=False),
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    inject_contexts,
                ],
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": formatter,
                "level": console_level,
            },
            "file_debug": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": LOG_DIR / "debug.log",
                "maxBytes": 10 * 1024 * 1024,  # 10 MB
                "backupCount": 5,
                "formatter": "verbose",
                "level": "DEBUG",
            },
            "file_app": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": LOG_DIR / "application.log",
                "maxBytes": 5 * 1024 * 1024,  # 5 MB
                "backupCount": 5,
                "formatter": "json" if not debug else "verbose",
                "level": file_level,
            },
            "file_error": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": LOG_DIR / "error.log",
                "maxBytes": 10 * 1024 * 1024,  # 10 MB
                "backupCount": 10,
                "formatter": "json",
                "level": "ERROR",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console", "file_app", "file_error"],
                "level": "INFO",
                "propagate": True,
            },
            "django.request": {
                "handlers": ["console", "file_error"],
                "level": "ERROR",
                "propagate": False,
            },
            "django.security": {
                "handlers": ["console", "file_error"],
                "level": "ERROR",
                "propagate": False,
            },
            "django.db.backends": {
                "handlers": ["console", "file_debug"] if debug else ["file_debug"],
                "level": "DEBUG" if debug else "INFO",
                "propagate": False,
            },
            "core": {
                "handlers": ["console", "file_app", "file_error"],
                "level": "DEBUG" if debug else "INFO",
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console", "file_app", "file_error"],
            "level": "INFO",
        },
    }


# Generate logging config
LOGGING = get_logging_config(debug=True)


# -------------------------------
# Structlog Configuration
# -------------------------------
def configure_structlog(debug: bool = True) -> None:
    """
    Configure structlog based on environment.
    """
    structlog_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        inject_contexts,
    ]

    # Add JSON processor for production, colorful console for development
    if not debug:
        structlog_processors.append(structlog.processors.JSONRenderer())
    else:
        structlog_processors.extend([
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer(colors=True),
        ])

    structlog.configure(
        processors=structlog_processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Initialize structlog
configure_structlog(debug=True)


# -------------------------------
# Simplified Development Tools Integration
# -------------------------------
def configure_logging_for_environment(debug: bool = True, sentry_dsn: str | None = None) -> dict[str, Any]:
    """
    Configure all logging tools together.
    """
    result = {
        "debug": debug,
        "logging_configured": True,
        "structlog_configured": True,
        "sentry_configured": False,
    }

    # Configure structlog
    configure_structlog(debug)

    # Configure Sentry if DSN is provided
    if sentry_dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.django import DjangoIntegration
            from sentry_sdk.integrations.logging import LoggingIntegration

            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[
                    DjangoIntegration(),
                    LoggingIntegration(
                        level="INFO",
                        event_level="ERROR"
                    ),
                ],
                traces_sample_rate=0.1,
                environment="development" if debug else "production",
                debug=debug,
            )
            result["sentry_configured"] = True
            print("✅ Sentry initialized")
        except ImportError:
            print("⚠️  sentry-sdk not installed")

    return result


# -------------------------------
# Utility Functions
# -------------------------------
def setup_logging_for_debugging() -> dict[str, Any]:
    """
    Setup comprehensive logging for debugging sessions.
    """
    config = configure_logging_for_environment(debug=True)

    # Ensure log directory exists
    LOG_DIR.mkdir(exist_ok=True)

    # Create archive directory
    archive_dir = LOG_DIR / "archive"
    archive_dir.mkdir(exist_ok=True)

    # List existing log files
    log_files = list(LOG_DIR.glob("*.log"))
    if log_files:
        print("\n📄 Existing log files:")
        for log_file in log_files:
            size_mb = log_file.stat().st_size / (1024 * 1024)
            print(f"  • {log_file.name}: {size_mb:.2f} MB")

    return config


def log_system_info():
    """
    Log system information for debugging.
    """
    import platform
    import sys

    import django

    logger = structlog.get_logger("system")

    info = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "django_version": django.get_version(),
        "base_dir": str(BASE_DIR),
        "log_dir": str(LOG_DIR),
    }

    logger.info("System information", **info)


# -------------------------------
# Middleware Configuration
# -------------------------------
def get_logging_middleware() -> list[str]:
    """
    Get logging middleware based on environment.
    """
    middleware = [
        "django_structlog.middlewares.RequestMiddleware",
    ]

    # Add Celery middleware if Celery is used
    # Uncomment when you have INSTALLED_APPS imported
    # if "celery" in INSTALLED_APPS:
    #     middleware.append("django_structlog.middlewares.CeleryMiddleware")

    return middleware


LOGGING_MIDDLEWARE = get_logging_middleware()
