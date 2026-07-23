# Design: Infrastructure Middlewares

## Overview

Request/response middleware for Django sites.

## Directory

Path: `django_fusion/infrastructure/middlewares`


### Modules
- `component_error.py`
- `error_tracker.py`
- `freeze.py`
- `language.py`
- `service.py`
- `site.py`

## Architecture

```mermaid
flowchart LR
    Request --> infrastructure.middlewares
    {package_name} --> Response
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.infrastructure.middlewares import example_function

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
