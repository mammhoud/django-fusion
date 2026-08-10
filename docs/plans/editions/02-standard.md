# Standard Edition — Design, Architecture & Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the Standard tier as a **standalone Rust/Diesel edition** — it works without a Django sidecar. Multi-currency, tax profiles, custom roles, and CSV/JSON export all run in Rust/Diesel + SQLite. An **optional Django sidecar** can be connected for sync/cloud features but is not required for core operation.

**Architecture:** Offline-first desktop POS — same foundation as Community. Frontend: Astro 5 + React 19 + Alpine.js + Tauri 2 shell. Backend: Rust/Diesel + SQLite (`restaurant.db` extended with new tables). Optional: Django sidecar (`formint/sidecar/`) for multi-branch sync and cloud connectivity when available. The Standard edition works end-to-end with zero network dependencies when the sidecar is absent.

**Tech Stack:** Rust (diesel 2.2, diesel_migrations 2.2, tauri 2) · TypeScript (React 19, Astro 5, Alpine.js, Vitest) · Optional: Python (Django 5.2, django-fusion) for the sidecar.

## Global Constraints

- All Rust changes live under `projects/formints/formint/src-tauri/`.
- All frontend changes live under `projects/formints/formint/frontend/`.
- The optional sidecar lives under `projects/formints/formint/sidecar/`.
- **No new third-party dependencies** in Rust (diesel + diesel_migrations only). No new dependencies in the frontend (existing stack).
- **The Standard edition MUST work without the sidecar.** Every feature in Tasks B1–B4 runs in Rust/Diesel with no Django process required.
- Tauri port: 1420 (dev). Sidecar ports when enabled: backend 8767, bolt 8766.
- **Feature inheritance (hard):** Standard MUST include every Community feature (`01-community.md`) PLUS its own. Parity sweep in Task B8. Standard's features are inherited by Pro and Cloud.
- Test commands: Rust `cd projects/formints/formint/src-tauri && cargo test` · frontend `cd projects/formints/formint/frontend && pnpm test` · sidecar (when enabled) `cd projects/formints/formint/sidecar && make test`.

---

## Frontend

