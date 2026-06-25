"""
Managers module for django_osoul.

Provides custom Django model managers and QuerySet classes for common
data access patterns including caching, role hierarchy, group access,
search, tagging, and token-aware queries.

Classes:
    BaseManager: Base manager with common query utilities.
    CachedManager: Manager with built-in caching support.
    CacheSupportMixin: Mixin adding cache support to managers.
    UncachedManager: Manager that bypasses caching.
    TokenAwareManagerMixin: Mixin for token-based access control.
    UserManager: Custom manager for user models.
    SearchManagerMixin: Mixin adding full-text search capabilities.
    TokenCachedManager: Cached manager with token-aware queries.
    RoleHierarchyManager: Manager for role-based hierarchy access.
    GroupAccessControl: Manager for group-based access control.
    PersonTagCategoryManager: Manager for person tag categories.
    PersonTagManager: Manager for person tags.
    TaggedPersonManager: Manager for tagged person records.

Functions:
    cached_method: Decorator for caching manager method results.

Canonical imports::

    from django_osoul.core.managers import RoleHierarchyManager
    from django_osoul.core.managers import GroupAccessControl
    from django_osoul.core.managers import UserManager
    from django_osoul.core.managers import GroupManager
    from django_osoul.core.managers import BaseManager, CachedManager
"""

from .base import BaseManager, CachedManager, CacheSupportMixin, UncachedManager, cached_method
from .group_access import GroupAccessControl
from .role_hierarchy import RoleHierarchyManager
from .search import SearchManagerMixin
from .tags import PersonTagCategoryManager, PersonTagManager, TaggedPersonManager
from .token import TokenAwareManagerMixin, TokenCachedManager
from .user import UserManager

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
]
from django_osoul.cache import CachedManager, CachedModelManager
