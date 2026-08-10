# POS Editions — Plans Index

> **For agentic workers:** Each plan in this directory is self-contained and follows the writing-plans format. Execute them in order: Community → Standard → Pro → Cloud → pos-client. Each plan produces working, testable software on its own. This index is now the canonical home under `docs/plans/editions/`.

**Goal:** A complete plan for every POS edition — design, architecture, and data modeling per edition, modeled as an **extension chain** where each tier adds capabilities and schema on top of the previous one.

**Date:** 10 August 2026 · **Source project:** `projects/formints/`

> **Recent:** Cross-referenced with the [django-fusion Tasks & MCP plan](../django-fusion/django-fusion-tasks-mcp-plan.md) (2026-08-10) — background task infrastructure, Celery→Dramatiq replacement, and MCP task tooling now govern all async work across Django editions.
>
> **Architecture update (10 Aug 2026):** Standard is now **Rust/Diesel-first with an optional Django sidecar** — it works standalone (no sidecar required) and can optionally connect to a sidecar for sync/cloud features. Pro is the first edition with a required Django sidecar.

## The extension chain

```
Community (formintA/)              pos-client (formintC/)          ← separate branch
  Frontend: Astro 5 + React 19      Frontend: Vue 3
  Backend:  Rust/Diesel + SQLite    Backend:  Django shop
  No sidecar · offline-first        (employee, shop apps)
        │                                   │
        ▼                                   │
Standard (formint/)                         │
  Frontend: Astro 5 + React 19 + Alpine     │
  Backend:  Rust/Diesel + SQLite (primary)  │
  Sidecar:  Django (optional — sync/cloud)  │
  = Community capabilities +                │
  multi-currency · tax profiles ·           │
  custom roles · CSV/JSON export ·          │
  offline sync queue                        │
        │                                   │
        ▼                                   │
Pro (formint/ — same codebase as Standard;  │
  gated up)                                 │
  Frontend: Astro 5 + Alpine + HTMX         │
  Backend:  Django sidecar (required, 48    │
            models) + django-fusion +       │
            django-bolt + Unfold admin      │
  adds CRM, fusion render-mode, Channels WS,│
  full multi-terminal operation             │
        │
        ▼
Cloud (formintB/, pos-cloud)
  Frontend: Astro 5 + Alpine
  Backend:  Django (multi-tenant, Channels)
  hosted master: Organization → Branch
  hierarchy, async sync pipeline,
  backups + monitoring
```

## Editions at a glance (frontend / backend / sidecar)

| Edition | Frontend | Backend (primary) | Sidecar | Stack |
|---------|----------|-------------------|---------|-------|
| **Community** | Astro 5 + React 19 | Rust/Diesel + SQLite | None | Tauri 2 desktop |
| **Standard** | Astro 5 + React 19 + Alpine | Rust/Diesel + SQLite | Django (optional — sync/cloud) | Tauri 2 + optional Django |
| **Pro** | Astro 5 + Alpine + HTMX | Django (full, 48 models) | Required — django-fusion, django-bolt, Unfold | Django + Tauri shell |
| **Cloud** | Astro 5 + Alpine | Django (multi-tenant) | Required — Channels, django-fusion | Django + Daphne |
| **pos-client** | Vue 3 | Django shop | Required — Django API | Vue SPA + Django |
| **Community version** | (bundled from formintA/) | Rust/Diesel + SQLite | None | Standalone repo bundle |

## Data model at each extension