**Stack:** Astro 5 pages (28 pages — Community's 25 + 3 new: Currencies, Tax Profiles, Export) + React 19 components + Alpine.js for local state.

**Pages added by Standard:**

| Page | Route | Purpose |
|------|-------|---------|
| Currencies | `/settings/currencies` | Manage ISO-4217 currency list, set default, toggle active |
| Tax Profiles | `/settings/tax-profiles` | Named tax rates (Standard, Reduced, Zero-rated) |
| Export | `/reports/export` | CSV/JSON export selection: products, sales, customers, inventory |

**Key components:**

- `CurrencyPicker.tsx` — select active currency for sale screens
- `TaxProfileBadge.tsx` — display tax profile on product cards and sale lines
- `ExportPanel.tsx` — format selection, download trigger, progress indicator
- `RoleGate.tsx` — wraps actions behind permission checks (consumes `usePermissions` hook)

**Loading states:** Each new page follows the existing Community skeleton pattern (`Skeleton.astro`), `aria-live` regions, and empty/error states.

---

## Backend (Rust/Diesel — primary)

**Schema extension over Community** (`restaurant.db`):

| New table | Key columns | Purpose |
|-----------|-------------|---------|
| `currencies` | `code` (unique), `name`, `symbol`, `exchange_rate`, `is_default`, `is_active` | Multi-currency pricing |
| `tax_profiles` | `name` (unique), `rate` (fraction), `is_default`, `is_active` | Named tax rates |
| `export_jobs` | `format` (csv/json), `resource` (products/sales/customers/inventory), `status`, `file_path`, `created_at` | Track export runs |

**Column additions to existing tables:**

| Table | New column | Type | Purpose |
|-------|-----------|------|---------|
| `products` | `tax_profile_id` | FK → `tax_profiles` (nullable) | Product-level tax linkage |
| `sales` | `currency_id` | FK → `currencies` (nullable) | Sale currency |
| `sales` | `tax_profile_id` | FK → `tax_profiles` (nullable) | Sale-level tax override |

**Rust module structure** (under `src-tauri/src/`):

```
src/
├── db/
│   ├── schema.rs              # + currencies, tax_profiles, export_jobs tables
│   └── migrations/
│       └── 002_standard/       # new migration
├── operations/
│   ├── sales.rs               # refund_sale (existing) + tax/currency on sale
│   ├── currency.rs            # NEW — list, create, update, set_default, toggle
│   ├── tax_profile.rs         # NEW — list, create, update, set_default, toggle
│   ├── export.rs              # NEW — export_csv, export_json for 4 resources
│   └── permissions.rs         # NEW — resolve_permissions, has_permission
└── lib.rs                     # register new commands in invoke_handler
```

**Tauri commands (Rust → frontend via `invoke`):**

| Command | Purpose |
|---------|---------|
| `list_currencies` | Return all currencies (active first, default flagged) |
| `create_currency` | Add a currency; enforces single default |
| `update_currency` | Edit code/name/symbol/rate/active; single-default enforcement |
| `delete_currency` | Soft-delete (set inactive); reject if only remaining default |
| `list_tax_profiles` | Return all tax profiles |
| `create_tax_profile` | Add a named rate; single-default enforcement |
| `update_tax_profile` | Edit name/rate/active |
| `delete_tax_profile` | Soft-delete; reject if only remaining default |
| `export_resource` | Generate CSV or JSON for a resource, write to disk, return `ExportJob` |
| `compute_tax` | `(subtotal: f64, rate: f64) -> f64` — rounds to cents via `round_half_up` |
| `resolve_permissions` | Return effective permission set for current user/role |

**Migrations:** `diesel migration generate 002_standard` then `diesel migration run`.

---

## Optional Sidecar (Django)

When connected, the Django sidecar (`formint/sidecar/`) provides sync and cloud features. It is **not required** for core Standard operation. If the sidecar is unreachable, Standard degrades gracefully — all local features continue working.

**Sidecar capabilities when enabled:**

| Feature | Rust/Diesel (always available) | Django sidecar (when connected) |
|---------|:---:|:---:|
| Multi-currency | ✅ Local | ➕ Sync to cloud |
| Tax profiles | ✅ Local | ➕ Sync to cloud |
| Custom roles | ✅ Local (JSON permissions on `roles` table) | ➕ Admin-managed via Unfold |
| CSV/JSON export | ✅ Local (streams from SQLite) | ➕ Large-dataset async export via `@task` |
| Branch sync | ❌ | ✅ `Node`, `SyncApproval`, `SyncLog` |
| Cloud connectivity | ❌ | ✅ `CloudLink`, `DeviceToken` |
| django-fusion fragments | ❌ | ✅ `TABLE_COMPONENTS` for currencies/tax profiles |
| Background tasks | ❌ | ✅ `django_fusion.tasks.@task` for scheduled sync |

**Sidecar activation:** Set `STANDARD_SIDECAR_ENABLED=true` in the Tauri app config or environment. When disabled, the Django models, routes, and fragment tests are skipped. Pro is Standard with the sidecar permanently enabled.

---

## DataToken Shell & Sidecar Fallback System

Standard edition uses a **tiered data pipeline** that falls back gracefully:

```
┌─────────────────────────────────────────────────────────────┐
│                   Standard Data Pipeline                    │
│                                                             │
│  Frontend (React/Astro)                                     │
│    │ invoke("create_currency", ...)                         │
│    ▼                                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Data Dispatcher (Rust)                   │  │
│  │                                                      │  │
│  │  1. Try Sidecar API (if connected)                   │  │
│  │     POST http://127.0.0.1:8767/api/v1/currencies     │  │
│  │     → Success: return, DataToken auto-tagged ✓       │  │
│  │     → Failure: fall through...                       │  │
│  │                                                      │  │
│  │  2. Write to Rust/Diesel (always)                    │  │
│  │     INSERT INTO currencies ...                       │  │
│  │     → Success: emit on_data_changed signal           │  │
│  │                                                      │  │
│  │  3. Tag with DataToken Shell (local marker)          │  │
│  │     INSERT INTO sync_queue ...                       │  │
│  │     → Marks row as "pending sync" in local SQLite    │  │
│  │                                                      │  │
│  │  4. On sidecar reconnect: flush sync_queue           │  │
│  │     → Push pending tokens to Django sidecar          │  │
│  │     → Sidecar creates real DataToken rows            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────┐    ┌──────────────────────────┐  │
│  │ DataToken Shell      │    │ Django DataToken         │  │
│  │ (SQLite, always on)  │◄──►│ (PostgreSQL, when online)│  │
│  │                      │    │                          │  │
│  │ sync_queue table     │    │ ci_datatoken table       │  │
│  │ local markers        │    │ GenericFK tagging        │  │
│  │ flush on reconnect   │    │ parent/child trees       │  │
│  └──────────────────────┘    └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### DataToken Shell — Local Sync Markers (Rust/SQLite)

The **DataToken Shell** is a lightweight Rust-level equivalent of django-fusion's `DataToken`. It lives entirely in SQLite and requires no Django process. Its sole purpose is to **mark which rows need syncing** so that when the sidecar becomes available, pending changes can be flushed.

```sql
-- migration: 003_datatoken_shell/up.sql
CREATE TABLE sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- What changed
    entity_type TEXT NOT NULL,        -- e.g. "currency", "sale", "product"
    entity_id TEXT NOT NULL,          -- PK of the changed row (string for flexibility)
    change_type TEXT NOT NULL,        -- "create" | "update" | "delete"
    -- Ordering
    sync_order INTEGER NOT NULL DEFAULT 0,
    -- Status
    status TEXT NOT NULL DEFAULT 'pending',  -- pending | flushing | flushed | failed
    retry_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT DEFAULT '',
    -- Payload (snapshot of the row at change time)
    payload_json TEXT NOT NULL DEFAULT '{}',
    -- Timestamps
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    flushed_at TEXT
);

