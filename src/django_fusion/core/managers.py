"""Core manager shims for django-fusion.

This module re-exports cache-aware managers from the site management layer
so that consumer code can import them from a stable public path.
"""
from __future__ import annotations

from django_fusion.site.management.managers.cache.managers import (
    CachedManager as TokenCachedManager,
)

__all__ = ["TokenCachedManager"]
