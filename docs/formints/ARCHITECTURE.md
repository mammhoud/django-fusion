# Formints POS — Architecture Decision Record

> **Status:** Active (2026-08-10)
> **Product:** Formints restaurant point-of-sale platform
> **Path:** `projects/formints/`
> **Editions:** Community → Standard → Pro → Cloud → Client
> **Updated:** 10 August 2026

---

## Context

Formints is a multi-edition restaurant POS platform. Each edition shares core
POS operations (sales, products, customers, inventory) but adds capabilities
along an extension chain. The platform spans native desktop (Tauri 2 + Rust),
server-side rendering (Django + django-fusion), and cloud multi-tenancy
(Django + Channels).

## Goals

- **Edition chain.** Each tier builds on the previous: Community (offline-first)
  → Standard (multi-currency, tax) → Pro (CRM, multi-terminal) → Cloud (SaaS).
- **Offline-first where possible.** Community and Standard run entirely on-device
  via Tauri + Rust/Diesel + SQLite; no server required.
- **Progressive sidecar adoption.** Standard adds an optional Django sidecar;
  Pro requires it. Community has none.
- **DataToken Shell.** Offline mutations are tagged for sync via a local
  `sync_queue` table; sidecar reconnect flushes pending items.
- **Modular JS SDK.** `@formints/client` provides framework-agnostic API
  clients per resource (currencies, taxProfiles, exports, monitor).
- **Shared conventions.** All editions use typed API contracts, Fusion response
  envelopes, and vertical-slice development (model → API → UI → test).

---

## Architecture Decisions

### ADR-1: Five-edition extension chain

**Decision:** The POS surface is delivered as five editions, each extending
the one below it. A single `projects/formints/` monorepo owns all editions,
with a root Makefile dispatching per-edition targets.

```
Community (Tauri + React + Rust/Diesel + SQLite)
  No sidecar. Offline-first desktop POS.
  │
  ▼
Standard (Community + multi-currency, tax, roles, export, sync queue)
  Optional Django sidecar for cloud sync.
  │
  ▼
Pro (Standard + CRM, fusion fragments, Unfold admin, Channels WS)
  Required Django sidecar with 48 models.
  │
  ▼
Cloud (Pro + multi-tenant, Organization→Branch, async sync, backup)
  Django + Channels ASGI. Hosted SaaS.
  │
  └── Client (Vue 3 + Django shop — separate branch, employee-facing)
```

**Rationale:**
- A single monorepo avoids code drift between editions.
- Each edition is independently buildable and testable.
- The extension model matches the business: users start with Community and
  upgrade through Standard → Pro → Cloud.

**Trade-offs:**
- Synchronizing shared Rust/TypeScript types across editions requires
  discipline.
- The Pro edition's `formint/` package serves both Standard and Pro gated
  surfaces — feature flags prevent Standard users from accessing Pro models.

### ADR-2: Community is Rust/Diesel-only (no Python)

**Decision:** `formint-community` has zero Python runtime. All data operations
flow through Tauri `invoke` → Rust → Diesel → SQLite.

**Architecture:**

```
React 19 Frontend
  │  invoke('create_sale', { items: [...] })
  ▼
Tauri 2 IPC Bridge
  │
  ▼
Rust Command Handler (lib.rs — 80+ commands)
  │
  ▼
Diesel ORM → SQLite (restaurant.db)
  │
  ▼
Response → JSON → React state update
```

**Rationale:**
- Single binary deployment — no Python, no Docker, no pip.
- Offline-first: all data lives in local SQLite.
- Fast: Rust/Diesel compiles to native code with zero network latency.

**Key modules** (27 operations):

| Module | Purpose |
|:-------|:--------|
| `sales.rs` | Create/void/refund sales, sale items |
| `products.rs` | Product CRUD, variants, pricing |
| `customers.rs` | Customer profiles, loyalty |
| `employees.rs` | Staff management, roles |
| `inventory.rs` | Stock tracking, purchase orders |
| `recipes.rs` | Recipe management, ingredient costing |
| `kitchen_tickets.rs` | Kitchen display system |
| `settings.rs` | Store configuration, tax defaults |

### ADR-3: Standard is Rust-first with optional Django sidecar

