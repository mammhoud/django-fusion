"""
Prometheus configuration for django_fusion.

This module provides Prometheus metrics configuration including app
and middleware setup for monitoring Django applications.

Classes:
    PrometheusSetup: Prometheus metrics configuration.

Functions:
    configure: Configure Prometheus metrics.
    is_installed: Check if Prometheus is installed.
    get_status: Get Prometheus status.

Usage::

    from django_fusion.contrib.debug_tools.prometheus import PrometheusSetup

    setup = PrometheusSetup()
    apps, middleware = setup.configure(installed_apps, middleware)
"""

from typing import Any

try:
    from core import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from .base import BaseSetup
from .config import (
    PROMETHEUS_AFTER_MIDDLEWARE,
    PROMETHEUS_APP,
    PROMETHEUS_BEFORE_MIDDLEWARE,
)


class PrometheusSetup(BaseSetup):
    """
    Prometheus metrics configuration.
    """

    @classmethod
    def configure(
        cls,
        installed_apps: list[str],
        middleware: list[str],
        enabled: bool = True,
        positions: dict[str, int | None] = None
    ) -> tuple[list[str], list[str]]:
        """
        Configure Prometheus metrics.

        Args:
            installed_apps: Current INSTALLED_APPS
            middleware: Current MIDDLEWARE
            enabled: Whether to enable Prometheus
            positions: Positions for Prometheus middleware

        Returns:
            Tuple of (updated_apps, updated_middleware)
        """
        if not enabled:
            return installed_apps[:], middleware[:]

        updated_apps = installed_apps[:]
        updated_middleware = middleware[:]

        # Add Prometheus app if not present
        if PROMETHEUS_APP not in updated_apps:
            updated_apps.append(PROMETHEUS_APP)
            logger.debug(f"Added {PROMETHEUS_APP} to INSTALLED_APPS")

        # Configure positions
        if positions is None:
            positions = {
                'prometheus_before': 0,  # First
                'prometheus_after': None,  # Last (append)
            }

        # Add Prometheus middleware
        if PROMETHEUS_BEFORE_MIDDLEWARE not in updated_middleware:
            updated_middleware = cls._add_middleware(
                updated_middleware,
                PROMETHEUS_BEFORE_MIDDLEWARE,
                positions.get('prometheus_before'),
                skip_if_exists=True
            )

        if PROMETHEUS_AFTER_MIDDLEWARE not in updated_middleware:
            updated_middleware = cls._add_middleware(
                updated_middleware,
                PROMETHEUS_AFTER_MIDDLEWARE,
                positions.get('prometheus_after'),
                skip_if_exists=True
            )

        return updated_apps, updated_middleware

    @classmethod
    def is_installed(cls) -> bool:
        """Check if Prometheus is installed."""
        return cls._is_package_installed('django_prometheus')

    @classmethod
    def get_status(cls) -> dict[str, Any]:
        """Get Prometheus status."""
        return {
            'name': 'prometheus',
            'installed': cls.is_installed(),
            'app_name': PROMETHEUS_APP,
            'middleware_classes': {
                'before': PROMETHEUS_BEFORE_MIDDLEWARE,
                'after': PROMETHEUS_AFTER_MIDDLEWARE,
            }
        }
