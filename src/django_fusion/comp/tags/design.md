# Design: Comp Templatetags

## Overview

This package (`comp.templatetags`) is part of `django-fusion` and provides reusable components, utilities, or routing helpers.

## Directory

Path: `django_fusion/comp/templatetags`


### Modules
- `components/` — component inclusion tags (table, pagination, search, form, modal, breadcrumbs, navigation, menu, card, etc.)
- `tags/` — core component tags (block, slot, prop, var, asset)
- `menu.py` — site and application menu tags
- `routable_components.py` — routable component helpers (component_url, active_menu)
- `format.py` — text, number, and date filters
- `field_adapter.py` — Wagtail form field adapter
- `content_type.py` — content type helpers
- `user_role.py` — role/permission filters
- `embed_blocks.py` — embed block filters

## Architecture

```mermaid
flowchart LR
    Request --> comp.templatetags
    {package_name} --> Response
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.comp.templatetags import example_function

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
