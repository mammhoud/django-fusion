"""
Django Osoul views module.

This module provides view mixins and base classes for Django applications.
These mixins provide common functionality for AJAX responses, JSON rendering,
user messages, dashboard integration, cart functionality, filtering, and search.

Classes:
    AjaxResponseMixin: Mixin for handling AJAX requests with appropriate responses.
    JSONResponseMixin: Mixin for rendering JSON responses.
    MessageMixin: Mixin for adding user messages to views.
    BaseDashboardMixin: Base mixin for dashboard views.
    BaseCartMixin: Base mixin for cart-related views.
    FilterMixin: Mixin for filtering querysets.
    SearchMixin: Mixin for search functionality.
"""

from .mixins import (
    AjaxResponseMixin,
    BaseCartMixin,
    BaseDashboardMixin,
    FilterMixin,
    JSONResponseMixin,
    MessageMixin,
    SearchMixin,
)

__all__ = [
    "AjaxResponseMixin",
    "BaseDashboardMixin",
    "BaseCartMixin",
    "FilterMixin",
    "JSONResponseMixin",
    "MessageMixin",
    "SearchMixin",
]
