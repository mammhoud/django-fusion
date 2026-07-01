# ceptor-ai Documentation

## Overview
ceptor-ai is the Wagtail automation layer that builds on top of django-osoul. It provides pipelines, services, workflows, email handling, and Wagtail-specific components.

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
cd venv/libs/ceptor-ai
uv sync
```

## Usage

```python
# In your Django settings
INSTALLED_APPS = [
    ...
    'ceptor_ai',
    ...
]
```

## Thin Layer Pattern
Projects should use thin subclasses of ceptor-ai services:

```python
# In your project
from ceptor_ai.services import CartServiceBase

class CartService(CartServiceBase):
    # Project-specific customizations only
    pass
```

## Documentation Links
- [ceptor-ai README](../../README.md)

## Related Packages
- [django-osoul](../../../django-osoul/) - Base layer (ceptor-ai depends on this)
