"""Generic class-based views — moved from django_fusion.site.generic.

CRUD, list, search, and table views. All are HTMX-aware.

Canonical import::

    from django_fusion.comp.generic import (
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
