"""
Repository interfaces for the Django Seed package.

This module defines repository interfaces for the domain layer.
"""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar, Protocol
from uuid import UUID

from django_seed.domain.entities import SeedObject, CacheEntry, ServiceDefinition
from django_seed.domain.value_objects import ObjectType, CacheKey

T = TypeVar('T')
Entity = TypeVar('Entity')


class Repository(Protocol[T]):
    """Protocol for repository interfaces."""

    @abstractmethod
    def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """Get an entity by its ID."""
        ...

    @abstractmethod
    def save(self, entity: T) -> T:
        """Save an entity."""
        ...

    @abstractmethod
    def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by ID."""
        ...

    @abstractmethod
    def find_all(self, **filters) -> List[T]:
        """Find all entities matching the filters."""
        ...


class SeedObjectRepository(Protocol):
    """Repository for SeedObject entities."""

    def get_by_id(self, object_id: UUID) -> Optional[SeedObject]:
        """Get a seed object by ID."""
        ...

    def get_by_name(self, name: str) -> Optional[SeedObject]:
        """Get a seed object by name."""
        ...

    def get_by_type(self, object_type: str) -> List[SeedObject]:
        """Get all seed objects of a specific type."""
        ...

    def get_by_tag(self, tag: str) -> List[SeedObject]:
        """Get all seed objects with a specific tag."""
        ...

    def save(self, seed_object: SeedObject) -> SeedObject:
        """Save a seed object."""
        ...

    def delete(self, object_id: UUID) -> bool:
        """Delete a seed object by ID."""
        ...

    def find_all(self, **filters) -> List[SeedObject]:
        """Find all seed objects matching the filters."""
        ...


class CacheRepository(Protocol):
    """Repository for cache entries."""

    def get(self, key: str) -> Optional[CacheEntry]:
        """Get a cache entry by key."""
        ...

    def set(self, key: str, value: any, ttl: Optional[int] = None) -> CacheEntry:
        """Set a cache entry."""
        ...

    def delete(self, key: str) -> bool:
        """Delete a cache entry by key."""
        ...

    def exists(self, key: str) -> bool:
        """Check if a cache entry exists."""
        ...

    def clear(self) -> None:
        """Clear all cache entries."""
        ...

    def get_all(self) -> List[CacheEntry]:
        """Get all cache entries."""
        ...


class ServiceRepository(Protocol):
    """Repository for service definitions."""

    def get_by_id(self, service_id: UUID) -> Optional[ServiceDefinition]:
        """Get a service definition by ID."""
        ...

    def get_by_type(self, service_type: str) -> List[ServiceDefinition]:
        """Get all services of a specific type."""
        ...

    def get_enabled_services(self) -> List[ServiceDefinition]:
        """Get all enabled services."""
        ...

    def save(self, service: ServiceDefinition) -> ServiceDefinition:
        """Save a service definition."""
        ...

    def delete(self, service_id: UUID) -> bool:
        """Delete a service definition by ID."""
        ...


class UnitOfWork(Protocol):
    """Unit of Work pattern for managing transactions."""

    def __enter__(self):
        """Enter the context manager."""
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        ...

    def commit(self):
        """Commit the transaction."""
        ...

    def rollback(self):
        """Rollback the transaction."""
        ...

    def get_repository(self, repo_type: type) -> any:
        """Get a repository of the specified type."""
        ...


class UnitOfWorkFactory(Protocol):
    """Factory for creating Unit of Work instances."""

    def create(self) -> UnitOfWork:
        """Create a new unit of work."""
        ...


# Repository implementations would go here in the infrastructure layer
# These are just the interfaces/abstract classes
