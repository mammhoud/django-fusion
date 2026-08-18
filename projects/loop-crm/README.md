# Loop-CRM — the unified sales & marketing platform

One platform that combines a modern CRM (Twenty DNA) with enterprise-grade
social media scheduling (Postiz DNA), creating a single source of truth for
revenue operations.

> **From social impression to closed deal — one platform, one source of truth.**

## Status

Foundation integrated. The domain models, django-fusion Site/Application
registry, shared module/sidebar navigation, finance ledger, RevOps dashboard
(revenue-trend card + funnel-to-board deep links), responsive Astro shell,
canonical optional django-bolt API, compatibility JSON API, workflow catalog,
provider-neutral connector surface, cross-module workflow actions, and
Dramatiq publishing boundary are in place. Multi-tenant isolation is enforced
end-to-end: every read/mutation path is workspace-scoped through
`apps/core/tenancy.py`, dashboard pages and data APIs require login, and the
kanban move mutation is CSRF-protected. A Wagtail-managed public landing
(`/cms/` editor → `/apis/pages/<slug>/` JSON → Astro), Stripe-backed SaaS
billing (`apps/billing`: checkout/portal/webhook, `/apis/billing/plans/`),
a `/reports/` catalog, and a `/settings/plan/` billing surface are shipped.
Provider OAuth credentials and concrete API adapters are intentionally the
next integration boundary (see `docs/plans/loop-crm/merge-plan.md`).

## Layout

```text
loop-crm/
├── backend/                 # Django + django-fusion (modular monolith)
│   ├── apps/
│   │   ├── core/            # Workspace tenancy, User (RBAC), AuditLog, navigation, workflows
│   │   ├── crm/             # Company, Contact, Pipeline, Deal, Activity, custom fields
│   │   ├── marketing/       # Campaign, SocialChannel, Post, Analytics
│   │   ├── attribution/     # Touchpoints + multi-touch weighting engines
│   │   ├── finance/         # Invoice, Payment, RevenueEvent + finance screens
│   │   ├── pos/             # Formint POS ingestion ledger
│   │   ├── billing/         # SaaS billing: Plan, BillingAccount, Seat + Stripe
│   │   ├── pages/           # Wagtail landing pages (public JSON road)
│   │   ├── content/         # Wagtail StreamField section blocks
│   │   └── tasks/           # Dramatiq actors (publish, aggregate, attribute)
│   └── templates/           # base.html + dashboard
├── frontend/                # Astro 5 + Tailwind 4 + HTMX + Alpine + Redux + GSAP
├── docker-compose.yml       # Django + Postgres + Redis + Dramatiq worker
└── Makefile                 # project dispatcher (dev | build | check | backend-*)
```

## Quick start

> 📖 Full step-by-step setup & build: [`docs/SETUP_AND_BUILD.md`](docs/SETUP_AND_BUILD.md)

```bash
# Backend (SQLite by default; USE_POSTGRES=1 for the cluster)
cd backend
make check            # Django system checks
make migrate          # makemigrations + migrate
make dev              # runserver on :8000
make test             # backend interactions + live HTTP E2E checks

# Frontend
cd ../frontend
npm install
npm run dev           # Astro on :4321, proxies /api|/admin|/fragment(s) to :8000
```

## Architecture notes

- **django-fusion replaces django-cotton** — `{% comp %}`, fragments, and the
  render-first / data-API pipeline come from `libs/django-fusion`.
- **Dramatiq replaces Temporal (Twenty) and BullMQ (Postiz)** as the single
  Dramatiq background runtime (`backend/plugins/workers/`).
- **Redux (RTK) is the client data source of truth** on the data road;
  Alpine + HTMX handle lightweight interactions and server-side DOM swaps.
- **django-bolt is the canonical API road when installed** at `/bolt/` with
  JWT bearer tokens and optional `X-API-Key` authentication. `/api/v1/` stays
  as a compatibility fallback for environments that do not install the
  optional `django-fusion[bolt]` extra.
- **Tenancy + auth are enforced, not assumed** — `Workspace` is the multi-tenant
  root on every domain record, and `apps/core/tenancy.py`
  (`current_workspace_id`) scopes every read/write path (render-first screens,
  `/api/v1/`, and `/bolt/`). Dashboard pages, read APIs, and mutations require
  a session; anonymous callers are redirected to `/accounts/login/`. The kanban
  drag-to-move POST is CSRF-protected: the board echoes the `csrftoken` cookie
  as `X-CSRFToken`, and the board payload sets that cookie via
  `ensure_csrf_cookie`.
- **Navigation is shared by contract** — `apps/core/navigation.py` drives
  Django and the top-level django-fusion `LoopCrmModule` → `LoopCrmApplication`
  route tree. `/fragments/navigation/` preloads the complete navigator through
  HTMX; Astro caches that response in session storage and updates only active
  classes/ARIA state after navigation.
- **Interactions are persisted, not mocked** — workflow definitions/runs live
  in `core.WorkflowDefinition`/`WorkflowRun`; the content calendar uses real
  `Post` records and guarded draft → approval → scheduled → publishing states.
  Empty states are explicit and never filled with placeholder data.
