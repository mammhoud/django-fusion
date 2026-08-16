# Formints Editions — Plans Index (canonical, latest)

> **For agentic workers:** Each plan in this directory is self-contained and follows the writing-plans format. Execute them in order: Community → Standard → Pro → Cloud → pos-client. Each plan produces working, testable software on its own. This index is the **canonical** Formints home; the retired `docs/plans/pos/` product plans were superseded and deleted (2026-08-14).

**Goal:** A complete plan for every Formints edition — design, architecture, and data modeling per edition, modeled as an **extension chain** where each tier adds capabilities and schema on top of the previous one.

**Date:** 14 August 2026 · **Source project:** `projects/formints/` (canonical; `projects/pos/` is retired)

> **Recent:** Cross-referenced with the [django-fusion Tasks & MCP plan](../django-fusion/django-fusion-tasks-mcp-plan.md) (2026-08-10) — background task infrastructure, Celery→Dramatiq replacement, and MCP task tooling now govern all async work across Django editions.
>
> **Architecture update (16 Aug 2026):** All editions now live under canonical `projects/formints/` paths with **short directory names** — `community`, `standard`, `pro`, `cloud`, `client` (renamed from `formint-community`, `formint-standard`, `formint-pro`, `formint-cloud`, `formint-client` in `de5ff0821`). Standard is **Rust/Diesel-first with an optional Django sidecar**; Pro (merged `pos-full` + `pos-solo`) is the first edition with a required Django backend; Cloud is the schema-per-tenant master. The retired `projects/pos/` plans are superseded by this chain (deleted 2026-08-14).

## The extension chain

```
Community (community/)               pos-client (client/)           ← separate branch
  Frontend: Astro 5 + React 19      Frontend: Vue 3
  Backend:  Rust/Diesel + SQLite    Backend:  Django shop
  No sidecar · offline-first        (employee, shop apps)
        │                                   │
        ▼                                   │
Standard (standard/)                        │
  Frontend: Astro 5 + React 19 + Alpine     │
  Backend:  Rust/Diesel + SQLite (primary)  │
  Sidecar:  Django (optional — sync/cloud)  │
  = Community capabilities +                │
  multi-currency · tax profiles ·           │
  custom roles · CSV/JSON export ·          │
  offline sync queue                        │
        │                                   │
        ▼                                   │
Pro (pro/ — merged pos-full+pos-solo)        │
  Frontend: Astro 5 + Alpine + HTMX         │
  Backend:  Django (required) + django-fusion│
            + django-bolt + Unfold admin    │
  adds CRM, fusion render-mode, Channels WS,│
  full multi-terminal operation             │
        │
        ▼
Cloud (cloud/)
  Frontend: Astro 5 + Alpine
  Backend:  Django (multi-tenant, Channels)
  hosted master: Organization → Branch
  hierarchy, async sync pipeline,
  backups + monitoring
```

## Editions at a glance (frontend / backend / sidecar)

| Edition | Directory | Frontend | Backend (primary) | Sidecar |
|---------|-----------|----------|-------------------|---------|
| **Community** | `community/` | Astro 5 + React 19 | Rust/Diesel + SQLite | None |
| **Standard** | `standard/` | Astro 5 + React 19 + Alpine | Rust/Diesel + SQLite | Django (optional) |
| **Pro** | `pro/` | Astro 5 + Alpine + HTMX | Django + django-fusion + django-bolt + Unfold | Required |
| **Cloud** | `cloud/` | Astro 5 + Alpine | Django (multi-tenant, Channels) | Required |
| **pos-client** | `client/` | Vue 3 | Django shop | Required |
| **Community version** | (bundled from `community/`) | Rust/Diesel + SQLite | None | None |

## Data model at each extension

