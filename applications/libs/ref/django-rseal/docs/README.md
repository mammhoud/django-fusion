# django-rseal Documentation

## Overview
django-rseal is the Wagtail automation layer that builds on top of django-osoul. It provides pipelines, services, workflows, email handling, and Wagtail-specific components.

## Key Principles
- **Depends on django-osoul** - Uses base classes from django-osoul
- **Wagtail-focused** - Provides Wagtail-specific automation
- **No project dependencies** - Must not import project-specific code

## Sub-modules

### pipelines/
Data processing pipelines

### services/
Service layer classes including CartServiceBase

### workflows/
Workflow definitions and handlers

### email/
Email handling and templates

### signals/
Django signal handlers

### admin/
Custom admin configurations

### cache/
Caching utilities

### commands/
Custom management commands

### blocks/
Wagtail streamfield blocks

### snippets/
Wagtail snippets

### hooks/
Wagtail hooks

## Installation

```bash
cd venv/libs/django-rseal
uv sync
```

## Usage

```python
# In your Django settings
INSTALLED_APPS = [
    ...
    'django_rseal',
    ...
]
```

## Thin Layer Pattern
Projects should use thin subclasses of django-rseal services:

```python
# In your project
from django_rseal.services import CartServiceBase

class CartService(CartServiceBase):
    # Project-specific customizations only
    pass
```

## Documentation Links
- [django-rseal README](../../../venv/libs/django-rseal/README.md)

## Related Packages
- [django-osoul](../django-osoul/) - Base layer (django-rseal depends on this)
- [django-grep](../django-grep/) - Testing infrastructure
