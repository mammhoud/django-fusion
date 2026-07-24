"""Core manager exports for django-fusion.

This module is the stable public path for manager classes.  It aggregates
re-exports from the site management layer and provides local stubs for
managers that haven't been migrated to their canonical locations yet.
"""
from __future__ import annotations

from django.db import models

# ── Re-exports from site management layer ──
from django_fusion.site.management.managers.cache.managers import (
    CachedManager as _SiteCachedManager,
)
from django_fusion.site.management.managers.tags import (
    PersonTagCategoryManager,
)

# ── Public names ──
CachedManager = _SiteCachedManager


class TokenCachedManager(_SiteCachedManager):
    """Token-aware cached manager (alias for CachedManager)."""
    pass


class BaseManager(models.Manager):
    """Base manager with common query helpers."""
    pass


class RoleHierarchyManager(models.Manager):
    """Manager for role-based hierarchical queries."""
    pass


class GroupAccessControl(models.Manager):
    """Manager for group access control."""
    pass


class PersonTagManager(models.Manager):
    """Manager for person tags."""
    pass


class TaggedPersonManager(models.Manager):
    """Manager for tagged persons."""
    pass


def cached_method(method):
    """Decorator to cache method results.

    Simple pass-through stub — replace with real caching in production.
    """
    return method


__all__ = [
    "BaseManager",
    "CachedManager",
    "TokenCachedManager",
    "RoleHierarchyManager",
    "GroupAccessControl",
    "PersonTagManager",
    "TaggedPersonManager",
    "PersonTagCategoryManager",
    "cached_method",
]
