"""
Base service framework.

Canonical imports::
    from django_fusion.services.base import ServiceRegistry
    from django_fusion.services.base import BaseService
    from django_fusion.services.base import ModelService
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

from django.db import models

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """
    Registry for services.

    Canonical import: from django_fusion.services.base import ServiceRegistry
    """

    _registry = {}

    @classmethod
    def register(cls, name: str, service_class: type["BaseService"]):
        """Register a service."""
        cls._registry[name] = service_class

    @classmethod
    def get(cls, name: str) -> type["BaseService"] | None:
        """Get a service by name."""
        return cls._registry.get(name)

    @classmethod
    def get_all(cls) -> dict[str, type["BaseService"]]:
        """Get all registered services."""
        return cls._registry.copy()


class BaseService(ABC):
    """
    Abstract base service.

    Canonical import: from django_fusion.services.base import BaseService
    """

    model_class: type[models.Model] = None
    service_name: str = None

    def __init__(self, model_class: type[models.Model] = None):
        if model_class:
            self.model_class = model_class

        # Model-free services, such as TokenService, can still use the
        # lifecycle and registry helpers. Model operations fail clearly in
        # ``manager``/``create`` if no model was configured.
        if self.service_name:
            ServiceRegistry.register(self.service_name, self.__class__)

    @property
    def manager(self):
        """Get the configured model manager.

        Model-free services are valid, but attempting a model operation on
        one should produce a useful error instead of an ``AttributeError``.
        """
        if self.model_class is None:
            raise ValueError("This service does not have a model_class")
        return self.model_class.objects

    @abstractmethod
    def execute(self, operation: str, **kwargs) -> Any:
        """Execute service operation."""

    def validate_input(self, data: dict[str, Any], operation: str) -> dict[str, Any]:
        """Validate input data."""
        # Override in subclasses
        return {"valid": True, "data": data}

    def handle_error(self, error: Exception, operation: str, **kwargs) -> Any:
        """Handle service errors."""
        logger.error(f"Service error in {operation}: {error}")
        raise error

    def before_execute(self, operation: str, **kwargs) -> dict[str, Any]:
        """Hook executed before service operation."""
        return kwargs

    def after_execute(self, operation: str, result: Any, **kwargs) -> Any:
        """Hook executed after service operation."""
        return result

    def run(self, operation: str, **kwargs) -> Any:
        """
        Run service operation with hooks and error handling.
        """
        try:
            # Pre-execution hook
            kwargs = self.before_execute(operation, **kwargs)

            # Execute operation
            result = self.execute(operation, **kwargs)

            # Post-execution hook
            result = self.after_execute(operation, result, **kwargs)

            return result

        except Exception as e:
            return self.handle_error(e, operation, **kwargs)

    # Common operations

    def get(self, identifier: Any, **kwargs) -> models.Model | None:
        """Get object by identifier."""
        return self.manager.get_by_field(identifier, **kwargs)

    def create(self, data: dict[str, Any], **kwargs) -> models.Model:
        """Create new object."""
        return self.model_class.objects.create(**data, **kwargs)

    def update(
        self,
        identifier: Any,
        data: dict[str, Any],
        **kwargs,
    ) -> models.Model | None:
        """Update existing object."""
        obj = self.get(identifier, **kwargs)
        if obj:
            for field, value in data.items():
                setattr(obj, field, value)
            obj.save()
        return obj

    def delete(self, identifier: Any, **kwargs) -> bool:
        """Delete object."""
        obj = self.get(identifier, **kwargs)
        if obj:
            obj.delete()
            return True
        return False

    def list(
        self,
        filters: dict[str, Any] = None,
        ordering: list[str] = None,
        limit: int = None,
        offset: int = 0,
        **kwargs,
    ) -> dict[str, Any]:
        """List objects with pagination."""
        qs = self.manager.all()

        if filters:
            qs = qs.filter(**filters)

        if ordering:
            qs = qs.order_by(*ordering)

        total_count = qs.count()

        if offset:
            qs = qs[offset:]
        if limit:
            qs = qs[:limit]

        results = list(qs)

        return {
            "results": results,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + len(results)) < total_count,
        }


class ModelService(BaseService):
    """
    Concrete service for model operations.

    Canonical import: from django_fusion.services.base import ModelService
    """

    def execute(self, operation: str, **kwargs) -> Any:
        """Execute model operation."""
        if operation == "get":
            return self.get(**kwargs)
        elif operation == "create":
            return self.create(**kwargs)
        elif operation == "update":
            return self.update(**kwargs)
        elif operation == "delete":
            return self.delete(**kwargs)
        elif operation == "list":
            return self.list(**kwargs)
        else:
            raise ValueError(f"Unknown operation: {operation}")
