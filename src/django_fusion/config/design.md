# Design: Config

## Overview

Package-level configuration — constants, conf helpers, and logging setup.

## Directory

Path: `django_fusion/config`


### Modules
- `conf.py`
- `conf_utils.py`
- `constants.py`
- `dynaconf_loader.py`
- `logging.py`

## Architecture

```mermaid
flowchart LR
    Request --> config
    {package_name} --> Response
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.config.conf import import_attribute, import_model

# Import a class/function by dotted path
renderer_class = import_attribute("myapp.rendering.CustomRenderer")

# Import a Django model by app_label.ModelName
User = import_model("auth.User")
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
