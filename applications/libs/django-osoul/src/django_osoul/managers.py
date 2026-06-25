"""Compatibility exports for legacy ``django_osoul.managers`` imports."""

from __future__ import annotations

from django_osoul.core.managers import *  # noqa: F401,F403
from django_osoul.core.managers import cached_method

__all__ = [
    "BaseManager",
    "CachedManager",
    "CacheSupportMixin",
    "UncachedManager",
    "TokenAwareManagerMixin",
    "UserManager",
    "SearchManagerMixin",
    "TokenCachedManager",
    "RoleHierarchyManager",
    "GroupAccessControl",
    "PersonTagCategoryManager",
    "PersonTagManager",
    "TaggedPersonManager",
    "cached_method",
]
