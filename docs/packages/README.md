# Shared Packages Documentation

> Reusable packages across the ecosystem

## Overview

This section contains documentation for shared packages used by all projects.

## Packages

### [django-fusion](django-fusion/)
**Pure Django foundation layer**

Abstract models, managers, mixins, utilities, and components
- No Wagtail dependencies
- No Celery dependencies
- No ceptor-ai dependencies

**Sub-modules:**
- `handlers/` - Page handlers
- `managers/` - Custom managers
- `mixins/` - Reusable mixins
- `utils/` - Utility functions
- `comp/` - Component library
- `contrib/` - Extensions
- `middlewares/` - Custom middleware
- `filters/` - Django filters
- `forms/` - Form classes
- `backends/` - Auth backends
- `adapters/` - Third-party adapters
- `services/` - Service layer

### [ceptor-ai](ceptor-ai/)
**Wagtail automation layer**

Pipelines, services, workflows, email handling, and Wagtail components
- Depends on django-fusion
- Wagtail-focused automation
- No project-specific code

**Sub-modules:**
- `pipelines/` - Data processing
- `services/` - Service layer (CartServiceBase)
- `workflows/` - Workflow definitions
- `email/` - Email handling
- `signals/` - Django signals
- `admin/` - Custom admin
- `cache/` - Caching utilities
- `commands/` - Management commands
- `blocks/` - Wagtail blocks
- `snippets/` - Wagtail snippets
- `hooks/` - Wagtail hooks

### [django-fusion](django-fusion/)
**Unified testing framework**

Test base classes, fixtures, factories, pytest plugins, and health checks
- Test-only imports
- Standalone (no dependencies)
- Hypothesis integration

**Features:**
- `BaseTestCase` - Base test class
- `st_email`, `st_slug`, `st_uuid` - Hypothesis strategies
- Health check endpoints
- Data seeding utilities

### [ceptor-ai](ceptor-ai/)
**Pure Python AI/MCP toolkit**

AI integrations, chat functionality, and MCP server support
- Zero Django imports
- Standalone (no dependencies)
- AI/NLP focused

**Sub-modules:**
- `ai/` - AI integrations
- `chat/` - Chat functionality
- `mcp/` - MCP server support
- `orchestrator/` - Task orchestration
- `seeder/` - Data seeding

---

## Installation

```bash
# Install all packages
cd venv/libs/django-fusion && uv sync
cd venv/libs/ceptor-ai && uv sync
cd venv/libs/django-fusion && uv sync
uv pip install -e core/libs/ceptor-ai/
```

## Usage

### django-fusion
```python
# In settings.py
INSTALLED_APPS = [
    'django_fusion',
    ...
]
```

### ceptor-ai
```python
# Thin layer pattern
from ceptor_ai.services import CartServiceBase

class CartService(CartServiceBase):
    # Project-specific customizations only
    pass
```

### django-fusion
```python
from django_fusion import BaseTestCase

class MyTest(BaseTestCase):
    def test_something(self):
        pass
```

### ceptor-ai
```python
from ceptor_ai import package_info

info = package_info()
```

---

## Dependency Direction

```
ctc-research.com  →  django-fusion, django-fusion, ceptor-ai, ceptor-ai
structa.cloud     →  django-fusion, django-fusion, ceptor-ai, ceptor-ai
ceptor-ai      →  django-fusion
django-fusion       →  (standalone)
ceptor-ai         →  (standalone)
```

---

## Related Documentation

- [Ecosystem Overview](../ecosystem/)
- [ctc-research.com](../ctc-research/)
- [structa.cloud](../structa-cloud/)
