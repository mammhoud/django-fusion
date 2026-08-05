# 🖥️ Sidecar — Server Architecture

> The POS sidecar is a Python server that extends the Rust/Tauri desktop app with REST APIs, WebSocket, Django ORM, and cloud sync capabilities.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  POS Sidecar (Robyn + Django ORM)            │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Robyn HTTP Server (:8765 Solo / :8766 Full)        │    │
│  │  • 60-70+ REST endpoints (CRUD + custom)            │    │
│  │  • WebSocket real-time streaming                     │    │
│  │  • Pydantic validation (optional)                    │    │
│  │  • Built-in OpenAPI docs                             │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Django ORM (managed=True models in models/ package)  │    │
│  │  • Solo: models/pos.py, menu.py, node.py, config, sync│    │
│  │  • Full: models/node.py, config.py, sync.py           │    │
│  │  • Full (Rust-backed): posapp/models.py (30+ tables)  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Shared Module (projects/pos/shared/)                 │    │
│  │  • signals/       — Django signal definitions        │    │
│  │  • models/        — SignalEvent, SyncApproval, Token │    │
│  │  • handlers/      — Signal receivers (log, webhook)  │    │
│  │  • services/      — ProductSyncEngine                 │    │
│  │  • middleware/    — Auth middleware                   │    │
│  │  • api/           — CRUD helpers                     │    │
│  │  • portal_viewsets — Django Portal viewsets           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  WebSocket Streams                                   │    │
│  │  • /ws/config — Config change stream (both editions) │    │
│  │  • /ws/nodes — Node event stream (Full only)         │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

---

## Sidecar by Edition

| Edition | Sidecar | Port | Server | Models | Key Features |
|---------|---------|------|--------|--------|-------------|
| **Minimal** | None | — | — | — | Pure Rust backend |
| **Solo** | `pos-solo/sidecar/` | 8765 | Robyn | `models/pos.py, menu.py, node.py, config.py, sync.py` | 15 unified models + cloud sync client |
| **Full** | `pos-full/sidecar/` | 8766 | Robyn | `models/node.py, config.py, sync.py` + `posapp/` (Rust-backed) | Cloud master + approval + WebSocket + Bolt API |

---

## Sidecar Package Structure

| File/Directory | Edition | Purpose |
|---------------|---------|---------|
| `server.py` | Solo, Full | Robyn HTTP + WebSocket server (entry point) |
| `models/__init__.py` | Solo, Full | Model package init |
| `models/pos.py` | Solo | POS core models (Category, Product, Customer, Sale, etc.) |
| `models/menu.py` | Solo | Menu models (MenuItem, Menu, Assignment) |
| `models/node.py` | Solo, Full | Node registry models (Node, Heartbeat, NodeEvent) |
| `models/config.py` | Solo, Full | Config models (DeviceConfig, MasterDevice, CloudLink) |
| `models/sync.py` | Solo, Full | SyncLog model |
| `posapp/models.py` | Full | 30+ Rust-mirror tables (managed=False) |
| `settings.py` | Solo, Full | Django settings for ORM |
| `manage.py` | Solo, Full | Django management commands |
| `tests/test_server.py` | Full | 53 server tests |
| `tests/test_webhook_e2e.py` | Full | 10 webhook E2E tests |
| `tests/test_unified_api.py` | Solo | 155 model tests |
| `bolt_api.py` | Full | django-bolt high-performance API |

### Shared Module Structure

| Path | Purpose |
|------|---------|
| `shared/signals/` | Django signal definitions + fire_* helpers |
| `shared/models/audit.py` | SignalEvent (audit trail) |
| `shared/models/approval.py` | SyncApproval (approve/reject workflow) |
| `shared/models/token.py` | DeviceToken (SHA-256 auth) |
| `shared/handlers/signal.py` | @receiver handlers (log, webhook, audit) |
| `shared/services/sync.py` | ProductSyncEngine (Master↔Child sync) |
| `shared/middleware/auth.py` | Auth middleware + endpoints |
| `shared/api/crud.py` | CRUD helpers (_ser, _paginate, _register_crud) |
| `shared/portal_viewsets.py` | Django Portal viewsets |
| `shared/portal_urls.py` | Portal URL patterns |

---

## How the Sidecar Starts

The Rust backend auto-spawns the sidecar process:

```rust
// src-tauri/src/sidecar.rs (conceptual)
use tauri::api::process::Command;

pub fn start_sidecar(db_path: &str) {
    Command::new_sidecar("pos-sidecar")
        .expect("failed to create sidecar command")
        .args(["--db", db_path, "--port", "8765"])
        .spawn()
        .expect("failed to spawn sidecar");
}
```

No manual launch needed — the sidecar starts when the desktop app starts.

---

## How the Sidecar Starts

