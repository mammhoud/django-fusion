# CTC Research — Setup & Build Guide

> **Path:** `projects/precis/precis-ctc/`
> **Stack:** Django 5.2 + Wagtail 7.4 + django-fusion (backend) · Astro 5 (frontend)
> **Backend port:** 5070 · **Frontend port:** 3002

CTC Research is the standalone medical research center site serving
`ctc-research.com`. It owns its own backend, Astro frontend, Compose stack,
and database (`db_precis_ctc`) — it does **not** share Precis/LMS runtime state.
The medical research catalog (clinical trial design, biostatistics,
evidence synthesis, medical AI, manuscript writing, research integrity) is
seeded from fixtures.

---

## 1. Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | ≥ 3.11 | Backend runtime |
| [uv](https://docs.astral.sh/uv/) | latest | Workspace venv + deps |
| Node.js | 20/22 | Astro frontend + webpack assets |
| npm | 10+ | Frontend package manager |
| Docker (optional) | latest | Containerized stack (`make up`) |

```bash
python3 --version && uv --version && node --version && npm --version
```

---

## 2. Install dependencies

### 2.1 Python (backend)

```bash
cd projects/precis/precis-ctc/backend
just install
```

### 2.2 Frontend (Astro)

```bash
cd projects/precis/precis-ctc/frontend
npm install
```

### 2.3 Webpack assets (Django-side SCSS/JS)

```bash
cd projects/precis/precis-ctc
make install-assets
make build-assets       # webpack production + skeleton manifest
```

---

## 3. Database & seed

```bash
cd projects/precis/precis-ctc/backend
make migrate            # makemigrations --noinput + migrate --noinput
make populate-data      # seed pages + medical research catalog fixtures
make superuser          # interactive admin user
```

The medical research catalog is loaded from
`backend/apps/learning/fixtures/medical_research_catalog.json`,
`backend/apps/learning/fixtures/medical_research_curriculum.json`, and
`backend/assets/fixtures/dump-data.json`. Run `populate-data` after
`migrate` so the site has its course/catalog pages, modules, and lessons.

---

## 4. Run in development

### 4.1 Backend (Django)

```bash
cd projects/precis/precis-ctc/backend
make dev                # http://localhost:5070 — Wagtail admin at /admin/
```

### 4.2 Frontend (Astro)

In a second terminal:

```bash
cd projects/precis/precis-ctc/frontend
npm run dev             # http://localhost:3002
```

### 4.3 From the project root

```bash
cd projects/precis/precis-ctc
make run-dev            # backend dev server
make frontend-dev       # astro dev server
make check              # django checks
make test               # backend tests
```

---

## 5. Tests

```bash
cd projects/precis/precis-ctc/backend
make test               # workspace test runner
```

Frontend:

```bash
cd projects/precis/precis-ctc/frontend
npm test                # node --test tests/frontend-smoke.test.mjs
npx playwright test     # full suite (needs servers running)
```

---

## 6. Production build

### 6.1 Frontend

```bash
cd projects/precis/precis-ctc/frontend
npm run build           # → frontend/dist/
npm run preview         # preview the build
```

### 6.2 Backend static + assets

```bash
cd projects/precis/precis-ctc/backend
make collectstatic      # collectstatic --noinput
make assets-setup       # frontend-install + frontend-build (webpack)
```

### 6.3 Production server (gunicorn)

```bash
cd projects/precis/precis-ctc/backend
make server             # gunicorn on 0.0.0.0:5070 (WSGI; SERVER_TYPE=asgi → uvicorn)
```

Tunables: `HOST`, `PORT`, `WORKERS` (4), `TIMEOUT` (120), `LOG_LEVEL`,
`SERVER_TYPE=wsgi|asgi`.

---

## 7. Docker

```bash
cd projects/precis/precis-ctc
make build              # install-assets + build-assets + docker compose build
make up                 # docker compose up -d
make status             # docker compose ps
make logs               # tail all logs
make down
make rebuild-backend    # rebuild backend + worker without cache
make rebuild-frontend   # rebuild frontend without cache
```

---

## 8. Common tasks

| Task | Command (from `backend/`) |
|------|---------------------------|
| Django shell | `make shell` |
| Format code | `make format` (ruff) |
| Lint unused imports | `make lint` |
| Reset DB (destructive!) | `make reset-db` |
| Clean caches | `make clean-python` |
| APScheduler runner | `make scheduler` |

---

## 9. Troubleshooting

### Pages empty after fresh migrate

Run the data populator — the page/catalog tree is created by it:

```bash
cd projects/precis/precis-ctc/backend
make populate-data
```

### Bundles not found / blank CSS

```bash
cd projects/precis/precis-ctc
make build-assets
```

### Port conflict

```bash
lsof -ti :5070 | xargs kill -9
PORT=5080 make dev
```

### Confusing CTC with Precis LMS state

CTC is standalone: its database is `db_precis_ctc`, its settings are self-contained,
and its Compose stack is independent. Do not point it at Precis/LMS runtime
databases or volumes.

---

## 10. Shared assets, locales, and full-stack redeploy

CTC runtime media and Django-side bundles use the shared monorepo asset tree:

```text
projects/assets/media/ctc-research/
projects/assets/bundles/ctc-research/
```

Generate the target locale catalogs and compiled files with:

```bash
cd projects/precis/precis-ctc
python3 scripts/generate_locales.py
```

The command reports exact, pattern, and English-fallback coverage. Review
fallback entries with a qualified translator before publishing a locale.

For the full CTC stack (backend, Dramatiq worker, scheduler, and frontend):

```bash
cd projects/precis/precis-ctc
make redeploy
```

From the project dispatcher:

```bash
cd projects
make redeploy-with-stack WEBSITE=precis-ctc
```

See [ENVIRONMENT.md](ENVIRONMENT.md) for variable names, shared proxy mounts,
requirements, and safety/rollback remarks.

## See also

- [Project README](../README.md) — editions, features, quick start
- [CONTENTS.md](CONTENTS.md) — page and data map
- [ENHANCEMENTS.md](ENHANCEMENTS.md) — completed and proposed improvements
- [ENVIRONMENT.md](ENVIRONMENT.md) — environment and redeploy runbook
- [TEMPLATES.md](TEMPLATES.md) — template conventions
- [COMPONENTS.md](COMPONENTS.md) — component conventions
- [`../../../../libs/django-fusion/README.md`](../../../../libs/django-fusion/README.md) — component library

## Remarks & Notes

- The backend venv must be available before running Django checks; do not install dependencies globally as a workaround.
- `make redeploy` rebuilds and recreates containers but intentionally does not remove volumes or replace fixture data.
- The generated `.mo` files are runtime artifacts derived from the `.po` files; regenerate them whenever catalogs change.
