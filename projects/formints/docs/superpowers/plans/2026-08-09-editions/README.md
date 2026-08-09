# POS Editions — Plans Index

> **For agentic workers:** Each plan in this directory is self-contained and follows the writing-plans format. Execute them in order: Community → Standard → Pro → Cloud → pos-client. Each plan produces working, testable software on its own.

**Goal:** A complete plan for every POS edition — design, architecture, and data modeling per edition, modeled as an **extension chain** where each tier adds capabilities and schema on top of the previous one.

**Date:** 9 August 2026 · **Repo:** `projects/formints/`

## The extension chain

```
Community (formintA/)            pos-client (formintC/)          ← separate branch
  Astro 5 + React 19 · Tauri ·   Vue 3 client + Django shop
  Rust/Diesel · offline-first    (employee, shop apps)
        │                              │
        ▼                              │
Standard (merged into formint/)        │
  = Community capabilities +           │
  Django sidecar (48 models) +         │
  sync client · multi-currency ·       │
  tax profiles · custom roles ·        │
  CSV/JSON export                      │
        │                              │
        ▼                              │
Pro (formint/)                    ← same codebase as Standard (gated);
  adds CRM, fusion render-mode,   the full surface + reference data model
  Unfold admin, Channels WS,
  django-bolt
        │
        ▼
Cloud (formintB/, pos-cloud)
  hosted multi-tenant master:
  Organization → Branch hierarchy,
  async sync pipeline, backups +
  monitoring (this plan)
```

## Data model at each extension

| Edition | Schema | Core entities added at this tier | Plan file |
|---------|--------|----------------------------------|-----------|
| Community | Diesel/SQLite `restaurant.db` | `sales`, `sale_items`, `products`, `categories`, `customers`, `employees`, `ingredients`, `recipes`, `settings`, … | [`01-community.md`](01-community.md) |
| Standard | Django `full_*` (48 models) | `Node`, `Heartbeat`, `DeviceConfig`, `MasterDevice`, `CloudLink`, `SyncApproval`, `SyncLog`, loyalty/CRM basics, **+ `Currency`, `TaxProfile` (new)** | [`02-standard.md`](02-standard.md) |
| Pro | Django `full_*` (same 48 as Standard) | CRM: `Company`, `Pipeline`, `Stage`, `Contact`, `Deal`, `Activity`, `CRMNote`; fusion render-mode; Unfold admin — no schema delta over Standard | [`03-pro.md`](03-pro.md) |
| Cloud | Django `pos_cloud.db` | `Organization`, `Branch`, `Lead`, `Contact`, `Deal`, `InventoryReport`, `BranchReport`, `BranchSyncLog`, `BranchProduct`, `BranchSale`, `BranchInventory`, `DeviceToken`, `SyncConflict`, `SyncQueueItem`, **+ `BackupRun` (new)** | [`04-cloud.md`](04-cloud.md) |
| pos-client | Rust/Diesel + Django shop | Vue client tables + `Category`, `Product`, `Cart`, `CartItem`, `Order`, `OrderItem`, `Employee` | [`05-pos-client.md`](05-pos-client.md) |
| Community version | (generated from `formintA/`) | standalone `formint-community/` repo bundle — Formints Community rename + publish checklist | [`07-community-version.md`](07-community-version.md) |

## Execution order & dependencies

1. **Community** (`01-community.md`) — refunds & returns, offline-first mode. No dependencies.
2. **Standard** (`02-standard.md`) — money, tax, roles, export. No dependencies on Community code (different stack), but docs share `editions.md`.
3. **Pro** (`03-pro.md`) — docs accuracy + verification gate. Depends on Standard being merged (same codebase).
4. **Cloud** (`04-cloud.md`) — backups + monitoring. Independent; do after Pro to keep doc churn in one place.
5. **pos-client** (`05-pos-client.md`) — shop API tests + verification. Independent branch; can run in parallel with 1-4.

Each plan ends with the standard execution handoff (subagent-driven vs inline).

## Cross-cutting enhancements (added 9 Aug 2026)

Four dimensions apply across the edition plans:

1. **django-fusion everywhere.** New features ship with django-fusion `TableMixin`/`FormMixin` fragments (registered in `TABLE_COMPONENTS`/`FORM_COMPONENTS`), not just JSON controllers — see the fusion task in each applicable plan (02 B6, 04 C5, 05 D4). Community (01) is Rust-only and consumes the SDK instead.
2. **Modular TS/JS client bundle.** [`06-js-sdk.md`](06-js-sdk.md) builds `@formints/client` — a framework-agnostic, tree-shakeable fetch client with one module per resource (`currencies`, `taxProfiles`, `exports`, `monitor`). Each edition plan's SDK task wires it into its frontend.
3. **Complete Playwright e2e per edition.** One suite per edition, run separately: Community (01 A4, reuses `formintA/e2e/`), Standard (02 B8, new config in `formint/frontend/`), Cloud (04 C7, reuses `formintB/frontend/`), pos-client (05 D4, new config in `formintC/`).
4. **Feature inheritance (the "lower all features" rule).** Every higher edition MUST include all features of every tier below it. Stated as a hard constraint in each plan; each edition's final task includes a parity sweep that verifies the inheritance and fixes gaps.

New/changed files: [`06-js-sdk.md`](06-js-sdk.md) (new) · [`07-community-version.md`](07-community-version.md) (new — standalone community repo bundle + publish plan) · `01-community.md` (A4, A5) · `02-standard.md` (B6-B8) · `04-cloud.md` (C5-C7) · `05-pos-client.md` (D4-D5).
