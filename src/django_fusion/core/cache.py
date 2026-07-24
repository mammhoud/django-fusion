"""Core cache shim — re-exports CachedManager from site management layer."""
from __future__ import annotations

from django_fusion.site.management.managers.cache import CachedManager

__all__ = ["CachedManager"]
