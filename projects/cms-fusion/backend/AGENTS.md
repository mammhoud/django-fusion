# cms-fusion — AI Agent Instructions

Path: `projects/cms-fusion/backend/`

## Overview

cms-fusion is a self-contained Fusion project. Templates, static assets,
fixtures, and locale files should live inside this project unless they are
genuinely shared across sites or part of the `django-fusion` framework.

## Directory Structure

```
cms-fusion/backend/
├── apps/                          # All Django application code
│   ├── core/                      # Shared core: handlers, content, services, models, api, schemas
│   │   ├── handlers/              # Shared handlers (services, views, forms, models, signals, filters)
│   │   ├── content/               # Content models, search, tasks, Wagtail hooks
│   │   ├── api/                   # Shared REST API endpoints (bolt_apis, fusion_health, data_adapter)
│   │   ├── schemas/               # Shared schema definitions (core, apps, site_settings)
│   │   ├── urls.py                # Cart & checkout endpoints
│   │   ├── handlers/urls.py       # Privacy & Terms endpoints
│   │   └── routes.py              # Routable component site configuration
│   └── pages/                     # Domain-specific apps (one per feature module)
│       ├── blog/                  # Blog app (models, views, API, components)
│       ├── lms/                   # LMS app (courses, enrollment, learning)
│       ├── profile/               # User profile app (settings, dashboard, notes)
│       ├── products/              # Products & cart app
│       ├── accounts/              # Authentication & registration app
│       ├── branding/              # Branding & customization app
│       ├── pages/                 # Wagtail page types (home, about, contact, team, services)
│       ├── components/            # Shared component templates
│       ├── templatetags/          # Shared template tags
│       └── urls.py                # Root URL aggregator for all apps
├── templates/                     # Site-root entry templates + project-wide overrides
├── www/                           # Project entry point (urls.py + __init__.py only)
├── settings.py                    # Site-local Django settings
├── server.py                      # ASGI/WSGI application
└── manage.py                      # Django management CLI
```

## Template Resolution Order

Django resolves templates in this order (highest priority first):

1. `cms-fusion/backend/templates/` — site-root entry templates and project-wide overrides
2. `cms-fusion/backend/apps/pages/<app>/templates/` — app-owned templates
3. `cms-fusion/backend/apps/core/**/templates/` — core app templates
4. `cms-fusion/assets/templates/` — project asset templates
5. `libs/django-fusion/src/django_fusion/templates/` — django-fusion framework templates
6. `projects/assets/templates/` — legacy monorepo shared templates (for non-fusion sites only)

## Asset / Static Resolution Order

Django static and media files resolve in this order (highest priority first):

1. `cms-fusion/assets/static/` — project-specific compiled static files
2. `cms-fusion/assets/media/` — project-specific uploaded media
3. `libs/django-fusion/src/django_fusion/static/` — django-fusion framework static
4. `projects/assets/static/` — legacy monorepo shared static (for non-fusion sites only)

Source design assets (SCSS, logos, fonts, images) live in the project root
`cms-fusion/assets/` and are compiled/copied into the locations above for
both Next.js and Django consumption.

## URL Structure

```
/                              → apps.pages.urls (namespace: "plugins")
/accounts/                     → apps.pages.accounts.urls (namespace: "accounts")
/profile/                      → apps.pages.profile.urls (namespace: "profile")
/learning/                     → apps.pages.lms.urls (namespace: "lms")
/cart/                         → apps.core.urls (namespace: "cart")
/legal/                        → apps.core.handlers.urls (namespace: "legal")
/api/                          → apps.core.api.urls (namespace: "api")
/admin/                        → Wagtail admin
/django-admin/                 → Django admin
/osoul/                        → Routable component site
```

## Import Conventions

Use canonical import paths from the new structure:

| Old Path | New Path |
|----------|----------|
| `plugins.blog.*` | `apps.pages.blog.*` |
| `plugins.lms.*` | `apps.pages.lms.*` |
| `plugins.profile.*` | `apps.pages.profile.*` |
| `plugins.products.*` | `apps.pages.products.*` |
| `plugins.accounts.*` | `apps.pages.accounts.*` |
| `plugins.branding.*` | `apps.pages.branding.*` |
| `plugins.pages.*` | `apps.pages.pages.*` |
| `www.core.*` | `apps.core.*` |
| `www.apps.*` | `apps.core.*` |
| `www.api.*` | `apps.core.api.*` |
| `www.schemas.*` | `apps.core.schemas.*` |
| `www.worker.*` | `tools.worker.*` |

## Fragment Components

django-fusion `FragmentComponent` / `RoutableComponent` subclasses live in
each app's `components.py`:

- `apps/pages/lms/components.py` — `StaticPageFragment`, `CourseListFragment`
- `apps/pages/blog/components.py` — `BlogPostListFragment`, `BlogPostCreateFragment`
- `apps/pages/profile/views/` — Profile fragments (dashboard, settings, courses, etc.)

API endpoints that need fragment pointers use `data_adapter.fusion_response()`:
```python
from apps.core.api.data_adapter import bolt_view, fusion_response
```

## Current Template Tree

```
cms-fusion/backend/templates/
├── base.html               # Project base layout (extends django-fusion base)
├── base_page.html          # Page layout wrapper
├── index.html              # Home / entry point template
├── errors/                 # Site-wide error pages
├── events/                 # Event page templates (site-root)
├── wagtailadmin/           # Wagtail admin overrides (site-root)
└── AGENTS.md               # This file
```

> **App-specific templates** belong in `apps/pages/<app>/templates/`.
> Only site-root entry templates, error pages, event pages, Wagtail admin
> overrides, and project-wide overrides belong in `backend/templates/`.

## Template Organization

