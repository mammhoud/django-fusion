# Landing-Fusion — AI Agent Instructions

**Path:** `projects/landing-fusion/`  
**Stack:** Astro 5 + Tailwind CSS 4 + HTMX + Alpine.js; Django 5.2 + Wagtail 7.4 + django-fusion

Read the repository root and `projects/AGENTS.md` first. This file is the
project-level source of truth for the landing/catalog product.

## Boundary and layout

```text
landing-fusion/
├── frontend/                 # Astro pages, layout, Fusion client helpers, E2E
│   ├── src/pages/            # Marketing/catalog routes
│   ├── src/layouts/          # Document shell, SEO, theme, AHA bootstrap
│   ├── src/fusion/           # HTMX, fragments, SSE, scroll, theme helpers
│   ├── src/lib/              # API, site config, translations, brand helpers
│   ├── src/styles/           # Frontend tokens/global styles
│   └── e2e/                  # Playwright site/backend/learning tests
├── backend/                  # Standalone Django + Wagtail application
│   ├── apps/content/         # StreamField blocks and content APIs
│   ├── apps/pages/           # Wagtail page models, APIs, migrations, tests
│   ├── apps/handlers/        # PageHandlers, URL applications, middleware
│   ├── apps/learning/        # Catalog, enrollment, progress, learner flows
│   ├── apps/auth/            # Allauth adapters and auth integration
│   ├── settings.py           # Self-contained settings
│   ├── urls.py               # Admin, auth, API, fragments, Wagtail routes
│   └── Makefile               # Backend commands (default port 8074)
├── assets/                   # Product SCSS, compiled CSS, images/media
├── templates/                # Narrow legacy/project template overrides
├── docs/                     # Product design, use cases, ADRs
├── docker-compose.yml        # Frontend/backend container composition
├── Makefile                  # Frontend + backend orchestration
└── README.md
```

The frontend and backend are separate runtime surfaces but one product. Keep
API schemas, route names, render-mode behavior, translations, and navigation
contracts synchronized across both directories.

## Rendering contract

Landing-Fusion supports two roads:

1. **Astro/data API road:** Astro requests `/apis/*` data and renders pages.
2. **Django/Fusion road:** Django `PageHandler`/Wagtail routes render full HTML
   or HTMX fragments directly.

Relevant backend routes include:

- `/api/auth/` and `/accounts/` — headless and server-rendered auth
- `/apis/*` — page, navigation, settings, content, catalog, brand, and assets
- `/fragment/*` — HTML fragment endpoints for HTMX swaps
- `/learning/` — learning application routes
- `/admin/`, `/django-admin/`, `/documents/` — Wagtail/Django administration
- Wagtail catch-all routes are deliberately registered last

When changing a route or response, check both `backend/urls.py`, the matching
frontend client/page, and the backend/frontend tests. Do not make the frontend
silently fall back to hard-coded demo content when an API is unavailable.

## Content and templates

- Wagtail page models and StreamField blocks live in `backend/apps/pages/` and
  `backend/apps/content/`.
- A block's template must preserve its StreamField `value` contract and remain
  safe for both full-page and fragment rendering.
- Use `{% comp %}` for django-fusion components; use `{% include_block %}` for
  Wagtail blocks and `{% include %}` only for dynamic/local includes.
- Product-specific templates and styles belong in this project. Do not move
  landing branding into `libs/django-fusion`.
- Keep CSS tokens shared between Astro and Django-generated output. Edit source
  styles and rebuild; do not hand-edit generated bundles.

## Commands

```bash
cd projects/landing-fusion
make install                 # frontend npm dependencies
make dev                     # Astro frontend
make check                   # Astro diagnostics
make build                   # CSS + Astro production build
make e2e                     # requires backend and frontend running
make backend-migrate
make backend-seed
make backend-dev             # Django on :8074 by default
make backend-check
make backend-test

cd backend
make migrate
make seed
make check
make test
```

The backend Makefile uses the workspace `uv` environment. A fresh local backend
usually needs `make migrate` and `make seed` before page rendering is useful.
Do not run seed/reset commands against a shared or production database.

## Testing checklist

- Backend model/page/API change: targeted `backend` tests plus `make backend-check`.
- Astro page/client change: `npm run check`, relevant frontend tests, and E2E
  when the route or browser behavior changes.
- Shared content contract change: test both the Django/Fusion and Astro roads.
- Asset change: run the CSS/build target and verify that generated files are
  intentionally updated.

## Related guidance

- `backend/AGENTS.md` files under Precis do not apply here; this backend is
  standalone and owns its own settings/template search path.
- `libs/django-fusion/AGENTS.md` governs framework imports and component APIs.
- `docs/projects/landing-fusion/` contains deployment and API notes.
