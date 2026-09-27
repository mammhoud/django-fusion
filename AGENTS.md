# django-fusion — AI Agent Instructions

Canonical guide for the `django-fusion` reusable Django and Wagtail library.
When this directory is checked out as a submodule of a larger workspace, read
that workspace's root `AGENTS.md` first; the rules here still apply to
everything under `libs/django-fusion/`.

This repository is **published to PyPI**. It must build, test, and make sense as
a standalone package. It has no knowledge of a surrounding workspace.

## Framework role

`django-fusion` provides:

- `{% comp %}`, `{% prop %}`, `{% slot %}`, `{% var %}` template components
- Declarative `Site`, `Application`, `Viewset`, `ModelViewset`, and `Route` routing
- HTMX / Unpoly / SSE fragment detection and rendering
- Generic CRUD views, forms, tables, search, and pagination
- Shared abstract model bases, mixins, and service-layer primitives
- Render-mode resolution, health checks, and asset-manifest contracts
- Wagtail-aware viewsets, blocks, and snippets
- Optional integrations: django-bolt API bridge, django-tables2, allauth,
  django-webpack-loader, an interactive designer, and MCP routers

**Framework changes belong here.** Product branding, page content, concrete
models, migrations, and API contracts belong to the consuming project.

## Package architecture

```text
libs/django-fusion/
├── src/django_fusion/
│   ├── comp/                 # component registry, {% comp %} tags, loaders, cache
│   ├── routes/               # applications, viewsets, components, handlers, renderers
│   ├── fragments/            # fragment views, forms, tables, generic CBVs, analyzer
│   ├── core/                 # middleware, context, rendering, assets, health, encoder
│   ├── config/               # typed conf, Dynaconf loader, asset manifest
│   ├── models/               # base models, mixins, email, interaction, datatoken
│   ├── services/             # base/model services, jobs, token, crud
│   ├── management/           # commands, handlers, filters, managers, utils
│   ├── tasks/                # broker-agnostic task registry and backends
│   ├── site/                 # site-level authentication mixins
│   ├── plugins/              # optional integrations (apis, designer, htmx, ...)
│   ├── builder/              # landing builder: page assembly, themes, styles
│   ├── template_fields/      # sandboxed dynamic template field engine
│   ├── mcp/                  # MCP routers (requires the bolt extra)
│   ├── contrib/              # admin, privacy, cache, utility extensions
│   ├── assets/               # SCSS/JS source for the webpack bundle
│   └── templates/            # framework templates and components
├── tests/                    # self-contained pytest suite + fixtures
├── docs/                     # numbered docs (DF-0NN) + INDEX.md
├── .github/workflows/ci.yml  # library CI
├── MANIFEST.in               # sdist contents
├── Makefile                  # asset build + release targets
└── pyproject.toml            # metadata, extras, tool config
```

## Canonical imports

Import the real symbol from its owning module. Do not add re-export shims,
alias modules, or forwarding `__init__.py` re-exports.

```python
from django_fusion.routes.core.base import Viewset, Route, route
from django_fusion.routes.core.sites import Application, Module
from django_fusion.routes.components.routable import RoutableComponent
from django_fusion.routes.components.fragments import FragmentComponent
from django_fusion.routes.http.detection import FragmentDetector
from django_fusion.routes.rendering.decorators import fusion_view
from django_fusion.fragments.forms import FormMixin
from django_fusion.fragments.tables import TableMixin
from django_fusion.comp._init import components
from django_fusion.comp.registry import register_include_paths
from django_fusion.core.assets import urls as assets_urls
from django_fusion.services import BaseService, TokenService, dispatch_job
```

`tests/test_documented_import_paths.py` imports every path advertised in the
README and docs. If you rename or move a public symbol, update that list and the
docs in the same change.

## Hard boundaries

1. **No product vocabulary in `src/`.** No site names, product names, product
   page types, or product model classes. If a helper only makes sense for one
   product, it belongs in that product.
2. **No monorepo paths.** Nothing under `src/`, `tests/`, or `docs/` may
   reference a surrounding workspace, its `projects/`, its CI, or its scripts.
3. **Concrete models stay; abstract bases may move.** `Call` and `Notification`
   (`models/interaction/`) are concrete, migrated models — removing them needs a
   schema migration. Abstract bases such as `AbstractCoupon` describe a product's
   vocabulary and belong to the product.
4. **Optional integrations must not break a base install.** Every third-party
   import behind an extra must be guarded, and a missing extra must degrade to a
   skip (tests) or an import-safe fallback (runtime).

`tests/test_imports.py` and `tests/test_site_management_commands.py` pin rules 1
and 3.

## Component and fragment rules

- Use `{% comp "name" /%}` for registered/static components.
- Use `{% include %}` only for genuinely dynamic template names or local includes.
- Use `fragment_name` consistently for fragment identifiers and context keys.
- Register include paths through the registry or an app startup hook.
- Keep fragment responses compatible with full-page, HTMX, and data-API roads.

## Tests and commands

```bash
cd libs/django-fusion
uv run --extra test pytest     # full suite
uv run --extra test pytest -q  # quiet
uv run --with ruff ruff check src tests
make dist && make check-dist   # packaging validation
```

Two gotchas, both already handled in `tests/conftest.py` — do not undo them:

- Django caches both the engine instances (`engines._engines`) **and** the
  `settings.TEMPLATES` reference (`engines._templates`). Clearing only the first
  leaves a later test module pointing at a deleted temp directory.
- The component registry is a process-global singleton; module-scoped state must
  be restored between modules or the suite becomes order-dependent.

## Assets

- Source SCSS/JS lives in `src/django_fusion/assets/`; generated bundles live in
  `static/bundles/` and are gitignored. Never edit generated output instead of
  its source.
- `[tool.setuptools.package-data]` and `MANIFEST.in` decide what ships. If you
  add a new asset directory to the package, add it to both, then verify with
  `make dist` and inspect the wheel.

## Release

Releases are documented in [`docs/23-publishing.md`](./docs/23-publishing.md).
`pyproject.toml`, `src/django_fusion/__init__.py`, and `CHANGELOG.md` must agree
on the version. Do not push a tag or publish to PyPI unless explicitly asked.

## Submodule rules

When this directory is a git submodule, a change has two review surfaces: the
library commit and the parent repository's gitlink. Do not commit or push either
unless the user explicitly requests it. Keep branch and remote details in git
metadata, never in application code.
