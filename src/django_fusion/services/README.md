# `django_fusion.services`

Shared service infrastructure for Structa Cloud Django sites.

## Contents

- `base` — model-backed service base classes and registry
- `jobs` — queued job dispatch and task logging
- `token` — token generation, validation, and protected services
- `cart` — extensible cart service base
- `crud` — functional and class-based CRUD helpers
- `person` — extensible person service base

## Public API

```python
from django_fusion.services import (
    BaseService,
    TokenProtectedService,
    TokenService,
    dispatch_job,
)
from django_fusion.services.base import ModelService, ServiceRegistry
```

Import implementation modules directly when using cart, CRUD, or person
extensions. The legacy `services.py` payload module has been removed; use the
canonical modules above.
