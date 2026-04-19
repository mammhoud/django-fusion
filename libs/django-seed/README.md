# Django Seed

A Django package for object types, cache mechanisms, managers, and services following clean architecture principles.

## Features

- **Object Types**: Type-safe object definitions with validation
- **Cache Mechanisms**: Configurable caching with Redis backend
- **Service Layer**: Business logic encapsulation
- **Manager Pattern**: Clean data access patterns
- **Clean Architecture**: Clear separation of concerns

## Installation

```bash
pip install django-seed
```

## Quick Start

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ...
    'django_seed',
    # ...
]
```

## Architecture

The package follows clean architecture principles:

- **Domain Layer**: Core business logic and entities
- **Application Layer**: Use cases and business logic
- **Infrastructure Layer**: External services, databases, caches
- **Interface Layer**: APIs, web interfaces, and external systems

## License

MIT License
