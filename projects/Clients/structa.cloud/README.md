# Precis — unified product (`projects/structa.cloud`)

> **Rename note:** this project moved from `projects/structa.cloud/` to
> `projects/structa.cloud/`. The runtime identity (container names
> `precis-main-*`, images, `DJANGO_SITE=precis-main`) is intentionally preserved
> so volumes and deployed environments stay valid; `WEBSITE=precis-main` remains
> a legacy alias for `WEBSITE=structa.cloud`.

> **Status:** 🟢 Active — unified Precis product (marketing shell + LMS)
> **Tags:** #precis #landing #lms #astro #django #wagtail #aha-stack #fusion
> **Stack:** Astro 5 + Tailwind CSS 4 + HTMX + Alpine.js (frontend) · Django 5.2 + Wagtail 7.4 + django-fusion (backend)

Precis is the unified Structa Cloud product, merging the Precis Landing
marketing shell with the Precis LMS learning platform (courses, enrollment,
progress, profiles, assistant). It serves both the public/catalog pages and
the learning application from one Astro frontend and one Django + Wagtail
backend, using the **AHA stack** (Astro + HTMX + Alpine.js) with django-fusion
`PageHandler` views for server-rendered HTML and HTMX fragments.

> This directory was previously documented as a plain Precis Landing slice;
> that (older) landing-only variant still lives at
> [`../precis-landing/`](../precis-landing/README.md).

## Why this project exists

Precis is the canonical product boundary: one frontend and one backend that
cover marketing/catalog pages, learning journeys, and AI-assistant surfaces.
Every editable section is a Wagtail StreamField; every dynamic interaction is
an HTMX fragment or an Alpine component — no large client-side bundle.

| Factor | Approach in Precis |
|--------|:------------------:|
| Client JS shipped | Minimal (~30KB HTMX + Alpine) |
| Rendering | django-fusion `PageHandler` (full HTML + HTMX fragments) |
| Dynamic interactions | HTMX fragments + Alpine.js |
| Content editing | Wagtail CMS StreamFields |
| Learning | Courses, enrollment, progress, profile, certificates |

## Repository layout

```
projects/structa.cloud/
├── frontend/                 # Astro 5 + Tailwind 4 + HTMX + Alpine.js
│   ├── src/
│   │   ├── layouts/          # Document shell, SEO, theme, AHA runtime
│   │   ├── pages/            # Landing, courses, blog, brand, assistant, profile, …
│   │   ├── components/       # ui/, blocks/, layout/, AssistantPanel
│   │   ├── lib/              # api.ts, site config, translations
│   │   └── styles/globals.css# Tailwind 4 + Fusion tokens + .dark variant
│   └── package.json
├── backend/                  # Django 5.2 + Wagtail 7.4
│   ├── apps/
│   │   ├── content/          # StreamField blocks + content templates
│   │   ├── pages/            # Page models + seed_pages + tests
│   │   ├── learning/         # Courses, enrollments, progress, profile
│   │   ├── domain/           # Domain models (users, contacts, locations, …)
│   │   ├── handlers/         # django-fusion PageHandler views
│   │   ├── auth/             # Allauth adapters
│   │   ├── components/       # Shared django-fusion components
│   │   ├── core/             # Core app scaffolding
│   │   └── tasks/            # Background tasks
│   ├── settings.py / urls.py / Makefile
├── assets/                   # Product SCSS, compiled CSS, images/media
├── templates/                # Template overrides
├── docs/                     # Design, use cases, ADRs, setup guide
├── docker-compose.yml
├── Makefile                  # Frontend + backend orchestration
└── README.md
```

## Quick start

> 📖 Full step-by-step setup, build, deployment, and render-flow reference: [`docs/README.md`](docs/README.md) and [`../../../../docs/precis/landing-fusion-render-flow.html`](../../../../docs/precis/landing-fusion-render-flow.html)

### Frontend (Astro)

```bash
cd projects/structa.cloud
just install          # cd frontend && npm install
make dev              # http://localhost:4321
make check            # astro check
```

### Backend (Django + Wagtail)

```bash
cd projects/structa.cloud/backend
just install          # workspace venv (uv sync)
make migrate          # makemigrations + migrate (SQLite)
make seed             # create site + full page tree (idempotent)
make dev              # http://localhost:8074 — Wagtail admin at /admin/
make check            # django system checks
make test             # apps.pages tests
```

### Full setup in one go (project root)

```bash
cd projects/structa.cloud
make backend-migrate
make backend-seed
make backend-dev      # Django :8074
# second terminal
make dev              # Astro :4321
```

> Full detailed steps — prerequisites, asset builds, tests, production
> build, Docker, troubleshooting — are in
> [`../docs/precis-main/SETUP_AND_BUILD.md`](../docs/precis-main/SETUP_AND_BUILD.md).

## Deployment and Nx

```bash
# Local Compose overlay — publishes :8074 and :3000
make validate-local
make deploy-local

# Production base Compose — no local override
make validate-production
make deploy-production

# Same project contract through Nx
npx nx run precis-main-assets:check
npx nx run precis-main-assets:test
npx nx run precis-main-assets:build
npx nx run precis-main-assets:deploy-local
npx nx run precis-main-assets:deploy-production
```

The repository dispatcher remains available from `projects/` with
`WEBSITE=precis-main`; `precis-lms`, `precis-landing`, `lms`, and `structa` are
compatibility aliases where supported.


- **Marketing/catalog shell** — landing, company, services, products,
  contact, FAQ, privacy, brand, blog, AI-agents pages
- **Learning platform** — course catalog + detail, enrollment, progress,
  profile, certificates
- **AI assistant** — `AssistantPanel` surfaces wired through HTMX
- **Wagtail-driven content** — every section editable via StreamFields
- **django-fusion views** — `PageHandler` renders full HTML or HTMX
  fragments; skeleton loading on both roads
- **Dark mode** — persisted theme toggle, FOUC-free init, cross-tab sync
- **Multilingual** — Arabic + English editorial overlays

## Commands reference

| Target (project root) | Purpose |
|-----------------------|---------|
| `make dev` | Astro dev server |
| `make build` | CSS + webpack assets + Astro production build |
| `make build-prod` | Explicit production build (CI) |
| `make css` | Compile Tailwind globals → `assets/static/css/fusion.css` |
| `make check` | Astro diagnostics |
| `make e2e` | Browser smoke test (requires both servers) |
| `make install-assets` / `build-assets` | Webpack assets for Django |
| `make skeleton-manifest` | Regenerate skeleton manifest |
| `make backend-*` | Delegate to `backend/Makefile` (migrate, seed, dev, check, test, help) |
| `make clean` | Remove build artifacts |

## Not yet ported / next

- Full Playwright E2E suite across learning + assistant flows
- Final Docker/Traefik production rollout gates

## See also

- [`docs/README.md`](docs/README.md) — project-local documentation index
- [`docs/landing-fusion-render-flow.html`](docs/landing-fusion-render-flow.html) — project-local render-flow reference
- [`../../../../docs/precis/README.md`](../../../../docs/precis/README.md) — canonical product documentation
- [`../../../../docs/precis/deployment.md`](../../../../docs/precis/deployment.md) — deployment and proxy runbook
- [`../../../../docs/plans/repository/precis-main-render-flow.md`](../../../../docs/plans/repository/precis-main-render-flow.md) — accepted command/render plan
- [`../precis-landing/README.md`](../precis-landing/README.md) — landing-only compatibility copy
- [`../../libs/django-fusion/README.md`](../../libs/django-fusion/README.md) — component library
