# crafts-ai Documentation

## Overview
crafts-ai is the Wagtail automation layer that builds on top of django-fusion. It provides pipelines, services, workflows, email handling, and Wagtail-specific components.

## Key Principles
- **Depends on django-fusion** - Uses base classes from django-fusion
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
cd venv/libs/crafts-ai
uv sync
```

## Usage

```python
# In your Django settings
INSTALLED_APPS = [
    ...
    'crafts_ai',
    ...
]
```

## Thin Layer Pattern
Projects should use thin subclasses of crafts-ai services:

```python
# In your project
from crafts_ai.services import CartServiceBase

class CartService(CartServiceBase):
    # Project-specific customizations only
    pass
```

## Documentation Links
- [crafts-ai README](../../../venv/libs/crafts-ai/README.md)

## Related Packages
- [django-fusion](../django-fusion/) - Base layer (crafts-ai depends on this)
- [django-fusion](../django-fusion/) - Testing infrastructure