CREATE INDEX idx_sync_queue_status_order
    ON sync_queue(status, sync_order, created_at);
CREATE INDEX idx_sync_queue_entity
    ON sync_queue(entity_type, entity_id);
```

**Rust operations** (`src-tauri/src/operations/sync_queue.rs`):

| Function | Purpose |
|----------|---------|
| `tag_for_sync(db, entity_type, entity_id, change_type, payload)` | Insert a sync_queue row |
| `get_pending_batch(db, limit) -> Vec<SyncQueueItem>` | Return next batch ordered |
| `mark_flushed(db, ids)` | Bulk-update status to `flushed` |
| `mark_failed(db, id, error)` | Record failure + increment retry |
| `flush_to_sidecar(db, sidecar_url)` | Push pending batch to Django API |
| `purge_flushed(db, older_than_days)` | Cleanup old flushed rows |

### Sidecar Fallback Chain (Rust Dispatcher)

Every data mutation command follows the same dispatch pattern:

```rust
// src-tauri/src/operations/dispatcher.rs

/// Dispatch a data mutation with sidecar fallback.
///
/// Order:
///   1. Try sidecar API (if connected and STANDARD_SIDECAR_ENABLED)
///   2. Always write to local Diesel/SQLite (primary store)
///   3. Tag with DataToken Shell for later sync
pub fn dispatch_mutation(
    db_path: &PathBuf,
    mutation: Mutation,
) -> Result<MutationResult, String> {
    let sidecar_available = check_sidecar_health().unwrap_or(false);

    // ── Step 1: Try sidecar (best-effort) ──
    if sidecar_available {
        match post_to_sidecar(&mutation) {
            Ok(result) => {
                // Sidecar accepted the write and auto-tagged with DataToken.
                // Still write locally for offline resilience.
                let local = write_to_diesel(db_path, &mutation)?;
                return Ok(MutationResult { sidecar: Some(result), local });
            }
            Err(e) => {
                log::warn!("Sidecar write failed: {e} — falling back to local");
                // Fall through to local write
            }
        }
    }

    // ── Step 2: Write to local Diesel (always) ──
    let local = write_to_diesel(db_path, &mutation)?;

    // ── Step 3: Tag with DataToken Shell ──
    tag_for_sync(
        db_path,
        &mutation.entity_type,
        &mutation.entity_id,
        &mutation.change_type,
        &mutation.payload_json,
    )?;

    // ── Step 4: Emit change signal (for sidecar reconnection) ──
    emit_data_changed(&mutation);

    Ok(MutationResult { sidecar: None, local })
}
```

### Sidecar Reconnect Hook — Flush Pending Sync Queue

When the sidecar comes back online (detected via periodic health check or a Tauri `online` event), the Rust side flushes the pending `sync_queue`:

```rust
// src-tauri/src/operations/sidecar_reconnect.rs

