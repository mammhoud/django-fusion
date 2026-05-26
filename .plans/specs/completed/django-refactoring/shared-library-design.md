# Shared Library Structure Design

## Overview
This document outlines the design for the shared library structure, focusing on django_osoul as the foundation layer for the refactored Django codebase.

## 1. Library Architecture

### 1.1 Core Principles
1. **Dependency Inversion**: High-level modules depend on abstractions
2. **Single Responsibility**: Each module has one clear purpose
3. **Open/Closed**: Open for extension, closed for modification
4. **Interface Segregation**: Small, focused interfaces
5. **Liskov Substitution**: Subtypes are substitutable for base types

### 1.2 Library Boundaries
- **django_osoul**: Foundation layer (models, utilities, base classes)
- **django_rseal**: Pipeline and automation layer
- **django_grep**: Testing and quality assurance layer

## 2. django_osoul Structure

### 2.1 Core Package Structure
```
django_osoul/
├── __init__.py              # Public API exports
├── conf.py                  # Configuration utilities
├── constants.py             # Shared constants
├── enums.py                 # Shared enumerations
├── exceptions.py            # Base exception classes
├── typing.py                # Type hints and aliases
├── logging_config.py        # Logging configuration
├── rendering.py             # Template rendering utilities
├── forms.py                 # Base form classes
│
├── domain/                  # Domain layer (DDD)
│   ├── __init__.py
│   ├── entities/           # Domain entities
│   ├── value_objects/      # Value objects
│   ├── events/             # Domain events
│   ├── services/           # Domain services
│   └── repositories/       # Repository interfaces
│
├── application/            # Application layer
│   ├── __init__.py
│   ├── use_cases/         # Application use cases
│   ├── dto/               # Data transfer objects
│   ├── services/          # Application services
│   └── events/            # Application event handlers
│
├── infrastructure/         # Infrastructure layer
│   ├── __init__.py
│   ├── persistence/       # Database implementations
│   ├── external/          # External service adapters
│   ├── messaging/         # Message brokers, queues
│   └── caching/           # Cache implementations
│
├── interfaces/             # Interface layer
│   ├── __init__.py
│   ├── web/               # Web controllers
│   ├── api/               # REST/GraphQL APIs
│   ├── cli/               # Command line interfaces
│   └── events/            # Event consumers/producers
│
├── models/                 # Django models (legacy/transitional)
│   ├── __init__.py
│   ├── base.py            # Base model classes
│   ├── mixins.py          # Model mixins
│   ├── managers.py        # Custom managers
│   └── querysets.py       # Custom querysets
│
├── views/                  # Django views
│   ├── __init__.py
│   ├── mixins.py          # View mixins
│   ├── base.py            # Base view classes
│   └── generics.py        # Generic view classes
│
├── services/               # Service layer
│   ├── __init__.py
│   ├── base.py            # Base service classes
│   ├── crud.py            # CRUD service implementations
│   └── validators.py      # Service-level validation
│
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── text.py            # Text manipulation
│   ├── datetime_utils.py  # Date/time utilities
│   ├── validators.py      # Input validators
│   ├── decorators.py      # Function decorators
│   └── responses.py       # Response utilities
│
├── contrib/                # Optional contributions
│   ├── __init__.py
│   ├── choices.py         # Field choice constants
│   ├── context.py         # Context processors
│   ├── enums.py           # Shared enumerations
│   ├── responses.py       # Response helpers
│   └── schemas.py         # Schema definitions
│
├── comp/                   # Component system
│   ├── __init__.py
│   ├── blocks.py          # StreamField blocks
│   ├── site.py            # Site components
│   ├── payloads.py        # Data payloads
│   └── partials/          # Partial components
│
├── handlers/               # Request handlers
│   ├── __init__.py
│   ├── base.py            # Base handler classes
│   └── mixins.py          # Handler mixins
│
├── middlewares/           # Django middlewares
│   ├── __init__.py
│   └── base.py            # Base middleware classes
│
├── templatetags/          # Template tags and filters
│   ├── __init__.py
│   └── django_osoul_tags.py
│
├── management/            # Management commands
│   ├── __init__.py
│   └── commands/          # Command implementations
│
└── tests/                 # Test utilities
    ├── __init__.py
    ├── factories.py       # Test data factories
    ├── fixtures.py        # Test fixtures
    └── utils.py           # Test utilities
```

## 3. Key Components Design

### 3.1 Domain Layer Components

**BaseEntity**:
```python
class BaseEntity:
    """Base class for all domain entities."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __hash__(self):
        return hash(self.id)
```

**ValueObject**:
```python
class ValueObject:
    """Base class for value objects."""
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
```

**DomainEvent**:
```python
class DomainEvent:
    """Base class for domain events."""
    event_id: UUID
    occurred_on: datetime
    aggregate_id: UUID

    def __init__(self, aggregate_id: UUID):
        self.event_id = uuid4()
        self.occurred_on = datetime.now()
        self.aggregate_id = aggregate_id
```

### 3.2 Application Layer Components

**UseCase**:
```python
class UseCase(ABC):
    """Base class for application use cases."""

    @abstractmethod
    def execute(self, request: Any) -> Any:
        """Execute the use case."""
        pass
```

