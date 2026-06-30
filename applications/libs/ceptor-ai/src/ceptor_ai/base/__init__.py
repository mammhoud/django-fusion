"""
Core ceptor_ai module.

Contains core configuration, apps, and integration points.

Canonical imports::
    from ceptor_ai.base import DjangoRsealConfig
"""

from ceptor_ai.apps import DjangoRsealConfig  # noqa: F401

__all__ = ["DjangoRsealConfig"]
