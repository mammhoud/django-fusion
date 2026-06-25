"""
Core crafts_ai module.

Contains core configuration, apps, and integration points.

Canonical imports::
    from crafts_ai.base import DjangoRsealConfig
"""

from crafts_ai.apps import DjangoRsealConfig  # noqa: F401

__all__ = ["DjangoRsealConfig"]