**ApplicationService**:
```python
class ApplicationService:
    """Base class for application services."""

    def __init__(self, repository: Repository, event_bus: EventBus):
        self.repository = repository
        self.event_bus = event_bus
```

### 3.3 Infrastructure Layer Components

**Repository**:
```python
class Repository(ABC, Generic[T]):
    """Base repository interface."""

    @abstractmethod
    def get(self, id: UUID) -> Optional[T]:
        pass

    @abstractmethod
    def save(self, entity: T) -> T:
        pass

    @abstractmethod
    def delete(self, entity: T) -> None:
        pass
```

**UnitOfWork**:
```python
class UnitOfWork(ABC):
    """Unit of work pattern for transaction management."""

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, *args):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass
```

## 4. Migration Strategy

### 4.1 Phase 1: Foundation (Week 1-2)
1. **Extract Base Models**: Move BaseModel, TimeStampedModel, etc.
2. **Create Domain Layer**: Implement base entities and value objects
3. **Setup Repository Pattern**: Define repository interfaces
4. **Implement Unit of Work**: Transaction management

### 4.2 Phase 2: Services (Week 3-4)
1. **Extract Service Layer**: Move common services to django_osoul
2. **Implement Use Cases**: Define application use cases
3. **Create DTOs**: Data transfer objects for API contracts
4. **Event System**: Domain event publishing/subscribing

### 4.3 Phase 3: Integration (Week 5-6)
1. **API Layer**: REST/GraphQL API base classes
2. **CLI Commands**: Shared management commands
3. **Testing Utilities**: Shared test fixtures and factories
4. **Documentation**: API documentation and usage guides

### 4.4 Phase 4: Optimization (Week 7-8)
1. **Performance**: Caching strategies and optimizations
2. **Monitoring**: Health checks and metrics
3. **Security**: Security utilities and validators
4. **Deployment**: Deployment utilities and scripts

## 5. Integration with Projects

### 5.1 ctc-research.com Integration
```python
# Before refactoring
from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=255)
    # ... other fields

# After refactoring
from django_osoul.domain.entities import BaseEntity
from django_osoul.infrastructure.persistence.django import DjangoModel

class Course(BaseEntity):
    title: str

class CourseModel(DjangoModel[Course]):
    """Django model for Course entity."""
    title = models.CharField(max_length=255)

    def to_entity(self) -> Course:
        return Course(
            id=self.id,
            title=self.title,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @classmethod
    def from_entity(cls, entity: Course) -> 'CourseModel':
        return cls(
            id=entity.id,
            title=entity.title,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
```

### 5.2 structa.cloud Integration
```python
# Similar pattern with domain-driven design
from django_osoul.domain.repositories import Repository
from django_osoul.infrastructure.persistence.django import DjangoRepository

class CourseRepository(DjangoRepository[Course]):
    """Repository for Course entities."""

    def find_by_title(self, title: str) -> List[Course]:
        models = self.model.objects.filter(title__icontains=title)
        return [model.to_entity() for model in models]
```

## 6. Testing Strategy

### 6.1 Unit Tests
- **Domain Layer**: Test entities, value objects, domain services
- **Application Layer**: Test use cases, application services
- **Infrastructure Layer**: Test repositories, external adapters

### 6.2 Integration Tests
- **Repository Tests**: Test database integration
- **Service Tests**: Test service layer integration
- **API Tests**: Test API endpoints

### 6.3 Property-Based Tests
- **Domain Properties**: Test domain invariants
- **Business Rules**: Test business rule properties
- **API Contracts**: Test API contract properties

## 7. Documentation

### 7.1 API Documentation
- **Type Hints**: Comprehensive type hints
- **Docstrings**: Google-style docstrings
- **Examples**: Usage examples for all public APIs
- **Tutorials**: Step-by-step tutorials

### 7.2 Architecture Documentation
- **Design Decisions**: Architecture decision records (ADRs)
- **Patterns**: Design patterns used
- **Guidelines**: Development guidelines
- **Migration Guides**: Migration from old to new patterns

## 8. Versioning and Compatibility

### 8.1 Semantic Versioning
- **Major**: Breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, backward compatible

### 8.2 Backward Compatibility
- **Deprecation Warnings**: Warn before removing features
- **Migration Paths**: Clear migration paths
- **Compatibility Layers**: Temporary compatibility layers

## 9. Success Criteria

### 9.1 Technical Criteria
- [ ] All existing tests pass
- [ ] Code coverage > 80%
- [ ] No circular dependencies
- [ ] All SOLID principles followed

### 9.2 Business Criteria
- [ ] Both projects can use shared library
- [ ] Development velocity improved
- [ ] Code duplication reduced by 50%
- [ ] Maintenance cost reduced

## 10. Next Steps

1. **Week 1**: Implement domain layer foundation
2. **Week 2**: Implement repository and unit of work patterns
3. **Week 3**: Implement application layer and use cases
4. **Week 4**: Implement infrastructure layer adapters
5. **Week 5**: Implement interface layer (API, CLI)
6. **Week 6**: Testing and documentation
7. **Week 7**: Performance optimization
8. **Week 8**: Deployment and monitoring

This shared library design provides a solid foundation for building maintainable, testable, and scalable Django applications following clean architecture principles.
