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

```flowchart
flowchart LR
    A[Request] --> B{Handler}
    B --> C[Service/Logic]
    C --> D[Response/Template]
    style A fill:#f9f,stroke:#333
    style D fill:#bbf,stroke:#333
```

## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from infrastructure.middlewares import ...

# TODO: replace with a concrete example for this package.
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
