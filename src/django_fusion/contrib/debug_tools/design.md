# Design: Contrib Debug Tools

## Overview

Debug tools for django_fusion.

## Directory

Path: `django_fusion/contrib/debug_tools`


### Modules
- `autoreload.py`
- `base.py`
- `common_urls.py`
- `config.py`
- `core.py`
- `detection.py`
- `dev_urls.py`
- `development.py`
- `error_views.py`
- `middleware.py`
- `monitoring.py`
- `orchestrator.py`
- `prometheus.py`
- `sentry.py`
- `urls.py`

## Architecture

```mermaid
flowchart LR
    Request --> contrib.debug_tools
    {package_name} --> Response
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.contrib.debug_tools import example_function

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
