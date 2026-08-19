# CTC Research — Component Registry & `{% comp %}` Tag

> **Last updated:** 2026-08-18
> **Package:** `libs/django-fusion/src/django_fusion/comp/`
> **Applies to:** Django/Wagtail templates in `projects/precis/precis-ctc/`

CTC’s public marketing and LMS shell is primarily Astro (`frontend/src/components/`).
This guide covers the backend Django/Wagtail component road. For the public Astro
component map, see [CONTENTS.md](CONTENTS.md).

---

## 1. What Is `{% comp %}`?

`{% comp %}` is django-fusion's self-closing component tag. It renders a template by its
**include path** — a dot-path or slash-path that maps to a `.html` file under a registered
template root.

```django
{% comp "partials/logo.html" /%}
```

Unlike `{% include %}`, components are:
- **Self-closing** — no `{% endcomp %}` needed
- **Discoverable** — auto-registered by scanning template directories at startup
- **Aliasable** — the same component can be registered under multiple names
- **Context-aware** — accepts `key=value` args passed into the component's scope

---

## 2. Registry Architecture

```
django_fusion.comp.apps.CoreExtAppConfig.ready()
    │
    ├── _register_builtin_component_paths()
    │   └── globs *.html under configured template roots
    │       └── components.register(IncludePathComponent(path), name=path)
    │
    ├── register_include_path("partials/logo.html")
    │   └── components.register(IncludePathComponent("partials/logo.html"))
    │
    └── register_default_partials()
        └── discover_under_root(<template_dir>)
            └── register_include_paths([...])
```

### 2.1 Key Classes

| Class | Location | Role |
|---|---|---|
| `ComponentRegistry` | `comp/_init.py` | Singleton — stores all registered components |
| `Component` | `comp/_init.py` | Base component class |
| `IncludePathComponent` | `comp/registry.py` | Path-style component — maps a string path to a template file |
| `BoundComponent` | `comp/_init.py` | A component bound to a specific render context |

### 2.2 Key Functions

| Function | File | Purpose |
|---|---|---|
| `register_include_path(path)` | `comp/registry.py` | Register one template path as a component |
| `register_include_paths(paths)` | `comp/registry.py` | Bulk register multiple paths |
| `discover_under_root(root)` | `comp/registry.py` | Glob `*.html` under a directory, register each file |
| `register_default_partials()` | `comp/registry.py` | Discover and register from configured template dirs |
| `components.register(comp, name)` | `comp/_init.py` | Direct component registration |
| `components.register_alias(alias, comp)` | `comp/_init.py` | Add an alias for an existing component |

---

## 3. Template Tag Syntax

### 3.1 Basic Usage

```django
{# Simple component — renders the template at the given include path #}
{% comp "partials/logo.html" /%}

{# With context arguments #}
{% comp "blocks/partials/form_field.html" field_config=field_config block=block /%}

{# Dynamic component name from a context variable #}
{% comp fragment_name /%}
```

### 3.2 Component vs Include

```django
{# DON'T use {% include %} for registered components #}
{% include "partials/logo.html" %}         ← works but bypasses registry

{# DO use {% comp %} — self-closing, discoverable #}
{% comp "partials/logo.html" /%}           ← registered, supports aliases
```

### 3.3 Available Companion Tags

django-fusion's `components` template tag library also provides:

| Tag | Purpose | Example |
|---|---|---|
| `{% comp "path" /%}` | Render a registered component | `{% comp "partials/logo.html" /%}` |
| `{% slot "name" %}` | Define a named slot in a component template | `{% slot "footer" %}...{% endslot %}` |
| `{% prop "name" %}` | Access a prop passed to the component | `{% prop "title" %}` |
| `{% var "name" %}...{% endvar %}` | Define a local variable in scope | `{% var "items" %}...{% endvar %}` |
| `{% css %}` / `{% js %}` | Asset block for CSS/JS | `{% css %}style.css{% endcss %}` |
| `{% block "name" %}...{% endblock %}` | Content block (like Django `{% block %}`) | `{% block "content" %}...{% endblock %}` |

