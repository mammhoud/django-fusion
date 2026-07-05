"""
Development orchestrator for django_fusion.

This module provides the DevelopmentOrchestrator class for orchestrating
the complete development environment setup including logging, monitoring,
and development tools.

Classes:
    DevelopmentOrchestrator: Orchestrator for complete development environment setup.

Usage::

    from django_fusion.contrib.debug_tools.orchestrator import DevelopmentOrchestrator

    orchestrator = DevelopmentOrchestrator()
    orchestrator.setup_environment(installed_apps, middleware)
"""

from typing import Any

try:
    from core import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from configs.settings import settings

from .base import is_debug_mode
from .development import DevelopmentEnvironment
from .monitoring import MonitoringSetup


class DevelopmentOrchestrator:
    """
    Orchestrator for complete development environment setup.
    """

    def __init__(self):
        self.development_env = DevelopmentEnvironment()
        self.monitoring_setup = MonitoringSetup()

    def setup_environment(
        self,
        installed_apps: list[str],
        middleware: list[str],
        debug: bool = None,
        sentry_dsn: str | None = None,
        **kwargs
    ) -> dict[str, Any]:
        """
        Complete development environment setup.
        Combines logging, monitoring, and development tools.

        Args:
            installed_apps: Current INSTALLED_APPS
            middleware: Current MIDDLEWARE
            debug: Whether debug mode is enabled
            sentry_dsn: Sentry DSN (optional)
            **kwargs: Additional configuration options

        Returns:
            Complete configuration dictionary
        """
        if debug is None:
            debug = is_debug_mode()

        result = {
            "debug": debug,
            "installed_apps": installed_apps.copy(),
            "middleware": middleware.copy(),
            "development_tools_configured": False,
            "monitoring_configured": False,
        }

        # Step 1: Configure development tools (if debug mode)
        if debug:
            try:
                dev_config = self.development_env.configure_all(
                    installed_apps=installed_apps,
                    middleware=middleware,
                    positions=kwargs.get("positions"),
                    include_prometheus=kwargs.get("include_prometheus", True),
                    sentry_dsn=sentry_dsn,
                    sentry_environment=kwargs.get("sentry_environment", settings.SERVER_ENV.value)
                )

                # Update results
                result["installed_apps"] = dev_config["installed_apps"]
                result["middleware"] = dev_config["middleware"]
                result["development_tools_configured"] = True
                result["development_config"] = dev_config

                # Print status
                if kwargs.get("print_status", True):
                    self.development_env.print_status()

            except Exception as e:
                print(f"⚠️  Error configuring development tools: {e}")
                result["development_tools_error"] = str(e)

        # Step 2: Setup monitoring
        monitoring_config = self.monitoring_setup.setup(
            enable_prometheus=kwargs.get("enable_prometheus", True),
            enable_health_checks=kwargs.get("enable_health_checks", True),
            enable_sentry=bool(sentry_dsn),
            sentry_dsn=sentry_dsn
        )
        result.update(monitoring_config)

        # Log completion
        logger.info(
            "Development environment configured",
            debug=debug,
            tools_configured=result.get("development_tools_configured", False),
            sentry_configured=result.get("sentry_enabled", False)
        )

        return result
