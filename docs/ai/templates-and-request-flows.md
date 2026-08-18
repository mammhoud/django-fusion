# Templates & Request Flows

> How the monorepo's reusable templates work and how a request travels through
> a Structa Cloud product (with Loop-CRM as the worked example).

<!-- AI-generated: review needed -->

## Part 1 — Templates

### 1.1 Documentation Templates (Diátaxis, repo-flavored)

The `structa-docs` skill defines the repo's document types. Every generated
document ends with a `## Remarks & Notes` section and AI-written sections carry
`<!-- AI-generated: review needed -->`.

| Template | Location | When to use |
|----------|----------|-------------|
| ADR / Decision | `docs/plans/` or `docs/decisions/` | Architecture decisions. Structure: Context → Options → Decision → Consequences → Remarks. Requires date + status (Proposed/Accepted/Superseded). |
| Architecture doc | follows `docs/ARCHITECTURE.md` style | Context/goals, diagrams, key decisions, data flow. |
| Runbook | `docs/guides/` | When-to-use → prerequisites → step-by-step → rollback → escalation, with real Makefile commands. |
| API doc | product `backend-api.md` | Endpoint reference with request/response, auth, errors, pagination, render contract. |
| Product guide | product `frontend.md` | Setup, key systems, common tasks, who to ask. |
| Session changelog | `docs/changelogs/session-YYYY-MM-DD.md` | Per-session summary with completed-task tables and commit list. |

### 1.2 Project Scaffold Templates

Each product follows a consistent layout:

```text
<product>/
├── Makefile               # project orchestration (dev/build/check/backend-*)
├── .env.example           # env contract (generated from configs/ package)
├── configs/               # dependency-free env catalog + validator (loop-crm)
├── Env/                   # site identity YAML + per-env overrides
├── docs/                  # product docs (DESIGN_SYSTEM.md, SETUP_AND_BUILD.md)
├── backend/
│   ├── settings.py        # bootstraps configs.site → configs.default
│   ├── configs/
│   │   ├── site.py        # site discovery + env seeding
│   │   └── default/       # the actual Django settings module
│   ├── Makefile           # dev/server/check/test/migrate/i18n
│   ├── locale/            # gettext catalogs (en, ar, …)
│   └── apps/<module>/     # models, forms, views, services, tables
└── frontend/
    ├── project.json       # Nx targets (build/check/test/dev/backend-*)
    ├── astro.config.mjs   # dev proxy → Django backend
    └── src/               # Astro shell + React islands
```

### 1.3 Env Config Template (loop-crm configs package)

`projects/loop-crm/configs/` is the canonical env contract, dependency-free:

```text
configs/
├── __init__.py    # architecture doc + re-exports
├── env.py         # ENV_VARS catalog (name, default, purpose) + env_defaults()
└── validate.py    # validate_environment() + render_env_example()
```

```bash
make configs       # sanity: prints catalog size
make validate-env  # checks current env against the catalog
make env-example   # regenerates .env.example.generated
```

### 1.4 Makefile Target Template

Project Makefiles expose a consistent verb set; Nx mirrors it:

```make
dev              # run frontend dev server
build            # build frontend
check            # frontend typecheck
backend-dev      # Django runserver (delegates to backend/Makefile)
backend-check    # Django system checks
backend-test     # Django test suite
backend-migrate  # makemigrations + migrate
backend-seed     # seed demo workspace
nx-check         # npx nx run loop-crm:check (Make → Nx)
```

Nx targets live in `frontend/project.json` with `nx:run-commands` executors
pointing `cwd` at the project root and `command` at the Makefile verb.

### 1.5 API Table Contract Template

Schema-aware fusion table JSON shared by both API roads:

```json
{
  "resource": "companies",
  "headers": [{ "key": "name", "label": "Name", "type": "text" }],
  "rows": [["Acme"]],
  "count": 1
}
```

`type` ∈ `text | money | date | pill | link`. Built by `RowGenerator` in
`apps/core/resource_tables.py` (per-resource column config, formatters, types).

## Part 2 — Request Flows

### 2.1 Render Road (Django render-first)

