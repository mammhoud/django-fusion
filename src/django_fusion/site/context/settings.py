"""Backward-compatibility re-exports for django_fusion.site.context.settings.

The implementation moved to ``django_fusion.ci.context.settings``.
"""
from django_fusion.ci.context.settings import SETTINGS  # noqa: F401

__all__ = ["SETTINGS"]
