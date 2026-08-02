# Design: Shared Services

## Overview

`django_fusion.services` contains the canonical service implementations shared
by Structa Cloud sites. Site-specific services should compose or subclass these
modules rather than copy their infrastructure.

## Modules

- `base.py` — `BaseService`, `ModelService`, and `ServiceRegistry`
- `jobs.py` — logged background-job dispatch
- `token.py` — token validation and protected model operations
- `cart.py` — cart extension base
- `crud.py` — functional CRUD helpers and compatibility facades
- `person.py` — person-service extension base

## Canonical imports

```python
from django_fusion.services import TokenService, dispatch_job
from django_fusion.services.base import BaseService, ModelService
from django_fusion.services.crud import get_first, update_one
```

The obsolete `services.py` payload module is intentionally absent. Do not add
new imports through compatibility namespaces or recreate that module.

## Related documentation

- [Django docs](https://docs.djangoproject.com/)
- [Wagtail docs](https://docs.wagtail.io/)
- Other `django_fusion` packages: see the root `design.md`.

