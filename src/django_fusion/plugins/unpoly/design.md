# Design: Comp Fragment Plugins Unpoly

## Overview

Unpoly plugin for django-fusion fragments

## Directory

Path: `django_fusion/plugins/unpoly`


### Modules
- `adapter.py`
- `core.py`

## Architecture

```mermaid
flowchart LR
    Request --> django_fusion.plugins.unpoly
    {package_name} --> Response
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.plugins.unpoly import DjangoAdapter

adapter = DjangoAdapter(request)
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
