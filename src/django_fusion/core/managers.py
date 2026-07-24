"""Core manager shims for django-fusion.

This module re-exports cache-aware managers from the site management layer
so that consumer code can import them from a stable public path.
"""
from __future__ import annotations

from django.db import models

from django_fusion.site.management.managers.cache.managers import (
    CachedManager as TokenCachedManager,
)


class BaseManager(models.Manager):
    """Base manager with common query helpers."""
    pass


class RoleHierarchyManager(models.Manager):
    """Manager for role-based hierarchical queries."""
    pass


__all__ = ["TokenCachedManager", "BaseManager", "RoleHierarchyManager"]
