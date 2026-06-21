"""
Core django_rseal module.

Contains core configuration, apps, and integration points.

Canonical imports::
    from django_rseal.base import DjangoRsealConfig
"""

from django_rseal.apps import DjangoRsealConfig  # noqa: F401

__all__ = ["DjangoRsealConfig"]
