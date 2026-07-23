"""Backward-compatibility re-exports for django_fusion.site.adapters.main.

The implementation moved to ``django_fusion.ci.adapters.main``.
"""
from django_fusion.ci.adapters.main import DjangoAdapter  # noqa: F401

__all__ = ["DjangoAdapter"]
