# Routable Applications — Application, AppMenuMixin, IndexViewMixin

> **Related Code**
> * **Domain:** Routing hierarchy
> * **Paths:**
>   * `applications/libs/django-fusion/src/django_fusion/comp/routes/sites.py` (lines 41, 68, 142)
>   * `applications/libs/django-fusion/src/django_fusion/comp/routes/base.py`
> * **Classes:** `Application`, `AppMenuMixin`, `IndexViewMixin`, `Viewset`, `BaseViewset`

An **Application** is a logical grouping (often a domain vertical: `blog`, `portfolio`, `users`) that wires one or more `Viewset`/`RoutableComponent` instances together under a single `app_name`. The django-fusion router passes control to an Application by include()'ing its URL conf at `<site-prefix>/<app_name>/`.

## Application class

```python
class Application(IndexViewMixin, Viewset):
    """IndexViewMixin redirects from /<app>/ to the first parameterized URL
       so visiting the app root always lands the user somewhere useful."""
```

The metaclass `ViewsetMeta` (in `comp/routes/base.py`) walks `__mro__` and collects every class attribute ending in `_path`, deduplicating subclass overrides.

## AppMenuMixin — menu integration

```python
class AppMenuMixin:
    menu_label: str            # Sidebar label rendered in admin nav
    menu_icon: str             # SVG / icon-CSS class
    menu_order: int = 0        # Sort key in nav
    menu_items():              # Yields menu children sorted by menu_order
```

Mix this into any `Viewset` subclass that should appear in the standard admin sidebar. The registered `Site.menu_items()` then walks registered Applications and yields each one's menu entries.

## IndexViewMixin — auto-redirect

When a user visits `/<app>/` with no suffix, `IndexViewMixin` redirects to the first URL pattern that has dynamic parameters (e.g. `/blog/<slug>/`). This avoids 404s on the bare app root.

## Auto app_name derivation

`Application.app_name` defaults to the underscore-cased class name with viewflow-style suffixes stripped:

| Class name                  | Derived app_name     |
|-----------------------------|----------------------|
| `BlogApp`                   | `blog`               |
| `PortfolioApp`              | `portfolio`          |
| `AuthHTMXSocialApp`         | `auth_htmx_social`   |

Setting `app_name = "..."` on the class overrides; the router honors the override verbatim.

## Site-wide autodiscovery (LMS sites)

LMS sites (ctc-research, lms-demo) have `show_all_applications: True` in their dynaconf — every `Application` subclass is auto-discovered. CMS sites (VResume) explicitly register via `VResumeSite.register(VResumeSite.Blog)` to keep the surface curated. See `applications/lms-demo/settings.py` and `applications/VResume/www/pages/routable_components.py` for both patterns side by side.

## See also

* [`docs/architecture/routable_components.md`](routable_components.md) — the layers above Applications.
* [`docs/architecture/routable_site.md`](routable_site.md) — the layers below.
