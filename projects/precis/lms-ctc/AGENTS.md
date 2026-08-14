# CTC Research — AI Agent Instructions

**Path:** `projects/precis/ctc-research/`  
**Product:** CTC Research / medical research center (`ctc-research.com`)  
**Stack:** Django 5.2 + Wagtail 7.4 + django-fusion + allauth; Astro 5 frontend shell; SCSS + JS assets

Read the repository root and `projects/AGENTS.md` first. This file covers the
full CTC Research project surface — backend, frontend, assets, templates, and
deployment. For backend-only details, see [`backend/AGENTS.md`](backend/AGENTS.md).

## Layout

```text
ctc-research/
├── backend/                  # Django + Wagtail application
│   ├── apps/                 # content, learning, pages, handlers, auth, core, domain
│   ├── templates/            # Site-root shells, errors, admin overrides
│   ├── settings.py           # Backend settings and app registration
│   ├── urls.py               # Root URL configuration
│   ├── tests/                # Backend test suite (API smoke, fixtures, page rendering)
│   ├── Makefile              # Backend commands (check, test, migrate, collectstatic)
│   └── AGENTS.md             # Backend-scoped guidance (app ownership, URL flow, templates)
├── assets/                   # Product templates, static files, SCSS, locale, fixtures
│   ├── templates/            # Product template source (blog, lms, pages, profile, components, plugins)
│   │   └── AGENTS.md         # Template organization and resolution order
│   ├── static/               # JS (fusion-bridge, htmx-config, core), CSS, fonts
│   ├── styles/               # SCSS source (fusion-theme, vendor styles)
│   ├── locale/               # fr, es, de, ar .po files
│   ├── fixtures/             # Data fixtures and dump-data.json
│   ├── media/                # Runtime media storage
│   └── Makefile              # Asset build pipeline
├── frontend/                 # Astro 5 frontend shell
│   ├── src/pages/            # Public pages (index, blog, courses, pricing, about, contact, products, faq)
│   ├── src/layouts/          # Document shell, SEO, theme
│   ├── src/fusion/           # HTMX, fragments, SSE, scroll, theme helpers
│   ├── src/lib/              # API client, site config, state stores
│   ├── src/styles/           # Global styles, typography, buttons, variables
│   ├── src/components/       # Blocks (Hero, CTA, Features, Pricing, BlogPreview),
│   │                          │   layout (Header, Footer), UI (Modal, LoginModal, Toast, Accordion, Card)
│   ├── e2e/                  # Playwright tests (courses, site, backend, pages, login)
│   ├── tests/                # Frontend smoke/placement tests
│   ├── astro.config.mjs      # Astro configuration
│   └── playwright.config.ts  # Playwright configuration
├── brandkit/                 # Brand assets and identity reference
├── compose/                  # Docker Compose (frontend + backend containers)
├── templates/                # Narrow project-level template overrides
├── data/                     # Data and seed files
├── websites/                 # Per-site configuration
├── docker-compose.yml        # Container orchestration
├── Makefile                  # Project-level orchestration
├── pyproject.toml            # Python dependencies
└── README.md
```

## Project boundaries

- **Backend** (`backend/`): Django/Wagtail application — models, page handlers,
  viewsets, Wagtail hooks, API endpoints, HTMX fragments. See
  [`backend/AGENTS.md`](backend/AGENTS.md) for app ownership and URL flow.
- **Frontend** (`frontend/`): Astro 5 shell providing public-facing pages. Can
  render from Django APIs or serve static/pre-rendered content. Keep API
  contracts and navigation synchronized with the backend.
- **Assets** (`assets/`): Django templates (`templates/`), static files
  (`static/`), SCSS source (`styles/`), locale files (`locale/`), and
  fixtures. Template resolution follows the order documented in
  `assets/templates/AGENTS.md`.
- **Brandkit** (`brandkit/`): Reference brand assets and identity. Not runtime
  code; do not import from here.
- **Compose** (`compose/`): Dockerfiles and entrypoint scripts for
  containerized deployment.

## Rendering

CTC Research uses Django/Wagtail server-rendered pages with HTMX fragment swaps and
an Astro frontend shell. A request may be:

1. A full Wagtail page render (Django template → HTML document).
2. An HTMX fragment (Django template → HTML fragment for swap).
3. An API response (JSON) consumed by the Astro frontend.
4. A static/pre-rendered Astro page.

Preserve the existing detection and response contracts. Use `{% comp %}` for
django-fusion components, `{% include_block %}` for Wagtail blocks, and
`{% include %}` only for dynamic/local includes.

## Conventions

- Keep backend app code under `backend/apps/<app>/`; use `apps.*` imports.
- Template resolution: backend app templates → `assets/templates/` →
  `libs/django-fusion/templates/` (see `assets/templates/AGENTS.md`).
- Use BEM-style CSS classes for reusable components.
- Preserve Wagtail context, translation tags (`{% trans %}`), permissions
  checks, and HTMX attributes (`hx-get`, `hx-target`, `hx-swap`).
- Product-specific branding and styles belong here, not in `libs/django-fusion`.
- Keep SCSS source separate from compiled CSS and collected static files.

## Commands

```bash
# Project dispatcher
cd projects
make check WEBSITE=ctc-research
make test WEBSITE=ctc-research
make run-dev WEBSITE=ctc-research
make show-config WEBSITE=ctc-research

# Backend
cd projects/precis/ctc-research/backend
make check
make test
make migrate
make collectstatic

# Frontend
cd projects/precis/ctc-research/frontend
npm run dev
npm run check
npm run build
npx playwright test

# Assets
cd projects/precis/ctc-research/assets
make build    # SCSS compilation and asset pipeline
```

## Testing

- **Backend:** `cd backend && make test` — API smoke, fixture contracts,
  learning search/detail/progress, page rendering, domain invariants.
- **Frontend:** `cd frontend && npm run check` (Astro diagnostics) +
  `npx playwright test` (e2e) + `npm run test` (Vitest).
- **Cross-product:** Use `tests/` workspace suite for cross-product behavior.

## Do not

- Do not use old `plugins.*`, `www.*`, or `projects/lms-fusion/` paths in new
  imports or files.
- Do not move Landing-Fusion-only APIs or templates into Precis.
- Do not hand-edit generated static bundles or collected static files.
- Do not add compatibility re-exports when a canonical import already exists.
- Do not place app-specific templates in the backend root.

## Related

- [`backend/AGENTS.md`](backend/AGENTS.md) — Backend app ownership, URL flow, templates
- [`assets/templates/AGENTS.md`](assets/templates/AGENTS.md) — Template organization
- [`../../libs/django-fusion/AGENTS.md`](../../libs/django-fusion/AGENTS.md) — Framework components
- [`../../docs/projects/precis/main/`](../../docs/projects/precis/main/) — Product documentation
- [`../precis/landi/AGENTS.md`](../precis/landi/AGENTS.md) — Separate product; do not merge
