"""
Debug tools for django_osoul.

This module provides debug utilities and tools for development and
production monitoring. It re-exports from django_grep for backward
compatibility.

.. deprecated:: 0.1.0
    This module has been moved to django_grep.contrib.debug_tools.
    Please update your imports.

Usage::

    from django_grep.contrib.debug_tools import development
    from django_grep.contrib.debug_tools import monitoring
"""

import warnings

# Re-export everything from django_grep.contrib.debug_tools
from django_grep.contrib.debug_tools import (  # noqa: F401
    autoreload,
    base,
    common_urls,
    config,
    core,
    detection,
    dev_urls,
    development,
    error_views,
    middleware,
    monitoring,
    orchestrator,
    prometheus,
    sentry,
    urls,
)

__all__ = [
    "autoreload",
    "base",
    "common_urls",
    "config",
    "core",
    "detection",
    "dev_urls",
    "development",
    "error_views",
    "middleware",
    "monitoring",
    "orchestrator",
    "prometheus",
    "sentry",
    "urls",
]

warnings.warn(
    "django_osoul.contrib.debug_tools has been moved to django_grep.contrib.debug_tools. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)
