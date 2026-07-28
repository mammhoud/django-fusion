# Routable Components — RoutableComponent / FragmentComponent

> **Related Code**
> * **Domain:** Routing hierarchy
> * **Paths:**
>   * `applications/libs/django-fusion/src/django_fusion/comp/routes/components.py`
>   * `applications/libs/django-fusion/src/django_fusion/comp/routes/fragments.py`
>   * `applications/libs/django-fusion/src/django_fusion/comp/routes/base.py`
>   * `applications/VResume/www/pages/routable_components.py`
> * **Classes:** `RoutableComponent`, `FragmentComponent`, `ComponentViews`

The **routable component** layer attaches Django URL routing directly to a component-style view. A single `RoutableComponent` subclass combines:

* a `template_name` (or `fragment_name`) — what to render
* a `route_path` — where to mount it in the URL tree
* the surrounding view logic (breadcrumbs, permissions, breadcrumbs)

A **fragment component** is a RoutableComponent whose render result is meant to be swapped into another page via HTMX / Unpoly rather than rendered standalone.

## When to use each

| You want...                                 | Use                                |
|---------------------------------------------|--------------------------------------|
| full-page response to a URL                 | `RoutableComponent`                 |
| HTMX fragment for a sidebar / panel swap    | `FragmentComponent`                 |
| model-driven CRUD over a model              | `BaseModelViewset` (see applications doc) |
| static Markdown rendered from disk          | `Viewset` (`comp.routes.base`)      |

## Mounting onto a Site

```python
from django_fusion.comp.routes import Application, Application, FragmentComponent
from django_fusion.comp.routes import Viewset, viewprop

class BlogApp(Application):
    class BlogList(FragmentComponent):
        route_path = "list/"            # RELATIVE — produces /fusion/blog/list/
        fragment_name = "blog.fragments.post_list"

    class BlogDetail(RoutableComponent):
        route_path = "<slug:slug>/"
        fragment_name = "blog.fragments.post_detail"

    @viewprop
    def viewsets(self):
        return [self.BlogList(), self.BlogDetail()]
```

The `route_path` is **relative** to the parent `Application`'s `app_name/` prefix (auto-derived from the class name). Setting `route_path = "blog/list/"` instead of `"list/"` causes a duplicate-prefix 404.

## Fragment detection

`FragmentComponent` uses `FragmentDetector` (see `routes/detection.py`) to recognize HTMX-style requests (`HX-Request: true` header) and strip the surrounding page chrome. See `applications/VResume/www/pages/routable_components.py` for a real consumer.

## See also

* [`docs/architecture/routable_applications.md`](routable_applications.md) — `Application`, `AppMenuMixin`, menus.
* [`docs/architecture/routable_site.md`](routable_site.md) — `Site` registration + URL mounting.
* [`docs/ROUTING.md`](../../ROUTING.md) — full viewflow-style Site→Application→Viewset hierarchy.