```text
Browser
  → Traefik / astro dev proxy (:4323 → :8001)
  → project urls.py
  → middleware (sessions, auth, CSRF, locale, HTMX)
  → fusion Application registry (loop_crm_module.url_pattern)
  → view (ListView/ResourceListView/fusion tables+forms)
  → template (base.html → dashboard/<screen>.html → fusion comps)
  → HTML response (or HTMX fragment)
```

Used by: companies, contacts, deals, invoices, payments, revenue, tasks —
the canonical road for the CRM screens. HTMX list/form partials swap
`#<resource>-section` and trigger OOB updates.

### 2.2 Data-API Roads

```text
Astro React island (ResourceTable.tsx, RevOpsDashboard, …)
  → fetch(`${apiPrefix}/tables/${resource}`)      # canonical: /bolt
  → 404/401? → fetch(`${fallbackPrefix}/tables/${resource}/`)  # /api/v1
  → JSON table contract → tactical table render
```

| Road | Path | Auth | Notes |
|------|------|------|-------|
| Bolt (canonical) | `/bolt/tables/{resource}` | JWT (Bearer) | Requires `django_bolt` installed; workspace-scoped. |
| Compat | `/api/v1/tables/{resource}/` | Session cookie | Django JSON road, always available. |
| Token | `/api/v1/auth/token/` | Session (POST) | Issues the compatibility JWT. |

### 2.3 HTMX Fragment Flow

```text
Screen interaction (create form / list refresh / status pill)
  → hx-post / hx-get / hx-target="#<id>"
  → /fragments/crm/<resource>/create/ (or list partial)
  → Django view → validated form → save → HTMX fragment + OOB swap
```

Fragments are routed under `/fragments/...` and proxied through the Astro shell.

### 2.4 Realtime Flow (SSE/WS)

```text
Browser (htmx-ext-sse / WebSocket)
  → /sse/workspace/<id>/events/ (SSE) or /ws/... (channels)
  → Redis channel layer (compose/prod) or InMemoryChannelLayer (dev fallback)
  → event published via safe_publish_workspace_event
  → live-sync chip flips "synced", tables refetch
```

### 2.5 Auth Flow (allauth)

```text
GET /accounts/login/ → login page (demo credentials surfaced in DEMO_MODE)
POST /accounts/login/ → allauth LoginView
  → cache rate-limiter (Redis or LocMem fallback)
  → session cookie (DB-backed sessions)
  → redirect → LOGIN_REDIRECT_URL (/overview/)
```

Redis-free: `_redis_reachable()` performs a RESP PING probe; when Redis is
missing or a non-Redis listener squats the port, DEBUG falls back to LocMem
cache + in-memory channel layer so login never 500s.

### 2.6 i18n / Translation Flow

```text
Code: gettext_lazy(_("…")) in models/forms/views
  → make i18n (backend): makemessages → locale/<lang>/LC_MESSAGES/django.po
  → translate → compilemessages → django.mo
  → LocaleMiddleware picks language from Accept-Language / ?lang= / session
```

## Part 3 — Request Flow Diagram (Loop-CRM)

```text
                           ┌──────────────────────────────┐
                           │      Astro static shell      │
                           │  [...path].astro + islands   │
                           └──────┬───────────────┬───────┘
                                  │ proxy         │ fetch
                    /fragments /api /bolt /accounts│
                                  ▼               ▼
                           ┌──────────────────────────────┐
                           │     Django backend (:8001)    │
                           │  fusion registry → views →    │
                           │  templates / JSON roads       │
                           └──────┬───────────┬───────────┘
                                  │           │
                          cache/channels    PostgreSQL/SQLite
                          (Redis or LocMem/in-memory fallback)
```

## Remarks & Notes

- Always check the owning product's `AGENTS.md` before choosing a template or
  flow — nearest file wins for local details.
- `make -n <target>` dry-runs a Makefile command before executing it.
- Nx execution requires root `npm install` (root `node_modules` absent in the
  current workspace); the Nx wiring is validated with `make -n nx-*`.
- Multi-line `{% comp %}` tags break Django's template lexer — keep them on a
  single line.
