# Python / Sidecar Docs — POS Full

> **Directory:** `docs/python/`
> **Language:** Python 3.11+
> **Framework:** Robyn + Django ORM
> **Project:** `projects/pos/pos-full/`

---

## Import Conventions

```python
from django_fusion.comp.routes import RoutableComponent, FragmentComponent
from django_fusion.web.views import FilterMixin
from django_fusion.core.handlers import BaseHandler
from django_fusion.core.models import BaseModel
```

## Sidecar Architecture

```
sidecar/
├── models/          # Django ORM models (pos.py, extra.py)
├── routes/          # Robyn route handlers
├── services/        # Business logic
├── configs/         # Django admin config
├── middleware/       # Fusion + auth
├── fragments/       # HTMX fragment components
└── tests/           # pytest tests
```

## Testing

```bash
cd sidecar && python -m pytest tests/ -v
```

See `../PROMPTS.md#python--sidecar-prompts` for code generation templates.

## Detailed Guides

| Guide | Description |
|-------|-------------|
| [Sidecar Patterns](./sidecar-patterns.md) | Route handler, Fusion response, Django ORM model, testing patterns |
