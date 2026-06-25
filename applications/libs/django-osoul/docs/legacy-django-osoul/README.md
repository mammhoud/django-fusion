# django-osoul Documentation

## Overview
django-osoul is the pure Django foundation layer for the ecosystem. It provides abstract models, managers, mixins, utilities, and components that can be used across all projects.

## Key Principles
- **No Wagtail dependencies** - Must not import wagtail
- **No Celery dependencies** - Must not import celery
- **No crafts-ai dependencies** - Must remain independent

## Sub-modules

### handlers/
Page handlers for request processing

### managers/
Custom model managers and querysets

### mixins/
Reusable model and view mixins

### utils/
Utility functions and helpers

### comp/
Component library for reusable UI components

### contrib/
Contributed extensions and integrations

### middlewares/
Custom middleware classes

### filters/
Django filter configurations

### forms/
Form classes and widgets

### backends/
Custom authentication backends

### adapters/
Third-party adapters (e.g., allauth)

### services/
Service layer classes

## Installation

```bash
cd venv/libs/django-osoul
uv sync
```

## Usage

```python
# In your Django settings
INSTALLED_APPS = [
    ...
    'django_osoul',
    ...
]
```

## Documentation Links
- [django-osoul README](../../../venv/libs/django-osoul/README.md)

## Related Packages
- [crafts-ai](../crafts-ai/) - Wagtail automation (depends on django-osoul)
- [django-osoul](../django-osoul/) - Testing infrastructure
