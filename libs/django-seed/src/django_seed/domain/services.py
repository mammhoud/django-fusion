"""
Domain services for the Django Seed package.

Domain services contain business logic that doesn't naturally fit within entities.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Protocol
from uuid import UUID

from django_seed.domain.entities import SeedObject, CacheEntry, ServiceDefinition
from django_seed.domain.repositories import (
    SeedObjectRepository,
    CacheRepository,
    ServiceRepository,
    UnitOfWork,
)
from django_seed.domain.value_objects import ObjectType, CacheKey


class SeedObjectService(Protocol):
    """Service for managing seed objects."""

    def create_object(
        self,
        name: str,
        object_type: str,
        data: dict,
        metadata: Optional[dict] = None,
        tags: Optional[List[str]] = None,
    ) -> SeedObject:
        """Create a new seed object."""
        ...

    def get_object(self, object_id: UUID) -> Optional[SeedObject]:
        """Get a seed object by ID."""
        ...

    def update_object(
        self,
        object_id: UUID,
        data: Optional[dict] = None,
        metadata: Optional[dict] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[SeedObject]:
        """Update a seed object."""
        ...

    def delete_object(self, object_id: UUID) -> bool:
        """Delete a seed object."""
        ...

    def find_objects(
        self,
        object_type: Optional[str] = None,
        tag: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[SeedObject]:
        """Find seed objects by criteria."""
        ...

    def activate_object(self, object_id: UUID) -> bool:
        """Activate a seed object."""
        ...

    def deactivate_object(self, object_id: UUID) -> bool:
        """Deactivate a seed object."""
        ...


class CacheService(Protocol):
    """Service for managing cache operations."""

    def get(self, key: str) -> Optional[any]:
        """Get a value from cache."""
        ...

    def set(self, key: str, value: any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache."""
        ...

    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        ...

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        ...

    def clear(self) -> bool:
        """Clear all cache entries."""
        ...

    def get_stats(self) -> dict:
        """Get cache statistics."""
        ...

    def get_keys(self, pattern: str = "*") -> List[str]:
        """Get cache keys matching a pattern."""
        ...


class ServiceManager(Protocol):
    """Service manager for managing service definitions."""

    def register_service(
        self,
        name: str,
        service_type: str,
        implementation: str,
        configuration: Optional[dict] = None,
        priority: int = 0,
    ) -> ServiceDefinition:
        """Register a new service."""
        ...

    def get_service(self, service_id: UUID) -> Optional[ServiceDefinition]:
        """Get a service by ID."""
        ...

    def get_services_by_type(self, service_type: str) -> List[ServiceDefinition]:
        """Get all services of a specific type."""
        ...

    def enable_service(self, service_id: UUID) -> bool:
        """Enable a service."""
        ...

    def disable_service(self, service_id: UUID) -> bool:
        """Disable a service."""
        ...

    def update_service_config(
        self,
        service_id: UUID,
        configuration: dict,
    ) -> Optional[ServiceDefinition]:
        """Update service configuration."""
        ...

    def execute_service(
        self,
        service_id: UUID,
        *args,
        **kwargs,
    ) -> any:
        """Execute a service."""
        ...


class ObjectTypeService(Protocol):
    """Service for managing object types."""

    def register_type(
        self,
        name: str,
        version: str = "1.0.0",
        schema: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ) -> ObjectType:
        """Register a new object type."""
        ...

    def get_type(self, name: str, version: Optional[str] = None) -> Optional[ObjectType]:
        """Get an object type."""
        ...

    def validate_object(self, object_type: str, data: dict) -> bool:
        """Validate an object against its type schema."""
        ...

    def get_all_types(self) -> List[ObjectType]:
        """Get all registered object types."""
        ...


class DomainEventPublisher(Protocol):
    """Publisher for domain events."""

    def publish(self, event: any) -> None:
        """Publish a domain event."""
        ...

    def subscribe(self, event_type: type, handler: callable) -> None:
        """Subscribe to an event type."""
        ...

    def unsubscribe(self, event_type: type, handler: callable) -> None:
        """Unsubscribe from an event type."""
        ...


# Concrete implementations would go in the application or infrastructure layer
# These are just the interfaces/abstract classes