> **Note:** The `components` library must be loaded or registered as a builtin. Precis does
> this via `configs/base/templates.py` which adds `"components"` as a builtin.

---

## 4. Registration Patterns

### 4.1 Auto-Discovery (Default)

When the `django_fusion` app starts, it scans `.html` files under configured template roots
and registers each one as an `IncludePathComponent`. This means ANY `.html` file in a
template directory is automatically usable as `{% comp "path/to/file.html" /%}`.

**Template roots are configured via:**
- Django's `TEMPLATES['DIRS']` setting
- django-fusion's `FUSION_COMPONENT_ROOTS` setting
- `APP_DIRS: True` — any app's `templates/` directory

### 4.2 Explicit Registration

```python
# In an app's ready() or in settings
from django_fusion.comp.registry import register_include_path, register_include_paths

register_include_path("partials/logo.html")
register_include_path("plugins/certifications/certificate.html")

# Bulk
register_include_paths([
    "partials/logo.html",
    "partials/meta.html",
    "partials/header_links.html",
    "plugins/base/loader.html",
    "components/cookies/cookie-consent.html",
])
```

### 4.3 Inclusion Tag Registration

Components can also be registered via Django's `@register.inclusion_tag()` decorator:

```python
# django_fusion/comp/templatetags/components/table.py
from django_fusion.comp.templatetags.components import register

@register.inclusion_tag("fusion/components/table.html", takes_context=False)
def fusion_table(rows, columns, **kwargs):
    return {"rows": rows, "columns": columns}
```

This registers `fusion_table` as BOTH a template tag AND a comp-style component.

### 4.4 Alias Registration

The same component can have multiple names:

```python
from django_fusion.comp._init import components

component = components.get("partials/logo.html")
components.register_alias("logo", component)       # Now {% comp "logo" /%} works
components.register_alias("header-logo", component) # {% comp "header-logo" /%}
```

---

## 5. Usage by Project

The examples below describe the shared django-fusion registry. CTC uses the same
registry for backend-rendered fragments and Wagtail/admin surfaces; it does not
turn Astro components into Django `{% comp %}` templates.

### 5.1 Precis LMS — Heavy `{% comp %}` User

Precis uses `{% comp %}` pervasively across all layouts. Components are referenced by
their include path:

```django
{# Landing header #}
{% comp "partials/logo.html" /%}
{% comp "partials/header_links.html" /%}
{% comp "partials/header_extra.html" /%}

{# Learning header #}
{% comp "learning/header/learning.html" /%}

{# Cookie consent #}
{% comp "components/cookies/cookie-consent.html" /%}
{% comp "components/cookies/cookie-policy.html" /%}
{% comp "components/cookies/privacy-policy.html" /%}

{# Dynamic component from context #}
{% comp fragment_name /%}

{# With arguments #}
{% comp "blocks/partials/form_field.html" field_config=field_config block=block /%}
```

**Note:** Precis templates are duplicated across layout directories (landing, learning,
auth, profile, apps) — e.g., `partials/logo.html` exists in multiple locations. The
`{% comp %}` tag resolves through the registry, not the filesystem, so only the
registered name matters.

### 5.2 Landing-Fusion — Uses `{% include %}` Instead

Landing-fusion does NOT use `{% comp %}`. Its `base.html` uses traditional `{% include %}`:

```django
{% include "pages/partials/skeleton.html" %}
{% include "pages/partials/header.html" %}
{% include "pages/partials/footer.html" %}
```

This works because precis-landing is a simpler project — one layout, fewer templates.
The `{% comp %}` system is available (django_fusion is in INSTALLED_APPS) but not
exercised. If the template surface grows, migrating to `{% comp %}` would make components
discoverable and aliasable.

