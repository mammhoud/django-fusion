"""Django model manager classes with caching, role hierarchy, and search support.

All imports here are lazy-safe. Managers that depend on ``CachedManager``
(e.g. ``TokenCachedManager``) import it from ``django_fusion.core.cache``
directly in their own module to avoid circular-import issues.

Available managers
------------------
BaseManager             Thin manager base with common queryset shortcuts.
CacheSupportMixin       Mixin adding cache invalidation to any manager.
UncachedManager         Bypass-cache manager for admin and internal tooling.
TokenAwareManagerMixin  Token-based queryset filtering.
TokenCachedManager      Combined token-aware and cached manager.
UserManager             Custom user manager with create_user/create_superuser.
SearchManagerMixin      Full-text and trigram search on any manager.
RoleHierarchyManager    Role inheritance resolution.
GroupAccessControl      Group-based object permission scoping.
PersonTagCategoryManager, PersonTagManager, TaggedPersonManager  (tagging)

``CachedManager`` is available at ``django_fusion.core.cache.CachedManager``.

Usage::

    from django_fusion.core.managers import BaseManager, RoleHierarchyManager
    from django_fusion.core.cache import CachedManager   # avoid cycle
"""

from .base import BaseManager, CacheSupportMixin, UncachedManager
from .group_access import GroupAccessControl
from .role_hierarchy import RoleHierarchyManager
from .search import SearchManagerMixin
from .tags import PersonTagCategoryManager, PersonTagManager, TaggedPersonManager
from .user import UserManager

# token.py imports CachedManager from core.cache, not from here, so it is safe
from .token import TokenAwareManagerMixin, TokenCachedManager  # noqa: E402

# cached_method lives in core.managers.base — re-export it from here
from .base import cached_method  # noqa: E402
# CachedManager lives in core.cache — import after token to avoid cycle
from django_fusion.core.cache import CachedManager  # noqa: E402

__all__ = [
    "BaseManager",
    "CachedManager",
    "CacheSupportMixin",
    "GroupAccessControl",
    "PersonTagCategoryManager",
    "PersonTagManager",
    "RoleHierarchyManager",
    "SearchManagerMixin",
    "TaggedPersonManager",
    "TokenAwareManagerMixin",
    "TokenCachedManager",
    "UncachedManager",
    "UserManager",
]
