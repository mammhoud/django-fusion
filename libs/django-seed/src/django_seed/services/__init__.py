"""
Services module for Django Seed.

This module provides service implementations for the Django Seed package.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Callable
from uuid import UUID
import logging
import importlib

from django_seed.domain.entities import SeedObject, CacheEntry, ServiceDefinition
from django_seed.domain.repositories import (
    SeedObjectRepository,
    CacheRepository,
    ServiceRepository,
    UnitOfWork,
)
from django_seed.domain.services import (
    SeedObjectService,
    CacheService,
    ServiceManager as DomainServiceManager,
    ObjectTypeService,
    DomainEventPublisher,
)
from django_seed.domain.value_objects import ObjectType

# Import service implementations
from .certificate_service import CertificateService, CertificateServiceFactory
from .form_submission_service import FormSubmissionService, FormSubmissionServiceFactory
from .message_service import MessageService, MessageServiceFactory
from .notes_service import NotesService, NotesServiceFactory
from .person_service import PersonService, PersonServiceFactory
from .email_service import EmailService, EmailServiceFactory

logger = logging.getLogger(__name__)


class ConcreteSeedObjectService(SeedObjectService):
    """Concrete implementation of SeedObjectService."""

    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    def create_object(
        self,
        name: str,
        object_type: str,
        data: dict,
        metadata: Optional[dict] = None,
        tags: Optional[List[str]] = None,
    ) -> SeedObject:
        """Create a new seed object."""
        from django_seed.managers import SeedObjectManager
        manager = SeedObjectManager(self.unit_of_work)
        return manager.create_object(
            name=name,
            object_type=object_type,
            data=data,
            metadata=metadata,
            tags=tags
        )

    def get_object(self, object_id: UUID) -> Optional[SeedObject]:
        """Get a seed object by ID."""
        from django_seed.managers import SeedObjectManager
        manager = SeedObjectManager(self.unit_of_work)
        return manager.get_object(object_id)

    def update_object(
        self,
        object_id: UUID,
        data: Optional[dict] = None,
        metadata: Optional[dict] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[SeedObject]:
        """Update a seed object."""
        from django_seed.managers import SeedObjectManager
        manager = SeedObjectManager(self.unit_of_work)
        return manager.update_object(
            object_id=object_id,
            data=data,
            metadata=metadata,
            tags=tags
        )

    def delete_object(self, object_id: UUID) -> bool:
        """Delete a seed object."""
        from django_seed.managers import SeedObjectManager
        manager = SeedObjectManager(self.unit_of_work)
        return manager.delete_object(object_id)

    def find_objects(
        self,
        object_type: Optional[str] = None,
        tag: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[SeedObject]:
        """Find seed objects by criteria."""
        from django_seed.managers import SeedObjectManager
        manager = SeedObjectManager(self.unit_of_work)
        return manager.find_objects(
            object_type=object_type,
            tag=tag,
            is_active=is_active
        )

    def activate_object(self, object_id: UUID) -> bool:
        """Activate a seed object."""
        obj = self.get_object(object_id)
        if not obj:
            return False

        obj.activate()
        from django_seed.managers import SeedObjectManager
        manager = SeedObjectManager(self.unit_of_work)
        manager.update_object(object_id, is_active=True)
        return True

    def deactivate_object(self, object_id: UUID) -> bool:
        """Deactivate a seed object."""
        obj = self.get_object(object_id)
        if not obj:
            return False

        obj.deactivate()
        from django_seed.managers import SeedObjectManager
        manager = SeedObjectManager(self.unit_of_work)
        manager.update_object(object_id, is_active=False)
        return True


class ConcreteCacheService(CacheService):
    """Concrete implementation of CacheService."""

    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        from django_seed.managers import CacheManager
        manager = CacheManager(self.unit_of_work)
        return manager.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache."""
        from django_seed.managers import CacheManager
        manager = CacheManager(self.unit_of_work)
        return manager.set(key, value, ttl)

    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        from django_seed.managers import CacheManager
        manager = CacheManager(self.unit_of_work)
        return manager.delete(key)

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        from django_seed.managers import CacheManager
        manager = CacheManager(self.unit_of_work)
        return manager.exists(key)

    def clear(self) -> bool:
        """Clear all cache entries."""
        from django_seed.managers import CacheManager
        manager = CacheManager(self.unit_of_work)
        return manager.clear()

    def get_stats(self) -> dict:
        """Get cache statistics."""
        from django_seed.managers import CacheManager
        manager = CacheManager(self.unit_of_work)
        return manager.get_stats()

    def get_keys(self, pattern: str = "*") -> List[str]:
        """Get cache keys matching a pattern."""
        # This would need to be implemented in the repository
        # For now, return empty list
        return []


