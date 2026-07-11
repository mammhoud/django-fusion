# django-fusion — AI Agent Instructions

This file is the canonical entry point for AI agents and human contributors
working in the `django-fusion` repository. Path-relative links below are valid
in both the standalone repo and the Structa Cloud submodule (which lives at
`core/libs/django-fusion/` inside the monorepo).

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
├── core/            # Handlers, managers, models, services, cache, middlewares
├── health/          # HealthCheckView, DatabaseHealthView, AssetsHealthView
├── infrastructure/  # Management commands, scripts, template tags, locale
├── site/            # Auth mixins, context processors, paginators, plugins
└── wagtail/         # StreamField blocks, AuthEmailTemplate snippet, viewsets
```

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
