# django-fusion

[![PyPI](https://img.shields.io/pypi/v/django-fusion.svg)](https://pypi.org/project/django-fusion/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-fusion.svg)](https://pypi.org/project/django-fusion/)
[![Django versions](https://img.shields.io/badge/django-4.2%20%7C%205.0%20%7C%205.1%20%7C%205.2-0C4B33.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

`django-fusion` is a Django + Wagtail helper library that gives you a
**component system, declarative routing, a `{% comp %}` template tag,
fragment rendering, forms/tables mixins, and health/asset plumbing** —
without a JavaScript build step for your templates.

It has no product vocabulary. Everything in the base package is generic
Django/Wagtail behavior; site-specific models, page types, and content belong to
the consuming project (see [Base vs. customization](#base-vs-customization)).

## What it gives you

- **`{% comp %}` template tag** with `{% prop %}`, `{% slot %}`, `{% var %}`,
  `{{ props.* }}`, `{{ attrs }}`, and `fragment_name=` for HTMX scoping. Pure
  Django template syntax — comparable to django-bird / django-cotton.
  ([DF-004](./docs/04-component-tag.md))
- **Declarative routing** — `Site`, `Application`, `Viewset`, `ModelViewset`
  (CRUD from one class), `RoutableComponent`, `FragmentComponent`,
  `FragmentDetector`. ([DF-005](./docs/05-routing.md))
- **Fragment rendering** — request any template fragment by dotted name over
  HTTP, HTMX, Unpoly, or SSE, with one `fragment_name` contract.
  ([DF-003](./docs/03-component-system.md))
- **Forms & tables** — `FormMixin`, `TableMixin`, `FormTableMixin` with a
  template-resolution cascade. ([DF-006](./docs/06-forms-and-tables.md))
- **Render contract** — render-first HTML, HTMX fragments, or a data API from
  the same view, resolved through one `FUSION_RENDER_MODE` chain.
  ([DF-018](./docs/18-render-contract.md))
- **Health checks** — `/health/`, `/health/db/`, `/health/assets/`.
  ([DF-009](./docs/09-health.md))
- **Asset pipeline** — a webpack bundle for component SCSS/JS plus a
  backend-controlled asset manifest for decoupled frontends.
  ([DF-016](./docs/16-assets.md))
- **Background tasks** — broker-agnostic registration with a Dramatiq backend
  and an in-process backend for tests.
- **Dynaconf configuration** — multi-environment YAML settings loader, plus
  privacy/cache/middleware helpers in `contrib/`. ([DF-007](./docs/07-configuration.md))

## Install

```bash
pip install django-fusion
```

Optional extras — each is a real, separately installable integration:

| Extra | Adds | For |
|---|---|---|
| `django-fusion[bolt]` | `django-bolt`, `msgspec`, `PyJWT` | `django_fusion.plugins.apis`, `django_fusion.mcp` |
| `django-fusion[tables]` | `django-tables2` | the django-tables2 adapter |
| `django-fusion[auth]` | `django-allauth` | allauth adapters and social signup |
| `django-fusion[webpack]` | `django-webpack-loader` | `{% render_bundle %}` integration |
| `django-fusion[tasks]` | `dramatiq[redis]`, `apscheduler` | the Dramatiq task backend |
| `django-fusion[test]` | `pytest`, `pytest-django`, `hypothesis`, `pytest-cov` | running this library's suite |
| `django-fusion[dev]` | `build`, `twine`, `ruff`, test stack | releasing |

## Quick start

Add the apps you need to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
<<<<<<< HEAD
    "django_fusion",                 # app config: task wiring + sub-app discovery
    "django_fusion.comp",            # component system, registry, {% comp %}
    "django_fusion.core",            # handlers, managers, services, cache, middlewares
    "django_fusion.config",          # Dynaconf settings loader

    # optional — only when used
    "django_fusion.core.health",             # /health/ endpoints
    "django_fusion.fragments.analyzer",      # {% comp %} usage scanner
    "django_fusion.builder",                 # Wagtail page-builder blocks
    "django_fusion.contrib",                 # admin, privacy, cache utils
=======
    "django_fusion",                    # base models, migrations, task bootstrap
    "django_fusion.comp",               # component registry + {% comp %} (required)
    "django_fusion.fragments.analyzer", # optional: template usage analyzer
    "django_fusion.builder",            # optional: landing builder
>>>>>>> refs/remotes/origin/generic
]
```

Render a component:

```django
{% comp "components/button.html" label="Save" variant="primary" / %}
```

Route a viewset:

```python
from django_fusion.routes.core.sites import Application, Module
from django_fusion.routes.core.base import Viewset
```

The full walkthrough — middleware ordering, template-tag builtins, and a first
fragment — is in [**DF-001 Getting Started**](./docs/01-getting-started.md).

## Canonical imports

Import from the owning module. Do not add re-export shims.

```python
from django_fusion.routes.core.base import Viewset, Route, route
from django_fusion.routes.core.sites import Module, Application
from django_fusion.routes.components.routable import RoutableComponent
from django_fusion.routes.components.fragments import FragmentComponent
from django_fusion.routes.http.detection import FragmentDetector
from django_fusion.routes.rendering.decorators import fusion_view
from django_fusion.routes.rendering.render_mode import resolve_render_mode
from django_fusion.fragments.forms import FormMixin
from django_fusion.fragments.tables import TableMixin
from django_fusion.comp._init import components
from django_fusion.comp.registry import register_include_paths
from django_fusion.core.assets import urls as assets_urls
from django_fusion.services import BaseService, TokenService, dispatch_job
from django_fusion.config.conf import resolve_render_mode_setting
```

`tests/test_documented_import_paths.py` imports every path on this page, so a
rename fails the build instead of silently breaking the documentation.

## Base vs. customization

The library stays minimal on purpose. This is the line:

| Belongs in `django-fusion` | Belongs in the consuming project |
|---|---|
| The component system, `{% comp %}` tags, and the registry | Component *templates* and their copy/branding |
| Routing primitives (`Site`, `Application`, `Viewset`, `RoutableComponent`) | Project URL mounts and route paths |
| Generic CBVs, forms/tables mixins, fragment rendering | Project models, page types, and admin panels |
| Shared abstract model *bases* and mixins | Concrete project models and their migrations |
| Render-mode resolution, health checks, asset manifest contracts | Deployment policy, CDN/S3 credentials, host routing |
| Task registry and broker-agnostic dispatch | Project task implementations and schedules |

Two rules that follow from this:

1. **No product vocabulary.** The base package must not name a site, a product,
   or a product's page types. If a helper only makes sense for one product, it
   lives in that product.
2. **No monorepo paths.** The library is a standalone, published package. It has
   no knowledge of a surrounding workspace, its `projects/`, or its CI.

## Asset pipeline (webpack)

`django-fusion` ships a Webpack 5 pipeline for its component SCSS and JS. It
produces a single `fusion` bundle consumed through django-webpack-loader.

```bash
make build      # production (content-hashed, minified)
make dev        # dev build with source maps
make watch      # dev + file watcher
make clean      # remove generated assets
```

Output:

```
static/bundles/fusion.<hash>.css
static/bundles/fusion.<hash>.js
webpack-stats.json
```

Source layout:

| Path | Contents |
|---|---|
| `src/django_fusion/assets/entry.js` | JS entry point |
| `src/django_fusion/assets/fusion.scss` | SCSS entry point |
| `src/django_fusion/assets/variables/` | Design tokens |
| `src/django_fusion/assets/{base,button,card,form,modal,navigation,table,utilities}/` | Component partials |
| `src/django_fusion/templates/fusion/_layout.scss` | Layout grid styles |
| `src/django_fusion/builder/scss/` | Landing-builder themes |

In a Django template:

```django
{% load render_bundle from webpack_loader %}
{% render_bundle 'fusion' 'css' %}
{% render_bundle 'fusion' 'js' %}
```

Never edit generated bundles as source. Full detail in
[DF-016](./docs/16-assets.md).

## Development

```bash
git clone https://github.com/mammhoud/django-fusion.git
cd django-fusion

uv run --extra test pytest     # full suite
uv run --extra test pytest -q  # quiet
```

The suite is self-contained: no services, no network, no monorepo. Django
settings live in `tests/_django_settings.py` and are applied by
`tests/conftest.py`.

Linting:

```bash
uv run --with ruff ruff check src tests
```

## Releasing

Version bumps, tagging, building, and publishing are documented end to end in
[**DF-023 Publishing**](./docs/23-publishing.md), with `make` targets:

```bash
make version        # print the version from pyproject.toml
make dist           # build sdist + wheel into dist/
make check-dist     # twine check the built artifacts
make publish-test   # upload to TestPyPI
make publish        # upload to PyPI (requires a clean tree at the release tag)
```

## Documentation

The library docs live in [`docs/`](./docs/INDEX.md) with stable `DF-0NN` IDs.

| ID | Topic |
|----|-------|
| [DF-001](./docs/01-getting-started.md) | Getting started |
| [DF-002](./docs/02-architecture.md) | Architecture overview |
| [DF-003](./docs/03-component-system.md) | Component system (Python) |
| [DF-004](./docs/04-component-tag.md) | `{% comp %}` template tag |
| [DF-005](./docs/05-routing.md) | Routing & viewsets |
| [DF-006](./docs/06-forms-and-tables.md) | Forms & tables |
| [DF-007](./docs/07-configuration.md) | Settings & configuration |
| [DF-008](./docs/08-api-reference.md) | API reference |
| [DF-009](./docs/09-health.md) | Health checks |
| [DF-010](./docs/10-wagtail-integration.md) | Wagtail integration |
| [DF-011](./docs/11-best-practices.md) | Best practices |
| [DF-012](./docs/12-integration-examples.md) | Integration examples |
| [DF-013](./docs/13-troubleshooting.md) | Troubleshooting |
| [DF-014](./docs/14-faq.md) | FAQ |
| [DF-015](./docs/15-viewflow-mapping.md) | Viewflow / django-material mapping |
| [DF-016](./docs/16-assets.md) | Asset pipeline & webpack |
| [DF-017](./docs/17-integration-modes.md) | Integration modes and project boundaries |
| [DF-018](./docs/18-render-contract.md) | Slot & prop render contract |
| [DF-019](./docs/19-openapi-and-filtering.md) | OpenAPI docs and viewset filtering |
| [DF-020](./docs/20-language-contract.md) | Shared language/locale contract |
| [DF-021](./docs/21-landing-builder.md) | Landing builder |
| [DF-022](./docs/22-template-fields.md) | Template field engine |
| [DF-023](./docs/23-publishing.md) | Building and publishing to PyPI |

## Author & contact

**Mahmoud Ezzat Moustafa** — Structa Cloud

- GitHub: [github.com/mammhoud](https://github.com/mammhoud)
- LinkedIn: [linkedin.com/in/mammhoud](https://www.linkedin.com/in/mammhoud)
- Facebook: [facebook.com/mammhoud](https://www.facebook.com/mammhoud)

Bug reports and feature requests: [open an issue](https://github.com/mammhoud/django-fusion/issues).

## Citation

> django-fusion — Reusable Django and Wagtail helpers.
> https://github.com/mammhoud/django-fusion

## License

[MIT](./LICENSE). Copyright (c) 2024-2026 Structa Cloud / Mahmoud Ezzat Moustafa.