**Decision:** `formint-standard` uses Rust/Diesel as its primary data layer.
A Django sidecar is optional — the edition works standalone and can optionally
connect to a sidecar for sync/cloud features.

**When sidecar is present:**

```
Standard Desktop
  │
  ├─ Primary: Rust/Diesel → SQLite (all CRUD)
  │
  └─ Optional: Django Sidecar
      ├─ POST /sync-proxy/sale/         ← DataToken tagging
      ├─ POST /sync-proxy/product/      ← multi-terminal sync
      └─ Sidecar reconnect:
          └─ flush_pending_sync()
              → reads sync_queue → POST to sidecar
              → Django creates DataToken rows
```

**Added capabilities over Community:**
- Multi-currency (currencies table, exchange rates, single-default enforcement)
- Tax profiles (rates, per-product assignment)
- Custom roles (permission-based, not preset tiers)
- CSV/JSON export engine
- Offline sync queue (`sync_queue` table)

### ADR-4: Fusion response envelope (shared API contract)

**Decision:** All Django API responses across Pro and Cloud editions use a
standardized Fusion envelope:

```json
{
  "status": "success" | "error",
  "message": "OK",
  "data": { ... }
}
```

For list endpoints, `data` contains `{ "count": N, "items": [...] }`.
The `@formints/client` SDK's `FormintsClient.request<T>()` unwraps this
envelope — callers receive `T` directly, never the raw envelope.

**Rationale:**
- Consistent error handling: the JS SDK always checks `res.ok` and throws
  `ApiError`; the envelope status field is a secondary signal for business
  errors.
- django-ninja schemas guarantee typed `data` payloads per endpoint.
- The FusionCodec variant (base64-encoded JSON via `X-Fusion-Codec` header)
  is available for desktop editions that need binary-safe transport.

**Trade-offs:**
- Adds a wrapper layer to every response — ~40 bytes overhead.
- Requires all consumers to unwrap before using data; the JS SDK handles
  this transparently.

### ADR-5: DataToken Shell for offline sync

**Decision:** When the Django sidecar is unreachable, mutations are tagged in
a local `sync_queue` table. A sidecar reconnect hook flushes pending items.
This is the "DataToken Shell" pattern — the SQLite table acts as a proxy
until the real DataToken row can be created on the Django side.

**Pipeline:**

```
Any data mutation (create/update/delete)
  │
  ▼
dispatch_mutation(resource_type, resource_id, action)
  │
  ├─ 1. Try sidecar API (POST /sync-proxy/{type}/)
  │     → Success: emit 'data-changed' event ✓
  │     → Failure: fall through...
  │
  ├─ 2. Tag with DataToken Shell
  │     → INSERT INTO sync_queue (resource_type, resource_id, action, payload)
  │
  └─ 3. Emit 'data-changed' Tauri event
        → Frontend refreshes without polling


Sidecar Reconnect:
  check_sidecar_health() → /health → "connected"
  flush_pending_sync()
    → get_pending_batch(limit=100)
    → POST each to /sync-proxy/{type}/
    → mark_flushed() on success, mark_failed() on error
    → Django sidecar creates real DataToken rows
```

**New components:**

| File | Purpose |
|:-----|:--------|
| `migrations/...sync_queue/up.sql` | `sync_queue` table + indexes |
| `operations/sync_queue.rs` | `tag_for_sync`, `get_pending_batch`, `mark_flushed`, `mark_failed`, `purge_flushed` |
| `operations/dispatcher.rs` | `dispatch_mutation` 3-tier pipeline |
| `operations/sidecar_reconnect.rs` | `flush_pending_sync`, `check_sidecar_health`, `pending_sync_count` |
| `Cargo.toml` | `ureq` dependency for HTTP |

**Tauri commands exposed:**
- `flush_pending_sync` — push pending to Django
- `check_sidecar_health_cmd` — returns "connected" or "disconnected"
- `pending_sync_count` — unflushed queue depth

### ADR-6: Pro is the reference Django tier

**Decision:** `formint-pro` has a required Django sidecar with django-fusion,
django-ninja, Unfold admin, and Channels WebSocket. It's the first edition
with full multi-terminal operation.

**Architecture:**

