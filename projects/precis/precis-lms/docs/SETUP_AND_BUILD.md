# Precis LMS — Setup & Build Guide

> **Path:** `projects/precis/precis-lms/`
> **Stack:** Django 5.2 + Wagtail 7.4 + django-fusion (backend) · Astro 5 (frontend)
> **Backend port:** 5071 · **Frontend port:** 3002

This guide walks through a fresh clone to a running Precis LMS instance,
then through the production build, in small, verifiable steps.

---

## 1. Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | ≥ 3.11 | Backend runtime (workspace requirement) |
| [uv](https://docs.astral.sh/uv/) | latest | Python environment + dependency management |
| Node.js | 20/22 | Astro frontend + webpack assets |
| npm | 10+ | Frontend package manager |
| Docker (optional) | latest | Containerized stack (`make up`) |
| tmux (optional) | any | Multi-pane dev env (used by other projects) |

Check the workspace toolchain:

```bash
python3 --version   # 3.11+
uv --version
node --version
npm --version
```

> The backend depends on the workspace venv defined by
> `projects/pyproject.toml` (`websites-workspace`). `uv` resolves the
> workspace root automatically from any path under `projects/`.

---

## 2. Install dependencies

### 2.1 Python (backend)

```bash
cd projects/precis/precis-lms/backend
make install
```

`make install` runs `uv sync` for the workspace and installs the local
`django-fusion` library in editable mode.

If you prefer raw commands (same effect):

```bash
uv --project ../.. sync
cd ../../libs/django-fusion && uv pip install -e .
```

### 2.2 Frontend (Astro)

```bash
cd projects/precis/precis-lms/frontend
npm install
```

### 2.3 Frontend assets (webpack, Django-side SCSS/JS)

From the project root:

```bash
cd projects/precis/precis-lms
make install-assets    # npm install at project root (webpack deps)
make build-assets      # webpack production build + skeleton manifest
```

`make build-assets` depends on `skeleton-manifest`, which runs
`generate_skeleton_manifest` against the Django backend. Run it before the
first Django render so template skeletons resolve.

---

## 3. Database

### 3.1 Migrate

```bash
cd projects/precis/precis-lms/backend
make migrate          # makemigrations --noinput + migrate --noinput
```

Raw equivalent:

```bash
uv run --project ../.. python manage.py makemigrations --noinput
uv run --project ../.. python manage.py migrate --noinput
```

### 3.2 Populate data (optional but recommended)

```bash
make populate-data          # pages + test data
make populate-data-pages-only   # pages only
make populate-data-test-only    # test data only
make populate-data-clear        # remove populated data
```

> `populate-data` seeds Wagtail pages, course catalog content, and demo
> records. Run it once after `migrate` so the site has real pages to render.

### 3.3 Create a superuser

```bash
make superuser              # interactive
# or non-interactive:
DJANGO_SUPERUSER_PASSWORD=... uv run --project ../.. python manage.py createsuperuser --noinput
```

---

## 4. Run in development

### 4.1 Backend (Django)

```bash
cd projects/precis/precis-lms/backend
make dev                 # http://localhost:5071
```

Override the port with `PORT`:

```bash
PORT=8080 make dev
```

Verify:

```bash
curl -s http://localhost:5071/ | head -20        # homepage
open http://localhost:5071/admin/                 # Wagtail admin
```

### 4.2 Frontend (Astro)

In a second terminal:

```bash
cd projects/precis/precis-lms/frontend
npm run dev              # http://localhost:3002
```

### 4.3 One-shot from the project root

```bash
cd projects/precis/precis-lms
make run-dev             # backend dev server (delegates to backend/Makefile)
make frontend-dev        # astro dev server
```

### 4.4 Running Django checks

```bash
cd projects/precis/precis-lms/backend
make check               # python manage.py check
```

---

## 5. Tests

```bash
cd projects/precis/precis-lms/backend
make test                # workspace test runner (tests.runner)
make test-quick          # same, less output
make test-url URL=http://localhost:5071   # test against a live server
```

Frontend smoke tests:

```bash
cd projects/precis/precis-lms/frontend
npm test                 # node --test tests/frontend-smoke.test.mjs
npm run test:e2e         # node --test tests/e2e.test.mjs
npx playwright test      # full Playwright suite (needs servers running)
```

---

## 6. Production build

### 6.1 Frontend production build

```bash
cd projects/precis/precis-lms/frontend
npm run build            # → frontend/dist/
npm run preview          # preview the static build
```

### 6.2 Backend static + assets

```bash
cd projects/precis/precis-lms/backend
make collectstatic       # collect static incl. webpack bundles
make assets-setup        # frontend-install + frontend-build (webpack)
```

### 6.3 Production server (gunicorn)

```bash
cd projects/precis/precis-lms/backend
make server              # gunicorn, WSGI by default; SERVER_TYPE=asgi → uvicorn
```

Tunables: `HOST`, `PORT`, `WORKERS` (default 4), `TIMEOUT` (120),
`LOG_LEVEL`, `SERVER_TYPE=wsgi|asgi`, `DB_NAME_PRECIS_LMS`.

> `make server` validates/rebuilds webpack bundles (`webpack-validate`) and
> populates data before binding, so a fresh container starts with a
> renderable site.

---

## 7. Docker

```bash
cd projects/precis/precis-lms
make build               # install-assets + build-assets + docker compose build
make up                  # docker compose up -d
make status              # docker compose ps
make logs                # tail all service logs
make front-logs          # frontend logs only
make back-logs           # backend logs only
make worker-logs         # worker logs only
make restart
make down
```

Rebuild specific images without cache:

```bash
make rebuild-backend     # backend + worker
make rebuild-frontend    # frontend
```

---

## 8. Common tasks

| Task | Command (from `backend/`) |
|------|---------------------------|
| Django shell | `make shell` (shell_plus if available) |
| Format code | `make format` (ruff format) |
| Lint unused imports | `make lint` |
| Fix lint issues | `make fix` |
| Reset DB (destructive!) | `make reset-db` |
| Clean caches | `make clean-python` |
| Reset migrations (destructive!) | `make reset-migrations` |
| APScheduler runner | `make scheduler` |
| Show env wiring | `make env-show` |

---

## 9. Troubleshooting

### Broken venv

The Makefile auto-detects and removes a broken `.venv` on `dev`/`install`.
If you still hit import errors, remove it manually:

```bash
rm -rf projects/precis/precis-lms/.venv
cd projects/precis/precis-lms/backend && make install
```

### `No module named 'django_fusion'`

The local `django-fusion` library is installed in editable mode by
`make install`. Re-run it:

```bash
cd projects/precis/precis-lms/backend && make install
```

### Bundles not found / blank CSS

Rebuild the webpack bundles:

```bash
cd projects/precis/precis-lms
make build-assets
```

### Port already in use

```bash
lsof -ti :5071 | xargs kill -9   # or pick another port
PORT=5080 make dev
```

### Pages render empty after fresh migrate

Run the data populator — the page tree is created by it, not by
`migrate` alone:

```bash
cd projects/precis/precis-lms/backend
make populate-data
```
