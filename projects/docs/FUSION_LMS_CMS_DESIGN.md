# Fusion LMS/CMS Design Document

## Overview

Create two new, isolated product lines:

- **Fusion LMS** (`projects/lms-fusion/`)
- **Fusion CMS** (`projects/cms-fusion/`)

Each product line has its own backend (Django/Wagtail), frontend (Next.js), and assets (styles, scripts, images). They reuse the proven ctc-research design system but are branded independently through `fu-*` CSS classes and dynamic display names from Wagtail models.

## Design Principles

1. **Isolation** — New directories do not overlap with `projects/lms/`, `projects/cms/ctc-research/`, or `projects/cms/lms-full/`.
2. **Reuse** — Copy ctc-research templates, styles, and Python boilerplate as the starting point, then rename `ctc-*` to `fu-*`.
3. **Variation** — Each product line customizes colors, animations, and layout tokens without touching shared `projects/assets/`.
4. **Dynamic Branding** — Site name, company name, and creator name come from a Wagtail **Site Settings** snippet, falling back to environment variables.
5. **Backend-First Rendering** — Django/Wagtail renders pages fully by default; `fusion_render_first` is enabled so the Fusion frontend can hydrate from the same HTML.

## Directory Structure

```
projects/
├── lms-fusion/
│   ├── backend/                 # Django/Wagtail (mirrors cms/ctc-research)
│   │   ├── assets/
│   │   │   ├── static/
│   │   │   │   ├── styles/      # merged shared + ctc styles, renamed fu-*
│   │   │   │   ├── js/          # entry points
│   │   │   │   └── images/
│   │   │   ├── media/
│   │   │   └── fixtures/
│   │   ├── templates/
│   │   │   ├── base.html
│   │   │   ├── base_page.html
│   │   │   └── home/
│   │   ├── plugins/
│   │   │   ├── core/            # branding snippet + context processors
│   │   │   ├── lms/
│   │   │   ├── accounts/
│   │   │   └── blog/
│   │   ├── www/
│   │   │   ├── core/
│   │   │   └── urls.py
│   │   ├── settings.py
│   │   ├── server.py
│   │   ├── manage.py
│   │   └── pyproject.toml
│   ├── frontend/                # Next.js 14 (mirrors lms/front-end)
│   │   ├── src/
│   │   │   ├── app/
│   │   │   ├── components/
│   │   │   ├── lib/
│   │   │   └── store/
│   │   ├── public/
│   │   └── package.json
│   └── assets/                  # product-line shared assets
│       └── styles/
│           └── fusion-theme.scss
├── cms-fusion/
│   ├── backend/
│   ├── frontend/
│   └── assets/
└── docs/FUSION_LMS_CMS_DESIGN.md  # this file
```

## Merging Shared + CTC Styles

Each backend copies the ctc-research `main.scss` and resolves shared imports via webpack alias `~shared` to `projects/assets/static/styles`. The new `main.scss` for Fusion becomes:

```scss
// fusion/backend/assets/static/styles/main.scss
@import '~shared/styles/base/base';
@import '~shared/styles/base/buttons';
// ... all shared imports
@import 'colors/index';           // Fusion palette
@import 'components/progress';  // renamed fu-progress
@import 'pages/auth';             // renamed fu-auth
```

The `~shared` alias is preserved by adding the new site to `assets/scripts/workspace.mjs`.

## CSS Rename Strategy: `ctc-*` → `fu-*`

- Copy `projects/cms/ctc-research/assets/static/styles` to the new backend.
- Run a script to replace `ctc-` with `fu-` in class names, IDs, and CSS selectors in the copied files only.
- Do **not** touch `projects/assets/static/styles` (shared) or `projects/cms/ctc-research` (source).
- Preserve JavaScript selectors by prefixing with `data-fu-` attributes where needed.

## Dynamic Branding

A new `FusionBranding` Wagtail snippet holds:

| Field | Fallback env var | Usage |
|-------|------------------|-------|
| `site_name` | `FUSION_SITE_NAME` | `<title>`, nav logo text |
| `company_name` | `FUSION_COMPANY_NAME` | Footer copyright |
| `creator_name` | `FUSION_CREATOR_NAME` | Admin / credits |
| `primary_color` | `FUSION_PRIMARY_COLOR` | CSS custom property override |
| `favicon` | `FUSION_FAVICON` | Favicon URL |

A context processor `fusion_branding_context` injects `fusion_branding` into every template.

## Backend Fallback & fusion_render_first

New base template `base.html`:

```django
{% load fusion_tags %}
<!DOCTYPE html>
<html data-fusion-render-first="{% fusion_render_first_flag %}">
<head>...</head>
<body>
  {% block body %}{% endblock %}
  {% render_fusion_scripts %}
</body>
</html>
```

`fusion_render_first=True` is the default for every RoutableComponent so the Next.js frontend can bootstrap from the server-rendered HTML.

## Testing Checklist

- [ ] `fusion_branding_context` returns env fallback when no Wagtail snippet exists.
- [ ] `fusion_render_first` flag is `True` for all public page components.
- [ ] `ctc-` classes no longer exist in copied styles/templates (only `fu-`).
- [ ] Webpack build for new site alias succeeds.
- [ ] Django system checks pass for new backend.

## Next Steps

1. Run the scaffold generator script (`tools/scaffold-fusion.py`).
2. Register new webpack aliases in `assets/scripts/workspace.mjs`.
3. Create base Wagtail models and migrations.
4. Build a single page (homepage) to verify the pipeline.
