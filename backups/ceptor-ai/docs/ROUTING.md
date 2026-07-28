# Routing — Site → Application → Viewset

django-fusion's routing layer (`django_fusion.comp.routes`) was inspired by
[viewflow](https://github.com/viewflow/viewflow)'s declarative URL
configuration. They share the same conceptual hierarchy:

```
Site → Application → Viewset → URLPattern
```

This document records what we found, what we wired up, and how to use it.

---

## Viewflow references

From viewflow docs and code (`viewflow/site.py`, `viewflow/urls.py`):

* **`Site`** — the top-level container. Holds multiple `Application`s and
  provides a `urls` property that returns
  `([urlconf_list], app_name, namespace)`.
* **`Application`** — subclasses `Site`/`Viewset` and represents a logical
  grouping (e.g., *Inventory*, *Blog*). Generates `app_name` automatically
  from the class name unless overridden.
* **`Viewset`** — declarative class-based routing. URL patterns declared as
  class attributes ending in `_path` are auto-collected by the metaclass.
* **URL mounting** — typically done via Django's `include((urlconf, app_name), namespace=...)`.

```python
# viewflow-style example
from viewflow.site import Site, Application
from viewflow.urls import ModelViewset

inventory_app = Application(
    title='Inventory',
    app_name='inventory',
    viewsets=[ModelViewset(model=Product)],
)

site = Site(title='ACME', viewsets=[inventory_app])
# urlpatterns += [path('base/', include((site.urls, site.app_name), namespace=site.namespace))]
```

---

## django-fusion implementation

django-fusion located in `applications/libs/django-fusion/src/django_fusion/comp/routes/`.

### Canonical exports (`__init__.py`)

```python
from django_fusion.comp.routes import (
    # Base
    Viewset, BaseViewset, Route, route, menu_path, IndexViewMixin, viewprop,
    # Models
    ModelViewset, ReadonlyModelViewset,
    ListBulkActionsMixin, CreateViewMixin, UpdateViewMixin, DeleteViewMixin, DetailViewMixin,
    # Hierarchy
    Application, AppMenuMixin, Site,
    # HTMX + component rendering
    RoutableComponent, FragmentComponent,
    # Detection
    FragmentDetector, FragmentDetectionMixin,
)
```

### `Site` and `Application`

* Inherit `IndexViewMixin` (auto redirect from the root to first parameterized URL).
* Hold child viewsets on the `viewsets` attribute (declared as `@viewprop` so
  subclasses can lazily import child classes — avoids circular dependencies).
* `Application.menu_items()` yields `AppMenuMixin` children sorted by
  `menu_order`. `Site.menu_items()` yields registered applications.
* `register(app_class)` instantiates the class, sets `app._parent = self`,
  and appends to `self.viewsets`.

### `Viewset.urls` returns `(list[URLResolver], app_name, namespace)`

```python
@property
def urls(self) -> tuple[list[URLResolver], str | None, str | None]:
    namespace = self.namespace or self.app_name
    if self._urls_cache is None:
        self._urls_cache = self._get_urls()
    pattern = RoutePattern("", is_endpoint=False)
    resolver = _URLResolver(pattern, self._urls_cache, extra=self._get_resolver_extra())
    return [resolver], self.app_name, namespace
```

### `ViewsetMeta` collects `_path` attributes

The metaclass walks `__mro__` and inherits URL patterns from base classes
while letting subclass patterns override. Attributes starting with `get_`
or that are functions are skipped.

---

## RoutableComponent special handling

In `Viewset._get_urls()`:

```python
for viewset in self.viewsets or []:
    if isinstance(viewset, RoutableComponent):
        viewset.__dict__["_parent"] = self
        view = type(viewset).as_view()
        urlpatterns.append(path(viewset.route_path, view, name=...))
        continue
    # Regular Application/Viewset
    if viewset.app_name is None:
        viewset.app_name = camel_case_to_underscore(strip_suffixes(...))
    urlpatterns.append(self._create_url_pattern(route(f"{viewset.app_name}/", viewset)))
```

Two key consequences:

1. **`RoutableComponent` is included FLAT** — its `route_path` is appended
   directly to the parent prefix with no sub-namespace wrapper.
2. **`Application` is wrapped via `route(f"{app_name}/", ...)`** — adds a
   per-app namespace prefix.

---

## ⚠️ route_path convention: **RELATIVE** under an Application

Because `RoutableComponent` is included flat, **and** the parent `Application`
adds the `app_name/` prefix, the `RoutableComponent.route_path` is **relative
to the parent Application's app_name**. Setting it to the absolute path
(including the `app_name/` prefix) causes a duplicate segment that 404s.

### Example: VResume blog app

```python
class BlogListComponent(FragmentComponent):
    route_name = "blog-list"
    route_path = "list/"              # ✅ RELATIVE — produces /fusion/blog/list/
    fragment_name = "blog.fragments.post_list"

class BlogDetailComponent(RoutableComponent):
    route_name = "blog-detail"
    route_path = "<slug:slug>/"       # ✅ RELATIVE — produces /fusion/blog/<slug>/
    fragment_name = "blog.fragments.post_detail"

class BlogApp(Application):
    # app_name auto-generated from class name → "blog"
    class BlogList(AppMenuMixin, BlogListComponent): pass
    class BlogDetail(BlogDetailComponent): pass
    @viewprop
    def viewsets(self):
        return [self.BlogList(), self.BlogDetail()]

class VResumeSite(Site):
    class Blog(BlogApp): pass
    class Portfolio(PortfolioApp): pass

vresume_site = VResumeSite()
vresume_site.register(VResumeSite.Blog)
vresume_site.register(VResumeSite.Portfolio)
```

Mount in `urls.py` (must be **before** i18n catch-all to avoid Wagtail eating
fusion routes):

```python
urlpatterns += [
    path(
        "fusion/",
        include((vresume_site.urls[0], vresume_site.urls[1], vresume_site.urls[2])),
    )
]
```

### Wrong ❌ — duplicates prefix → 404

```python
class BlogListComponent(FragmentComponent):
    route_path = "blog/list/"   # ❌ produces /fusion/blog/blog/list/
```

### Right ✅ — relative sub-path

```python
class BlogListComponent(FragmentComponent):
    route_path = "list/"        # ✅ produces /fusion/blog/list/
```

---

## Class-as-object-arg pattern

The user can pass class references (not just instances) when registering
children, in the spirit of viewflow's typed-object param pattern:

```python
# Class-as-object-arg
vesume_site.register(VResumeSite.Blog)   # passes the class
vesume_site.register(VResumeSite.Portfolio)
```

`Site.register(app_class: type[T])` accepts a class, instantiates it,
wires `_parent`, and adds it to `viewsets`. Children remain idiomatic
Python classes — easier to type-check than passing instances of nested
classes as args.

For dispatching, the metaclass + `@viewprop` combination keeps child
classes lazy — they are only imported / instantiated on first URL
rendering. This avoids circular import problems.

---

## Two-line URL mount

Django-fusion exposes `Site.urls` returning a tuple
`([resolver], app_name, namespace)`. Use Django's standard `include()`:

```python
# Including mounted fusion site (3-tuple form)
include((site.urls[0], site.urls[1], site.urls[2]))
#           ^list       ^app_name    ^namespace
```

This is equivalent to `include((urlconf_list, app_name, namespace))`.

---

## Quick reference

| Django URL element | Fusion equivalent                |
| ------------------ | ------------------------------- |
| `path('foo/', ...)` | Viewset with `_path` attribute  |
| `include('app.urls')` | Site/Application with `.urls[0]` |
| `namespace='foo'` | `viewset.namespace or app_name` |
| `app_name='foo'` | `Application` class — auto-derived from name |
| `URLResolver` | `_URLResolver(pattern, _get_urls(), extra=...)` |
| `urlpatterns` | `Viewset.declared_patterns + viewsets.flat` |

See `applications/libs/django-fusion/src/django_fusion/comp/routes/` for the
full implementation (`base.py`, `components.py`, `sites.py`, `fragments.py`).