```
┌─ Astro 5 Frontend (:4321) ──────────────────────────────────────────┐
│  Astro pages (pos, admin, crm, hr, ops, kitchen, data)              │
│  Alpine.js + HTMX for interactivity                                 │
│  FusionDecoder → base64-encoded JSON via FusionCodec                │
│  SessionSync → cross-tab sync via BroadcastChannel                  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ proxy /api, /htmx, /fusion
                               ▼
┌─ Django Sidecar (:8767) ────────────────────────────────────────────┐
│  django-ninja → typed REST API with Fusion envelope                 │
│  django-fusion → tables, forms, fragments, render-mode              │
│  Unfold → admin dashboard                                           │
│  Channels → WebSocket multi-terminal sync                           │
│  ┌─ formint/ ─────────────────────────────────────────────────┐     │
│  │  controllers.py → 45+ ModelControllerBase CRUD endpoints    │     │
│  │  schemas.py → Ninja writable/patch factory                  │     │
│  │  components.py → django-fusion table/form components        │     │
│  │  fusion.py → render-mode/nav/assets parity                 │     │
│  │  handlers.py → Class-based HTMX fragment handlers          │     │
│  │  models/ → POS/CRM/HR/inventory/sync models                │     │
│  └────────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────┘

┌─ Tauri 2 Desktop Shell ─────────────────────────────────────────────┐
│  Wraps Astro frontend + Django sidecar as external binary            │
│  Single-install desktop app                                          │
└──────────────────────────────────────────────────────────────────────┘
```

**Key features over Standard:**
- CRM (leads, contacts, deals, pipeline)
- HR (staff scheduling, shifts, payroll)
- Unfold admin (modern Django admin theme)
- Fusion render-mode (precis-landing parity — `X-Fusion-Render-First` header)
- Channels WebSocket (real-time multi-terminal sync)
- 48 Django models

### ADR-7: Cloud is multi-tenant SaaS

**Decision:** `formint-cloud` serves multiple organizations from a single
Django instance with Channels ASGI. Each organization has branches; sync
flows from branch terminals → cloud master.

**Architecture:**

```
┌─ Organization ───────────────────────────────────────────────────────┐
│  ├── Branch A (Bar)   → terminals sync to cloud                     │
│  ├── Branch B (Kitchen) → terminals sync to cloud                   │
│  └── Branch C (Floor)  → terminals sync to cloud                    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─ Cloud Master (Daphne ASGI) ────────────────────────────────────────┐
│  Organization model → Branch model → per-branch data                 │
│  Channels WebSocket → real-time sync from terminals                  │
│  Sync Conflict resolution → timestamp-based, manual review fallback  │
│  Backup pipeline → sqlite .backup() + BackupRun audit                │
│  Monitoring → /monitor/status, @formints/client.getMonitorStatus()  │
└──────────────────────────────────────────────────────────────────────┘
```

**Cloud-specific models:**

| Model | Purpose |
|:------|:--------|
| `Organization` | Multi-tenant boundary, billing, plan tier |
| `Branch` | Physical location, sync config, timezone |
| `BranchSyncLog` | Append-only sync audit per branch |
| `BranchProduct`, `BranchSale`, `BranchInventory` | Synced data snapshots |
| `SyncConflict` | Conflict resolution queue |
| `SyncQueueItem` | Inbound sync processing queue |
| `BackupRun` | Database backup audit trail |

**Backup command:**

```bash
python manage.py backup_db
# → sqlite3.connect().backup() — online, no write locks
# → creates BackupRun row (status, size_bytes, timestamps)
# → Cloud defaults to SQLite; PostgreSQL via DATABASE_URL override
# → output: db.sqlite3.backup-2026-08-10.db
```

### ADR-8: Modular JS SDK (`@formints/client`)

**Decision:** A framework-agnostic TypeScript client package with one module
per API resource. Zero runtime dependencies (browser `fetch` only).
Tree-shakeable, consumes `FormintsClient` from `core.ts`.

**Package:** `projects/formints/packages/formints-client/`

