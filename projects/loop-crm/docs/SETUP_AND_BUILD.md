# Loop-CRM — Setup & Build Guide

> **Path:** `projects/loop-crm/`
> **Stack:** Django + django-fusion + Dramatiq (backend) ·
> Astro 5 + Tailwind 4 + HTMX + Alpine + Redux + GSAP (frontend)
> **Backend port:** 8000 · **Frontend port:** 4321

Loop-CRM is the unified sales & marketing platform — a CRM (Twenty DNA) +
enterprise social media scheduling (Postiz DNA) in one source of truth for
revenue operations: **from social impression to closed deal, one platform.**

---

## 1. Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | ≥ 3.11 | Backend runtime |
| [uv](https://docs.astral.sh/uv/) | latest | Workspace venv + deps |
| Node.js | 20/22 | Astro frontend |
| npm | 10+ | Frontend package manager |
| Docker (optional) | latest | Postgres + Redis + Dramatiq worker stack |

```bash
python3 --version && uv --version && node --version && npm --version
```

---

## 2. Install dependencies

### 2.1 Backend (Django + django-fusion)

```bash
cd projects/loop-crm/backend
make install            # uv sync in the workspace (projects/)
```

### 2.2 Frontend (Astro)

```bash
cd projects/loop-crm/frontend
npm install
```

---

## 3. Database & seed

### 3.1 SQLite (default dev)

```bash
cd projects/loop-crm/backend
make migrate            # makemigrations --noinput + migrate --noinput
make seed-demo          # seed demo workspace + demo accounts (idempotent, superuser)
make superuser          # interactive admin user (if not using seed-demo)
```

### 3.2 PostgreSQL + Redis (cluster, optional)

```bash
# From the project root — bring up the Compose stack (Django + Postgres + Redis + Dramatiq)
cd projects/loop-crm
docker compose up -d --build
export USE_POSTGRES=1
cd backend && make migrate
```

---

## 4. Run in development

### 4.1 Backend (Django)

```bash
cd projects/loop-crm/backend
make dev                # http://localhost:8000
```

### 4.2 Background worker (Dramatiq)

```bash
cd projects/loop-crm/backend
make worker             # rundramatiq --processes 2 --threads 4
```

### 4.3 Frontend (Astro)

In a second terminal:

```bash
cd projects/loop-crm/frontend
npm run dev             # http://localhost:4321 — proxies /api|/admin|/fragment(s) → :8000
```

### 4.4 From the project root

```bash
cd projects/loop-crm
make dev                # Astro dev
make backend-dev        # Django dev server
make backend-check      # django system checks
make backend-migrate
make backend-test
make backend-help
```

---

## 5. Verification

```bash
cd projects/loop-crm/backend
make check              # django check
make test               # manage.py test apps (interactions + live HTTP E2E)
```

```bash
cd projects/loop-crm/frontend
npm run check           # astro check
npm test                # node --test tests/*.test.mjs
npx playwright test     # full E2E (needs backend + frontend running)
```

---

## 6. Production build

```bash
cd projects/loop-crm/frontend
npm run build           # → frontend/dist/
npm run preview         # preview the build
```

Backend production server:

```bash
cd projects/loop-crm/backend
make server             # gunicorn on 0.0.0.0:8000 (WSGI)
make collectstatic      # collectstatic --noinput
```

Docker deployment:

```bash
cd projects/loop-crm
cp .env.example .env
# Set DJANGO_SECRET_KEY, POSTGRES_PASSWORD, FUSION_BOLT_JWT_SECRET
docker compose config -q
docker compose up -d --build
docker compose ps
curl -fsS -H 'Host: crm.structa.cloud' http://127.0.0.1/
```

> Do not use the example secret values in a public deployment. DNS for
> `crm.structa.cloud` and `www.crm.structa.cloud` must point at the Traefik
> host.

---

## 7. API modes

### Optional Bolt API (`/bolt/`, JWT bearer)

```bash
pip install 'django-fusion[bolt]'
```

Set `FUSION_BOLT_JWT_SECRET` to a dedicated production secret. Login via
allauth, then exchange the session for a user-bound token pair:

```bash
curl -c cookies.txt -X POST http://localhost:8000/accounts/login/ \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'login=member@example.com&password=your-password'
curl -b cookies.txt -X POST http://localhost:8000/api/v1/auth/token/ \
  -H 'Content-Type: application/json' -d '{}'
curl http://localhost:8000/api/v1/auth/me/ \
  -H 'Authorization: Bearer <access-token>'
```

The frontend `BoltApiClient` keeps the access/refresh pair in session
storage, rotates before expiry, retries one 401, then clears auth state and
falls back to `/api/v1`.

### Key endpoints

| Path | Purpose |
|------|---------|
| `/accounts/login|signup|logout/` | allauth |
| `/account/profile/` | Role + effective permissions |
| `/crm`, `/marketing`, `/finance`, `/settings` | Module screens |
| `/finance/invoices/`, `/payments/`, `/revenue/` | Finance surface |
| `/tasks/` | Task Center (authenticated, merged job history) |
| `/fragments/navigation/` | HTMX navigator preload |
| `/api/v1/*` · `/bolt/*` | JSON APIs |

---

## 8. Common tasks

| Task | Command (from `backend/`) |
|------|---------------------------|
| Django shell | `make shell` |
| Format code | `make format` (ruff) |
| Lint | `make lint` |
| Auto-fix lint | `make fix` |
| APScheduler runner | `make scheduler` |

---

## 9. Troubleshooting

### Frontend can't reach the API

The Astro dev server proxies `/api`, `/admin`, `/fragment(s)` to `:8000`.
Start the backend first, then check:

```bash
curl -s http://localhost:8000/api/v1/ | head -20
```

### Dashboard redirects to login

Dashboard pages and data APIs require a session. Create/login a user:

```bash
cd projects/loop-crm/backend
make seed-demo          # creates demo workspace + accounts
```

### Kanban move fails with CSRF error

The board echoes the `csrftoken` cookie as `X-CSRFToken`. If it fails, log
out/in again to refresh the cookie, or check the browser is sending it.

### 401 from Bolt API

Refresh tokens are rejected on protected routes by design. Exchange a fresh
token pair after login; check `FUSION_BOLT_JWT_SECRET` is set consistently.

### Dramatiq tasks not running

Start the worker:

```bash
cd projects/loop-crm/backend
make worker
```

---

## See also

- [Project README](../README.md) — architecture notes, tenancy, API modes
- [`docs/plans/loop-crm/merge-plan.md`](../../docs/plans/loop-crm/merge-plan.md) — 18-week roadmap
- [`../../libs/django-fusion/README.md`](../../libs/django-fusion/README.md) — component library