- **Extensibility** — `custom_attributes` JSON plus the custom-object catalog
  provide tenant-specific Twenty-style fields without provider lock-in.
- **Attribution + finance glue** — `crm.Deal.campaign` links a closed deal to
  the marketing campaign that influenced it; `apps/attribution` weights
  touchpoints; `apps/finance` records invoices, payments, and recognized
  revenue events. The deal-won workflow creates those records idempotently.
- **Task Center (dual storage)** — the Dramatiq backend dual-writes every
  execution to the shared `django_fusion` `BackgroundTaskLog` and the
  website-local `core.TaskExecution` record (both stamped with `site_name`).
  The authenticated `/tasks/` page merges the two via the reusable
  `django_fusion.tasks.views.TaskCenterView`, and `sync_task_history` mirrors
  the shared record into the website record idempotently.

## API modes

```bash
# Optional high-throughput API runtime
pip install 'django-fusion[bolt]'

# Sign in through allauth first, then exchange the authenticated session for
# a user-bound access/refresh pair (no arbitrary subject/device tokens).
curl -c cookies.txt -X POST http://localhost:8000/accounts/login/ \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'login=member@example.com&password=your-password'
curl -b cookies.txt -X POST http://localhost:8000/api/v1/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{}'

# Verify the bearer token against the live Django user and role profile.
curl http://localhost:8000/api/v1/auth/me/ \
  -H 'Authorization: Bearer <access-token>'
```

Set `FUSION_BOLT_JWT_SECRET` to a dedicated production secret. The local
`SECRET_KEY` fallback exists only to keep development friction low.The frontend `BoltApiClient` keeps the access/refresh pair in session storage,
rotates it before expiry, retries one 401 once, then clears auth state and
tries `PUBLIC_API_FALLBACK_PREFIX` (`/api/v1` by default). The backend resolves
JWT `sub` to an active Django user, checks live role/workspace claims, rejects
refresh tokens on protected routes, and never renders raw token values.

Allauth pages live at `/accounts/login/`, `/accounts/signup/`, and
`/accounts/logout/`; `/account/profile/` displays the current role and effective
permissions. Members and roles use django-tables2. Custom fields use persisted
`CustomFieldDefinition` metadata plus validated JSON values rather than a
polymorphic model dependency.


The finance surface is available at `/finance/`, `/finance/invoices/`,
`/finance/payments/`, and `/finance/revenue/`; the API exposes `invoices`,
`payments`, and `revenue` on both Bolt and `/api/v1/`, plus the read-only
revenue-trend aggregate (on `/bolt/revenue/trend` and `/api/v1/revenue/trend`)
that feeds the RevOps dashboard's recognized-revenue card. The Task Center lives at
`/tasks/` (authenticated) and shows the merged shared + website-record job
history. Playwright covers the CRM navigation shell, workflow mutations, and
content lifecycle.

The **public landing** is Wagtail-managed and rendered by Astro from
`/apis/pages/<slug>/` (editor at `/cms/`); the **billing** surface is
`/settings/plan/` (account + plan catalog) backed by `apps/billing`, with
`/billing/checkout/`, `/billing/portal/`, `/billing/webhook/stripe/`, and the
public `/apis/billing/plans/` catalog. The **report catalog** lives at
`/reports/` (`/apis/reports/`). See
[`docs/FUSION_FORMS_TABLES.md`](docs/FUSION_FORMS_TABLES.md) for the
fusion forms/tables usage and
[`docs/plans/loop-crm/wagtail-landing-plan.md`](../../docs/plans/loop-crm/wagtail-landing-plan.md)
for the billing/landing architecture.

## Docker deployment

The production Compose file runs the backend on the shared `common` and
`traefik-net` networks, applies migrations and static collection before
Gunicorn starts, runs the Dramatiq worker, and builds the Astro frontend.
Traefik exposes the site at `https://crm.structa.cloud` with backend priority
for `/crm`, `/marketing`, `/finance`, `/settings`, `/accounts`, `/fragments`,
`/api`, and `/bolt`.

```bash
cp .env.example .env
# Set DJANGO_SECRET_KEY, POSTGRES_PASSWORD, and FUSION_BOLT_JWT_SECRET.
docker compose config -q
docker compose up -d --build

docker compose ps
curl -fsS -H 'Host: crm.structa.cloud' http://127.0.0.1/
```

Do not use the example secret values in a public deployment. DNS for
`crm.structa.cloud` and `www.crm.structa.cloud` must point at the Traefik host.

## Documentation

- [**docs/SETUP_AND_BUILD.md**](docs/SETUP_AND_BUILD.md) — full step-by-step setup & build guide
- [**docs/FUSION_FORMS_TABLES.md**](docs/FUSION_FORMS_TABLES.md) — django-fusion forms/tables usage in Loop-CRM
- [**docs/DESIGN_SYSTEM.md**](docs/DESIGN_SYSTEM.md) — the Tactical Telemetry design system
- See the merge plan for the full 18-week roadmap and the Twenty/Postiz
  feature-merging matrix.
