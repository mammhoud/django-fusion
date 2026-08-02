"""
URL configuration for django_fusion debug tools.

This module provides URL configuration utilities for adding development
tools URLs including Debug Toolbar, Silk, and Livereload.

Functions:
    configure_urls: Conditionally add Debug Toolbar, Silk, and Livereload URLs.

Usage::

    from django_fusion.contrib.debug_tools.urls import configure_urls

    urlpatterns = [...]
    urlpatterns = configure_urls(urlpatterns)
"""

import contextlib

from django.urls import include, path

try:
    from core import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from .base import enable_livereload, enable_silk, show_toolbar


def configure_urls(urlpatterns: list) -> list:
    """
    Conditionally adds Debug Toolbar, Silk, and Livereload URLs.

    Returns:
        Updated urlpatterns list
    """
    updated_urlpatterns = urlpatterns[:]

    # Add Livereload URLs if enabled
    if enable_livereload():
        try:
            import livereload.urls
            livereload_urls = [
                path("livereload/", include(livereload.urls)),
            ]
            # Add to beginning for proper routing
            updated_urlpatterns = livereload_urls + updated_urlpatterns
            logger.debug("Livereload URLs added to urlpatterns.")
        except ImportError:
            logger.warning(
                "livereload package not installed; skipping URL configuration."
            )

    # Add Silk URLs if enabled
    if enable_silk():
        try:
            with contextlib.suppress(ImportError):
                import silk.urls
                silk_urls = [
                    path("silk/", include(silk.urls)),
                ]
                # Add to beginning for proper routing
                updated_urlpatterns = silk_urls + updated_urlpatterns
                logger.debug("Silk URLs added to urlpatterns.")
        except ImportError:
            logger.warning(
                "silk package not installed; skipping URL configuration."
            )

    # Add Debug Toolbar URLs if enabled
    if show_toolbar():
        try:
            import debug_toolbar.urls
            debug_urls = [
                path("__debug__/", include(debug_toolbar.urls)),
            ]
            # Append to the end (toolbar URLs are usually added last)
            updated_urlpatterns.extend(debug_urls)
            logger.debug("Debug Toolbar URLs added to urlpatterns.")
        except ImportError:
            logger.warning(
                "debug_toolbar package not installed; skipping URL configuration."
            )

    return updated_urlpatterns
