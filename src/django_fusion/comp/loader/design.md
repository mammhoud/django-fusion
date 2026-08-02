# Design: Comp Loader

## Overview

Template management for django_fusion components.

## Directory

Path: `django_fusion/comp/loader`


### Modules
- `discovery.py`
- `htmx.py`
- `templates.py`
- `up.py`
- `urls.py`

## Architecture

```mermaid
flowchart LR
    Request --> comp.fragment.loader
    {package_name} --> Response
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.comp.loader.discovery import discover_sections
from django_fusion.comp.loader.templates import get_template_names

# Discover reusable section templates
sections = discover_sections()

# Resolve possible template names for a component
names = get_template_names("input")
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
