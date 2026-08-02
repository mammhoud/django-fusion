# lms-fusion

`lms-fusion` is the Structa Cloud learning platform: a Django/Wagtail backend,
Next.js frontend, and django-fusion component/API layer.

## Layout

```text
projects/lms-fusion/
├── backend/       Django settings, apps, templates, migrations, and tests
├── frontend/      Next.js application and frontend tests
├── assets/        SCSS, static files, fixtures, media, and build scripts
├── configs/       Site-specific configuration overlays
└── compose/       Container entrypoints and Docker build files
```

Project-specific source assets stay under `assets/`; generated bundles and
Django `collectstatic` output remain generated artifacts. Framework behavior
comes directly from `libs/django-fusion`—do not add local compatibility shims
for components, routes, contexts, or management commands.

## Local validation

```bash
cd projects/lms-fusion/backend
uv run --project .. pytest -q
make check
make collectstatic

cd ../frontend
npm test -- --run
npm run build
```

From the monorepo, the canonical dispatcher is preferred when available:

```bash
cd projects
make check WEBSITE=lms-fusion
make test WEBSITE=lms-fusion
```

The backend test settings use SQLite and disable migrations for fast model/API
coverage. Production uses the site settings and configured database normally.

## Django-fusion integration

Use canonical imports directly:

```python
from django_fusion.comp.registry import component_registry
from django_fusion.routes import RoutableComponent
from django_fusion.config.manifest import load_merged_asset_manifest
from django_fusion.management.commands.base import BaseCommand
```

LMS-specific command adapters may subclass django-fusion commands when they
provide LMS model paths or fixture locations. They are adapters, not alternate
framework implementations.

## Asset pipeline

The build flow is:

1. Webpack/Next.js compiles project assets.
2. Django `collectstatic` collects generated and framework static files.
3. `generate_asset_manifest` writes the component usage manifest.
4. django-fusion merges configured assets, webpack output, and component data
   for API and template-tag consumers.

See [`assets/ASSETS_GUIDE.md`](../../../projects/lms-fusion/assets/ASSETS_GUIDE.md)
and [`django-fusion assets`](../../../libs/django-fusion/docs/16-assets.md).

## Plans and history

All active and historical repository plans are indexed under
[`docs/plans/`](../../plans/README.md). The lms-fusion migration and asset
plans are preserved under [`docs/plans/migrated/projects/lms-fusion/`](../../plans/migrated/projects/lms-fusion/).

- [Project configuration](../../projects/lms/README.md)
- [Monorepo development guide](../../guides/03-dev.md)
- [Root changelog](../../../CHANGELOG.md)
- [LMS Fusion changelog](../../../projects/lms-fusion/CHANGELOG.md)