/// Called when the sidecar becomes healthy after being offline.
/// Pushes all pending sync_queue rows to the Django sidecar API
/// so that real DataToken rows are created.
#[tauri::command]
pub fn flush_pending_sync(app: AppHandle) -> Result<FlushResult, String> {
    let db = db_path_str(&app);
    let sidecar_url = "http://127.0.0.1:8767";

    let batch = get_pending_batch(&PathBuf::from(&db), 100)?;
    if batch.is_empty() {
        return Ok(FlushResult { pushed: 0, failed: 0 });
    }

    let mut pushed = 0;
    let mut failed = 0;
    let mut flushed_ids = Vec::new();

    for item in &batch {
        match post_sync_item_to_sidecar(sidecar_url, item) {
            Ok(_) => {
                flushed_ids.push(item.id);
                pushed += 1;
            }
            Err(e) => {
                mark_failed(&PathBuf::from(&db), item.id, &e)?;
                failed += 1;
            }
        }
    }

    mark_flushed(&PathBuf::from(&db), &flushed_ids)?;
    Ok(FlushResult { pushed, failed })
}
```

### on_data_changed Signal (Event Bus)

Every data mutation emits a Tauri event so the frontend can react without polling:

```rust
// After every successful Diesel write:
app.emit("data-changed", serde_json::json!({
    "entity_type": "currency",
    "entity_id": "42",
    "change_type": "create",
    "timestamp": chrono::Utc::now().to_rfc3339(),
}))?;
```

```typescript
// frontend/src/hooks/useDataChanged.ts
import { listen } from '@tauri-apps/api/event';
import { useEffect } from 'react';

export function useDataChanged(
  entityType: string,
  onChanged: () => void,
) {
  useEffect(() => {
    const unlisten = listen<DataChangeEvent>('data-changed', (event) => {
      if (event.payload.entity_type === entityType) {
        onChanged();
      }
    });
    return () => { unlisten.then(fn => fn()); };
  }, [entityType, onChanged]);
}
```

### Sidecar Health Monitor (Frontend)

The frontend periodically checks sidecar health and triggers a flush when it comes online:

```typescript
// frontend/src/hooks/useSidecarMonitor.ts
import { useEffect, useRef } from 'react';
import sidecar from '../api/sidecar';
import { invoke } from '@tauri-apps/api/core';

const CHECK_INTERVAL_MS = 15_000; // 15 seconds

export function useSidecarMonitor() {
  const wasOnline = useRef(false);

  useEffect(() => {
    const interval = setInterval(async () => {
      const healthy = await sidecar.healthCheck();

      // Sidecar just came online — flush pending sync
      if (healthy && !wasOnline.current) {
        console.log('[sidecar] Reconnected — flushing sync queue');
        invoke('flush_pending_sync').catch(console.error);
      }

      // Sidecar just went offline — mark pending data for later
      if (!healthy && wasOnline.current) {
        console.log('[sidecar] Disconnected — data will sync on reconnect');
      }

      wasOnline.current = healthy;
    }, CHECK_INTERVAL_MS);

    return () => clearInterval(interval);
  }, []);
}
```

### Sidecar API Contract for DataToken Tagging

When the sidecar receives a mutation from the Rust dispatcher, it:

1. Writes the row to Django ORM
2. Auto-tags with a real `DataToken` via `DataToken.objects.tag_row()`
3. Returns the token ID to the Rust caller

```python
# formint/sidecar/routes/sync_proxy.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django_fusion.models.datatoken import DataToken, AbstractDataToken

@csrf_exempt
def sync_proxy_create(request, entity_type):
    """
    Proxy endpoint: accept a mutation from the Rust dispatcher,
    write to Django ORM, and auto-tag with DataToken.

    POST /sync-proxy/<entity_type>/
    Body: { "entity_id": "42", "payload": {...}, "node_id": "standard-001" }
    """
    body = json.loads(request.body)
    model_class = _get_model(entity_type)

    # Create the Django row
    instance = model_class.objects.create(**body["payload"])

    # Auto-tag with DataToken for cloud sync
    token = DataToken.objects.tag_row(
        model_instance=instance,
        token=f"{entity_type}_{instance.pk}_{body['node_id']}",
        node_id=body["node_id"],
        sync_order=0,
        app_type=AbstractDataToken.AppType.POS_SOLO,
        metadata=body.get("metadata", {}),
    )

    return JsonResponse({
        "ok": True,
        "id": str(instance.pk),
        "data_token": token.token,
    })
