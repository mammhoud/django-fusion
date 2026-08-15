# Routing System — DF-005

> Source of truth: `src/django_fusion/comp/routes/{base.py, sites.py,
> components.py, model.py, other.py, fragments.py, detection.py,
> template_resolver.py}`, `src/django_fusion/comp/generic.py`,
> `AGENTS.md` canonical-import table.

## Concepts (top-down)

A **Site** registers one or more **Applications**. An Application holds one
or more **Viewsets** (or plain `RoutableComponent` instances).
A ModelViewset turns one model into 5 CRUD routes. Anything can opt into
HTMX fragment behaviour via the FragmentDetector.

| Class | Where defined | Role |
|-------|---------------|------|
| `Site` | `comp.routes.sites` | Top-level URL config + menu builder |
| `Application` | `comp.routes.sites` | Mid-level grouping (admin, blog, pricing) |
| `BaseViewset` / `Viewset` / `ViewsetMeta` | `comp.routes.base` | Declarative URL-list container |
| `Route`, `route`, `menu_path`, `IndexViewMixin` | `comp.routes.{other,base}` | Per-route helpers |
| `viewprop` | `comp.routes.base` | Class-level URL-as-attribute descriptor |
| `BaseModelViewset`, `ModelViewset`, `ReadonlyModelViewset` | `comp.routes.model` | CRUD scaffold from one model |
| `ListBulkActionsMixin`, `CreateViewMixin`, `UpdateViewMixin`, `DeleteViewMixin`, `DetailViewMixin` | `comp.routes.model` | Granular CRUD mixins |
| `RoutableComponent`, `FragmentComponent` | `comp.routes.{components,fragments}` | View+template pair with HTMX awareness |
| `FragmentDetector`, `FragmentDetectionMixin` | `comp.routes.detection` | Ad-hoc HTMX-aware rendering |

## Minimal `Site` example

```python
# mysite/urls.py
from django.urls import path
from django_fusion.routes.core.sites import (
    Site,
    Application,
)

blog_app = Application(
    title="Blog",
    icon="bi-newspaper",
    components=[
        # RoutableComponent subclasses, see comp.routes.components
    ],
)

pricing_app = Application(
    title="Pricing",
    icon="bi-currency-dollar",
    viewsets=[
        # Viewset subclasses, see comp.routes.base
    ],
)

site = Site(title="My Site", apps=[blog_app, pricing_app])

urlpatterns = [path("", site.urls)]
```

## `ModelViewset` — all CRUD routes from one class

```python
# myapp/viewsets.py
from django_fusion.routes.models.crud import ModelViewset

class PostViewset(ModelViewset):
    model = Post
    paginate_by = 25
    template_name = "blog/post"   # resolves _list, _detail, _form

# myapp/urls.py
from django_fusion.routes.core.sites import Application
from myapp.viewsets import PostViewset

blog = Application(
    title="Blog",
    urlpatterns=PostViewset.get_urlpatterns(),
)
```

This auto-emits:

| URL | View | Name |
|-----|------|------|
| `""` | list | `<app>:list` |
| `"<int:pk>/"` | detail | `<app>:detail` |
| `"create/"` | create | `<app>:create` |
| `"<int:pk>/update/"` | update | `<app>:update` |
| `"<int:pk>/delete/"` | delete | `<app>:delete` |

Override any of them by setting `urlpatterns = [...]` on the viewset.

## Pick-and-mix CRUD with `BaseModelViewset` + mixins

```python
from django_fusion.routes.models.base import BaseModelViewset
from django_fusion.routes.models.crud import (
    DetailViewMixin,
    UpdateViewMixin,
    DeleteViewMixin,
)

class ReadOnlyWithDelete(BaseModelViewset,
                          DetailViewMixin,
                          DeleteViewMixin):
    model = Audit
    paginate_by = 50
```

Use this when you only need a subset of CRUD (read-only listings with a
delete action, archive-then-soft-delete, etc.).

## `Viewset` (non-model)

For viewsets without a `model` (e.g. dashboards, settings pages):