| Edition | Schema | Core entities added at this tier | Plan file |
|---------|--------|----------------------------------|-----------|
| Community | Diesel/SQLite `restaurant.db` | `sales`, `sale_items`, `products`, `categories`, `customers`, `employees`, `ingredients`, `recipes`, `settings`, … | [`01-community.md`](01-community.md) |
| Standard | Diesel/SQLite `restaurant.db` (primary) + optional Django `full_*` (48 models when sidecar enabled) | **Primary:** Rust `Currency`, `TaxProfile`, `Role` permissions, export engine. **Sidecar (optional):** `Node`, `Heartbeat`, `DeviceConfig`, `SyncApproval`, `SyncLog` | [`02-standard.md`](02-standard.md) |
| Pro | Django `full_*` (48 models) | CRM: `Company`, `Pipeline`, `Stage`, `Contact`, `Deal`, `Activity`, `CRMNote`; fusion render-mode; Unfold admin | [`03-pro.md`](03-pro.md) |
| Cloud | Django `pos_cloud.db` | `Organization`, `Branch`, `Lead`, `Contact`, `Deal`, `InventoryReport`, `BranchReport`, `BranchSyncLog`, `BranchProduct`, `BranchSale`, `BranchInventory`, `DeviceToken`, `SyncConflict`, `SyncQueueItem`, **+ `BackupRun` (new)** | [`04-cloud.md`](04-cloud.md) |
| pos-client | Rust/Diesel + Django shop | Vue client tables + `Category`, `Product`, `Cart`, `CartItem`, `Order`, `OrderItem`, `Employee` | [`05-pos-client.md`](05-pos-client.md) |
| Community version | (generated from `formintA/`) | standalone `formint-community/` repo bundle — Formints Community rename + publish checklist | [`07-community-version.md`](07-community-version.md) |

## Execution order & dependencies

1. **Community** (`01-community.md`) — refunds & returns, offline-first mode. No dependencies.
2. **Standard** (`02-standard.md`) — money, tax, roles, export. No dependencies on Community code; builds on the same Rust/Diesel patterns. Optional sidecar is additive.
3. **Pro** (`03-pro.md`) — the first edition with a required Django sidecar. Shares the `formint/` codebase with Standard; gates up from Standard's optional-sidecar baseline to the full 48-model surface.
4. **Cloud** (`04-cloud.md`) — backups + monitoring. Independent; do after Pro to keep doc churn in one place.
5. **pos-client** (`05-pos-client.md`) — shop API tests + verification. Independent branch; can run in parallel with 1-4.

Each plan ends with the standard execution handoff (subagent-driven vs inline).

## Cross-cutting enhancements (added 9 Aug 2026, updated 10 Aug 2026)

Five dimensions apply across the edition plans:

1. **django-fusion everywhere (Pro+).** django-fusion `TableMixin`/`FormMixin` fragments apply from Pro upward (required sidecar). Community (01) and Standard (02) are Rust/Diesel-first with no required sidecar — they use the modular TS SDK [`06-js-sdk.md`](06-js-sdk.md) instead. See fusion tasks in 04 C5, 05 D4.
2. **Modular TS/JS client bundle.** [`06-js-sdk.md`](06-js-sdk.md) builds `@formints/client` — a framework-agnostic, tree-shakeable fetch client with one module per resource (`currencies`, `taxProfiles`, `exports`, `monitor`). Each edition plan's SDK task wires it into its frontend.
3. **Complete Playwright e2e per edition.** One suite per edition, run separately: Community (01 A4, reuses `formintA/e2e/`), Standard (02 B8, new config in `formint/frontend/`), Cloud (04 C7, reuses `formintB/frontend/`), pos-client (05 D4, new config in `formintC/`).
4. **Feature inheritance (the "lower all features" rule).** Every higher edition MUST include all features of every tier below it. Stated as a hard constraint in each plan; each edition's final task includes a parity sweep that verifies the inheritance and fixes gaps.
5. **Unified background tasks via django-fusion (Pro+).** Celery is replaced by Dramatiq via the [`django-fusion Tasks & MCP plan`](../django-fusion/django-fusion-tasks-mcp-plan.md). Pro and Cloud (required Django sidecar) use `django_fusion.tasks.@task` for sync pushes, reports, scheduled backups, email dispatch. Community (01) and Standard (02) are Rust/Diesel-first — no background-task infrastructure needed. MCP tools (`task.inspect`, `task.queues`, `task.retry`) are available at `/fusion/mcp/tools/` on Pro and Cloud. AI advisory/reporting workflows follow the companion [`LLM & AI MCP enhancement plan`](../django-fusion/django-fusion-llm-mcp-enhancement-plan.md); they do not change offline POS authority, prices, stock, refunds, or DataToken synchronization without separate approval.

New/changed files (10 Aug 2026): `01-community.md` · `02-standard.md` (major rewrite — Rust/Diesel-first, optional sidecar) · `03-pro.md` · `04-cloud.md` · `05-pos-client.md` · `06-js-sdk.md` · `07-community-version.md`.
