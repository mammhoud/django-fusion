"""
django_osoul.comp.site.generic
===============================

Generic Django views for CRUD operations (List, Create, Update, Delete, Detail).
"""
from .actions import DeleteBulkActionView  # noqa: F401
from .base import Action  # noqa: F401
from .create import CreateModelView  # noqa: F401
from .delete import DeleteModelView  # noqa: F401
from .detail import DetailModelView  # noqa: F401
from .list import ListModelView  # noqa: F401
from .list2 import ListModelView as ListModelView2  # noqa: F401
from .table import TableView  # noqa: F401
from .update import UpdateModelView  # noqa: F401

__all__ = [
    "Action",
    "ListModelView",
    "ListModelView2",
    "CreateModelView",
    "UpdateModelView",
    "DeleteModelView",
    "DetailModelView",
    "DeleteBulkActionView",
    "TableView",
]