```ts
import { createClient } from '@formints/client';
import { listCurrencies } from '@formints/client/currencies';
import { exportUrl } from '@formints/client/exports';
import { getMonitorStatus } from '@formints/client/monitor';

const client = createClient('http://127.0.0.1:8767');
const { items } = await listCurrencies(client);
const status = await getMonitorStatus(client);
const csv = exportUrl('http://127.0.0.1:8767', 'products', 'csv');
```

**Resource modules:**

| Module | Functions | API surface |
|:-------|:----------|:------------|
| `core.ts` | `createClient`, `ApiError` | Fetch wrapper |
| `currencies.ts` | `listCurrencies`, `createCurrency` | `/api/v1/currencies` |
| `taxProfiles.ts` | `listTaxProfiles` | `/api/v1/tax-profiles` |
| `exports.ts` | `exportUrl` | `/export/{resource}.csv?format=json` |
| `monitor.ts` | `getMonitorStatus` | `/monitor/status` |

**Validation:**

| Metric | Result |
|:-------|:------:|
| Tests | 6/6 pass (Vitest) |
| Typecheck | Clean (tsc --noEmit) |
| Build | 14 files in dist/ |
| Runtime deps | 0 |

### ADR-9: Vertical-slice development

**Decision:** Every feature follows the same slice: model/schema → API →
frontend type → test. No feature spans more than one edition without
deliberate choice.

```
1. Model/Schema
   ├─ Rust: db/migrations/ + db/schema.rs + db/models.rs + operations/<name>.rs
   └─ Django: apps/core/models.py + migration + schemas.py

2. API
   ├─ Rust: lib.rs → invoke_handler registration
   └─ Django: controllers.py + api.py URL registration

3. Frontend type
   ├─ TypeScript: types.ts or @formints/client module
   └─ Astro page: src/pages/<name>.astro

4. Test
   ├─ Rust: operations/<name>.rs bottom-of-file #[cfg(test)]
   ├─ Django: sidecar/tests/ or backend/apps/*/tests/
   ├─ Frontend: Vitest or Playwright
   └─ Integration: tests/pos-e2e/
```

---

## Edition Comparison

| Feature | Community | Standard | Pro | Cloud |
|:--------|:---------:|:--------:|:---:|:-----:|
| **Frontend** | React 19 | React 19 + Alpine | Astro 5 + Alpine/HTMX | Astro 5 + Alpine |
| **Backend** | Rust/Diesel | Rust/Diesel | Django (48 models) | Django (multi-tenant) |
| **Database** | SQLite | SQLite | PostgreSQL/SQLite | SQLite (PostgreSQL optional) |
| **Sidecar** | None | Optional Django | Required Django | Required Django |
| **Offline** | ✅ Full | ✅ Full | ❌ Hybrid | ❌ Server-only |
| **Multi-currency** | ❌ | ✅ | ✅ | ✅ |
| **Tax profiles** | ❌ | ✅ | ✅ | ✅ |
| **CRM** | ❌ | ❌ | ✅ | ✅ |
| **Multi-terminal** | ❌ | ❌ | ✅ (Channels) | ✅ (Channels) |
| **Multi-tenant** | ❌ | ❌ | ❌ | ✅ |
| **Backups** | Manual | Manual | Manual | ✅ (auto + audit) |
| **Sync queue** | ❌ | ✅ (DataToken Shell) | ✅ (Channels) | ✅ (Channels) |
| **JS SDK** | ❌ | ✅ (@formints/client) | ✅ (@formints/client) | ✅ (@formints/client) |

---

## Build & Deploy

### Community

```bash
cd projects/formints/formint-community
pnpm install
pnpm tauri dev            # Dev with hot reload
pnpm tauri build          # Production binary
pnpm test                 # Vitest
cargo check --manifest-path src-tauri/Cargo.toml
```

### Standard

```bash
cd projects/formints/formint-standard
pnpm install
pnpm dev                  # Astro dev + Tauri
pnpm tauri dev
pnpm test
cargo check --manifest-path src-tauri/Cargo.toml
```

### Pro

```bash
cd projects/formints/formint-pro
make install              # Backend .venv + deps + npm install + migrate
make seed                 # Demo data (admin@formint.local / admin123)
make env                  # Tmux: backend :8767 + frontend :4321
make test                 # Backend + frontend contract tests
make build                # Frontend production + collectstatic
```

### Cloud

