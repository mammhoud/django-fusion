# Design: Comp Templatetags

## Overview

This package (`comp.tags`) is part of `django-fusion` and provides reusable components, utilities, or routing helpers.

## Directory

Path: `django_fusion/comp/tags`


### Modules

- `content_type.py`
- `embed_blocks.py`
- `format.py`
- `fusion_assets.py`
- `fusion_form_field_adapter.py`
- `fusion_layout.py`
- `fusion_skeleton.py`
- `menu.py`
- `navigation.py`
- `routable_components.py`
- `user_role.py`
- `components/`
- `tags/`

## Architecture

```mermaid
flowchart LR
    Request --> django_fusion.comp.tags
    django_fusion.comp.tags --> Response
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
