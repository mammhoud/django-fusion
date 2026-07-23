"""Backward-compatibility re-exports for django_fusion.site.page_handler.

The implementation moved to ``django_fusion.ci.page_handler`` (and the
paginated helpers to ``django_fusion.ci.paginators``).
"""
from django_fusion.ci.page_handler import (  # noqa: F401
    ComponentViews,
    ModalComponent,
    PageHandler,
)
from django_fusion.ci.paginators import (  # noqa: F401
    PaginatedComponentView,
    PaginatedListView,
)

__all__ = [
    "ComponentViews",
    "ModalComponent",
    "PageHandler",
    "PaginatedComponentView",
    "PaginatedListView",
]
