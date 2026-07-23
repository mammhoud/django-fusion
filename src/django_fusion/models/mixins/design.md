# Design: Models Mixins

## Overview

django_fusion.models.mixins

## Directory

Path: `django_fusion/models/mixins`


### Modules
- `display_mode.py`

## Architecture

```mermaid
flowchart LR
    Request --> models.mixins
    {package_name} --> Response
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.models.mixins.models import DisplayModeMixin

# Create an instance
obj = DisplayModeMixin.objects.create(display_mode='...', modal_size='...', display_mode_panels='...')
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
