"""Public web view mixins for django-fusion sites.

This module re-exports the canonical ``FilterMixin`` and ``SearchMixin``
implementations so consumers can use the documented import path:

    from django_fusion.web.views import FilterMixin, SearchMixin
"""

from django_fusion.core.views.mixins import FilterMixin, SearchMixin

__all__ = [
    "FilterMixin",
    "SearchMixin",
]
