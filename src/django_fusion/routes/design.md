# Design: Routes

## Overview

django_fusion.routes

## Directory

Path: `django_fusion/routes`


### Modules

- `components/`
- `core/`
- `http/`
- `models/`
- `pages/`
- `rendering/`
- `schemas/`
- `views/`

## Architecture / ERD

```mermaid
erDiagram
    FusionFragmentSchema {
        Field status
        Field message
        Field data
    }
    FusionFragmentPointer {
        Field component
        Field fragment_name
        Field fragment_url
        Field fusion_render_first
    }
    APIResponse {
    }
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.routes.models.base import BaseModelViewset

# Wire into urls.py
from django.urls import path
urlpatterns = [
    path('basemodelviewset/', BaseModelViewset.as_view()),
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