class ConcreteServiceManager(DomainServiceManager):
    """Concrete implementation of ServiceManager."""

    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work
        self._service_cache = {}

    def register_service(
        self,
        name: str,
        service_type: str,
        implementation: str,
        configuration: Optional[dict] = None,
        priority: int = 0,
    ) -> ServiceDefinition:
        """Register a new service."""
        from django_seed.managers import ServiceManager
        manager = ServiceManager(self.unit_of_work)
        return manager.register_service(
            name=name,
            service_type=service_type,
            implementation=implementation,
            configuration=configuration,
            priority=priority
        )

    def get_service(self, service_id: UUID) -> Optional[ServiceDefinition]:
        """Get a service by ID."""
        from django_seed.managers import ServiceManager
        manager = ServiceManager(self.unit_of_work)
        return manager.get_service(service_id)

    def get_services_by_type(self, service_type: str) -> List[ServiceDefinition]:
        """Get all services of a specific type."""
        from django_seed.managers import ServiceManager
        manager = ServiceManager(self.unit_of_work)
        return manager.get_services_by_type(service_type)

    def enable_service(self, service_id: UUID) -> bool:
        """Enable a service."""
        from django_seed.managers import ServiceManager
        manager = ServiceManager(self.unit_of_work)
        return manager.enable_service(service_id)

    def disable_service(self, service_id: UUID) -> bool:
        """Disable a service."""
        from django_seed.managers import ServiceManager
        manager = ServiceManager(self.unit_of_work)
        return manager.disable_service(service_id)

    def update_service_config(
        self,
        service_id: UUID,
        configuration: dict,
    ) -> Optional[ServiceDefinition]:
        """Update service configuration."""
        service = self.get_service(service_id)
        if not service:
            return None

        service.update_configuration(configuration)
        from django_seed.managers import ServiceManager
        manager = ServiceManager(self.unit_of_work)
        return manager.register_service(
            name=service.name,
            service_type=service.service_type,
            implementation=service.implementation,
            configuration=configuration,
            priority=service.priority
        )

    def execute_service(
        self,
        service_id: UUID,
        *args,
        **kwargs,
    ) -> Any:
        """Execute a service."""
        service = self.get_service(service_id)
        if not service or not service.is_enabled:
            raise ValueError(f"Service {service_id} not found or disabled")

        # Import and execute the service
        try:
            module_path, class_name = service.implementation.rsplit('.', 1)
            module = importlib.import_module(module_path)
            service_class = getattr(module, class_name)
            service_instance = service_class(**service.configuration)
            return service_instance.execute(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error executing service {service_id}: {e}")
            raise


class ConcreteObjectTypeService(ObjectTypeService):
    """Concrete implementation of ObjectTypeService."""

    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    def register_type(
        self,
        name: str,
        version: str = "1.0.0",
        schema: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ) -> ObjectType:
        """Register a new object type."""
        from django_seed.managers import ObjectTypeManager
        manager = ObjectTypeManager(self.unit_of_work)
        return manager.register_type(
            name=name,
            version=version,
            schema=schema,
            metadata=metadata
        )

    def get_type(self, name: str, version: Optional[str] = None) -> Optional[ObjectType]:
        """Get an object type."""
        from django_seed.managers import ObjectTypeManager
        manager = ObjectTypeManager(self.unit_of_work)
        return manager.get_type(name, version)

    def validate_object(self, object_type: str, data: dict) -> bool:
        """Validate an object against its type schema."""
        from django_seed.managers import ObjectTypeManager
        manager = ObjectTypeManager(self.unit_of_work)
        return manager.validate_object(object_type, data)

    def get_all_types(self) -> List[ObjectType]:
        """Get all registered object types."""
        from django_seed.managers import ObjectTypeManager
        manager = ObjectTypeManager(self.unit_of_work)
        return manager.get_all_types()


class SimpleDomainEventPublisher(DomainEventPublisher):
    """Simple implementation of DomainEventPublisher."""

    def __init__(self):
        self._subscribers = {}

    def publish(self, event: Any) -> None:
        """Publish a domain event."""
        event_type = type(event)
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")

    def subscribe(self, event_type: type, handler: Callable) -> None:
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: type, handler: Callable) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            if handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)


# Default service instances
seed_object_service = ConcreteSeedObjectService()
cache_service = ConcreteCacheService()
service_manager = ConcreteServiceManager()
object_type_service = ConcreteObjectTypeService()
domain_event_publisher = SimpleDomainEventPublisher()

# Application-specific service factories
certificate_service_factory = CertificateServiceFactory()
form_submission_service_factory = FormSubmissionServiceFactory()
message_service_factory = MessageServiceFactory()
notes_service_factory = NotesServiceFactory()
person_service_factory = PersonServiceFactory()
email_service_factory = EmailServiceFactory()

# Export all services and factories
__all__ = [
    # Base service implementations
    'ConcreteSeedObjectService',
    'ConcreteCacheService',
    'ConcreteServiceManager',
    'ConcreteObjectTypeService',
    'SimpleDomainEventPublisher',

    # Application services
    'CertificateService',
    'CertificateServiceFactory',
    'FormSubmissionService',
    'FormSubmissionServiceFactory',
    'MessageService',
    'MessageServiceFactory',
    'NotesService',
    'NotesServiceFactory',
    'PersonService',
    'PersonServiceFactory',
    'EmailService',
    'EmailServiceFactory',

    # Default instances
    'seed_object_service',
    'cache_service',
    'service_manager',
    'object_type_service',
    'domain_event_publisher',
    'certificate_service_factory',
    'form_submission_service_factory',
    'message_service_factory',
    'notes_service_factory',
    'person_service_factory',
    'email_service_factory',
]
