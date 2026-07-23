"""Backward-compatibility re-exports for django_fusion.site._context_mixins.

The implementation moved to ``django_fusion.ci._context_mixins``.
"""
from django_fusion.ci._context_mixins import (  # noqa: F401
    BaseTemplateContextMixin,
    FragmentHandlerMixin,
    PaginatedBaseMixin,
    WagtailPageMixin,
    is_fragment_request,
    is_htmx_request,
)

__all__ = [
    "BaseTemplateContextMixin",
    "FragmentHandlerMixin",
    "PaginatedBaseMixin",
    "WagtailPageMixin",
    "is_fragment_request",
    "is_htmx_request",
]
