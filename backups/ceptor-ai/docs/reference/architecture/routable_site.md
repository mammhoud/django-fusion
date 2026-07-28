# Routable Site — Site registration, URL mount, lazy instantiation

> **Related Code**
> * **Domain:** Routing hierarchy
> * **Paths:**
>   * `applications/libs/django-fusion/src/django_fusion/comp/routes/sites.py` (line 142 `class Site(IndexViewMixin, Viewset)`)
>   * `applications/libs/django-fusion/src/django_fusion/comp/routes/base.py` (`Viewset.urls` returns the 3-tuple)
>   * `applications/VResume/www/pages/routable_components.py`
>   * `applications/VResume/www/projects/urls.py`
> * **Classes:** `Site`, `IndexViewMixin`, `viewprop`

A **Site** is the top-level container — it holds multiple `Application`s and exposes a single `urls` property that Django's `include()` can consume.

## Site class

```python
class Site(IndexViewMixin, Viewset):
    title: str                                # Display name in admin / docs
    namespace: str                            # URL namespace, defaults to app_name
    viewsets: list[Viewset]                   # Children: Applications + RoutableComponents
```

`Site.menu_items()` yields registered Applications (so the admin sidebar can render a global nav from them).

## Two-line URL mount

The router exposes `Site.urls` as a 3-tuple that supports Django's standard `include()` form:

```python
# applications/<site>/www/projects/urls.py
from django.urls import path, include
from pages.routable_components import vresume_site

urlpatterns += [
    path(
        "@app/",                                # local prefix; "fusion/" historically
        include((vresume_site.urls[0], vresume_site.urls[1], vresume_site.urls[2])),
    ),
]
```

`@app/` is the modern mount point (was `fusion/` before 2026-07 refactor). Both URLs resolve to the same routable components; existing inbound `/fusion/...` links 301 to `/@app/...`.

## Class-as-object-arg + @viewprop — lazy instantiation

```python
class VResumeSite(Site):
    class Blog(BlogApp): pass
    class Portfolio(PortfolioApp): pass

    @viewprop                                # deferred — class is only imported on first render
    def viewsets(self):
        return [self.Blog(), self.Portfolio()]

vresume_site = VResumeSite()
vresume_site.register(VResumeSite.Blog)                # class-as-object-arg
vresume_site.register(VResumeSite.Portfolio)
```

`@viewprop` is critical — it lets child `Application` classes reference each other without circular-import errors, because the property is only evaluated after both sides of the import graph have loaded.

## MNU checklist for adding a new Site

1. Create `applications/<site>/www/pages/routable_components.py` with `<Site>Site(Site)` per the example.
2. Add a `urlpatterns += [path('@app/', include(...))]` line in `applications/<site>/www/projects/urls.py`, **before** the i18n catch-all so Wagtail doesn't eat `@app/...` requests.
3. Add `<site>/settings.py:WEBSITE_PREFIX = '@app/'`.
4. Add docs entry under [`docs/websites/<site>/index.md`](../../websites) — walk through the per-site conventions.

## See also

* [`docs/architecture/routable_components.md`](routable_components.md) — `RoutableComponent` + `FragmentComponent` (top of the stack).
* [`docs/architecture/routable_applications.md`](routable_applications.md) — `Application` + `AppMenuMixin` (middle).
* [`docs/ROUTING.md`](../../ROUTING.md) — full hierarchy + viewflow origins.
