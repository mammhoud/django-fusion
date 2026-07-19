# 📚 Libraries Changelog

> django-fusion and ceptor-ai changes extracted from the real repo `CHANGELOG.md`.

---

## django-fusion

### fix: `_LazyIncludeTemplate.template` (2026-07-01)

`libs/django-fusion/src/django_fusion/comp/registry.py` — fixed `_LazyIncludeTemplate.template` to return the inner `django.template.Template` (matching the layer that has `.nodelist`) instead of the outer `DjangoTemplate` wrapper.

**Impact**: All four consumer sites (`Component.nodelist`, `Component.path`, `Component.source`, `BoundComponent.render`) now converge through the same path the eager `from_name` resolution always used.

### feat: render equivalence test (2026-07-01)

`libs/django-fusion/tests/test_register_include_path_render_equivalence.py` — confirms render equivalence across:
- `{% include "path" %}`
- `{% comp "path" /%}`
- `{% comp name /%}`

### feat: ceptor-ai integration tests (2026-07-01)

`libs/django-fusion/tests/django_grep/test_ceptor_ai/` — integration test suite for ceptor-ai within the django-fusion analyzer.

### Canonical Import Paths

All re-export shims removed — use these canonical paths directly:

```python
from django_fusion.comp.routes import Viewset, Route, route, viewprop, Site
from django_fusion.comp.generic import ListModelView, CreateModelView, TableView
from django_fusion.core.handlers import PageHandler
from django_fusion.core.services import BaseService
from django_fusion.web.views import FilterMixin, SearchMixin
```

---

## ceptor-ai

### docs: legacy docs sweep (2026-07-01)

- `libs/ceptor-ai/docs/legacy-ceptor-ai/README.md`
  - Quick Start: `CraftsClient` → `CeptorClient` (matching actual `ceptor_ai.chat.client` API)
  - `ChatBubble(client=client)` → `ChatBubble(server_url=…)` (matching actual constructor kwarg)
  - Install extras: `openai`, `anthropic`, `faker` → `mcp`, `test` (matching `pyproject.toml`)

### rename: legacy codenames → actual package names (2026-07-01)

- `test_nawaai/` → `test_ceptor_ai/`
- `legacy_crafts_ai/` → `legacy_ceptor_ai/`
- `legacy-crafts-ai/` → `legacy-ceptor-ai/`
- `crafts_ai`/`craftsai`/`crafts-ai`/`crafts.ai` → `ceptor_ai`/`ceptor-ai`
- Removed empty `ceptor-ai/crafts-ai/` dir

---

## Git Submodules

Both libraries are tracked as git submodules at `libs/`:

| Library | Remote | Branch |
|---------|--------|--------|
| django-fusion | `https://github.com/mammhoud/django-fusion.git` | `generic` |
| ceptor-ai | `https://github.com/mammhoud/ceptor-ai.git` | `generic` |

Push updates: `make push-libs` or `make push-lib LIB=django-fusion`

---

## Related

| Topic | Path |
|-------|------|
| django-fusion docs | [`../libs/django-fusion.md`](../libs/django-fusion.md) |
| ceptor-ai docs | [GitHub](https://github.com/mammhoud/ceptor-ai) |
| Repo changelog | [`repo.md`](repo.md) |
| POS changelog | [`pos.md`](pos.md) |
