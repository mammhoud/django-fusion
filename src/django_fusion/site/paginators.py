"""Backward-compatibility re-exports for django_fusion.site.paginators.

The implementation moved to ``django_fusion.ci.paginators``.
"""
from django_fusion.ci.paginators import (  # noqa: F401
    HTMXPaginationMixin,
    PaginatedComponentView,
    PaginatedListView,
)

__all__ = [
    "HTMXPaginationMixin",
    "PaginatedComponentView",
    "PaginatedListView",
]
