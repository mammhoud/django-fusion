# django-fusion Documentation

## Overview
django-fusion is the pure Django foundation layer for the ecosystem. It provides abstract models, managers, mixins, utilities, and components that can be used across all projects.

## Key Principles
- **No Wagtail dependencies** - Must not import wagtail
- **No Celery dependencies** - Must not import celery
- **No ceptor-ai dependencies** - Must remain independent

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
cd venv/libs/django-fusion
uv sync
```

## Usage

```python
# In your Django settings
INSTALLED_APPS = [
    ...
    'django_fusion',
    ...
]
```

## Documentation Links
- [django-fusion README](../../README.md)

## Related Package
- [ceptor-ai](../../../ceptor-ai/) — downstream lib (depends on django-fusion)