```

### Data Read Fallback Chain

Reads follow the reverse direction: try sidecar first (fresh data), fall back to local Diesel:

```rust
pub fn dispatch_read<T>(
    db_path: &PathBuf,
    entity_type: &str,
    query: ReadQuery,
) -> Result<Vec<T>, String> {
    // ── Step 1: Try sidecar (if connected) ──
    if check_sidecar_health().unwrap_or(false) {
        match get_from_sidecar(entity_type, &query) {
            Ok(data) => return Ok(data),
            Err(e) => log::warn!("Sidecar read failed: {e} — falling back to local"),
        }
    }

    // ── Step 2: Read from local Diesel (always works) ──
    read_from_diesel(db_path, entity_type, &query)
}
```

### How DataToken Shell Becomes a "Shell of Django Itself"

The `sync_queue` table + dispatcher pattern means Standard can:

1. **Tag data changes** without Django — the `sync_queue` is the local marker
2. **Push to sidecar** when available — the sidecar creates real `DataToken` rows
3. **Operate identically to Pro** when sidecar is connected — same DataToken tagging, same sync pipeline
4. **Degrade gracefully** when sidecar is off — data still works, sync markers accumulate

This is the "shell" — a lightweight Rust mechanism that mirrors django-fusion's `DataToken` behavior without requiring a single Python process.

---

## Task B_shell: DataToken Shell & Sidecar Dispatcher

**Files:**
- Create: `formint/src-tauri/src/db/migrations/003_datatoken_shell/up.sql`
- Create: `formint/src-tauri/src/operations/sync_queue.rs`
- Create: `formint/src-tauri/src/operations/dispatcher.rs`
- Create: `formint/src-tauri/src/operations/sidecar_reconnect.rs`
- Create: `formint/frontend/src/hooks/useSidecarMonitor.ts`
- Create: `formint/frontend/src/hooks/useDataChanged.ts`
- Create: `formint/sidecar/routes/sync_proxy.py` (optional sidecar endpoint)
- Modify: `formint/src-tauri/src/lib.rs` (register new commands)
- Modify: `formint/src-tauri/tauri.conf.json` (allow sidecar URL in CSP)

**Interfaces:**
- Produces: `sync_queue` table, `tag_for_sync`, `flush_pending_sync`, `dispatch_mutation`, `dispatch_read`.
- Consumed by: all write operations (B1-B4), the frontend sidecar monitor.

- [ ] **Step 1: Write the failing test for sync_queue**
- [ ] **Step 2: Create the migration for sync_queue table**
- [ ] **Step 3: Implement sync_queue operations (tag, batch, flush, purge)**
- [ ] **Step 4: Implement dispatcher with sidecar fallback chain**
- [ ] **Step 5: Implement sidecar_reconnect flush logic**
- [ ] **Step 6: Create sidecar health monitor hook (frontend)**
- [ ] **Step 7: Create data-changed event emitter + listener**
- [ ] **Step 8: Create sync_proxy endpoint on Django sidecar**
- [ ] **Step 9: Wire dispatcher into all B1-B4 write commands**
- [ ] **Step 10: Run full Rust + frontend + sidecar test suites**
- [ ] **Step 11: Test offline→online flush cycle**
- [ ] **Step 12: Commit**

---

## Design

**Audience:** a growing single-branch operator who needs money, tax, and role management but isn't ready for multi-branch sync or cloud. Everything works offline on one device.

**Multi-currency.** A `currencies` catalogue (ISO-4217 code, name, symbol, cross-rate). Exactly one currency is `is_default`. The sale screen picks from active currencies. A `currency_id` FK on `sales` records the currency used.

**Tax profiles.** Named tax rates managed in `tax_profiles` (Standard 15%, Reduced 7%, Zero-rated 0%). Products and sales may carry a `tax_profile_id` FK. `compute_tax(subtotal, rate)` replaces the fixed `tax_rate` string with a dynamic profile. Default enforcement: setting a profile as default clears the previous default.

**Custom roles & permissions.** The existing `roles` table already has a JSON `permissions` column. Standard adds `resolve_permissions(user, role)` (superusers get all keys; otherwise truthy JSON flags) and applies it to currency/tax write operations. A `RoleGate` React component gates UI actions.

**Data export.** Four Tauri commands (`export_resource` with `resource` = products/sales/customers/inventory, `format` = csv/json) stream from SQLite, write to the OS temp directory, and return an `ExportJob` row. The `ExportPanel` frontend component triggers the command and offers a download button.

**Copy register:** admin-facing labels stay concrete ("Standard", "Reduced"); buttons use plain verbs ("Set default", "Export CSV").

---

## Task B1: Multi-currency support (Rust/Diesel)

**Files:**
- Create: `formint/src-tauri/src/db/migrations/002_standard/up.sql` (currencies table)
- Create: `formint/src-tauri/src/operations/currency.rs`
- Modify: `formint/src-tauri/src/lib.rs` (register commands)
- Test: `formint/src-tauri/src/operations/currency.rs` (inline `#[cfg(test)]` module)