| Edition | Schema | Core entities added at this tier | Plan file |
|---------|--------|----------------------------------|-----------|
| Community | Diesel/SQLite `restaurant.db` | `sales`, `sale_items`, `products`, `categories`, `customers`, `employees`, `ingredients`, `recipes`, `settings`, … | [`01-community.md`](01-community.md) |
| Standard | Diesel/SQLite `restaurant.db` (primary) + optional Django `full_*` (48 models when sidecar enabled) | **Primary:** Rust `Currency`, `TaxProfile`, `Role` permissions, export engine. **Sidecar (optional):** `Node`, `Heartbeat`, `DeviceConfig`, `SyncApproval`, `SyncLog` | [`02-standard.md`](02-standard.md) |
| Pro | Django `full_*` (48 models) | CRM: `Company`, `Pipeline`, `Stage`, `Contact`, `Deal`, `Activity`, `CRMNote`; fusion render-mode; Unfold admin; **POS-KO gaming: `GamingStation`, `GamingToken`, `GamingSession`, `GamingQueueEntry`**; **gift cards: `GiftCard`, `GiftCardTransaction`**; **tables: `RestaurantTable`, `TableReservation`**; **delivery: `DeliveryProvider`, `DeliveryOrder`**; **time clock: `TimeClockEntry`**; **kiosk: `KioskSession`, `KioskCartItem`**; customer display + inventory forecasting are read-only (reuse `Sale`/`KitchenTicket`/`PurchaseOrder` — no new tables) | [`03-pro.md`](03-pro.md) |
| Cloud | Django `pos_cloud.db` | `Organization`, `Branch`, `Lead`, `Contact`, `Deal`, `InventoryReport`, `BranchReport`, `BranchSyncLog`, `BranchProduct`, `BranchSale`, `BranchInventory`, `DeviceToken`, `SyncConflict`, `SyncQueueItem`, `BackupRun`, **+ `Tenant`/`Domain` (schema registry), `BranchSettings` (new — see [08](08-tenant-schemas.md))** | [`04-cloud.md`](04-cloud.md) |
| Tenant schemas | PostgreSQL schemas (`django-tenants`) | `Tenant` (schema-per-Organization), `Domain` (host mapping), `BranchSettings` (complete per-branch config); flips on via `DB_ENGINE=django_tenants.postgresql_backend` | [`08-tenant-schemas.md`](08-tenant-schemas.md) |
| pos-client | Rust/Diesel + Django shop | Vue client tables + `Category`, `Product`, `Cart`, `CartItem`, `Order`, `OrderItem`, `Employee` | [`05-pos-client.md`](05-pos-client.md) |
| Community version | (generated from `community/`) | standalone `formint-community` repo bundle — Formints Community rename + publish checklist | [`07-community-version.md`](07-community-version.md) |

## Execution order & dependencies

1. **Community** (`01-community.md`) — refunds & returns, offline-first mode. No dependencies.
2. **Standard** (`02-standard.md`) — money, tax, roles, export. No dependencies on Community code; builds on the same Rust/Diesel patterns. Optional sidecar is additive.
3. **Pro** (`03-pro.md`) — the first edition with a required Django backend. Merged `pos-full` + `pos-solo`; gates up from Standard's optional-sidecar baseline to the full model surface.
4. **Cloud** (`04-cloud.md`) — backups + monitoring. Independent; do after Pro to keep doc churn in one place.
5. **pos-client** (`05-pos-client.md`) — shop API tests + verification. Independent branch; can run in parallel with 1-4.
6. **Tenant schemas** (`08-tenant-schemas.md`) — Cloud-side schema-per-tenant via django-tenants (Postgres flip-on).

Each plan ends with the standard execution handoff (subagent-driven vs inline).

## Cross-cutting enhancements (added 9 Aug 2026, updated 10 Aug 2026)

Five dimensions apply across the edition plans:

