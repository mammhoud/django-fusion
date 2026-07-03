"""Generic class-based views — CRUD, list, search, and table views.

All views are HTMX-aware: partial-template responses are returned when
the request carries an ``HX-Request`` header, full-page responses otherwise.

Classes
-------
BaseListModelView   Abstract list base with pagination, sorting, and bulk actions.
ListModelView       Full-featured paginated list with search and filter support.
CreateModelView     Form-based create with HTMX fragment success response.
UpdateModelView     Form-based update with optimistic concurrency check.
DeleteModelView     Confirmation-based delete with HTMX redirect response.
DetailModelView     Read-only detail view with related-object context.
SearchableViewMixin Search-focused view mixin with relevance sorting.
TableView           DataTable-compatible view with JSON export support.
BaseBulkActionView  Base for bulk action views (status changes, operations).
DeleteBulkActionView    Confirmation-based bulk delete action.
Action              UI action descriptor (name, url, icon).

Usage::

    from django_osoul.site.generic import (
        ListModelView, CreateModelView, UpdateModelView, DeleteModelView,
    )
"""
from .actions import BaseBulkActionView, DeleteBulkActionView
from .base import Action
from .create import CreateModelView
from .delete import DeleteModelView
from .detail import DetailModelView
from .list import BaseListModelView, ListModelView
from .search import SearchableViewMixin
from .table import TableView
from .update import UpdateModelView

__all__ = [
    "Action",
    "BaseBulkActionView",
    "BaseListModelView",
    "CreateModelView",
    "DeleteBulkActionView",
    "DeleteModelView",
    "DetailModelView",
    "ListModelView",
    "SearchableViewMixin",
    "TableView",
    "UpdateModelView",
]