**Interfaces:**
- Produces: `currencies` table + `list_currencies`, `create_currency`, `update_currency`, `delete_currency` commands. Consumed by the Currencies settings page (Task B5).

- [ ] **Step 1: Write the failing test**

In `formint/src-tauri/src/operations/currency.rs`:

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use crate::db::run_migrations;
    use std::path::PathBuf;

    fn temp_db(tag: &str) -> PathBuf {
        let mut path = std::env::temp_dir();
        path.push(format!("formint-standard-currency-{}-{}.db", std::process::id(), tag));
        let _ = std::fs::remove_file(&path);
        run_migrations(&path).expect("migrations ok");
        path
    }

    #[test]
    fn list_currencies_returns_empty_initially() {
        let db = temp_db("list");
        let result = list_currencies(&db, true, None).expect("list ok");
        assert!(result.is_empty());
        let _ = std::fs::remove_file(&db);
    }

    #[test]
    fn create_and_set_default() {
        let db = temp_db("default");
        let usd = create_currency(&db, "USD", "US Dollar", "$", 1.0, true).expect("create");
        assert!(usd.is_default);
        let eur = create_currency(&db, "EUR", "Euro", "€", 0.92, true).expect("create");
        // Single-default enforcement: USD should no longer be default
        let refreshed = get_currency(&db, usd.id).expect("get");
        assert!(!refreshed.is_default);
        assert!(eur.is_default);
        let _ = std::fs::remove_file(&db);
    }

    #[test]
    fn delete_rejects_last_default() {
        let db = temp_db("delete_def");
        let usd = create_currency(&db, "USD", "US Dollar", "$", 1.0, true).expect("create");
        let err = delete_currency(&db, usd.id).expect_err("should reject");
        assert!(err.contains("cannot delete the only default currency"));
        let _ = std::fs::remove_file(&db);
    }
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formint/src-tauri && cargo test currency`
Expected: FAIL — `error[E0425]: cannot find function 'list_currencies'`

- [ ] **Step 3: Write the migration**

Create `formint/src-tauri/src/db/migrations/002_standard/up.sql`:

```sql
CREATE TABLE currencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(3) NOT NULL UNIQUE,
    name VARCHAR(64) NOT NULL,
    symbol VARCHAR(8) NOT NULL DEFAULT '',
    exchange_rate REAL NOT NULL DEFAULT 1.0,
    is_default BOOLEAN NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

Also create `down.sql` to drop the table. Register the migration in `schema.rs`.

- [ ] **Step 4: Write the Rust operations**

In `formint/src-tauri/src/operations/currency.rs`:

```rust
use diesel::prelude::*;
use crate::db::models::{Currency, NewCurrency};
use crate::db::schema::currencies::dsl::*;
use std::path::PathBuf;

pub fn list_currencies(db_path: &PathBuf, active_only: bool, search: Option<&str>) -> Result<Vec<Currency>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    let mut query = currencies.into_boxed();
    if active_only { query = query.filter(is_active.eq(true)); }
    if let Some(q) = search { query = query.filter(name.like(format!("%{}%", q))); }
    query.order(code.asc()).load(&mut conn).map_err(|e| format!("list currencies: {e}"))
}

pub fn create_currency(db_path: &PathBuf, c_code: &str, c_name: &str, c_symbol: &str, rate: f64, default: bool) -> Result<Currency, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    if default {
        diesel::update(currencies.filter(is_default.eq(true)))
            .set(is_default.eq(false))
            .execute(&mut conn).map_err(|e| format!("clear default: {e}"))?;
    }
    let row = NewCurrency { code: c_code.to_string(), name: c_name.to_string(), symbol: c_symbol.to_string(), exchange_rate: rate, is_default: default, is_active: true };
    diesel::insert_into(currencies).values(&row).get_result(&mut conn).map_err(|e| format!("create currency: {e}"))
}
// ... update_currency, delete_currency, get_currency similar pattern
```

