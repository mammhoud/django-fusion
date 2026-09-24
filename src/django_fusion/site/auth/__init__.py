"""Generic authentication utilities for django_fusion.

Submodules:
- mixins: AuthConfig, AuthBaseMixin, AuthValidatorMixin, AuthProcessorMixin

Usage::

    from django_fusion.site.auth import AuthConfig, AuthProcessorMixin
"""

from __future__ import annotations

from .mixins import (
    AuthBaseMixin,
    AuthConfig,
    AuthProcessorMixin,
    AuthValidatorMixin,
)

__all__ = [
    "AuthConfig",
    "AuthBaseMixin",
    "AuthValidatorMixin",
    "AuthProcessorMixin",
]
