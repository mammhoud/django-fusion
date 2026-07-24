# API Reference — DF-008

> Source of truth: every symbol below was read from
> `src/django_fusion/` at the time this doc was written. After a
> refactor, run:
>
> ```bash
> grep -rEn '^class |^def [A-Za-z_][A-Za-z0-9_]*' src/django_fusion
> ```
>
> and update the tables above. Tables are intentionally curated rather
> than auto-generated: prominent symbols get a one-line role
> description, internal `_underscore` names are skipped, and only
> the canonical import paths from `AGENTS.md` are listed.

## Routing — `django_fusion.routes`

```python
from django_fusion.routes import (
    Viewset, BaseViewset, ViewsetMeta, Route, route, menu_path,
    IndexViewMixin, viewprop,
    BaseModelViewset, ModelViewset, ReadonlyModelViewset,
    ListBulkActionsMixin, CreateViewMixin, UpdateViewMixin,
    DeleteViewMixin, DetailViewMixin,
    Application, AppMenuMixin, Site,
    RoutableComponent, FragmentComponent,
    FragmentDetector, FragmentDetectionMixin,
)
```

| Symbol | Role |
|--------|------|
| `Viewset`, `BaseViewset`, `ViewsetMeta` | Declarative URL-list container. `Meta` holds `route_name`, `template_name`, etc. |
| `Route`, `route`, `menu_path` | Per-route helpers. `route()` returns a `Route`; `menu_path()` registers it with `Site.menu_items` automatically. |
| `IndexViewMixin` | Glue for `/` index routes. |
| `viewprop` | Class-level descriptor for properties that depend on `self`. |
| `BaseModelViewset`, `ModelViewset`, `ReadonlyModelViewset` | CRUD scaffold. `ModelViewset` covers list+detail+create+update+delete; `ReadonlyModelViewset` drops form routes. |
| `ListBulkActionsMixin`, `CreateViewMixin`, `UpdateViewMixin`, `DeleteViewMixin`, `DetailViewMixin` | Pick-and-mix CRUD mixins. |
| `Application`, `AppMenuMixin` | Mid-level URL grouping. `AppMenuMixin` adds menu items derived from registered routes. |
| `Site` | Top-level URL config. `site.urls` yields the URLconf. |
| `RoutableComponent` | View + template pair; a `Viewset` whose member is a component. |
| `FragmentComponent` | Subclass of `RoutableComponent` that strips layout when `HX-Request: true`. |
| `FragmentDetector`, `FragmentDetectionMixin` | Ad-hoc HTMX awareness for non-component views. |

See [DF-005 Routing](./05-routing.md) for the full breakdown.

## Generic CBVs — `django_fusion.components.generic`

```python
from django_fusion.components.generic import (
    Action, CreateModelView, DeleteBulkActionView, DeleteModelView,
    DetailModelView, ListModelView, UpdateModelView,
    BaseListModelView, BaseBulkActionView, SearchableViewMixin, TableView,
)
```

| Symbol | Role |
|--------|------|
| `ListModelView`, `BaseListModelView` | Paginated list. `SearchableViewMixin` adds query-string filtering. |
| `CreateModelView`, `UpdateModelView`, `DeleteModelView`, `DetailModelView` | One-shot CRUD views. |
| `DeleteBulkActionView`, `BaseBulkActionView` | Bulk selection + delete. |
| `Action` | Declarative action button descriptor on a list row. |
| `SearchableViewMixin` | Adds `?q=...` filter wiring. |
| `TableView` | Auto-renders through `components/table.html` when paired with `table_headers`. |

## Handlers / Managers / Models / Services — `django_fusion.core`

```python
from django_fusion.core.handlers import PageHandler       # base CBV mixin
from django_fusion.core.managers import CachedManager     # cache-aware manager
from django_fusion.core.models import TimeStampedModel    # created/updated_at
from django_fusion.core.services import BaseService       # CRUD-with-events base
from django_fusion.core.cache import CacheService         # singleton cache API
# middlewares: see src/django_fusion/projects/middlewares.py
```

> See `src/django_fusion/projects/{handlers.py,managers.py,models.py,services.py,cache.py,middlewares.py}`
> for the full class list. Each top-level module exports a small public
> surface; everything else is considered internal and may move without
> notice.

## Filters / Views / Loaders — `django_fusion.web` and `django_fusion.comp.loaders`

```python
from django_fusion.web.views import FilterMixin, SearchMixin
from django_fusion.comp.fragment.loader import component_loader
```

| Symbol | Role |
|--------|------|
| `FilterMixin` | Query-string filter chain (`?status=active&role=admin`). |
| `SearchMixin` | Single-field `?q=...` search. Often combined with `FilterMixin`. |
| `component_loader` | Decorator that marks a view as an HTMX-safe lazy loader. |

## Wagtail — `django_fusion.wagtail`

```python
from django_fusion.wagtail.blocks    import TimelineItemBlock, SkillBlock
from django_fusion.wagtail.snippets  import AuthEmailTemplate, BaseSnippetViewSet
from django_fusion.wagtail.viewsets  import export_to_csv, BaseSnippetViewSet
```

See [DF-010 Wagtail](./10-wagtail-integration.md).

## Health — `django_fusion.health`

```python
from django_fusion.health.views import (
    HealthCheckView, DatabaseHealthView, AssetsHealthView,
)
from django_fusion.health.urls   import health_urlpatterns
```

See [DF-009 Health](./09-health.md).

## Config — `django_fusion.config`

```python
from django_fusion.config.conf             import ImportStrategy, import_attribute
from django_fusion.config.conf_utils       import (
    ImportStrategy, import_model, import_form, import_adapter,
)
from django_fusion.config.dynaconf_loader import (
    DynaconfSettings, ModelsRegistry, TemplateRegistry, load_dynaconf_settings,
)
```

`config.constants` exists for runtime tunables (timeouts, pagination
limits, retries, slug/title/email length bounds, status / role /
permission enums, date formats). Import specific names — the file is
not a public re-export barrel.

## Cache — `django_fusion.comp.cache`

```python
from django_fusion.comp.cache import (
    ComponentMappingCache, get_component_map_cache,
)
```

| Symbol | Role |
|--------|------|
| `ComponentMappingCache` | Maps dotted `fragment_name` → template path. |
| `get_component_map_cache()` | Singleton accessor. Returns the active cache instance. |