- [ ] **Step 5: Register commands in lib.rs**

In `formint/src-tauri/src/lib.rs`, add `list_currencies, create_currency, update_currency, delete_currency,` to `tauri::generate_handler![...]`.

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd projects/formints/formint/src-tauri && cargo test currency`
Expected: PASS — all 3 tests green.

- [ ] **Step 7: Run full Rust suite**

Run: `cd projects/formints/formint/src-tauri && cargo test`
Expected: all pass (existing + new).

- [ ] **Step 8: Commit**

---

## Task B2: Tax profiles + compute_tax (Rust/Diesel)

**Files:**
- Modify: `formint/src-tauri/src/db/migrations/002_standard/up.sql` (tax_profiles table)
- Create: `formint/src-tauri/src/operations/tax_profile.rs`
- Create: `formint/src-tauri/src/operations/tax.rs` (compute_tax helper)
- Modify: `formint/src-tauri/src/lib.rs`
- Modify: `formint/src-tauri/src/db/schema.rs`

**Interfaces:**
- Produces: `tax_profiles` table + `list_tax_profiles`, `create_tax_profile`, `update_tax_profile`, `delete_tax_profile` + `compute_tax(subtotal: f64, rate: f64) -> f64`. FK columns on `products.tax_profile_id` and `sales.tax_profile_id`.

- [ ] **Step 1: Write the failing test**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Extend the migration with tax_profiles table**
- [ ] **Step 4: Add FK columns to products and sales (ALTER TABLE in migration)**
- [ ] **Step 5: Write the Rust operations + compute_tax helper**
- [ ] **Step 6: Register commands in lib.rs**
- [ ] **Step 7: Run tests to verify they pass**
- [ ] **Step 8: Run full Rust suite**
- [ ] **Step 9: Commit**

---

## Task B3: Custom roles & permissions enforcement (Rust)

**Files:**
- Create: `formint/src-tauri/src/operations/permissions.rs`
- Modify: `formint/src-tauri/src/operations/currency.rs` (gate write commands)
- Modify: `formint/src-tauri/src/lib.rs`
- Test: inline in `permissions.rs`

**Interfaces:**
- Consumes: the existing `roles` table (JSON `permissions` column).
- Produces: `resolve_permissions(user, role) -> HashSet<String>`, applied as a gate on `create_currency`, `update_currency`, `create_tax_profile`, `update_tax_profile`.

**Canonical permission keys:** `can_manage_products`, `can_issue_refunds`, `can_manage_inventory`, `can_manage_settings`.

- [ ] **Step 1: Write the failing test**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Write resolve_permissions (superusers get all keys; role JSON flags)**
- [ ] **Step 4: Gate currency write commands**
- [ ] **Step 5: Run tests to verify they pass**
- [ ] **Step 6: Run full Rust suite**
- [ ] **Step 7: Commit**

---

## Task B4: CSV/JSON data export (Rust/Diesel)

**Files:**
- Modify: `formint/src-tauri/src/db/migrations/002_standard/up.sql` (export_jobs table)
- Create: `formint/src-tauri/src/operations/export.rs`
- Modify: `formint/src-tauri/src/lib.rs`

**Interfaces:**
- Produces: `export_resource(db_path, resource: &str, format: &str) -> Result<ExportJob, String>`. Resource: `products` | `sales` | `customers` | `inventory`. Format: `csv` | `json`. Writes to OS temp dir, returns job row.

> **Sidecar note:** When the Django sidecar is enabled, replace the synchronous Rust export with `django_fusion.tasks.@task(queue="reports")` for large-dataset async exports. The Rust export remains available for offline/sidecar-disabled mode.

- [ ] **Step 1: Write the failing test**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Extend migration with export_jobs table**
- [ ] **Step 4: Write the export engine (CSV via std::io::Write, JSON via serde_json)**
- [ ] **Step 5: Register command in lib.rs**
- [ ] **Step 6: Run tests to verify they pass**
- [ ] **Step 7: Run full Rust suite**
- [ ] **Step 8: Commit**

---

# Frontend Tasks

## Task B5: Currencies, Tax Profiles & Export settings pages

**Files:**
- Create: `formint/frontend/src/pages/settings/Currencies.astro`
- Create: `formint/frontend/src/pages/settings/TaxProfiles.astro`
- Create: `formint/frontend/src/pages/reports/Export.astro`
- Create: `formint/frontend/src/components/CurrencyPicker.tsx`
- Create: `formint/frontend/src/components/TaxProfileBadge.tsx`
- Create: `formint/frontend/src/components/ExportPanel.tsx`
- Create: `formint/frontend/src/hooks/usePermissions.ts`
- Modify: `formint/frontend/src/components/AppShell.tsx` (add nav links)
- Test: new `.test.tsx` files for each component

**Interfaces:**
- Consumes: Tauri `invoke` commands from Tasks B1–B4.
- Produces: 3 Astro pages + 3 React components + 1 permissions hook.

- [ ] **Step 1: Write failing tests for each component**
- [ ] **Step 2: Run tests to verify they fail**
- [ ] **Step 3: Implement the pages and components**
- [ ] **Step 4: Wire nav links in AppShell**
- [ ] **Step 5: Run frontend tests to verify they pass**
- [ ] **Step 6: Run full frontend suite (`pnpm test`)**
- [ ] **Step 7: Commit**

## Task B6: RoleGate component (permission-gated UI)

**Files:**
- Create: `formint/frontend/src/components/RoleGate.tsx`
- Test: `formint/frontend/src/test/components/RoleGate.test.tsx`

**Interfaces:**
- Consumes: `usePermissions()` hook, `resolve_permissions` from Tauri.
- Produces: `<RoleGate permission="can_manage_settings">` wrapper.

- [ ] **Step 1: Write the failing test**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Implement RoleGate and usePermissions hook**
- [ ] **Step 4: Apply RoleGate to currency/tax write buttons**
- [ ] **Step 5: Run tests to verify they pass**
- [ ] **Step 6: Commit**

---

# Optional Sidecar Tasks

> These tasks are **only executed when the sidecar is enabled** (`STANDARD_SIDECAR_ENABLED=true`). They are additive — core Standard operates without them.

## Task B7: Django sidecar models + fragments (optional)

**Files:**
- Modify: `formint/sidecar/models/money.py` (Currency, TaxProfile — Django mirrors of Rust models)
- Modify: `formint/sidecar/formint/components.py` (django-fusion TABLE_COMPONENTS)
- Modify: `formint/sidecar/htmx_views.py` (fragment views)
- Modify: `formint/sidecar/configs/urls.py` (fragment routes)
- Test: `formint/sidecar/tests/test_standard_sidecar.py`

**Interfaces:**
- Consumes: Django ORM (mirrors Rust schema), `django_fusion.tasks.@task`.
- Produces: HTMX fragments at `/htmx/currencies/` and `/htmx/tax-profiles/`, plus async export via `@task(queue="reports")`.

- [ ] **Step 1: Write the failing test**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Implement Django models, fragments, and views**
- [ ] **Step 4: Run sidecar tests to verify they pass**
- [ ] **Step 5: Run full sidecar suite (`make test`)**
- [ ] **Step 6: Commit**

## Task B8: Inheritance parity sweep

Verify that every Community feature (refunds, offline-first) works in Standard, and that every Standard feature (currency, tax, roles, export) is inherited by Pro. Run the Community e2e suite against Standard, and the Standard + Pro suites against Pro.

- [ ] **Step 1: Run Community e2e suite against Standard**
- [ ] **Step 2: Verify Standard features appear in Pro**
- [ ] **Step 3: Record parity in editions.md**
- [ ] **Step 4: Commit**

---

## Self-Review

1. **Spec coverage:** Standard capability markers (multi-currency, tax profiles, custom roles, CSV/JSON export) all map to tasks (B1, B2, B3, B4). Rust/Diesel primary, sidecar optional.
2. **Type consistency:** All Tauri command signatures are `snake_case` and match the frontend `invoke` calls. `compute_tax(f64, f64) -> f64` rounds to cents.
3. **Offline-first:** Every feature works with zero network — currency/tax/roles/export all run in Rust/Diesel. The sidecar is additive only.

## Execution Handoff

**Plan complete and maintained at `docs/plans/editions/02-standard.md`.** Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
