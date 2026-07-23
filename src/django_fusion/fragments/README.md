# django_fusion.fragments

URL-driven fragment rendering for Django, HTMX, and Server-Sent Events (SSE).

`django_fusion.fragments` lets you request any template fragment (or any
registered `FragmentComponent`) over HTTP using a dotted name such as
`components.home.hero`. `FragmentComponent` subclasses register themselves
automatically. The same endpoint supports three request styles:

* **URL path:** `/fragments/<dotted.name>/`
* **Query parameter:** `/fragments/?q=<dotted.name>`
* **SSE:** request with `Accept: text/event-stream`

## Wiring into ROOT_URLCONF

Include `django_fusion.fragments.urls` under any path you like. The examples
below mount it at `/fragments/`:

```python
# myproject/urls.py
from django.urls import path, include

urlpatterns = [
    path("fragments/", include("django_fusion.fragments.urls")),
    # ... your other URL patterns
]
```

```python
# tests/urls.py (minimal example)
from django.urls import include, path

urlpatterns = [
    path("fragments/", include("django_fusion.fragments.urls")),
]
```

The fragments package itself does not require a separate `INSTALLED_APPS`
entry, but `django_fusion` must be in `INSTALLED_APPS` for the shared
templates (`django_fusion/templates/`) to be discovered through Django's
app-directories loader. If you override the templates in your own project,
ensure those template directories are listed in your `TEMPLATES` setting.

## Template lookup rules

A dotted fragment name is mapped to a template path by replacing dots with
slashes and appending `.html`:

```
components.home.hero  ->  components/home/hero.html
```

Make sure the template is discoverable through Django's `TEMPLATES` setting.

## Requesting a fragment via URL path

Send a `GET` to `/fragments/<dotted.name>/`:

```bash
curl http://localhost:8000/fragments/components.home.hero/
```

Response: the rendered fragment as `text/html` (HTTP 200).

If the request comes from HTMX (it carries `HX-Request: true`), the response
includes the header `HX-Reswap: innerHTML`. For Unpoly-compatible fragment
requests, the response includes `X-Up-Target: #<fragment-name-with-hyphens>`.

## Requesting a fragment via query parameter

Send a `GET` to `/fragments/?q=<dotted.name>`:

```bash
curl "http://localhost:8000/fragments/?q=components.home.sections.hero"
```

This is useful when the dotted name is generated client-side or when you want
a single endpoint URL.

If both the path and the query parameter are provided, the path takes
precedence.

## Requesting a fragment via Server-Sent Events (SSE)

Send a `GET` with `Accept: text/event-stream`:

```bash
curl -H "Accept: text/event-stream" \
     http://localhost:8000/fragments/components.home.hero/
```

The response is a `text/event-stream` with a single `fragment` event:

```text
event: fragment
data: <h1>Hello</h1>

```

This is compatible with the HTMX SSE extension (`sse-ext`), which can listen
for the `fragment` event and swap the payload into a target element.

### Minimal HTMX SSE example

```html
<div hx-ext="sse" sse-connect="/fragments/components.home.hero/" sse-swap="fragment">
  Loading…
</div>
```

## Python API

You can also render fragments programmatically:

```python
from django_fusion.fragments import FragmentRequestRenderer

renderer = FragmentRequestRenderer(request)
response = renderer.render("components.home.hero", context={"title": "Hello"})
```

## Component-aware fragments

If you define a `FragmentComponent` with a `fragment_name`, it registers
automatically and the endpoint routes to that component instead of a plain
template.

```python
from django_fusion.routes.fragments import FragmentComponent

class HeroComponent(FragmentComponent):
    fragment_name = "components.home.hero"
    template_name = "components/home/hero.html"

    def get_fragment_context(self, **kwargs):
        return {"title": "Welcome"}
```

No manual registration is required. `GET /fragments/components.home.hero/`
renders the component.

## Page context for fragments

Fragments often need the same context as the page that hosts them (e.g. a
Wagtail page, the current user, or site settings). The fragment view resolves
page context from the originating URL and merges it into the fragment context.

The view looks for the host page URL in this order:

1. `HX-Current-URL` request header (sent automatically by HTMX)
2. `page_path` query parameter
3. `page_url` query parameter

Example: a fragment on the home page receives the same context as the home page.

```bash
# HTMX automatically sends HX-Current-URL
curl -H "HX-Request: true" \
     -H "HX-Current-URL: http://localhost:8000/" \
     http://localhost:8000/fragments/components.home.hero/

# Or pass the host page explicitly
curl "http://localhost:8000/fragments/?q=components.home.hero&page_path=/"
```

For Wagtail pages, ``page.get_context(request)`` is merged. For regular
Django class-based views, ``get_context_data()`` is merged.

## Examples

### Application with a landing layout

```python
from django_fusion.routes.sites import Application, Site
from django_fusion.routes.components import RoutableComponent

class HomeComponent(RoutableComponent):
    route_name = "home"
    route_path = ""
    fragment_name = "myapp.home.hero"
    template_name = "django_fusion/layouts/landing.html"

class MyApp(Application):
    title = "My App"
    base_template_name = "django_fusion/layouts/landing.html"

class MySite(Site):
    title = "My Site"
    name = "my_site"

site = MySite()
site.register(MyApp)
```

### Fragment component used on multiple pages

```python
from django_fusion.routes.fragments import FragmentComponent

class HeroFragment(FragmentComponent):
    fragment_name = "myapp.home.hero"
    template_name = "myapp/fragments/hero.html"

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        # context now contains the host page's Wagtail/Django context.
        # For example, a Wagtail page might provide "page" and "self":
        page = context.get("page")
        if page:
            context["hero_title"] = page.title
        return context
```

Because the fragment view merges page context automatically, `HeroFragment`
can be embedded on the home page, a blog page, or any other page and still
receive the host page's context.

### RoutableComponent full-page context

A ``RoutableComponent`` can also expose context that fragments on the same
page will receive via ``get_context_data``::

```python
from django_fusion.routes.components import RoutableComponent

class HomePage(RoutableComponent):
    route_name = "home"
    route_path = ""
    template_name = "myapp/pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_name"] = "My Site"
        return context
```

A fragment requested from this page will see ``site_name`` in its context.

## Error responses

* **400 Bad Request** — returned when the fragment name is missing or contains
  invalid characters (only letters, digits, underscores, hyphens, and dots are
  allowed).
* **400 Bad Request** — returned when the resolved template cannot be found.
