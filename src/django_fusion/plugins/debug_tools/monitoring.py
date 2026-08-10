"""
Monitoring setup for django_fusion.

This module provides comprehensive monitoring setup including Prometheus
metrics and Sentry error tracking configuration.

Classes:
    MonitoringSetup: Comprehensive monitoring setup.

Functions:
    setup: Setup comprehensive monitoring.

Usage::

    from django_fusion.contrib.debug_tools.monitoring import MonitoringSetup

    setup = MonitoringSetup()
    config = setup.setup(enable_prometheus=True, enable_sentry=True)
"""

from typing import Any

try:
    from core import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from django.conf import settings

from .prometheus import PrometheusSetup
from .sentry import SentrySetup


class MonitoringSetup:
    """
    Comprehensive monitoring setup.
    """

    @staticmethod
    def setup(
        enable_prometheus: bool = True,
        enable_health_checks: bool = True,
        enable_sentry: bool = True,
        sentry_dsn: str | None = None
    ) -> dict[str, Any]:
        """
        Setup comprehensive monitoring.

        Args:
            enable_prometheus: Enable Prometheus metrics
            enable_health_checks: Enable health checks
            enable_sentry: Enable Sentry error tracking
            sentry_dsn: Sentry DSN (optional)

        Returns:
            Monitoring configuration
        """
        result = {
            "prometheus_enabled": enable_prometheus,
            "health_checks_enabled": enable_health_checks,
            "sentry_enabled": False,
            "sentry_config": None,
        }
        print("="*65)

        # Configure Sentry
        if enable_sentry:
            sentry_dsn_to_use = sentry_dsn
            sentry_section = getattr(settings, "SENTRY", {})
            sentry_enabled = (
                sentry_section.get("ENABLED", False)
                if isinstance(sentry_section, dict)
                else getattr(sentry_section, "ENABLED", False)
            )
            if not sentry_dsn_to_use and sentry_enabled:
                sentry_dsn_to_use = (
                    sentry_section.get("DSN")
                    if isinstance(sentry_section, dict)
                    else getattr(sentry_section, "DSN", None)
                )

            if sentry_dsn_to_use:
                sentry_config = SentrySetup.configure(
                    dsn=sentry_dsn_to_use,
                    environment=getattr(settings, "SERVER_ENV", "development"),
                    debug=getattr(settings, "DEBUG", False)
                )
                if sentry_config:
                    result["sentry_enabled"] = True
                    result["sentry_config"] = sentry_config
                    print("✅ Sentry configured")
            else:
                print("⚠️  Sentry disabled: No DSN provided")

        # Configure Prometheus
        if enable_prometheus:
            if PrometheusSetup.is_installed():
                result["prometheus_available"] = True
                result["prometheus_status"] = PrometheusSetup.get_status()
            else:
                print("⚠️  Prometheus not available: django-prometheus not installed")

        print("🚀 ENVIRONMENT CONFIGURED".center(60))
        print("="*65)

        return result
