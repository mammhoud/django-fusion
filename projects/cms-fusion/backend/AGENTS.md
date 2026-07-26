# cms-fusion — AI Agent Instructions

Path: `projects/cms-fusion/backend/`

## Overview

cms-fusion is a self-contained Fusion project. Templates, static assets,
fixtures, and locale files should live inside this project unless they are
genuinely shared across sites or part of the `django-fusion` framework.

## Template Resolution Order

Django resolves templates in this order (highest priority first):

1. `cms-fusion/backend/templates/` — site-root entry templates and project-wide overrides
2. `cms-fusion/backend/plugins/<app>/templates/` — plugin/app templates
3. `cms-fusion/backend/www/<app>/templates/` — www app templates
4. `cms-fusion/backend/assets/templates/` — project asset templates
5. `libs/django-fusion/src/django_fusion/templates/` — django-fusion framework templates
6. `projects/assets/templates/` — monorepo shared templates (kept for non-fusion sites)

## Asset / Static Resolution Order

Django static and media files resolve in this order (highest priority first):

1. `cms-fusion/backend/assets/static/` — project-specific compiled static files
2. `cms-fusion/backend/assets/media/` — project-specific uploaded media
3. `libs/django-fusion/src/django_fusion/static/` — django-fusion framework static
4. `projects/assets/static/` — monorepo shared static (for non-fusion sites)

Source design assets (SCSS, logos, fonts, images) live in the project root
`cms-fusion/assets/` and are compiled/copied into the locations above for
both Next.js and Django consumption.

## Current Template Tree

```
cms-fusion/backend/templates/
├── base.html               # Project base layout (extends django-fusion base)
├── base_page.html          # Page layout wrapper
├── index.html              # Home / entry point template
├── auth/                   # Auth-related entry templates
├── blog/                   # (target: move to plugins/blog/templates/)
├── lms/                    # (target: move to plugins/lms/templates/)
├── pages/                  # (target: move to plugins/pages/templates/)
├── products/               # (target: move to plugins/products/templates/)
├── registration/           # Account registration templates
├── services/               # Service page templates
└── ...
```

> **Migration in progress:** app-specific templates currently under
> `backend/templates/` are being moved to `plugins/<app>/templates/`. Keep new
> app-specific templates in the app directory; only site-root entry templates
> and project-wide overrides belong in `backend/templates/`.

## Target Template Organization

```
cms-fusion/backend/
├── templates/                       # Site-root entry + project-wide overrides
│   ├── base.html
│   ├── base_page.html
│   └── index.html
├── plugins/<app>/templates/         # App-owned templates
│   ├── accounts/
│   ├── blog/
│   ├── lms/
│   ├── pages/
│   ├── products/
│   └── profile/
└── www/core/templates/            # www/core app templates
```

## Asset Tree

```
cms-fusion/
├── assets/                       # Source design assets (single source of truth)
│   ├── styles/                   # SCSS source files, design tokens, theme
│   ├── images/                   # Project images, illustrations
│   ├── branding/                 # Logos, favicons, brand assets
│   └── fonts/                    # Project-specific web fonts
└── backend/assets/
    ├── static/                   # Compiled CSS, JS, images for Django collectstatic
    ├── templates/                # Project-specific template includes
    ├── media/                    # Uploaded media (runtime)
    ├── fixtures/                 # Project fixtures
    ├── locale/                   # Project .po/.mo files
    ├── emails/                   # Email templates
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
- Django consumes the compiled CSS from `backend/assets/static/css/fusion.css`
  or references CSS custom properties in templates.
- Logos are copied/symlinked to `frontend/public/branding/` and
  `backend/assets/static/branding/` during the build.

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

The compiled CSS is emitted to `backend/assets/static/css/fusion.css` and
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
    name = "plugins.my_app"

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
2. **App first** — app-specific templates belong in `plugins/<app>/templates/`
   or `www/<app>/templates/`, not `backend/templates/`.
3. **Site root is for overrides** — only entry templates and project-wide
   overrides live in `backend/templates/`.
4. **Source assets at project root** — design source files (SCSS, logos, fonts,
   images) live in `cms-fusion/assets/` (sibling of `backend/` and `frontend/`).
   Backend runtime output lives in `backend/assets/`.
5. **Single source of truth for branding** — logos, colors, and fonts are
   defined once in `assets/` and shared between Next.js and Django.
6. **Shared layer is controlled** — use `libs/django-fusion` for framework
   templates and components. Project-specific styles, logos, and branding
   never go into `libs/django-fusion`; they stay in the project-level
   `assets/` directory. Use `projects/assets/` only for cross-site design
   assets used by non-fusion sites.
7. **Use canonical paths** — import from `django_fusion.comp.registry`,
   `django_fusion.routes`, etc. (see `libs/django-fusion/AGENTS.md`).

## Related

- [`docs/plans.md`](../../../docs/plans.md) — master enhancement plan
- [`projects/cms-fusion/plan/ASSETS_TEMPLATES_CLEANUP.md`](../plan/ASSETS_TEMPLATES_CLEANUP.md) — localized cleanup plan
- [`libs/django-fusion/AGENTS.md`](../../../libs/django-fusion/AGENTS.md) — django-fusion conventions
- [`projects/assets/templates/AGENTS.md`](../../../projects/assets/templates/AGENTS.md) — shared template rules
