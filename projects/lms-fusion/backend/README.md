# lms-fusion backend

The lms-fusion backend is the Django/Wagtail API and server-rendered surface
for the Structa Cloud learning platform. It uses the canonical `django-fusion`
component, route, asset, health, and management-command APIs directly.

## Quick start

```bash
cd projects/lms-fusion/backend
uv run --project .. pytest -q
make check
make dev
```

Useful targets:

| Target | Purpose |
|---|---|
| `make check` | Django system checks |
| `make test` | Backend test suite |
| `make migrate` | Apply database migrations |
| `make collectstatic` | Collect static files and generate the component manifest |
| `make frontend-production` | Build project frontend assets |
| `make webpack-validate` | Validate the webpack stats file |

## Runtime structure

```text
backend/
├── apps/pages/       LMS, blog, accounts, profile, products, and page apps
├── apps/core/        Shared API, services, routes, and management commands
├── apps/domain/      Domain models and site behavior
├── templates/        Site-level overrides and entry templates
├── settings.py       lms-fusion Django settings
├── www/urls.py       Canonical URL composition
└── tests/             SQLite-backed API, fixture, model, and smoke tests
```

Framework implementations live in `libs/django-fusion`; project modules only
contain LMS-specific models, views, templates, configuration, or adapters.

## Canonical imports

```python
from django_fusion.comp.registry import component_registry
from django_fusion.config.assets import get_asset_pipeline_options
from django_fusion.config.manifest import load_merged_asset_manifest
from django_fusion.routes import RoutableComponent
from django_fusion.management.commands.base import BaseCommand
```

Do not introduce local re-export modules for these symbols. A management command
may subclass a django-fusion command only when it supplies LMS model paths or
fixture settings.

## Related documentation

- [`docs/projects/lms-fusion/`](../../../docs/projects/lms-fusion/README.md)
- [`docs/plans/`](../../../docs/plans/README.md)
- [`libs/django-fusion/docs/INDEX.md`](../../../libs/django-fusion/docs/INDEX.md)
- [`CHANGELOG.md`](../CHANGELOG.md)
