# django-fusion — AI Agent Instructions

This file is the canonical guide for the `libs/django-fusion/` reusable Django
and Wagtail framework library. Read the repository root `AGENTS.md` first when
working from the Structa Cloud checkout.

In this monorepo the library is at `libs/django-fusion/`. It may also be
checked out independently as its own repository.

## Framework role

`django-fusion` provides:

- `{% comp %}`, `{% prop %}`, `{% slot %}`, `{% var %}` template components
- Declarative `Site`, `Application`, `Viewset`, and model viewset routing
- HTMX fragment detection and rendering
- Generic CRUD views, forms, tables, search, and pagination
- Wagtail blocks/viewsets and shared auth integrations
- Component registry, include-path bridges, asset manifests, and health checks
- Configuration, middleware, privacy, cache, and debug/introspection helpers

Framework changes belong here. Product-specific branding, page content, API
contracts, and application behavior belong under the consuming product.

## Package architecture

```text
libs/django-fusion/
├── src/django_fusion/
│   ├── comp/                 # component registry, tags, loaders, cache
│   ├── routes/               # applications, viewsets, handlers, renderers
│   ├── fragments/            # fragment views, forms, tables, analyzer
│   ├── management/           # commands, handlers, managers, filters, utils
│   ├── core/                 # middleware, context, assets, health, rendering
│   ├── models/               # shared models and mixins
│   ├── services/             # reusable service layer
│   ├── plugins/              # HTMX, debug, API, Webpack, Unpoly, Robyn hooks
│   ├── contrib/              # admin, privacy, branding, integrations
│   ├── assets/               # SCSS/JS source and design tokens
│   └── templates/            # framework layouts and components
├── js/fusion-js/             # browser-side Fusion/HTMX helpers
├── tests/                    # framework tests
├── docs/                     # numbered architecture/API docs
├── webpack.config.js
├── setup.py / pyproject.toml
└── Makefile
```

## Consuming products in this checkout

Current active consumers include:

- `projects/precis/` — LMS/backend and Fusion application patterns
- `projects/landing-fusion/` — standalone Django/Wagtail landing backend
- `projects/formints/formint/` and `formint-cloud/` — APIs, fragments, render-mode,
  viewsets, and data components
- `projects/syntara/` — may use shared component conventions and integrations

The retired `lms-fusion`/`cms-fusion` names remain in migration plans and
compatibility aliases. Do not create new framework examples using nonexistent
paths; use the current consumers above.

## Canonical imports

Use concrete canonical modules and do not add re-export shims. Examples:

```python
from django_fusion.routes.core.base import Viewset, Route, route
from django_fusion.routes.core.sites import Application, Site
from django_fusion.routes.components.routable import RoutableComponent
from django_fusion.routes.components.fragments import FragmentComponent
from django_fusion.routes.http.detection import FragmentDetector
from django_fusion.fragments.forms import FormMixin
from django_fusion.fragments.tables import TableMixin
from django_fusion.comp.registry import component_registry
```

Consult the implementation tree and current package docs if an older import
example conflicts with the checked-out source.

## Component and fragment rules

- Use `{% comp "name" /%}` for registered/static components.
- Use `{% comp_include "path" %}` for tracked include-path components.
- Use `{% include %}` only for dynamic template names or intentionally local
  includes.
- Use `fragment_name` consistently for identifiers and context keys.
- Register include paths/components through the registry or app startup hooks;
  do not duplicate templates in consuming products without an ownership reason.
- Keep fragment responses compatible with full-page, HTMX, and API/data roads.

## Extension boundaries

Prefer, in order:

1. A product-level template override or component registration.
2. A product setting such as `FUSION_LAYOUTS`, `FUSION_FEATURES`, or
   `FUSION_RENDER_FIRST_DEFAULT`.
3. A project-owned service/handler extension.
4. A framework change here only when behavior is generic and tested by multiple
   consumers.

Keep framework assets, source SCSS, generated bundles, and collected static
files separate. Do not edit generated bundles as source.

## Tests and commands

```bash
cd libs/django-fusion
uv run pytest
make build
make check
```

Run targeted framework tests first, then at least one consuming product check
when changing public routing, component rendering, imports, assets, or fragment
contracts. Search all repository consumers before changing an exported symbol.

## Submodule rules

This directory is a git submodule in the parent repository. A submodule change
has two review surfaces: the library commit and the parent repository pointer.
Do not push or commit either repository unless the user explicitly requests it.
Keep branch/remote details in `.gitmodules` and the submodule's own repository
metadata; do not hard-code them in application code.
