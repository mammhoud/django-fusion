"""
Domain layer for Django Seed package.

This module contains the domain layer of the Django Seed package,
including entities, value objects, and domain services.
"""

from .entities import Entity, AggregateRoot, SeedObject, CacheEntry, ServiceDefinition
from .value_objects import (
    ValueObject, Email, Money, Percentage, Duration,
    ObjectType, CacheKey, Money, Percentage, Duration, ObjectType, CacheKey
)
from .repositories import (
    Repository,
    SeedObjectRepository,
    CacheRepository,
    ServiceRepository,
    UnitOfWork,
    UnitOfWorkFactory,
)
from .services import (
    SeedObjectService,
    CacheService,
    ServiceManager,
    ObjectTypeService,
    DomainEventPublisher,
)

__all__ = [
    # Entities
    'Entity',
    'AggregateRoot',
    'SeedObject',
    'CacheEntry',
    'ServiceDefinition',

    # Value Objects
    'ValueObject',
    'Email',
    'Money',
    'Percentage',
    'Duration',
    'ObjectType',
    'CacheKey',

    # Repositories
    'Repository',
    'SeedObjectRepository',
    'CacheRepository',
    'ServiceRepository',
    'UnitOfWork',
    'UnitOfWorkFactory',

    # Services
    'SeedObjectService',
    'CacheService',
    'ServiceManager',
    'ObjectTypeService',
    'DomainEventPublisher',
]
