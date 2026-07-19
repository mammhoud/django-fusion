# Getting Started — DF-001

> Source of truth: `pyproject.toml`, `src/django_fusion/__init__.py`,
> `src/django_fusion/comp/`, `QUICKSTART.md`, `src/django_fusion/infrastructure/`.

**Time:** ≈10 minutes.

## Install

### Standalone project

```bash
pip install django-fusion
```

### Local editable / development

```bash
git clone https://github.com/mammhoud/django-fusion.git
cd django-fusion
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
```

> Remark: `requires-python = ">=3.11"` per `pyproject.toml`. Python 3.10
> works in practice for most calls, but the type annotations in some
> `projects/*` modules assume 3.11+ syntax.

### Structa Cloud monorepo (submodule)

```bash
pip install -e projects/libs/django-fusion
```

## Add to `INSTALLED_APPS`

`src/django_fusion/__init__.py` lists the top-level modules. Add the
ones you actually use:

```python
# settings.py
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # django-fusion — required
    "django_fusion.comp",            # Component system
    "django_fusion.core",            # Handlers, managers, services, cache
    "django_fusion.config",          # Dynaconf loader
    "django_fusion.infrastructure",  # Management commands, scripts, locale
    "django_fusion.site",            # Auth mixins, context processors
    "django_fusion.web",             # Allauth adapters, view mixins

    # django-fusion — optional, only when used
    "django_fusion.health",          # /health/ endpoints
    "django_fusion.analyzer",        # {% comp %} usage scanner
    "django_fusion.wagtail",         # Wagtail integration (only if Wagtail)
    "django_fusion.contrib",         # Admin, cache utils, privacy
]
```

> Remark: see DF-007 for the full per-app purpose table and the optional
> `wagtail` dependency.

## Register the `{% comp %}` template tag globally

By registering `django_fusion.comp.templatetags.components` in `builtins`,
you avoid having to write `{% load components %}` in every template:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "builtins": [
                "django_fusion.comp.templatetags.components",
            ],
        },
    },
]
```

> Remark: `APP_DIRS: True` lets Django auto-discover `<app>/templates/`.
> If you skip it, you must add your component directories to `DIRS` or
> register them with `register_include_paths()` in an `AppConfig.ready()`
> hook (see DF-003).

## Wire health checks (optional but recommended)

```python
# urls.py
from django_fusion.health.urls import health_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", include((health_urlpatterns, "health"))),
]
```

`/health/`, `/health/db/`, and `/health/assets/` each return JSON
(see DF-009).

## Your first component

### Component template

```django
{# myapp/templates/components/button.html #}
{% load components %}
{% prop label %}
{% prop variant="primary" %}
{% prop disabled=False %}

<button class="btn btn--{{ props.variant }} {{ attrs }}"
        {% if props.disabled %}disabled{% endif %}>
  {{ props.label }}
</button>
```

### Use it from any template

```django
{% comp "components/button.html" label="Save" variant="primary" / %}

{% comp "components/button.html" label="Cancel" variant="outline-primary" / %}
```

### Use it from a Python view

The Python-side API is invocable from `comp.templatetags` and from
`web.rendering.TemplateRenderer` (see COMPONENT_CASE_STUDIES.md
*Python Entry Points* section). For a simple view:

```python
# myapp/views.py
from django.shortcuts import render

def landing(request):
    return render(request, "landing.html", {
        "request": request,  # ensure context_processors see request
    })
```

The full Python-rendering path lives in `src/django_fusion/web` and
`src/django_fusion/comp/templatetags/`.

## Bump to a routable component

When a component needs its own URL (for an HTMX fragment, a modal body,
or a full page), inherit from `RoutableComponent`:

```python
# myapp/components.py
from django_fusion.comp.routes import RoutableComponent

class PricingRows(RoutableComponent):
    route_name = "pricing_rows"
    route_path = "pricing/rows/"
    template_name = "pricing/rows.html"
    fragment_name = "components.pricing_rows"   # dotted HTMX identity
```

Register via an `Application` and a `Site`:

```python
# myapp/urls.py
from django_fusion.comp.routes import Site, Application

pricing_app = Application(
    title="Pricing",
    icon="bi-currency-dollar",
    components=[PricingRows],
)

site = Site(title="My App", apps=[pricing_app])

urlpatterns = [path("", site.urls)]
```

See DF-005 for the full routing reference.

## What to read next

- [DF-002 — Architecture](./02-architecture.md) — module map + request flow
- [DF-003 — Component System](./03-component-system.md) — registry, fragments, lifecycle
- [DF-004 — `{% comp %}` template tag](./04-component-tag.md) — props/slots/vars/attrs
- [DF-005 — Routing](./05-routing.md) — `Site`, `Application`, `Viewset`, fragments
