"""
Middleware configuration for django_fusion.

This module provides middleware configuration utilities for managing
development tools middleware including ordering and setup.

Classes:
    MiddlewareConfig: Configuration for middleware ordering and setup.

Functions:
    configure_all_middleware: Convenience function to configure all middleware.

Usage::

    from django_fusion.contrib.debug_tools.middleware import MiddlewareConfig

    config = MiddlewareConfig.configure_all(installed_apps, middleware)
"""

from typing import Any

try:
    from core import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from .base import enable_livereload, enable_silk, is_debug_mode, show_toolbar
from .config import DEFAULT_MIDDLEWARE_POSITIONS


class MiddlewareConfig:
    """
    Configuration for middleware ordering and setup.
    """

    @staticmethod
    def get_default_positions() -> dict[str, int | None]:
        """
        Get default middleware positions.

        Returns:
            Dictionary of middleware positions
        """
        return DEFAULT_MIDDLEWARE_POSITIONS.copy()

    @staticmethod
    def configure_middleware(
        middleware: list[str],
        positions: dict[str, int | None] = None,
        debug: bool = None
    ) -> dict[str, Any]:
        """
        Configure middleware with proper ordering.

        Args:
            middleware: Current middleware list
            positions: Custom positions dictionary
            debug: Whether debug mode is enabled

        Returns:
            Dictionary with configured middleware and info
        """
        if debug is None:
            debug = is_debug_mode()

        # Use default positions if not provided
        if positions is None:
            positions = DEFAULT_MIDDLEWARE_POSITIONS

        updated_middleware = middleware.copy()
        added_middleware = []

        # Helper function to add middleware
        def add_middleware(middleware_class: str, position: int | None, name: str):
            if middleware_class in updated_middleware:
                return

            if position is None:
                updated_middleware.append(middleware_class)
                logger.debug(f"Added {name} middleware at the end")
            else:
                updated_middleware.insert(position, middleware_class)
                logger.debug(f"Added {name} middleware at position {position}")

            added_middleware.append(name)

        # Add Prometheus middleware
        if debug and 'django_prometheus' in updated_middleware:
            from .config import (
                PROMETHEUS_AFTER_MIDDLEWARE,
                PROMETHEUS_BEFORE_MIDDLEWARE,
            )
            add_middleware(PROMETHEUS_BEFORE_MIDDLEWARE, positions.get('prometheus_before'), 'Prometheus Before')
            add_middleware(PROMETHEUS_AFTER_MIDDLEWARE, positions.get('prometheus_after'), 'Prometheus After')

        # Add Silk middleware
        if enable_silk():
            from .config import SILK_MIDDLEWARE
            add_middleware(SILK_MIDDLEWARE, positions.get('silk'), 'Silk')

        # Add Livereload middleware
        if enable_livereload():
            from .config import LIVERELOAD_MIDDLEWARE
            add_middleware(LIVERELOAD_MIDDLEWARE, positions.get('livereload'), 'Livereload')

        # Add Debug Toolbar middleware
        if show_toolbar():
            from .config import DEBUG_TOOLBAR_MIDDLEWARE
            add_middleware(DEBUG_TOOLBAR_MIDDLEWARE, positions.get('debug_toolbar'), 'Debug Toolbar')

        return {
            'middleware': updated_middleware,
            'added': added_middleware,
            'positions_used': positions,
        }

    @staticmethod
    def configure_all(
        installed_apps: list[str],
        middleware: list[str],
        debug: bool = None,
        custom_positions: dict[str, int | None] = None
    ) -> dict[str, Any]:
        """
        Configure both apps and middleware.

        Args:
            installed_apps: Current INSTALLED_APPS
            middleware: Current MIDDLEWARE
            debug: Whether debug mode is enabled
            custom_positions: Custom middleware positions

        Returns:
            Dictionary with configured apps and middleware
        """
        from .setup import DebugToolbarSetup

        # Configure apps
        configured_apps = DebugToolbarSetup.configure_apps(
            installed_apps=installed_apps,
            add_to_beginning=True
        )

        # Configure middleware
        middleware_config = MiddlewareConfig.configure_middleware(
            middleware=middleware,
            positions=custom_positions,
            debug=debug
        )

        return {
            'installed_apps': configured_apps,
            'middleware': middleware_config['middleware'],
            'middleware_info': {
                'added': middleware_config['added'],
                'positions': middleware_config['positions_used'],
            }
        }

    @classmethod
    def get_middleware_info(cls, middleware: list[str]) -> dict[str, Any]:
        """
        Get information about configured middleware.

        Args:
            middleware: Middleware list

        Returns:
            Dictionary with middleware information
        """
        from .config import (
            DEBUG_TOOLBAR_MIDDLEWARE,
            LIVERELOAD_MIDDLEWARE,
            PROMETHEUS_AFTER_MIDDLEWARE,
            PROMETHEUS_BEFORE_MIDDLEWARE,
            SILK_MIDDLEWARE,
        )

        debug_middleware = {
            'debug_toolbar': DEBUG_TOOLBAR_MIDDLEWARE,
            'silk': SILK_MIDDLEWARE,
            'livereload': LIVERELOAD_MIDDLEWARE,
            'prometheus_before': PROMETHEUS_BEFORE_MIDDLEWARE,
            'prometheus_after': PROMETHEUS_AFTER_MIDDLEWARE,
        }

        info = {
            'total_middleware': len(middleware),
            'debug_middleware_configured': {},
            'positions': {},
        }

        for name, middleware_class in debug_middleware.items():
            if middleware_class in middleware:
                position = middleware.index(middleware_class)
                info['debug_middleware_configured'][name] = {
                    'class': middleware_class,
                    'position': position,
                }
                info['positions'][name] = position

        return info


# Convenience functions
def configure_all_middleware(
    installed_apps: list[str],
    middleware: list[str],
    **kwargs
) -> dict[str, Any]:
    """
    Convenience function to configure all middleware.

    Args:
        installed_apps: Current INSTALLED_APPS
        middleware: Current MIDDLEWARE
        **kwargs: Additional arguments for MiddlewareConfig.configure_all

    Returns:
        Dictionary with configured apps and middleware
    """
    return MiddlewareConfig.configure_all(installed_apps, middleware, **kwargs)
