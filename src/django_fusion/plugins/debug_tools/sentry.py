"""
Sentry configuration for django_fusion.

This module provides Sentry error tracking configuration including
Django, Celery, and Redis integrations.

Classes:
    SentrySetup: Sentry error tracking configuration.

Functions:
    configure: Configure Sentry error tracking.
    from_settings: Configure Sentry from Django settings.

Usage::

    from django_fusion.contrib.debug_tools.sentry import SentrySetup

    setup = SentrySetup()
    config = setup.configure(dsn, environment)
"""

import os
from typing import Any

try:
    from core import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from .base import is_debug_mode


class SentrySetup:
    """
    Sentry error tracking configuration.
    """

    @staticmethod
    def configure(
        dsn: str,
        environment: str = "development",
        **kwargs
    ) -> dict[str, Any] | None:
        """
        Configure Sentry error tracking.

        Args:
            dsn: Sentry DSN
            environment: Environment name
            **kwargs: Additional Sentry configuration options

        Returns:
            Sentry configuration dictionary or None
        """
        if not dsn or not is_debug_mode():
            return {}

        try:
            import sentry_sdk
            from sentry_sdk.integrations.celery import CeleryIntegration
            from sentry_sdk.integrations.django import DjangoIntegration
            from sentry_sdk.integrations.redis import RedisIntegration
        except ImportError:
            logger.warning("sentry-sdk not installed. Install with: pip install sentry-sdk")
            return {}

        default_config = {
            'dsn': dsn,
            'integrations': [
                DjangoIntegration(),
                CeleryIntegration(),
                RedisIntegration(),
            ],
            'traces_sample_rate': kwargs.get('traces_sample_rate', 0.5),
            'profiles_sample_rate': kwargs.get('profiles_sample_rate', 0.0),
            'send_default_pii': kwargs.get('send_default_pii', True),
            'environment': environment,
            'debug': kwargs.get('debug', True),
            'attach_stacktrace': kwargs.get('attach_stacktrace', True),
            'max_breadcrumbs': kwargs.get('max_breadcrumbs', 50),
            'release': kwargs.get('release', f"{os.getenv('APP_VERSION', '1.0.0')}"),
        }

        # Filter out None values
        default_config = {k: v for k, v in default_config.items() if v is not None}

        try:
            sentry_sdk.init(**default_config)
            logger.info(f"Sentry initialized for environment: {environment}")
            return default_config
        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}")
            return None

    @classmethod
    def from_settings(cls, settings):
        """
        Configure Sentry from Django settings.
        """
        if hasattr(settings, "SENTRY") and settings.SENTRY.ENABLED:
            return cls.configure(
                dsn=settings.SENTRY.DSN,
                environment=settings.SENTRY.get("ENVIRONMENT", "production"),
                traces_sample_rate=settings.SENTRY.get("TRACES_SAMPLE_RATE", 0.1),
                send_default_pii=settings.SENTRY.get("SEND_DEFAULT_PII", False),
            )
        return None