### 5.3 Formints — No Django Templates in Desktop App

Formints' desktop app (Community/Standard editions) is entirely Astro + React — no Django
templates. The optional sidecar admin uses django-unfold's template system, which doesn't
use `{% comp %}`. The comp system is available if the sidecar's admin pages grow.

---

## 6. Component Resolution Order

When `{% comp "name" /%}` is called, django-fusion resolves by:

```
1. Exact name match in component registry  ← "partials/logo.html"
2. Alias match                              ← "logo" → partials/logo.html
3. IncludePathComponent                     ← loads template path verbatim
4. Fallback to include-like behavior        ← treats name as template path
```

---

## 7. Settings Template Library Registration

Projects register the `components` library as a builtin so `{% comp %}` is available in
ALL templates without `{% load components %}`:

```python
# In settings.py TEMPLATES['OPTIONS']
"builtins": [
    "django_fusion.comp.templatetags.components",
],
# or
"libraries": {
    "components": "django_fusion.comp.templatetags.components",
},
```

Precis uses this pattern (from `configs/base/templates.py`). Landing-fusion registers
it via `libraries` (not builtins) — so templates need `{% load components %}`.

---

## 8. Adding a New Component

1. **Create the template file** anywhere under a registered template root:
   ```
   assets/templates/components/my_banner.html
   ```

2. **Use it immediately** — auto-discovery picks it up:
   ```django
   {% comp "components/my_banner.html" /%}
   ```

3. **Optionally register an alias** in your app's `ready()`:
   ```python
   from django_fusion.comp.registry import register_include_path
   register_include_path("banner")  # Now {% comp "banner" /%} works
   ```

4. **Pass context** as keyword arguments:
   ```django
   {% comp "banner" title="Welcome" variant="hero" /%}
   ```

---

## 9. Related Files

| File | Role |
|---|---|
| `libs/django-fusion/src/django_fusion/comp/_init.py` | Component, ComponentRegistry, BoundComponent classes |
| `libs/django-fusion/src/django_fusion/comp/registry.py` | `register_include_path`, `discover_under_root`, auto-discovery |
| `libs/django-fusion/src/django_fusion/comp/apps.py` | `CoreExtAppConfig.ready()` — kicks off registration |
| `libs/django-fusion/src/django_fusion/comp/templatetags/components/__init__.py` | Template tag library — `comp`, `slot`, `prop`, `var`, `block` |
| `projects/precis/precis-main/assets/templates/` | Primary comp user — all layout skeletons + components |
| `projects/configs/base/templates.py` | Template config that registers `components` as builtin |

## 10. Public page-component compatibility route

The legacy public page paths below are routed through the same Wagtail-backed
fragment contract as the Astro shell:

```text
/components/lms/pages/<slug>/
→ /fragment/pages/<slug>/ behavior
```

This compatibility road is intentionally registered before the generic
`django-fusion` component resolver. It prevents the generic full-page fallback
from returning a server error when a deployment does not have the legacy
layout context, while preserving the existing staff-only restrictions on the
LMS dashboard and HTMX-only course/blog fragments.

The canonical public endpoint remains:

```text
GET /fragment/pages/<slug>/
```

## Remarks & Notes

- Production probing on 2026-08-18 found `/components/lms/pages/home/`, `/about/`, `/team/`, `/services/`, `/faq/`, and `/contact/` returning HTTP 500, while `/components/lms/pages/privacy/` returned HTTP 200. The compatibility route addresses the public static-page subset; deployment is required before rechecking production.
- `/components/lms/courses/list-fragment/` remains HTMX-only and correctly returns HTTP 403 without an authenticated/HTMX request; `/components/lms/dashboard/` remains staff-only.
- If production reports HTTP 503 rather than the observed HTTP 500, inspect the backend container health and Traefik service state separately; the route-level behavior must be rechecked after the backend rollout.