The Rust backend auto-spawns the sidecar process:

```rust
// src-tauri/src/sidecar.rs (conceptual)
use tauri::api::process::Command;

pub fn start_sidecar(db_path: &str) {
    Command::new_sidecar("pos-sidecar")
        .expect("failed to create sidecar command")
        .args(["--db", db_path, "--port", "8765"])
        .spawn()
        .expect("failed to spawn sidecar");
}
```

No manual launch needed — the sidecar starts when the desktop app starts.

---

## Sanic Server Specs

| Property | Value |
|----------|-------|
| Framework | Sanic 23+ |
| Port | 8765 (configurable via `--port`) |
| Protocol | HTTP/1.1 + WebSocket |
| CORS | Enabled for localhost |
| Endpoints | 35+ (CRUD for all entities) |
| PDF | Invoice generation via ReportLab |
| Email | SMTP via aiosmtplib |

### API Standard

```python
# Standard response format
{
    "ok": true,
    "data": {...},
    "error": null
}

# Standard error format
{
    "ok": false,
    "data": null,
    "error": "Product not found"
}
```

---

## Django ORM Integration (Full Edition)

The Full edition sidecar includes Django ORM models that mirror the Rust/SQLite schema:

```python
# posapp/models.py
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'products'  # Mirror the SQLite table
```

This enables:
- Django Admin for data management
- Django ORM queries for complex reports
- Fixtures for seed data (`posapp/fixtures/seed_data.json`)
- Migration management via Django

---

## Test Results (Session: 2026-07-20)

Full two-direction test run with stream verification and sync data analysis:

| Direction | Suite | Tests | Passed | Failed | Skipped |
|-----------|-------|------:|------:|------:|------:|
| **1: Django** | `tests/unit/` | — | — | — | — |
| **2a: Pos-Full** | `test_server.py` | 53 | 53 | 0 | 0 |
| **2a: Pos-Full** | `test_data_sync.py` | 18 | 6 | 0 | 12 |
| **2a: Pos-Full** | `test_webhook_e2e.py` | 10 | 10 | 0 | 0 |
| **2b: Pos-Solo** | `test_unified_api.py` | 155 | 155 | 0 | 0 |
| **TOTAL** | | **236** | **224** | **0** | **12** |

### Direction 1: Django Monorepo — `ModuleNotFoundError: No module named 'plugins'`

Runs from `projects/` directory in CI (GitHub Actions `pytest-core.yml`). Local `.venv` Django 5.2.16 resolves `tests.settings` which includes `plugins` apps via module remapping in `tests/conftest.py`. Requires `uv sync` from `projects/` before local execution.

### Direction 2a: Pos-Full Sidecar — 69/69 passed (100% of runnable) ✅

- **53/53 server tests pass** (REST CRUD, node registry, heartbeat, validation, error handling)
- **6/6 model parity tests pass** (table mapping, managed=False, unified DB path)
- **10/10 webhook tests pass** (URL config, send, audit trail — fixed: lazy `_WebhookUrls(dict)` subclass)
- **12 skipped**: RealCrossORM tests need Rust-built `restaurant.db`

### Direction 2b: Pos-Solo Sidecar — 155/155 passed (100%) ✅

All unified model CRUD, filtering, pagination, and validation tests pass.

### Sync Data Comparison

| Metric | Pos-Full | Pos-Solo |
|--------|----------|----------|
| Sync endpoints | 13 | 11 |
| Sync state | `sync_state.json` (status: error) | N/A (runtime) |
| Database | `restaurant.db` (270 KB) | `unified.db` (runtime) |
| Approval queue | ✅ | ✅ |
| Cloud push | ✅ | ✅ |
| Rust DB mirror | ✅ (posapp/) | ❌ |
| WebSocket streams | `/ws/nodes` + `/ws/config` | `/ws/config` |

### HTML Serving Assessment

Both sidecars serve **REST JSON + WebSocket only**. No HTML templates are rendered server-side. Tauri handles UI via React. Potential additions (not yet implemented):
- Dashboard HTML (`/` with Jinja2)
- Admin UI (`/admin/nodes`, `/admin/approvals`)
- Sync dashboard (`/sync/dashboard`)
- OpenAPI docs (Robyn auto-generates)

---

## Related

| Topic | Path |
|-------|------|
| Full test results | [`../TEST_RESULTS.md`](../TEST_RESULTS.md) |
| Sidecar API reference | [`sidecar-api.md`](sidecar-api.md) |
| WebSocket | [`sidecar-websocket.md`](sidecar-websocket.md) |
| Django ORM guide | [`django-orm.md`](django-orm.md) |
| django-bolt integration | [`django-bolt-integration.md`](django-bolt-integration.md) |
| Network architecture | [`network-architecture.md`](network-architecture.md) |
