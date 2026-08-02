"""
Handler mixins for django_fusion.

This package contains reusable mixin classes for handlers that are pure Django
and can be used across projects without Wagtail dependencies.
"""

from .fragment import ProfileOperationsMixin  # noqa
from .page import ProfileContextMixin, ProfileDashboardMixin  # noqa
"""
Mixins module exports.
"""

from .cache import CacheMixin, CacheSearchMixin
from .search import SearchMixin, UniversalSearchMixin
from .token import TokenAuthMixin, TokenProtectedMixin

__all__ = [
    'CacheMixin',
    'CacheSearchMixin',
    'TokenAuthMixin',
    'TokenProtectedMixin',
    'SearchMixin',
    'UniversalSearchMixin',
]

__all__ = [
    "ProfileOperationsMixin",
    "ProfileContextMixin",
    "ProfileDashboardMixin",
]
