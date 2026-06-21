# django-osoul Documentation

## Overview
django-osoul is the unified testing framework for the ecosystem. It provides test base classes, fixtures, factories, pytest plugins, and health check endpoints.

## Key Principles
- **Test-only imports** - Must not be imported by production code
- **Standalone** - No dependencies on other ecosystem packages
- **Hypothesis integration** - Property-based testing support

## Features

### Test Infrastructure
- `BaseTestCase` - Base test class with common utilities
- Test fixtures and factories
- Pytest plugin for enhanced testing

### Hypothesis Helpers
- `st_email` - Email address strategy
- `st_slug` - Slug strategy
- `st_uuid` - UUID strategy

### Health Checks
Built-in health check endpoints:
- `GET /health/` - Overall health status
- `GET /health/database/` - Database connectivity
- `GET /health/assets/` - Static assets availability
- `GET /health/media/` - Media files availability

### Seeder
Data seeding utilities for testing and development

## Installation

```bash
cd venv/libs/django-osoul
uv sync
```

## Usage

### In Tests
```python
from django_osoul import BaseTestCase

class MyTest(BaseTestCase):
    def test_something(self):
        # Test implementation
        pass
```

### Health Check URLs
```python
# In your urls.py
urlpatterns = [
    path("health/", include("django_osoul.health.urls")),
]
```

## Documentation Links
- [django-osoul README](../../../venv/libs/django-osoul/README.md)
- [django-osoul Overview](django-osoul-overview.md)
- [Usage Analysis](django-osoul-usage-analysis.md)

## Related Packages
- [django-osoul](../django-osoul/) - Pure Django foundation
- [crafts-ai](../crafts-ai/) - Wagtail automation