```
cms-fusion/backend/
├── templates/                             # Site-root entry + project-wide overrides
│   ├── base.html
│   ├── base_page.html
│   ├── index.html
│   ├── errors/
│   ├── events/
│   └── wagtailadmin/
├── apps/pages/<app>/templates/            # App-owned templates
│   ├── accounts/auth/
│   ├── accounts/account/
│   ├── accounts/registration/
│   ├── blog/
│   ├── lms/learning/
│   ├── lms/courses/
│   ├── lms/certification/
│   ├── pages/about/
│   ├── pages/contact/
│   ├── pages/home/
│   ├── pages/services/
│   ├── pages/team/
│   └── products/
└── apps/core/**/templates/                # Core app templates
```

## Asset Tree

```
cms-fusion/
└── assets/                       # Unified project assets (design source + runtime output)
    ├── styles/                   # SCSS source files, design tokens, theme
    ├── static/                   # Compiled CSS, JS, images for Django collectstatic
    ├── templates/                # Project-specific template includes
    ├── media/                    # Uploaded media (runtime)
    ├── fixtures/                 # Project fixtures
    ├── locale/                   # Project .po/.mo files
    ├── emails/                   # Email templates
    ├── branding/                 # Logos, favicons, brand assets
    ├── fonts/                    # Project-specific web fonts
    └── Makefile
```

## Shared Design Source (SCSS, Logos, Branding)

Keep a single source of truth for the visual design system under
`cms-fusion/assets/`:

- `assets/styles/fusion-theme.scss` — theme tokens and CSS custom properties.
- `assets/branding/logo.svg` — project logo used by both Django and Next.js.
- `assets/branding/favicon.ico` — favicon.

Build/compile steps:
- Next.js imports the SCSS in `frontend/src/app/globals.css` or `_app.tsx`
  (add `sass` dependency if needed).
- Django consumes the compiled CSS from `assets/static/css/fusion.css`
  or references CSS custom properties in templates.
- Logos are copied/symlinked to `frontend/public/branding/` and
  `assets/static/branding/` during the build.

## Site-Wide CSS Variables

Use CSS custom properties so Django templates and Next.js components share the
same color/type scale without recompiling per app.
The color values are driven by `FUSION_PRIMARY_COLOR` and
`FUSION_SECONDARY_COLOR` in `settings.py`:

```python
# settings.py
FUSION_PRIMARY_COLOR = "#7c3aed"
FUSION_SECONDARY_COLOR = "#5b21b6"
```

`assets/styles/fusion-theme.scss` should output these as CSS custom properties:

```css
:root {
  --fu-primary: var(--fu-primary, #7c3aed);
  --fu-secondary: var(--fu-secondary, #5b21b6);
  --fu-bg: #fafafa;
  --fu-text: #18181b;
}
```

The compiled CSS is emitted to `assets/static/css/fusion.css` and
referenced by the Django base template. Next.js imports the same SCSS source in
its root layout, so both apps share the same tokens.

## Customization Hooks

Use these hooks instead of editing `django-fusion` or `projects/assets/`:

### Layouts

```python
# settings.py
FUSION_LAYOUTS = {
    "default": "fusion/layouts/default.html",
    "full_width": "fusion/layouts/full_width.html",
    "sidebar": "fusion/layouts/sidebar.html",
    "blank": "fusion/layouts/blank.html",
}
FUSION_DEFAULT_LAYOUT = "default"
```

Override a layout by placing a template at the same path under
`cms-fusion/backend/templates/`.

### Features

```python
FUSION_FEATURES = {
    "blog": True,
    "courses": True,
    "products": True,
    "pages": True,
    "auth": True,
    "profile": True,
    "branding": True,
    "search": True,
}
```

### Component registry

Register or override components in `AppConfig.ready()`:

```python
from django_fusion.comp.registry import component_registry

class MyAppConfig(AppConfig):
    name = "apps.pages.my_app"

    def ready(self):
        component_registry.register("my_app.hero", "path/to/hero.html")
```

### Fragment rendering

Set `fragment_name` on `RoutableComponent` / `FragmentComponent` subclasses:

```python
from django_fusion.routes import RoutableComponent

class MyPage(RoutableComponent):
    fragment_name = "pages.my_page"
    fusion_render_first = True
```

## Rules for Agents

1. **Keep it local** — new templates and static files go in this project,
   not in `projects/assets/`.
2. **App first** — app-specific templates belong in `apps/pages/<app>/templates/`,
   not `backend/templates/`.
3. **Site root is for overrides** — only entry templates and project-wide
   overrides live in `backend/templates/`.
4. **Source assets at project root** — all project assets (design source, compiled
   static, templates, fixtures, locale, media) live in the unified `cms-fusion/assets/`
   directory (sibling of `backend/` and `frontend/`).
5. **Single source of truth for branding** — logos, colors, and fonts are
   defined once in `assets/` and shared between Next.js and Django.
6. **Shared layer is controlled** — use `libs/django-fusion` for framework
   templates and components. Project-specific styles, logos, and branding
   never go into `libs/django-fusion`; they stay in the project-level
   `assets/` directory. Use `projects/assets/` only for cross-site design
   assets used by non-fusion sites.
7. **Use canonical paths** — import from `apps.pages.*` for app code,
   `apps.core.*` for shared core, `django_fusion.*` for framework APIs.
   See the import convention table above and `libs/django-fusion/AGENTS.md`.

## Related

- [`docs/plans.md`](../../../docs/plans.md) — master enhancement plan
- [`projects/cms-fusion/plan/ASSETS_TEMPLATES_CLEANUP.md`](../plan/ASSETS_TEMPLATES_CLEANUP.md) — localized cleanup plan
- [`libs/django-fusion/AGENTS.md`](../../../libs/django-fusion/AGENTS.md) — django-fusion conventions
