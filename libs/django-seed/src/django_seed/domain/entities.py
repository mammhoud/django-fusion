"""
Entities for Django Seed package.

Entities are objects that have a distinct identity that runs through time
and different states. They are defined by their identity, not their attributes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Generic, Optional, TypeVar
from uuid import UUID, uuid4

from django.core.exceptions import ValidationError

from .value_objects import ValueObject

T = TypeVar('T', bound='Entity')


@dataclass(kw_only=True)
class Entity(Generic[T]):
    """Base class for all entities."""

    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate the entity after initialization."""
        self.validate()
        # Ensure updated_at is at least as recent as created_at
        if self.updated_at < self.created_at:
            self.updated_at = self.created_at

    def validate(self) -> None:
        """Validate the entity.

        Subclasses should override this method to implement validation logic.
        """
        pass

    def __eq__(self, other: Any) -> bool:
        """Two entities are equal if they have the same type and ID."""
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on the entity's ID."""
        return hash(self.id)

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()

    def is_new(self) -> bool:
        """Check if this entity is new (not yet persisted)."""
        # This is a simplified check - in a real implementation,
        # you might have a different way to track persistence
        return self.created_at == self.updated_at


@dataclass(kw_only=True)
class AggregateRoot(Entity[T]):
    """Base class for aggregate roots.

    Aggregate roots are entities that are the root of an aggregate,
    which is a cluster of associated objects that are treated as a unit
    for the purpose of data changes.
    """

    _domain_events: list = field(default_factory=list, init=False, repr=False)

    def add_domain_event(self, event: Any) -> None:
        """Add a domain event to the aggregate root."""
        self._domain_events.append(event)

    def clear_domain_events(self) -> list:
        """Clear and return all domain events."""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    @property
    def domain_events(self) -> list:
        """Get all domain events."""
        return self._domain_events.copy()


@dataclass(kw_only=True)
class SeedObject(AggregateRoot[T]):
    """Base class for seed objects.

    Seed objects are the core entities in the Django Seed package.
    They represent objects that can be cached, managed, and served.
    """

    name: str
    object_type: str
    data: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    is_active: bool = True
    version: int = 1

    def validate(self) -> None:
        """Validate the seed object."""
        if not self.name:
            raise ValidationError("Seed object name cannot be empty")
        if not self.object_type:
            raise ValidationError("Seed object type cannot be empty")
        if self.version < 1:
            raise ValidationError("Seed object version must be positive")

    def update_data(self, new_data: dict, increment_version: bool = True) -> None:
        """Update the object's data."""
        self.data.update(new_data)
        if increment_version:
            self.version += 1
        self.touch()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the object."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.touch()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the object."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.touch()

    def activate(self) -> None:
        """Activate the object."""
        if not self.is_active:
            self.is_active = True
            self.touch()

    def deactivate(self) -> None:
        """Deactivate the object."""
        if self.is_active:
            self.is_active = False
            self.touch()

    def to_dict(self) -> dict:
        """Convert the object to a dictionary."""
        return {
            'id': str(self.id),
            'name': self.name,
            'object_type': self.object_type,
            'data': self.data,
            'metadata': self.metadata,
            'tags': self.tags,
            'is_active': self.is_active,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> T:
        """Create a seed object from a dictionary."""
        return cls(
            id=UUID(data['id']) if 'id' in data else uuid4(),
            name=data['name'],
            object_type=data['object_type'],
            data=data.get('data', {}),
            metadata=data.get('metadata', {}),
            tags=data.get('tags', []),
            is_active=data.get('is_active', True),
            version=data.get('version', 1),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else datetime.now(),
        )


@dataclass(kw_only=True)
class CacheEntry(AggregateRoot[T]):
    """Cache entry entity."""

    key: str
    value: Any
    expires_at: Optional[datetime] = None
    hits: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)

    def validate(self) -> None:
        """Validate the cache entry."""
        if not self.key:
            raise ValidationError("Cache key cannot be empty")

    def hit(self) -> None:
        """Record a cache hit."""
        self.hits += 1
        self.last_accessed = datetime.now()
        self.touch()

    def is_expired(self) -> bool:
        """Check if the cache entry is expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def get_ttl(self) -> Optional[float]:
        """Get the time to live in seconds."""
        if self.expires_at is None:
            return None
        return (self.expires_at - datetime.now()).total_seconds()

    def extend(self, seconds: int) -> None:
        """Extend the expiration time."""
        if self.expires_at is None:
            self.expires_at = datetime.now()
        self.expires_at = self.expires_at.replace(
            microsecond=self.expires_at.microsecond + seconds * 1_000_000
        )
        self.touch()


@dataclass(kw_only=True)
class ServiceDefinition(AggregateRoot[T]):
    """Service definition entity."""

    name: str
    service_type: str
    implementation: str
    configuration: dict = field(default_factory=dict)
    is_enabled: bool = True
    priority: int = 0

    def validate(self) -> None:
        """Validate the service definition."""
        if not self.name:
            raise ValidationError("Service name cannot be empty")
        if not self.service_type:
            raise ValidationError("Service type cannot be empty")
        if not self.implementation:
            raise ValidationError("Service implementation cannot be empty")
        if self.priority < 0:
            raise ValidationError("Service priority cannot be negative")

    def enable(self) -> None:
        """Enable the service."""
        if not self.is_enabled:
            self.is_enabled = True
            self.touch()

    def disable(self) -> None:
        """Disable the service."""
        if self.is_enabled:
            self.is_enabled = False
            self.touch()

    def update_configuration(self, config: dict) -> None:
        """Update the service configuration."""
        self.configuration.update(config)
        self.touch()
