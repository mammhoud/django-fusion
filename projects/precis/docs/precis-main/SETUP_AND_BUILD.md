# Precis — Setup & Build Guide

> **Path:** `projects/precis/precis-main/`
> **Stack:** Astro 5 + Tailwind CSS 4 + HTMX + Alpine.js (frontend) ·
> Django 5.2 + Wagtail 7.4 + django-fusion (backend)
> **Backend port:** 8074 · **Frontend port:** 4321 (Astro default)

Precis is the unified Structa Cloud product: marketing/catalog shell +
learning platform + AI assistant, served by one Astro frontend and one
Django + Wagtail backend.

---

## 1. Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | ≥ 3.11 | Backend runtime |
| [uv](https://docs.astral.sh/uv/) | latest | Workspace venv + deps |
| Node.js | 20/22 (v22 preferred) | Astro frontend + webpack assets |
| npm | 10+ | Frontend package manager |

The root `Makefile` resolves the latest v22 Node from
`~/.nvm/versions/node/v22.*` automatically.

```bash
python3 --version && uv --version && node --version && npm --version
```

---

## 2. Install dependencies

### 2.1 Frontend (Astro)

```bash
cd projects/precis/precis-main
just install            # cd frontend && npm install
```

### 2.2 Backend (Django + Wagtail)

```bash
cd projects/precis/precis-main/backend
just install            # uv sync in the workspace (projects/)
```

### 2.3 Webpack assets (Django-side SCSS/JS)

```bash
cd projects/precis/precis-main
make install-assets     # npm install at project root
make build-assets       # webpack production + skeleton manifest
make build-assets-dev   # webpack development (source maps)
```

---

## 3. Database & seed

```bash
cd projects/precis/precis-main/backend
make migrate            # makemigrations --noinput + migrate --noinput
make seed               # seed_pages — site + full page tree (idempotent)
make superuser          # interactive admin user
```

The `seed_pages` command creates the Wagtail site and the page tree for
landing, blog, brand, and learning surfaces. Re-running is safe.

---

## 4. Run in development

### 4.1 Backend (Django + Wagtail)

```bash
cd projects/precis/precis-main/backend
make dev                # http://localhost:8074 — Wagtail admin at /admin/
```

### 4.2 Frontend (Astro)

In a second terminal:

```bash
cd projects/precis/precis-main
make dev                # http://localhost:4321
```

### 4.3 Root dispatcher

```bash
cd projects/precis/precis-main
make backend-dev        # Django dev server
make backend-check      # django system checks
make backend-test       # apps.pages tests
make backend-help       # list all backend targets
```

---

## 5. Verification

```bash
cd projects/precis/precis-main
make check              # astro check
make backend-check      # django check
make backend-test       # manage.py test apps.pages

cd frontend && npm test # node --test tests/*.test.mjs
```

E2E (requires both servers):

```bash
make e2e
```

---

## 6. Production build

```bash
cd projects/precis/precis-main
make build              # install-assets → build-assets → css → astro build
make build-prod         # explicit alias for CI
make preview            # astro preview of the built frontend
```

What `make build` runs:

1. `make install-assets` — npm install (webpack deps)
2. `make build-assets` — webpack production build + skeleton manifest
3. `make css` — Tailwind CLI compiles `frontend/src/styles/globals.css`
   → `assets/static/css/fusion.css` (used by the Django render; committed)
4. `cd frontend && npm run build` — Astro static output → `frontend/dist/`

Backend static + production server:

```bash
cd projects/precis/precis-main/backend
make collectstatic      # collectstatic --noinput
make server             # gunicorn on 0.0.0.0:8074 (WSGI)
```

---

## 7. Common tasks

| Task | Command |
|------|---------|
| Recompile fusion.css only | `make css` |
| Skeleton manifest only | `make skeleton-manifest` |
| Clean build artifacts | `make clean` |
| Django shell | `cd backend && make shell` |
| Format code | `cd backend && make format` (ruff) |
| Lint unused imports | `cd backend && make lint` |

---

## 8. Troubleshooting

### Pages render without content after fresh migrate

Run the seeder — `migrate` alone does not create the page tree:

```bash
cd projects/precis/precis-main/backend
make seed
```

### Backend styles missing

```bash
cd projects/precis/precis-main
make css && make build-assets
```

### Port conflict

```bash
lsof -ti :8074 | xargs kill -9
PORT=8090 make dev      # backend
```

### Auth failures when proxying via Astro

The backend settings trust `http://localhost:8074` as an allowed origin.
If you proxy Astro → Django on another port, add it to the allowed origins
in `backend/settings.py` (see the `CSRF_TRUSTED_ORIGINS`-adjacent list).

---

## See also

- [Project README](../README.md) — quick start + features
- [Project design](PROJECT_DESIGN.md) — design notes
- [Use cases](USECASE.md) — use cases
- [Wagtail render model](WAGTAIL_RENDER_MODEL.md) — render model
