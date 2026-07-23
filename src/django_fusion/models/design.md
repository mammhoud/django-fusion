# Design: Models

## Overview

django_fusion models — base models and mixins for Django applications.

## Directory

Path: `django_fusion/models`


### Modules
- `auth.py`
- `base.py`
- `datatoken.py`
- `email.py`
- `integrations.py`
- `managers.py`

## Architecture

```erd
erDiagram
    %% Generic entity-relationship placeholder.
    Replace with actual models discovered in this package.
```

## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from models import ...

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
