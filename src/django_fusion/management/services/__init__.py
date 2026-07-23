"""
django_fusion.services
=====================

Generic service patterns for common operations.
"""
# Tagging service bases live in handlers.tagging but are re-exported here
# so that plugins can do: from django_fusion.core.services import TagServiceBase
from django_fusion.core.handlers.tagging import (  # noqa: F401
    PostFilterServiceBase,
    TagServiceBase,
)

from .base import BaseService, ModelService, ServiceRegistry  # noqa: F401
from .cart import CartServiceBase  # noqa: F401
from .crud import BatchCRUDService, CRUDService  # noqa: F401
from .person import PersonServiceBase  # noqa: F401

__all__ = [
    "BaseService",
    "ModelService",
    "ServiceRegistry",
    "CRUDService",
    "BatchCRUDService",
    "CartServiceBase",
    "PersonServiceBase",
    "TagServiceBase",
    "PostFilterServiceBase",
]