```python
from django_fusion.routes.core.base import (
    Viewset,
    Route,
    route,
    menu_path,
)

class DashboardViewset(Viewset):
    route_name = "dashboard"

    overview = route("overview/", "DashboardView", name="overview", title="Overview")
    settings = route("settings/", "SettingsView", name="settings", title="Settings")
```

`route()` returns a `Route` instance; `menu_path()` is its menu-friendly
variant (auto-registers with `Site.menu_items`).

## `fusion_view` — dual-mode function views

The fastest way to expose a small endpoint that answers as **either** a
server-rendered component **or** a data API — no viewset, no mixin.
Wrap a plain function view that returns a plain Python object (dict /
list / ORM values) with `fusion_view`:

```python
from django_fusion.routes.rendering.decorators import fusion_view

@fusion_view(template_name="components/products/list.html")
def product_list(request):
    return {"products": Product.objects.all(), "total": 42}
```

One function, two roads:

| Request | Response |
|---|---|
| render-first (HTML client, `FUSION_RENDER_FIRST=True`, header/session override) | `HttpResponse` — template rendered with `{"data": …, "request": …}` in the context |
| data-API (`X-Fusion-Render-First=false`, JSON client, `force_data_mode=True`) | `{status, message, data: {encoded, data, view_name}}` via `FusionCodec` |

The mode is resolved by the canonical `resolve_render_first` chain
(header override → session preference → per-view default → setting), so
it stays consistent with `Application.respond`, `APISViewMixin`, and
`FusionPageView`. If the wrapped view returns an `HttpResponse` itself
(e.g. a redirect) it is passed through untouched.

Options: `template_name`, `fusion_render_first` (per-view default),
`force_data_mode`, `message` (JSON responses), `context_processors`
(callables `(request) -> dict` merged into the render-first context).
`dual_mode` is a backwards-friendly alias.

**Product pattern** — formint-pro ships `fusion_dual_views.py`: read-only
service payloads (forecast, customer display, kiosk, purchase orders, …)
wrapped in `fusion_view` and mounted at `/fusion/views/*`. Mutating
endpoints stay on their raw JSON views; only the advisory/reporting
surfaces take the dual-mode road. The per-view `fusion_render_first=True`
default makes the component the source of truth, with the data API one
header away (`X-Fusion-Render-First: false`).

`route()` returns a `Route` instance; `menu_path()` is its menu-friendly
variant (auto-registers with `Site.menu_items`).

## `viewprop` — class-level URL descriptor

```python
class PostViewset(ModelViewset):
    model = Post
    namespace = "blog"

    @viewprop
    def url_name(self):
        return f"{self.namespace}:detail"
```

Equivalent to setting `url_name = "blog:detail"` as a string. Prefer
`viewprop` when the value depends on `self`.

## Fragment naming for HTMX

`ViewsetMeta` accepts a dotted `fragment_name`:

```python
class PostViewset(ModelViewset):
    model = Post
    fragment_name = "components.blog.post_list"
```

This makes `{% comp "components.blog.post_list" %}` resolve to the
viewset's list template — handy when mounting the same content via
both a full route and an HTMX fragment.

## Layout decision: where to inherit from

```mermaid
flowchart LR
    A[Need a URL?] -->|yes| B[Neeed a model?]
    A -->|no| Z[Use {% comp %} + include]
    B -->|yes| C[Neeed all CRUD?]
    B -->|no| D[Viewset + route]
    C -->|yes| E[ModelViewset]
    C -->|subset| F[BaseModelViewset + mixins]
    D --> G{Neeed HTMX fragment?}
    G -->|yes| H[RoutableComponent / FragmentComponent]
    G -->|no| I[Viewset]
    E --> J[List+detail+create+update+delete]
    F --> K[picked subset]
    H --> L[Routes via Site]
    I --> L
```

## Cross-references

- [DF-003 Component system](./03-component-system.md) — registry, lifecycle
- [DF-006 Forms & tables](./06-forms-and-tables.md) — patterns for in-page CRUD
- [DF-015 Viewflow mapping](./15-viewflow-mapping.md) — how this compares to
  django-material's `Site`/`Application`/`menu_path`
