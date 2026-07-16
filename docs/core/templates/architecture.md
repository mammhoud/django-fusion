# Template Architecture

Templates are layered across shared and site-specific directories.

## Search order

Django resolves templates in this order:

1. `core/<site>/templates/`
2. `core/<site>/assets/templates/`
3. `core/assets/templates/`
4. `core/<site>/www/**/templates/`
5. Installed app templates (Wagtail, allauth, etc.)

## Base templates

### `core/assets/templates/base.html`

Root layout. Includes:
- `layout/meta.html`
- Cookie consent components
- Header / footer
- Main content block

### `core/assets/templates/ui/base_auth.html`

Auth layout that wraps a fragment based on `fragment_name`.

### `core/assets/templates/ui/base_page.html`

Standalone page base for full-page views.

## Include hierarchy

```
base.html
├── layout/meta.html
├── components/cookies/cookie-consent.html
├── components/cookies/cookie-policy.html
├── components/cookies/privacy-policy.html
├── [site header]
└── [active_tab]/fragment.html
     └── [active_tab]/sections/*.html
```

## Fragment naming convention

Use `fragment_name` only for fragment identifiers and context keys.

```python
class HomePage(Page):
    fragment_name = "home.main"
```

Dotted names map to `components/` paths:

```text
home.main → components/home/main.html
profile.blog → components/profile/blog.html
```

## HTMX request flow

### Full-page load

```
GET /pages/about/
  └─ is_htmx=False → render("skeleton.html")
       └─ extends base.html
            └─ includes about/fragment.html
                 └─ includes about/sections/*.html
```

### HTMX tab switch

```
hx-get="/pages/about/"
  └─ is_htmx=True → render("about/fragment.html")
       └─ <article class="about">...</article>
```

## Template naming conventions

| Pattern | Purpose |
|---|---|
| `<section>/fragment.html` | HTMX partial for tab switches |
| `<section>/main.html` | Full-page wrapper |
| `<section>/sections/<name>.html` | Sub-section included by fragment |
| `<section>/modals/<name>.html` | Modal content loaded via HTMX |
| `connect/emails/<name>.html` | Transactional email bodies |
| `connect/blocks/<name>.html` | Wagtail StreamField block renderers |

## Customization guide

### Override a shared template

Create a file with the same relative path in the site templates directory:

```
core/ctc-research/templates/base.html  # overrides core/assets/templates/base.html
```

### Add a new fragment

1. Create `core/<site>/templates/myapp/fragment.html`.
2. Create `core/<site>/templates/myapp/sections/*.html`.
3. Set `fragment_name = "myapp.fragment"` in the view or page model.

### Register include paths

In `AppConfig.ready()`:

```python
from django_fusion.comp import register_include_path

class MyAppConfig(AppConfig):
    def ready(self):
        register_include_path("myapp/components")
```

Or use the setting:

```python
COMPONENTS_INCLUDE_PATH_ROOTS = [
    "core/assets/templates",
]
```