1. **django-fusion everywhere (Pro+).** django-fusion `TableMixin`/`FormMixin` fragments apply from Pro upward (required sidecar). Community (01) and Standard (02) are Rust/Diesel-first with no required sidecar — they use the modular TS SDK [`06-js-sdk.md`](06-js-sdk.md) instead. See fusion tasks in 04 C5, 05 D4.
2. **Modular TS/JS client bundle.** [`06-js-sdk.md`](06-js-sdk.md) builds `@formints/client` — a framework-agnostic, tree-shakeable fetch client with one module per resource (`currencies`, `taxProfiles`, `exports`, `monitor`). Each edition plan's SDK task wires it into its frontend.
3. **Complete Playwright e2e per edition.** One shared suite lives in the canonical [`projects/formints/tests/pos-e2e/`](../../projects/formints/tests/pos-e2e/) directory — one Playwright *project* per edition boots its own dev server and runs the cross-edition `frontends.spec.ts` smoke + interaction + screenshot. Cloud adds `cloud.spec.ts` (browser flows against the Django admin/monitor/analytics) and the `tests/sync/` contract suite (REST + WebSocket + `@formints/client` SDK). See [E2E & sync matrix](#e2e--sync-matrix) below.
4. **Feature inheritance (the "lower all features" rule).** Every higher edition MUST include all features of every tier below it. Stated as a hard constraint in each plan; each edition's final task includes a parity sweep that verifies the inheritance and fixes gaps.
5. **Unified background tasks via django-fusion (Pro+).** Celery is replaced by Dramatiq via the [`django-fusion Tasks & MCP plan`](../django-fusion/django-fusion-tasks-mcp-plan.md). Pro and Cloud (required Django sidecar) use `django_fusion.tasks.@task` for sync pushes, reports, scheduled backups, email dispatch. Community (01) and Standard (02) are Rust/Diesel-first — no background-task infrastructure needed. MCP tools (`task.inspect`, `task.queues`, `task.retry`) are available at `/fusion/mcp/tools/` on Pro and Cloud. AI advisory/reporting workflows follow the companion [`LLM & AI MCP enhancement plan`](../django-fusion/django-fusion-llm-mcp-enhancement-plan.md); they do not change offline POS authority, prices, stock, refunds, or DataToken synchronization without separate approval.

## E2E & sync matrix

Canonical suite: [`projects/formints/tests/pos-e2e/`](../../projects/formints/tests/pos-e2e/)
(Playwright, Chromium). One **project** per edition + one backend-sync project.
Run with `npx playwright test` from that directory (booting a backend first for
`formint-cloud-sync`).

| Edition | Playwright project | Dev server | Port | Coverage |
|---|---|---|---|---|
| Community | `formint-community` | Astro + React | 1420 | `frontends.spec.ts` smoke + interaction + screenshot |
| Standard | `formint-standard` | Astro + React | 1430 | `frontends.spec.ts` smoke + interaction + screenshot |
| Pro | `formint-pro` | Astro + Alpine + HTMX | 4321 | `frontends.spec.ts` smoke + interaction + screenshot |
| Cloud | `formint-cloud` | Astro + Alpine | 4323 | `frontends.spec.ts` + `cloud.spec.ts` (Django admin/monitor/analytics browser flows) |
| pos-client | `formint-client` | Vue 3 (Vite) | 1433 | `frontends.spec.ts` smoke + interaction + screenshot |
| Cloud sync (backend) | `formint-cloud-sync` | daphne :8767 + runserver :8082 | — | `tests/sync/` REST + WebSocket + SDK contract |

**Sync contract** (`tests/sync/cloud-sync.spec.ts` + `sdk.spec.ts`) — the cloud
master is the only edition with a sync surface, and it is the integration point
for every *other* edition + the SDK:

| Surface | Endpoint / module | Verified by |
|---|---|---|
| Health | `GET /health` | `cloud-sync.spec.ts` → `health reports healthy` |
| Stats | `GET /stats` | `cloud-sync.spec.ts` → `stats enumerates core models` |
| Monitor status | `GET /monitor/status` | `cloud-sync.spec.ts` + SDK `getMonitorStatus()` |
| Dashboard health/queue/conflicts | `GET /dashboard/*` | `cloud-sync.spec.ts` (arrays + counts) |
| Sync push → broadcast | `POST /sync/push` → `/ws/sync-events/` | `cloud-sync.spec.ts` (live `sync_event` WebSocket frame) |
| Node 404 | `POST /sync/push` unknown node | `cloud-sync.spec.ts` → 404 |
| SDK error path | `@formints/client` `createClient` | `sdk.spec.ts` → `ApiError` on 404 |
| SDK export URLs | `@formints/client` `exportUrl` | `sdk.spec.ts` (documented download links) |

Screenshots are written to `projects/formints/docs/screenshots/`:
`frontend/<edition>-home.png` (+ `-nav.png` when a visible nav link exists) and
`admin/cloud-*.png` (sync monitor, analytics, Unfold login).

New/changed files (10 Aug 2026): `01-community.md` · `02-standard.md` (major rewrite — Rust/Diesel-first, optional sidecar) · `03-pro.md` · `04-cloud.md` · `05-pos-client.md` · `06-js-sdk.md` · `07-community-version.md` · **`08-tenant-schemas.md` (new — schema-per-tenant via `django-tenants`, complete `BranchSettings`, Postgres flip-on)**.
