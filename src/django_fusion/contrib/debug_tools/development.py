"""
Development environment setup for django_fusion.

This module provides the DevelopmentEnvironment class for configuring
all development tools at once including Debug Toolbar, Silk, Livereload,
and Sentry.

Classes:
    DevelopmentEnvironment: Complete development environment setup.

Functions:
    configure_all: Configure all development tools at once.

Usage::

    from django_fusion.contrib.debug_tools.development import DevelopmentEnvironment

    env = DevelopmentEnvironment()
    env.configure_all(installed_apps, middleware)
"""

from typing import Any

try:
    from core import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from .base import is_debug_mode
from .core import DebugToolbarSetup
from .prometheus import PrometheusSetup
from .sentry import SentrySetup


class DevelopmentEnvironment:
    """
    Complete development environment setup.
    """

    def __init__(self):
        self.debug_toolbar_setup = DebugToolbarSetup()
        self.sentry_setup = SentrySetup()

    def configure_all(
        self,
        installed_apps: list[str],
        middleware: list[str],
        positions: dict[str, int | None] = None,
        include_prometheus: bool = True,
        sentry_dsn: str | None = None,
        sentry_environment: str = "development"
    ) -> dict[str, Any]:
        """
        Configure all development tools at once.

        Args:
            installed_apps: Current INSTALLED_APPS
            middleware: Current MIDDLEWARE
            positions: Positions for all middleware
            include_prometheus: Whether to include Prometheus
            sentry_dsn: Sentry DSN (optional)
            sentry_environment: Sentry environment name

        Returns:
            Dictionary with all configured settings
        """
        result = {
            'installed_apps': installed_apps.copy(),
            'middleware': middleware.copy(),
            'debug_toolbar_config': {},
            'silk_config': {},
            'livereload_config': {},
            'sentry_config': {},
        }

        # Check if debug mode is enabled
        if not is_debug_mode():
            logger.debug("DEBUG is False, skipping development tools configuration.")
            return result

        # Configure debug apps and middleware
        updated_apps, updated_middleware = self.debug_toolbar_setup.do_settings(
            installed_apps=installed_apps,
            middleware=middleware,
            positions=positions,
            add_to_beginning=True,
            include_all=True
        )

        result['installed_apps'] = updated_apps
        result['middleware'] = updated_middleware

        # Configure Prometheus
        if include_prometheus:
            prometheus_apps, prometheus_middleware = PrometheusSetup.configure(
                installed_apps=updated_apps,
                middleware=updated_middleware,
                enabled=True,
                positions=positions
            )
            result['installed_apps'] = prometheus_apps
            result['middleware'] = prometheus_middleware

        # Configure individual tool settings
        tool_configs = self.debug_toolbar_setup.configure_all_tools()
        result.update(tool_configs)

        # Configure Sentry
        if sentry_dsn:
            result['sentry_config'] = self.sentry_setup.configure(
                dsn=sentry_dsn,
                environment=sentry_environment
            )

        # Create profiles directory
        self.debug_toolbar_setup.create_profiles_directory()

        return result

    def print_status(self):
        """Print development tools status."""
        self.debug_toolbar_setup.print_status()
