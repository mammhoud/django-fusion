# Architecture Overview — DF-002

> Source of truth: `src/django_fusion/__init__.py` docstring, `AGENTS.md`,
> top-level package directories under `src/django_fusion/`.

## Module map

```
django_fusion/
├── analyzer/        # Scanner + parser → JSON tracking of {% comp %} usage
├── comp/            # Component system: tag, registry, routing, generic CBVs
│   ├── registry.py
│   ├── routes/      # Site, Application, ModelViewset, RoutableComponent, FragmentComponent
│   ├── generic.py   # ListModelView, CreateModelView, …, TableView
│   ├── forms/       # FormMixin, TableMixin, FormTableMixin (legacy helpers)
│   ├── loaders.py   # component_loader / lazy HTMX-safe loader decorator
│   ├── cache.py     # ComponentMapping cache (Redis fallback)
│   └── templatetags/
├── config/          # conf, conf_utils, constants, dynaconf_loader
├── contrib/         # admin, cache utils, debug_tools, email_config, privacy
├── projects/            # Handlers, managers, models, services, cache, middlewares
├── health/          # /health/, /health/db/, /health/assets/
├── infrastructure/  # Management commands, scripts, template tags, locale
├── site/            # Allauth adapter, context processors, notifications, paginators
└── wagtail/         # blocks.py, snippets.py, viewsets.py
```

## Layered design

| Layer | Module(s) | Responsibility |
|-------|-----------|---------------|
| Foundation | `core.{models, managers, services, cache}` | TimeStampedModel, group-aware managers, CRUD service base, pluggable cache |
| Request-handling | `core.handlers`, `core.middlewares` | `PageHandler` base, error tracker, privacy, language |
| Routing | `comp.routes`, `comp.generic` | `Site` / `Application` / `ModelViewset` plus HTMX-aware `FragmentComponent` |
| Components | `comp.registry`, `comp.routes.{components,fragments}`, `comp.templatetags` | Registry, fragment detection, `{% comp %}` tag, `register_default_partials()` |
| Forms / Tables | `comp.routes.forms_tables` (legacy) | `FormMixin`, `TableMixin`, `FormTableMixin` — see DF-006 |
| Site-level | `site.*`), `web.*` | Allauth flows, context processors, template rendering helpers |
| CMS | `wagtail.*` | StreamField blocks, `AuthEmailTemplate` snippet, snippet viewsets |
| Ops | `health`, `contrib.{cache,debug_tools,privacy}` | `/health/`, monitoring, consent |
| Config | `config.{conf,dynaconf_loader}`, `infrastructure` | Multi-env YAML settings |
| Analysis | `analyzer` | Static analysis of `{% comp %}` usage across templates |

## Request flow (Mermaid)

```mermaid
flowchart LR
    A[HTTP Request] --> B[Django URLconf]
    B --> C[Site.urls]
    C --> D[Application.urls]
    D --> E[Viewset / ModelViewset]
    E --> F[RoutableComponent / FragmentComponent]
    F --> G[resolve_template_name]
    G --> H{strategy}
    H -->|fragment| I[fragment template]
    H -->|document| J[full-page template]
    I --> K[{% comp %} registry.render]
    J --> K
    K --> L[Response]
    L --> M[HTTP Response]
```

## When would I touch this?

- **`projects/`** — when adding a foundational manager, model, or service that
  every app reuses (rare).
- **`comp/`** — when extending the component system (most feature work).
- **`site/` / `web/`** — when adding an auth flow or new context processor.
- **`wagtail/`** — when adding a new StreamField block or snippet viewset.
- **`contrib/`** — when shipping opt-in Django tools (privacy, debug,
  monitoring) that callers can enable per project.
- **`infrastructure/`** — for locale files, custom `manage.py` commands,
  or pre-build scripts.

## Public surface (canonical imports)

Per `AGENTS.md`:

```python
from django_fusion.comp.routes import (
    Viewset, BaseViewset, ViewsetMeta, Route, route, menu_path,
    IndexViewMixin, viewprop,
    BaseModelViewset, ModelViewset, ReadonlyModelViewset,
    ListBulkActionsMixin, CreateViewMixin, UpdateViewMixin,
    DeleteViewMixin, DetailViewMixin,
    Application, AppMenuMixin, Site,
    RoutableComponent, FragmentComponent,
    FragmentDetector, FragmentDetectionMixin,
)
from django_fusion.comp.generic import (
    Action, CreateModelView, DeleteBulkActionView, DeleteModelView,
    DetailModelView, ListModelView, UpdateModelView,
    BaseListModelView, BaseBulkActionView, SearchableViewMixin, TableView,
)
```

See DF-008 for the full per-module docstring reference.

## Versioning & stability

`__version__ = "0.2.0"`. Below `1.0`, minor versions may reorganise
the public surface. After `1.0`, the canonical import paths above are
considered stable.
