"""
Privacy consent middleware for django_fusion.

This module provides middleware for handling user consent for cookies
and other tracking technologies. It checks for consent before setting
non-essential cookies and provides consent management functionality.

Classes:
    PrivacyMiddleware: Middleware for handling privacy consent.

Usage in Django settings::

    MIDDLEWARE = [
        ...
        "django_fusion.contrib.privacy.middleware.PrivacyMiddleware",
    ]
"""

