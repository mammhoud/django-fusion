# Design: Site Interface Context

## Overview

Request context processors and context data builders.

## Directory

Path: `django_fusion/core/context`


### Modules

- `_context_mixins.py`
- `auth.py`
- `context.py`
- `cookies.py`
- `htmx.py`
- `languages.py`
- `settings.py`

## Architecture / Class Diagram

```mermaid
classDiagram
    class FragmentHandlerMixin {
      +resolve_template_name()
      +render_response()
      +render_fragment()
      +render_layout()
    }
    BaseTemplateContextMixin <|-- FragmentHandlerMixin
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.core.context import example_function

# Replace example_function with a real symbol from this package
result = example_function()
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
