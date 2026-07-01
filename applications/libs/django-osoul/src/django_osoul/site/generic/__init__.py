"""Generic class-based views — CRUD, list, search, and table views.

All views are HTMX-aware: partial-template responses are returned when
the request carries an ``HX-Request`` header, full-page responses otherwise.

Classes
-------
BaseGenericView     Abstract base with permission checking and context injection.
GenericListView     Paginated list with optional search and filter support.
GenericListView2    Alternative list implementation with cursor-based pagination.
GenericCreateView   Form-based create with HTMX fragment success response.
GenericUpdateView   Form-based update with optimistic concurrency check.
GenericDeleteView   Confirmation-based delete with HTMX redirect response.
GenericDetailView   Read-only detail view with related-object context.
GenericSearchView   Search-focused view with relevance sorting.
GenericTableView    DataTable-compatible view with JSON export support.
GenericActionView   Non-form action view (status changes, bulk operations).

Usage::

    from django_osoul.site.generic import (
        GenericListView, GenericCreateView, GenericUpdateView, GenericDeleteView,
    )
"""
from .base import BaseGenericView
from .list import GenericListView
from .list2 import GenericListView2
from .create import GenericCreateView
from .update import GenericUpdateView
from .delete import GenericDeleteView
from .detail import GenericDetailView
from .search import GenericSearchView
from .table import GenericTableView
from .actions import GenericActionView

__all__ = [
    "BaseGenericView",
    "GenericListView",
    "GenericListView2",
    "GenericCreateView",
    "GenericUpdateView",
    "GenericDeleteView",
    "GenericDetailView",
    "GenericSearchView",
    "GenericTableView",
    "GenericActionView",
]
