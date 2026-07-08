"""
Privacy utilities for django_fusion.

Provides privacy-related utilities including middleware for cookie consent,
data anonymization, and privacy policy management.

Modules:
    privacy: Privacy policy and consent management utilities.

Usage in Django settings::

    MIDDLEWARE = [
        ...
        "django_fusion.contrib.privacy.middleware.PrivacyMiddleware",
    ]
"""

from .privacy import *  # noqa: F401, F403

__all__ = []
