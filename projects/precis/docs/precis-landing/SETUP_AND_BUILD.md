# Precis Landing — Setup & Build Guide

> **Path:** `projects/precis/precis-landing/`
> **Stack:** Astro 5 + Tailwind CSS 4 + HTMX + Alpine.js (frontend) ·
> Django 5.2 + Wagtail 7.4 + django-fusion (backend)
> **Backend port:** 8074 · **Frontend port:** 4321 (Astro default)

Precis Landing is the marketing/catalog slice: an **AHA stack** (Astro +
HTMX + Alpine.js) frontend with a **Django + Wagtail** backend whose editable
StreamFields drive every landing section.

---

## 1. Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | ≥ 3.11 | Backend runtime |
| [uv](https://docs.astral.sh/uv/) | latest | Workspace venv + deps |
| Node.js | 20/22 (v22 preferred) | Astro frontend + webpack assets |
| npm | 10+ | Frontend package manager |

The root `Makefile` picks the latest installed v22 Node from
`~/.nvm/versions/node/v22.*` automatically and prepends it to `PATH`.

Verify:

```bash
python3 --version && uv --version && node --version && npm --version
```

---

## 2. Install dependencies

### 2.1 Frontend (Astro)

```bash
cd projects/precis/precis-landing
just install            # cd frontend && npm install
```

### 2.2 Backend (Django + Wagtail)

```bash
cd projects/precis/precis-landing/backend
just install            # uv sync in the workspace (projects/)
```

> The backend runs from the workspace venv (`uv --project ../..`). There is
> no per-project venv; `projects/pyproject.toml` is the source of truth.

### 2.3 Webpack assets (Django-side SCSS/JS)

```bash
cd projects/precis/precis-landing
make install-assets     # npm install at project root
make build-assets       # webpack production + skeleton manifest
make build-assets-dev   # webpack development (source maps)
```

---

## 3. Database & seed

```bash
cd projects/precis/precis-landing/backend
make migrate            # makemigrations --noinput + migrate --noinput
make seed               # seed_pages — site + full 8-page tree (idempotent)
```

The seed command creates the Wagtail site and the home/about/company/
services/products/contact/faq/privacy pages, plus default landing content.
It is idempotent — safe to re-run.

Create an admin user:

```bash
make superuser          # interactive
```

---

## 4. Run in development

### 4.1 Backend (Django + Wagtail)

```bash
cd projects/precis/precis-landing/backend
make dev                # http://localhost:8074 — Wagtail admin at /admin/
```

### 4.2 Frontend (Astro)

In a second terminal:

```bash
cd projects/precis/precis-landing
make dev                # cd frontend && npm run dev (http://localhost:4321)
```

### 4.3 Root dispatcher (backend delegation)

```bash
cd projects/precis/precis-landing
make backend-dev        # Django dev server
make backend-migrate
make backend-seed
make backend-check
make backend-test
make backend-help       # list backend targets
```

---

## 5. Verification

```bash
cd projects/precis/precis-landing
make check              # astro check (types + diagnostics)
make backend-check      # django system checks

# Tests
make backend-test       # apps.pages tests (pytest-style via manage.py test)
cd frontend && npm test # node --test tests/*.test.mjs
```

### E2E (browser smoke)

Both servers must be running first:

```bash
# Terminal 1
cd projects/precis/precis-landing/backend && make dev
# Terminal 2
cd projects/precis/precis-landing && make dev
# Terminal 3
cd projects/precis/precis-landing && make e2e
```

---

## 6. Production build

```bash
cd projects/precis/precis-landing
make build              # install-assets → build-assets → css → astro build
make build-prod         # explicit alias of `build` for CI
```

What `make build` does, step by step:

1. `make install-assets` — npm install at project root (webpack deps)
2. `make build-assets` — `webpack --config webpack/precis-landing.config.js --mode=production` + skeleton manifest
3. `make css` — compiles `frontend/src/styles/globals.css` (Tailwind 4 CLI)
   into `assets/static/css/fusion.css` so the **Django** render gets the same
   styles as the Astro build. This file is committed to git.
4. `cd frontend && npm run build` — Astro static output → `frontend/dist/`

Verify the production frontend:

```bash
make preview            # astro preview
```

Backend static collection:

```bash
cd projects/precis/precis-landing/backend
make collectstatic      # collectstatic --noinput
```

Production server (gunicorn, WSGI):

```bash
cd projects/precis/precis-landing/backend
make server             # bind 0.0.0.0:8074, workers=4, timeout=120
```

---

## 7. Common tasks

| Task | Command |
|------|---------|
| Clean frontend build artifacts | `make clean` |
| Recompile fusion.css only | `make css` |
| Skeleton manifest only | `make skeleton-manifest` |
| Django shell | `cd backend && make shell` |
| Format code | `cd backend && make format` (ruff) |
| Lint unused imports | `cd backend && make lint` |

---

## 8. Troubleshooting

### Astro frontend renders unstyled

Rebuild the shared Tailwind stylesheet:

```bash
cd projects/precis/precis-landing
make css
```

### Backend page renders without sections

Run the seed command — the page tree + StreamField content is created by
`seed_pages`, not by `migrate`:

```bash
cd projects/precis/precis-landing/backend
make seed
```

### Missing webpack bundles

```bash
cd projects/precis/precis-landing
make build-assets
```

### Port conflict

```bash
lsof -ti :8074 | xargs kill -9
PORT=8090 make dev      # override the default 8074
```

---

## See also

- [Project README](../README.md) — quick start + implemented-features list
- [Catalog & Fusion](../precis-main/CATALOG_AND_FUSION.md) — product &
  edition comparison, django-fusion dependency surface
- [Project design](../precis-main/PROJECT_DESIGN.md) — design decisions
- [`docs/plans/precis-landing.md`](../../../../docs/plans/precis-landing.md) — canonical plan
