"""
logging_config.py
-----------------
Provides a Django-compatible ``LOGGING`` dictionary and a structlog
configuration helper for django-fusion projects.

In development, logs are rendered as colored, human-readable lines.
In production, logs are emitted as structured JSON.

Usage in ``settings.py``::

    from django_fusion.config.logging import configure_structlog, get_logging_config

    LOGGING = get_logging_config(log_dir="logs", log_level="INFO")
    configure_structlog(is_dev=DEBUG)

The module also exposes ``get_colored_console_renderer`` and
``get_json_renderer`` helpers for projects that want to build their own
structlog processor chain.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import structlog

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAX_BYTES = 100 * 1024 * 1024   # 100 MB per file before size-based rotation
BACKUP_COUNT_SIZE = 10           # Keep 10 size-rotated backups alongside timed ones
BACKUP_COUNT_DAYS = 90           # Keep 90 days of timed-rotation backups


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------

def get_colored_console_renderer() -> structlog.dev.ConsoleRenderer:
    """Return a structlog colored console renderer for development."""
    return structlog.dev.ConsoleRenderer(colors=True)


def get_json_renderer() -> structlog.processors.JSONRenderer:
    """Return a structlog JSON renderer for production / structured logging."""
    return structlog.processors.JSONRenderer()


# ---------------------------------------------------------------------------
# Processors
# ---------------------------------------------------------------------------

def get_shared_processors() -> list:
    """Return processors shared between dev and prod configurations."""
    return [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def configure_structlog(is_dev: bool = True) -> None:
    """
    Configure structlog for the running process.

    Args:
        is_dev: When ``True`` (default), emit colored, human-readable logs
                to the console. When ``False``, emit structured JSON.
    """
    processors = get_shared_processors()
    if is_dev:
        processors.append(get_colored_console_renderer())
    else:
        processors.append(get_json_renderer())

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------
_FORMATTERS = {
    # Human-readable format for console output
    'verbose': {
        'format': '[{asctime}] {levelname} {name} {message}',
        'style': '{',
        'datefmt': '%Y-%m-%dT%H:%M:%S',
    },
    # Structured JSON-like format for log files
    # Fields: timestamp, level, logger, recipient, subject, status, message
    'email_structured': {
        '()': 'logging.Formatter',
        'fmt': (
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": %(message)r}'
        ),
        'datefmt': '%Y-%m-%dT%H:%M:%S',
    },
    # Simple format for Django's default loggers
    'simple': {
        'format': '{levelname} {message}',
        'style': '{',
    },
}


# ---------------------------------------------------------------------------
# Public helper
# ---------------------------------------------------------------------------

def get_logging_config(
    log_dir: str = 'logs',
    log_level: str = 'INFO',
    django_log_level: str = 'WARNING',
) -> dict:
    """
    Return a Django LOGGING configuration dictionary.

    Args:
        log_dir:           Directory where log files will be written.
                           Created automatically if it does not exist.
        log_level:         Log level for django-fusion loggers (default INFO).
        django_log_level:  Log level for Django's own loggers (default WARNING).

    Returns:
        A dict suitable for assignment to Django's ``LOGGING`` setting.

    Log files created:
        <log_dir>/email.log          – size-rotated at 100 MB, 10 backups
        <log_dir>/email_daily.log    – daily rotation, 90-day retention
        <log_dir>/django.log         – Django framework messages
    """
    # Ensure the log directory exists
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    return {
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': _FORMATTERS,

        'handlers': {
            # ------------------------------------------------------------------
            # Console – useful during development / Docker stdout
            # ------------------------------------------------------------------
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
                'level': log_level,
            },

            # ------------------------------------------------------------------
            # Size-based rotation: rotates when file reaches 100 MB
            # Keeps up to 10 compressed backup files alongside the active log.
            # ------------------------------------------------------------------
            'email_file_size': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(log_dir, 'email.log'),
                'maxBytes': MAX_BYTES,
                'backupCount': BACKUP_COUNT_SIZE,
                'formatter': 'email_structured',
                'encoding': 'utf-8',
                'level': log_level,
            },

            # ------------------------------------------------------------------
            # Time-based rotation: rotates daily, retains 90 days of backups.
            # Combined with size-based handler above for belt-and-suspenders
            # log management.
            # ------------------------------------------------------------------
            'email_file_daily': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(log_dir, 'email_daily.log'),
                'when': 'midnight',
                'interval': 1,
                'backupCount': BACKUP_COUNT_DAYS,
                'formatter': 'email_structured',
                'encoding': 'utf-8',
                'utc': True,
                'level': log_level,
            },

            # ------------------------------------------------------------------
            # Django framework log file (size-rotated)
            # ------------------------------------------------------------------
            'django_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(log_dir, 'django.log'),
                'maxBytes': MAX_BYTES,
                'backupCount': BACKUP_COUNT_SIZE,
                'formatter': 'verbose',
                'encoding': 'utf-8',
                'level': django_log_level,
            },
        },

        'loggers': {
            # ------------------------------------------------------------------
            # django_fusion – captures all foundation activity
            # Each log record should include: timestamp, level, recipient,
            # subject, status (added by structlog context or extra= kwargs).
            # ------------------------------------------------------------------
            'django_fusion': {
                'handlers': ['console', 'email_file_size', 'email_file_daily'],
                'level': log_level,
                'propagate': False,
            },

            # ------------------------------------------------------------------
            # Django framework loggers
            # ------------------------------------------------------------------
            'django': {
                'handlers': ['console', 'django_file'],
                'level': django_log_level,
                'propagate': False,
            },
            'django.request': {
                'handlers': ['django_file'],
                'level': 'ERROR',
                'propagate': False,
            },
            'django.security': {
                'handlers': ['django_file'],
                'level': 'ERROR',
                'propagate': False,
            },
        },

        # Root logger – catches anything not handled above
        'root': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    }
