# Shared Packages Documentation

> Reusable packages across the ecosystem

## Overview

This section contains documentation for shared packages used by all projects.

## Packages

### [django-osoul](django-osoul/)
**Pure Django foundation layer**

Abstract models, managers, mixins, utilities, and components
- No Wagtail dependencies
- No Celery dependencies
- No django-rseal dependencies

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

### [django-rseal](django-rseal/)
**Wagtail automation layer**

Pipelines, services, workflows, email handling, and Wagtail components
- Depends on django-osoul
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

### [django-grep](django-grep/)
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

### [nawaai](nawaai/)
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
cd venv/libs/django-osoul && uv sync
cd venv/libs/django-rseal && uv sync
cd venv/libs/django-grep && uv sync
cd venv/libs/nawaai && uv sync
```

## Usage

### django-osoul
```python
# In settings.py
INSTALLED_APPS = [
    'django_osoul',
    ...
]
```

### django-rseal
```python
# Thin layer pattern
from django_rseal.services import CartServiceBase

class CartService(CartServiceBase):
    # Project-specific customizations only
    pass
```

### django-grep
```python
from django_grep import BaseTestCase

class MyTest(BaseTestCase):
    def test_something(self):
        pass
```

### nawaai
```python
from nawaai.ai import AIEngine

engine = AIEngine()
response = engine.process("Hello!")
```

---

## Dependency Direction

```
ctc-research.com  →  django-osoul, django-grep, django-rseal, nawaai
structa.cloud     →  django-osoul, django-grep, django-rseal, nawaai
django-rseal      →  django-osoul
django-grep       →  (standalone)
nawaai            →  (standalone)
```

---

## Related Documentation

- [Ecosystem Overview](../ecosystem/)
- [ctc-research.com](../ctc-research/)
- [structa.cloud](../structa-cloud/)
