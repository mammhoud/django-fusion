# django-fusion — AI Agent Instructions

Path: `applications/libs/django-fusion/`

## Canonical Import Paths

All imports use the re-export-free canonical paths below.

### Routing (`comp.routes`)

```python
from django_fusion.comp.routes import (
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
from django_fusion.comp.generic import (
    Action, CreateModelView, DeleteBulkActionView, DeleteModelView,
    DetailModelView, ListModelView, UpdateModelView,
    BaseListModelView, BaseBulkActionView, SearchableViewMixin, TableView,
)
```

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

## Component Tag (`{% comp %}`)

- Use `{% comp "name" %}` for ALL rendered components — the single canonical tag
- Reserved kwargs: use `fragment_name` for the fragment identifier
- Self-closing: `{% comp "icon.html" / %}`
- Pair tags with default slot: `{% comp "card" %}...{% endcomp %}`
- Prefer `{% comp "path" / %}` over `{% include "path" %}` for static paths

## Package Architecture

```
django_fusion/
├── comp/           # Component system: {% comp %} tag, registry, routes, generic CBVs
│   ├── routes.py   # Site, Application, ModelViewset, RoutableComponent, FragmentComponent
│   ├── generic.py  # ListModelView, CreateModelView, DeleteModelView, TableView
│   └── registry.py # Component registration, LazyIncludeTemplate
├── core/           # Handlers, managers, models, services, cache, middlewares, filters
│   ├── handlers.py # PageHandler base class
│   ├── managers.py  # Custom model managers
│   ├── models.py   # TimeStampedModel, base models
│   ├── services.py # BaseService
│   ├── cache.py    # CacheService
│   └── middlewares.py
├── health/         # HealthCheckView, DatabaseHealthView, AssetsHealthView
├── site/           # Auth mixins, context processors, paginators, notifications, plugins
│   ├── auth/       # Allauth integration mixins
│   ├── context/    # settings.py (brand_settings, social_settings context)
│   └── paginators.py
├── wagtail/        # StreamField blocks, AuthEmailTemplate snippet, viewsets
│   ├── blocks.py
│   ├── snippets.py
│   └── viewsets.py
├── contrib/        # admin, cache, debug_tools, email_config, enums, privacy, utils
├── infrastructure/ # Management commands, scripts, templatetags, locale
└── analyzer/       # Component scanner, parser, schemas
```

## Component Conventions

- Props declaration: `{% prop title %}` / `{% prop summary="" %}`
- Named slots: `{% slot header %}...{% endslot %}`
- Vars (local state): `{% var key="value" %}`
- Attrs passthrough: `class="{{ attrs }}"`
- Fragment names follow dot-notation: `<site>.fragments.<app>.<name>`
- `IncludePathComponent` maps plain template paths to component names verbatim
- `register_default_partials()` auto-registers all `*.html` under `COMPONENTS_INCLUDE_PATH_ROOTS`

## Documentation References

| Topic | File |
|-------|------|
| Component system | `applications/libs/django-fusion/docs/COMPONENT_SYSTEM.md` |
| Component tag API | `applications/libs/django-fusion/docs/COMPONENT_TAG.md` |
| Routing system | `applications/libs/django-fusion/docs/ROUTING_SYSTEM.md` |
| Forms & tables | `applications/libs/django-fusion/docs/FORMS_TABLES_INTEGRATION.md` |
| Viewflow mapping | `applications/libs/django-fusion/docs/VIEWFLOW_MAPPING.md` |
| Architecture overview | `applications/libs/django-fusion/docs/ARCHITECTURE_OVERVIEW.md` |
| Health module | `applications/libs/django-fusion/docs/HEALTH.md` |
