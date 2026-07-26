# django-fusion — AI Agent Instructions

This file is the canonical entry point for AI agents and human contributors
working in the `django-fusion` repository. Path-relative links below are valid
in both the standalone repo and the Structa Cloud submodule (which lives at
`projects/libs/django-fusion/` inside the monorepo).

## Canonical Import Paths

All imports use the re-export-free canonical paths below.

### Routing (`comp.routes`)

```python
from django_fusion.routes import (
    Viewset, BaseViewset, ViewsetMeta, Route, route, menu_path, IndexViewMixin,
    viewprop,  # Descriptor
    BaseModelViewset, ModelViewset, ReadonlyModelViewset,
    ListBulkActionsMixin, CreateViewMixin, UpdateViewMixin, DeleteViewMixin, DetailViewMixin,
    Application, AppMenuMixin, Site,
    RoutableComponent, FragmentComponent,
    FragmentDetector, FragmentDetectionMixin,
)
```

### Generic CBVs (`comp.generic`)

```python
from django_fusion.components.generic import (
    Action, CreateModelView, DeleteBulkActionView, DeleteModelView,
    DetailModelView, ListModelView, UpdateModelView,
    BaseListModelView, BaseBulkActionView, SearchableViewMixin, TableView,
)
```

### Forms & Tables (`comp.contrib`)

```python
from django_fusion.contrib.tables import TableMixin, RowGenerator
from django_fusion.contrib.forms import FormMixin, FormTableMixin, FormTagGenerator
```

Legacy imports from ``django_fusion.routes.forms_tables`` still work
but are forwarded to ``comp.contrib`` internally.

### Other Canonical Paths

| Module | Canonical Path |
|--------|---------------|
| Handlers | `django_fusion.core.handlers` |
| Managers | `django_fusion.core.managers` |
| Models | `django_fusion.core.models` |
| Services | `django_fusion.core.services` |
| Views (FilterMixin, SearchMixin) | `django_fusion.web.views` |
| Loaders | `django_fusion.comp.loaders` |
| Middlewares | `django_fusion.core.middlewares` |
| Cache | `django_fusion.core.cache` |
| Dynaconf config | `django_fusion.config.dynaconf_loader` |

## Component Tag (`{% comp %}`)

- Use `{% comp "name" %}` for ALL rendered components — the single canonical tag
- Reserved kwargs: use `fragment_name` for the fragment identifier
- Self-closing: `{% comp "icon.html" / %}`
- Pair tags with default slot: `{% comp "card" %}...{% endcomp %}`
- Prefer `{% comp "path" / %}` over `{% include "path" %}` for static paths

## Package Architecture

```
django_fusion/
├── analyzer/        # Component scanner, parser, schemas
├── comp/            # Component system + routing + generic CBVs
│   ├── registry.py  # Component registration, lazy include templates
│   ├── routes/      # Site, Application, ModelViewset, RoutableComponent, FragmentComponent
│   ├── generic.py   # ListModelView, CreateModelView, DeleteModelView, TableView
│   ├── forms/       # FormMixin, TableMixin, FormTableMixin
│   ├── loaders.py   # component_loader decorator
│   ├── cache.py     # ComponentMapping cache (Redis fallback)
│   └── templatetags/ # {% comp %}, {% slot %}, {% prop %}, {% var %}
├── config/          # Configuration (dynaconf_loader, constants)
├── contrib/         # admin, cache, debug_tools, email_config, privacy
├── projects/            # Handlers, managers, models, services, cache, middlewares
├── health/          # HealthCheckView, DatabaseHealthView, AssetsHealthView
├── infrastructure/  # Management commands, scripts, template tags, locale
├── site/            # Auth mixins, context processors, paginators, plugins
└── wagtail/         # StreamField blocks, AuthEmailTemplate snippet, viewsets
```

## Customization Hooks (for Structa Cloud projects)

django-fusion is designed to be fully customizable from parent projects. When working in Structa Cloud or any consuming project, prefer these extension points over editing django-fusion itself.

### 1. Template overrides

Django's template loader resolves app directories in `INSTALLED_APPS` order, followed by `TEMPLATES['DIRS']`. To override a django-fusion template:

1. Place a template at the same relative path in your project's `templates/` directory.
2. Ensure your project/app templates directory is listed before or instead of django-fusion's.
3. For layout overrides, use `FUSION_LAYOUTS` and `FUSION_DEFAULT_LAYOUT` in `settings.py`.

Example override tree:
```
<project>/templates/
├── fusion/
│   └── layouts/
│       └── default.html      # overrides django_fusion/templates/fusion/layouts/default.html
└── components/
│   └── blocks/
│       └── hero.html         # overrides a shared component
```

### 2. Settings-driven behavior

| Setting | Purpose |
|---------|---------|
| `FUSION_LAYOUTS` | Map logical layout names to template paths |
| `FUSION_DEFAULT_LAYOUT` | Default layout key to use |
| `FUSION_FEATURES` | Toggle high-level features (blog, courses, products, auth, etc.) |
| `FUSION_RENDER_FIRST_DEFAULT` | Default value for `fusion_render_first` |
| `COMPONENTS_INCLUDE_PATH_ROOTS` | Register include-path roots for `comp_include` |

### 3. Component registry extensibility

Register new components or replace existing ones in `AppConfig.ready()`:

```python
from django_fusion.comp.registry import component_registry

class MyAppConfig(AppConfig):
    name = "my_app"

    def ready(self):
        component_registry.register("my_app.hero", "path/to/hero.html")
```

For include-path bridges, use:

```python
from django_fusion.comp.registry import register_include_path

register_include_path("shared/components")
```

### 4. Fragment rendering overrides

`RoutableComponent` and `FragmentComponent` derive `fragment_name` from class/module names. Override `get_fragment_name()` or set `fragment_name` explicitly to control the rendered fragment.

```python
from django_fusion.routes import RoutableComponent

class MyPage(RoutableComponent):
    fragment_name = "pages.my_custom_page"
    fusion_render_first = True
```

### 5. Layout system extension

Add custom layout tags by extending `fusion_layout.py` templatetags or by registering a new loader. Keep project-specific layout tags in a project-level `templatetags/` module.

---

## Submodule / Integration Notes

When used inside Structa Cloud, django-fusion is a git submodule at `libs/django-fusion/`. Other submodules that commonly work with django-fusion:

| Submodule | Role | Key File |
|-----------|------|----------|
| `libs/ceptor-ai` | AI chat client, MCP server, agent generation | [`libs/ceptor-ai/AGENTS.md`](../ceptor-ai/AGENTS.md) |
| `libs/django-bolt` | High-performance BoltAPI (Rust-backed) | [`libs/django-bolt/README.md`](../django-bolt/README.md) |

- Keep framework-level changes in `libs/django-fusion/` and site-specific overrides in the relevant `projects/<site>/` directory.
- When modifying a template or component that is used across multiple Structa Cloud sites, consider whether the change belongs in django-fusion (shared) or in `projects/assets/` (cross-site design).

---

## Documentation Map (DF-0NN)

Stable doc IDs — equally valid from the standalone repo or the submodule.

| ID | Topic | File |
|----|-------|------|
| DF-000 | Documentation index | `docs/INDEX.md` |
| DF-001 | Getting started | `docs/01-getting-started.md` |
| DF-002 | Architecture overview | `docs/02-architecture.md` |
| DF-003 | Component system (Python) | `docs/03-component-system.md` |
| DF-004 | `{% comp %}` template tag | `docs/04-component-tag.md` |
| DF-005 | Routing & viewsets | `docs/05-routing.md` |
| DF-006 | Forms & tables | `docs/06-forms-and-tables.md` |
| DF-007 | Settings & configuration | `docs/07-configuration.md` |
| DF-008 | API reference | `docs/08-api-reference.md` |
| DF-009 | Health checks | `docs/09-health.md` |
| DF-010 | Wagtail integration | `docs/10-wagtail-integration.md` |
| DF-011 | Best practices | `docs/11-best-practices.md` |
| DF-012 | Integration examples | `docs/12-integration-examples.md` |
| DF-013 | Troubleshooting | `docs/13-troubleshooting.md` |
| DF-014 | FAQ | `docs/14-faq.md` |
| DF-015 | Viewflow mapping | `docs/15-viewflow-mapping.md` |

# @tested django-fusion - Component system, routing, forms/tables, all canonical import paths verified with pytest
