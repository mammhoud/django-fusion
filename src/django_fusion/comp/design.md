# Design: Comp

## Overview

components — Django component system with slot/prop/var template tags.

## Directory

Path: `django_fusion/comp`


### Modules
- `apps.py`
- `cache.py`
- `registry.py`

## Architecture / ERD

```mermaid
erDiagram
    CompUsage {
        Any path
        Any kind
        Field kwargs
    }
    SectionMarker {
        Any name
        Any marker_type
        Any line
    }
    ParsedTemplate {
        Any extends
        Any blocks
        Any comps
        Field sections
    }
    Prop {
        Any name
    }
    Slot {
        Any name
    }
    Component {
        Any name
        Any path
        Field props
        Field slots
    }
    Block {
        Any name
    }
    Section {
        Any name
        Any id
        Any marker_type
    }
    Template {
        Any name
        Any path
        Field blocks
        Field sections
    }
    PageComponentUsage {
        Any component_id
        Field props
    }
    Page {
        Any title
        Any path
        Field components
    }
    AnalyzeRequest {
        Field filters
    }
    ScannedFile {
        Any path
        Any relative_path
        Any content
        ConfigDict model_config
    }
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.comp.models import CompUsage

# Query and create instances
qs = CompUsage.objects.all()
obj = CompUsage.objects.create(kwargs='...')
```

```python
from django_fusion.comp import IncludePathComponent

# Wire into urls.py
from django.urls import path
urlpatterns = [
    path('includepathcomponent/', IncludePathComponent.as_view()),
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
