"""
Managers module for Django Seed.

This module provides manager classes for managing objects, caches, and services.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, TypeVar
from uuid import UUID
import logging

from django_seed.domain.entities import SeedObject, CacheEntry, ServiceDefinition
from django_seed.domain.repositories import (
    SeedObjectRepository,
    CacheRepository,
    ServiceRepository,
    UnitOfWork,
)

T = TypeVar('T')
logger = logging.getLogger(__name__)


class BaseManager:
    """Base manager class."""

    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    def _get_repository(self, repo_type):
        """Get a repository from the unit of work."""
        return self.unit_of_work.get_repository(repo_type)


class SeedObjectManager(BaseManager):
    """Manager for SeedObject entities."""

    def __init__(self, unit_of_work: UnitOfWork):
        super().__init__(unit_of_work)
        self.seed_object_repo = self._get_repository(SeedObjectRepository)

    def create_object(
        self,
        name: str,
        object_type: str,
        data: dict,
        metadata: Optional[dict] = None,
        tags: Optional[List[str]] = None,
        is_active: bool = True
    ) -> SeedObject:
        """Create a new seed object."""
        with self.unit_of_work:
            obj = SeedObject(
                name=name,
                object_type=object_type,
                data=data,
                metadata=metadata or {},
                tags=tags or [],
                is_active=is_active
            )
            return self.seed_object_repo.save(obj)

    def get_object(self, object_id: UUID) -> Optional[SeedObject]:
        """Get a seed object by ID."""
        return self.seed_object_repo.get_by_id(object_id)

    def update_object(
        self,
        object_id: UUID,
        data: Optional[dict] = None,
        metadata: Optional[dict] = None,
        tags: Optional[List[str]] = None,
        is_active: Optional[bool] = None
    ) -> Optional[SeedObject]:
        """Update a seed object."""
        obj = self.get_object(object_id)
        if not obj:
            return None

        if data is not None:
            obj.update_data(data)

        if metadata is not None:
            obj.metadata.update(metadata)

        if tags is not None:
            obj.tags = tags

        if is_active is not None:
            obj.is_active = is_active

        return self.seed_object_repo.save(obj)

    def delete_object(self, object_id: UUID) -> bool:
        """Delete a seed object."""
        return self.seed_object_repo.delete(object_id)

    def find_objects(
        self,
        object_type: Optional[str] = None,
        tag: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[SeedObject]:
        """Find seed objects by criteria."""
        filters = {}
        if object_type:
            filters['object_type'] = object_type
        if tag:
            filters['tag'] = tag
        if is_active is not None:
            filters['is_active'] = is_active

        return self.seed_object_repo.find_all(**filters)

    def get_by_tag(self, tag: str) -> List[SeedObject]:
        """Get all objects with a specific tag."""
        return self.seed_object_repo.get_by_tag(tag)

    def get_by_type(self, object_type: str) -> List[SeedObject]:
        """Get all objects of a specific type."""
        return self.seed_object_repo.get_by_type(object_type)


class CacheManager(BaseManager):
    """Manager for cache operations."""

    def __init__(self, unit_of_work: UnitOfWork):
        super().__init__(unit_of_work)
        self.cache_repo = self._get_repository(CacheRepository)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from cache."""
        entry = self.cache_repo.get(key)
        if entry and not entry.is_expired():
            entry.hit()
            return entry.value
        return default

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache."""
        entry = CacheEntry(
            key=key,
            value=value,
            expires_at=ttl
        )
        return self.cache_repo.set(entry)

    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        return self.cache_repo.delete(key)

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        return self.cache_repo.exists(key)

    def clear(self) -> bool:
        """Clear all cache entries."""
        return self.cache_repo.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'size': len(self.cache_repo.get_all()),
            'hits': sum(1 for entry in self.cache_repo.get_all() if entry.hits > 0),
            'total_hits': sum(entry.hits for entry in self.cache_repo.get_all())
        }


class ServiceManager(BaseManager):
    """Manager for services."""

    def __init__(self, unit_of_work: UnitOfWork):
        super().__init__(unit_of_work)
        self.service_repo = self._get_repository(ServiceRepository)

    def register_service(
        self,
        name: str,
        service_type: str,
        implementation: str,
        configuration: Optional[dict] = None,
        priority: int = 0
    ) -> ServiceDefinition:
        """Register a new service."""
        service = ServiceDefinition(
            name=name,
            service_type=service_type,
            implementation=implementation,
            configuration=configuration or {},
            priority=priority
        )
        return self.service_repo.save(service)

    def get_service(self, service_id: UUID) -> Optional[ServiceDefinition]:
        """Get a service by ID."""
        return self.service_repo.get_by_id(service_id)

    def get_services_by_type(self, service_type: str) -> List[ServiceDefinition]:
        """Get all services of a specific type."""
        return self.service_repo.get_by_type(service_type)

    def get_enabled_services(self) -> List[ServiceDefinition]:
        """Get all enabled services."""
        return self.service_repo.get_enabled_services()

    def enable_service(self, service_id: UUID) -> bool:
        """Enable a service."""
        service = self.service_repo.get_by_id(service_id)
        if service:
            service.enable()
            self.service_repo.save(service)
            return True
        return False

    def disable_service(self, service_id: UUID) -> bool:
        """Disable a service."""
        service = self.service_repo.get_by_id(service_id)
        if service:
            service.disable()
            self.service_repo.save(service)
            return True
        return False


class ObjectTypeManager(BaseManager):
    """Manager for object types."""

    def __init__(self, unit_of_work: UnitOfWork):
        super().__init__(unit_of_work)
        self.object_type_repo = self._get_repository(ObjectTypeRepository)

    def register_type(
        self,
        name: str,
        version: str = "1.0.0",
        schema: Optional[dict] = None,
        metadata: Optional[dict] = None
    ):
        """Register a new object type."""
        from django_seed.domain.value_objects import ObjectType

        obj_type = ObjectType(
            name=name,
            version=version,
            schema=schema or {},
            metadata=metadata or {}
        )
        return self.object_type_repo.save(obj_type)

    def get_type(self, name: str, version: Optional[str] = None):
        """Get an object type by name and optional version."""
        return self.object_type_repo.get_by_name(name, version)

    def validate_object(self, object_type: str, data: dict) -> bool:
        """Validate an object against its type schema."""
        obj_type = self.get_type(object_type)
        if not obj_type:
            return False

        # Simple schema validation
        # In a real implementation, this would validate against a JSON schema
        return True

    def get_all_types(self):
        """Get all registered object types."""
        return self.object_type_repo.get_all()


# Default managers
seed_object_manager = SeedObjectManager()
cache_manager = CacheManager()
service_manager = ServiceManager()
object_type_manager = ObjectTypeManager()