```bash
cd projects/formints/formint-cloud
make install
make migrate
make check
make test
make dev-backend          # Django runserver
make dev-frontend         # Astro dev
```

### SDK

```bash
cd projects/formints/packages/formints-client
pnpm install
pnpm test                 # Vitest (6 tests)
pnpm typecheck            # tsc --noEmit
pnpm build                # tsc → dist/
```

---

## Key Conventions

### Imports (Rust/Tauri)

```rust
mod operations;
use crate::operations::currency;
use crate::db::models::{Currency, NewCurrency};
use crate::db::schema::currencies;
```

### Imports (Django/Python)

```python
from django_fusion.tasks import task
from django_fusion.comp.tags import components  # Canonical path
```

### Imports (TypeScript)

```ts
import { createClient } from '@formints/client';
import { listCurrencies } from '@formints/client/currencies';
```

### API envelope

All Django API responses use the Fusion envelope:

```json
{
  "status": "success",
  "message": "OK",
  "data": { "count": 1, "items": [...] }
}
```

### Do not

- Do not copy Community Tauri/Rust patterns into Pro or Cloud.
- Do not import `formint-cloud` internals from any desktop edition.
- Do not reintroduce the Robyn sidecar — the API is Django-native.
- Do not commit `restaurant.db`, generated installers, or signing keys.
- Do not share static assets between POS editions.
- Do not use `projects/formints/formintA/` — use `formint-community/`.

---

## Directory Map

```
projects/formints/
├── formint-community/        # Community edition (Rust/React, no sidecar)
│   ├── src/                  # React 19 frontend (22 pages, 16 components)
│   ├── src-tauri/            # Rust/Diesel backend (27 ops, 80+ commands)
│   └── migrations/           # Diesel SQL migrations
│
├── formint-standard/         # Standard edition (Rust-first + optional Django)
│   ├── src/                  # React + Alpine + Astro frontend
│   ├── src-tauri/            # Rust/Diesel (38 ops, sync queue, dispatcher)
│   │   └── migrations/       # Including sync_queue migration
│   └── sidecar/              # Optional Django sidecar
│
├── formint-pro/              # Professional edition (required Django)
│   ├── sidecar/              # Django: models, Ninja API, fragments, admin
│   │   ├── formint/          # Domain controllers, schemas, components
│   │   ├── models/           # POS/CRM/HR/inventory/sync
│   │   ├── routes/           # API + fragment routes
│   │   └── tests/            # 66 integration tests
│   ├── frontend/             # Astro 5 + Alpine + HTMX
│   └── src-tauri/            # Tauri 2 desktop shell
│
├── formint-cloud/            # Cloud edition (multi-tenant SaaS)
│   ├── backend/
│   │   ├── apps/core/        # Organization, Branch, Sync, Backup
│   │   └── configs/          # Django settings, URLs
│   └── frontend/             # Astro 5 + Alpine
│
├── formint-client/           # Vue 3 client (separate branch)
│
├── packages/
│   └── formints-client/      # @formints/client JS SDK
│       ├── src/              # core, currencies, taxProfiles, exports, monitor
│       ├── tests/            # 6 Vitest tests
│       └── dist/             # 14 build artifacts
│
├── tests/                    # Cross-edition validation
│   └── pos-e2e/              # Playwright E2E
│
├── docs/                     # POS documentation
├── scripts/                  # Build/release/i18n tooling
└── Makefile                  # Root dispatcher (make community-dev, etc.)
```

---

## Related

- [`/docs/ARCHITECTURE.md`](/docs/ARCHITECTURE.md) — Monorepo-wide architecture
- [`projects/formints/AGENTS.md`](/projects/formints/AGENTS.md) — Multi-edition agent instructions
- [`docs/plans/editions/README.md`](/docs/plans/editions/README.md) — Editions plan index
- [`docs/plans/editions/06-js-sdk.md`](/docs/plans/editions/06-js-sdk.md) — JS SDK plan
- [`docs/plans/editions/03-pro.md`](/docs/plans/editions/03-pro.md) — Professional edition plan
- [`/docs/ARCHITECTURE.md`](/docs/ARCHITECTURE.md) — Monorepo MCP integration (Kilo server, designer/task tools)
