# Design: Infrastructure

## Overview

Infrastructure utilities — health endpoints, middleware, locale, management command base, and scripts.

## Directory

Path: `django_fusion/infrastructure`


## Architecture / Class Diagram

```mermaid
classDiagram
    class HealthCheckView {
      +get()
    }
    class DatabaseHealthView {
      +get()
    }
    class AssetsHealthView {
      +get()
    }
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.infrastructure import HealthCheckView

# Wire into urls.py
from django.urls import path
urlpatterns = [
    path('healthcheckview/', HealthCheckView.as_view()),
]
```
## Commands / Entry Points

*No management commands are defined here by default.*

If this package exposes management commands, list them below:

```bash
python manage.py <command_name>
```

## Related Documentation

- [Django docs](https://docs.djangoproject.com/)
- [Wagtail docs](https://docs.wagtail.io/)
- Other `django_fusion` packages: see the root `design.md`.
