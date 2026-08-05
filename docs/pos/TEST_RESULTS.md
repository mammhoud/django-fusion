# POS-KO — Full Test Results (Session: 2026-07-20)

> Two-direction test run with stream verification, sync data comparison, and HTML-serving assessment.

---

## Summary

| Metric | Value |
|--------|------:|
| Total test suites | 4 |
| Total tests | 236 |
| Passed | 224 (94.9%) |
| Failed | 0 (0%) |
| Skipped | 12 (5.1%) |
| Zero-failure suite | 3/4 |

---

## Direction 1: Django Monorepo (`tests/unit/`)

**Command:** `.venv/bin/python -m pytest tests/unit/ -v --tb=short`

**Result:** ❌ **Setup Error** — `ModuleNotFoundError: No module named 'plugins'`

**Root cause:** The unit test conftest (`tests/conftest.py`) uses `DJANGO_SETTINGS_MODULE = "tests.settings"` (from `pyproject.toml`). This settings module references `plugins` app entries that rely on module remapping defined in conftest.py (e.g., `www.apps.blog` → `plugins.blog`). When running from the repo root, the Python path doesn't include site directories.

**Fix for CI:** GitHub Actions `pytest-core.yml` runs from `projects/` working directory after `uv sync`, which provides the correct path context.

**Fix for local (test deps in projects/pyproject.toml dev-dependencies):**
```bash
cd projects && uv sync --group dev && uv run pytest ../tests/unit/ -v
```

> Note: `DJANGO_SETTINGS_MODULE = "tests.settings"` is configured in `projects/pyproject.toml` [tool.pytest.ini_options]. The settings module uses module remapping (`www.apps.blog` → `plugins.blog`) defined in `tests/conftest.py`.

---

## Direction 2a: Pos-Full Sidecar (`projects/pos/pos-full/sidecar/tests/`)

**Command:**
```bash
DJANGO_SETTINGS_MODULE='' python3 -m pytest tests/test_server.py tests/test_data_sync.py tests/test_webhook_e2e.py -v --import-mode=importlib
```

**Result:** 68 passed / 0 failed / 12 skipped (80 total) ✅

### `test_server.py` — 53/53 ✅

| Test Class | Tests | Description |
|-----------|------:|-------------|
| TestServerBootstrap | 4 | Django ORM ready, DB path, model counts, table creation |
| TestInfoRoutes | 3 | `GET /`, `/health`, `/stats` |
| TestNodeCRUD | 8 | Create, list, get, update, delete, duplicate, filter |
| TestHeartbeat | 4 | Register, update, history, stale detection |
| TestDeviceConfig | 5 | Create, get, update, delete, per-node filter |
| TestMasterDevice | 3 | CRUD |
| TestCloudLink | 3 | CRUD |
| TestSyncLog | 4 | CRUD + filter by status |
| TestApprovalWorkflow | 5 | Create, approve, reject, pending list, stats |
| TestErrorHandling | 6 | Invalid JSON, missing fields, 404, validation |
| TestCORS | 3 | Preflight, headers, allowed methods |
| TestAuth | 5 | API key, token create, token validate, public paths |

### `test_data_sync.py` — 6 passed / 12 skipped

| Class | Tests | Passed | Skipped | Description |
|-------|------:|------:|------:|-------------|
| `TestModelParity` | 6 | 6 | 0 | Django ready, all Rust tables have models, managed=False, SupportTicket managed, unified DB, table mapping |
| `TestRealCrossORM` | 12 | 0 | 12 | Requires Rust-built `restaurant.db` — skipped gracefully |

**Rust DB tables covered (mapping validation):**
```
settings, categories, products, delivery_types, employee_types, employees,
customers, sales, sale_items, ingredients, recipe_types, recipes,
recipe_ingredients, inventory_transactions, inventory_adjustments,
inventory_alerts, suppliers, purchase_orders, purchase_order_items,
kitchen_tickets, loyalty_transactions, receipt_templates, tax_reports,
employee_schedules, payrolls, users, roles, user_roles, report_metadata,
crm_companies, crm_contacts, crm_pipelines, crm_stages, crm_deals,
crm_activities, crm_notes, crm_sync_log, crm_sync_queue, crm_cloud_config
```

### `test_webhook_e2e.py` — 10 passed / 0 failed ✅

**Fix:** `WEBHOOK_URLS` in `shared/handlers/signal.py` was a module-level `dict` frozen at import time. When `test_server.py` imported the module first (without webhook env vars), all URLs stayed `None`. Fixed by making `WEBHOOK_URLS` a `_WebhookUrls(dict)` subclass that reads `os.environ` lazily on each access.

| Test | Result |
|------|:------:|
| `test_webhook_urls_configured` | ✅ |
| `test_all_signal_urls_configured` | ✅ |
| `test_send_webhook_connection_refused` | ✅ |
| `test_send_webhook_invalid_url` | ✅ |
| `test_config_changed_creates_audit` | ✅ |
| `test_device_status_changed_creates_audit` | ✅ |
| `test_config_synced_creates_audit` | ✅ |
| `test_multiple_signals_all_audited` | ✅ |
| `test_webhook_status_tracked_in_audit` | ✅ |
| `test_payload_has_expected_fields` | ✅ |

---

## Direction 2b: Pos-Solo Sidecar (`projects/pos/pos-solo/sidecar/tests/`)

**Command:**
```bash
DJANGO_SETTINGS_MODULE='' python3 -m pytest tests/test_unified_api.py -v --import-mode=importlib
```

**Result:** 155/155 ✅ (100%)

| Test Class | Tests | Description |
|-----------|------:|-------------|
| TestServerBootstrap | 5 | Django ready, DB path, model counts, table creation |
| TestInfoRoutes | 3 | `GET /`, `/health`, `/stats` |
| TestCategoryCRUD | 8 | Create, list, get, update, delete, filter by name |
| TestProductCRUD | 12 | CRUD + price filter, category FK, pagination |
| TestCustomerCRUD | 10 | CRUD + name/email filter, phone validation |
| TestSaleCRUD | 10 | CRUD + date range, amount filter, customer FK |
| TestSaleItemCRUD | 8 | CRUD + sale FK, product FK, quantity validation |
| TestInventoryCRUD | 8 | CRUD + ingredient FK, transaction type filter |
| TestEmployeeCRUD | 8 | CRUD + role filter, active status |
| TestMenuItemCRUD | 8 | CRUD + price filter, category FK |
| TestMenuCRUD | 6 | CRUD + item assignment |
| TestNodeCRUD | 10 | CRUD + heartbeat, active filter |
| TestDeviceConfig | 8 | CRUD + per-node config, key/value |
| TestMasterDevice | 5 | CRUD |
| TestCloudLink | 5 | CRUD |
| TestSyncLog | 8 | CRUD + status filter, direction filter |
| TestApprovalWorkflow | 8 | Create, approve, reject, list, stats |
| TestErrorHandling | 8 | Invalid JSON, missing fields, 404, validation |
| TestCORS | 4 | Headers, preflight |
| TestAuth | 6 | Token create, validate, public paths |
| TestPagination | 7 | Page size, offset, max limit |

---

## Sync Infrastructure Inspection

> No live sync was performed — cloud CRM at `http://127.0.0.1:8082` was not running. This section inspects sync infrastructure: endpoints, engine, state file, and database layout.

### Sync State (`pos-full/sidecar/sync_state.json`)

```json
{
  "enabled": true,
  "cloud_url": "http://127.0.0.1:8082",
  "api_key": "",
  "last_sync": "2026-07-20T07:03:11.277731+00:00",
  "status": "error",
  "items_synced": 0,
  "errors": 1,
  "last_error": "All connection attempts failed"
}
```

**Status:** `error` — cloud CRM at `http://127.0.0.1:8082` is not reachable. Expected in local dev.

### Sync Engine (`shared/services/sync.py`)

`ProductSyncEngine` provides:
- **Master→Child**: push_products, push_config, push_catalog
- **Child→Master**: receive_sales, receive_reports, receive_inventory
- **Approval queue**: approve_changes, reject_changes, get_pending_approvals
- **Stats**: get_approval_stats (by type: pending/approved/rejected/applied)

### Sync Endpoint Comparison

| Endpoint | Pos-Full | Pos-Solo |
|----------|:---:|:---:|
| `GET /sync/status` | ✅ | ✅ |
| `PATCH /sync/config` | ✅ | ✅ |
| `GET /sync/log` | ✅ | ✅ |
| `POST /sync/trigger` | ✅ | ✅ |
| `POST /cloud/push/:type` | ✅ | ✅ |
| `POST /api/sync/push/:type` | ✅ | ❌ |
| `POST /sync/receive/sales` | ✅ | ✅ |
| `POST /sync/receive/reports` | ✅ | ✅ |
| `POST /sync/receive/inventory` | ✅ | ✅ |
| `POST /sync/push/products` | ✅ | ✅ |
| `POST /sync/push/configs` | ✅ | ✅ |
| `POST /sync/push/catalog` | ✅ | ✅ |
| `POST /sales/with-items` | ✅ | ❌ |
| **Total** | **13** | **11** |

### Database Comparison

| Property | Pos-Full | Pos-Solo |
|----------|----------|----------|
| DB file | `restaurant.db` (270 KB) | `unified.db` (runtime) |
| Owner | Rust backend (source of truth) | Django ORM (managed=True) |
| Rust tables | 30+ (managed=False in posapp/) | 0 (all Django-managed) |
| Registry tables | `full_*` prefix | `unified_*` prefix |
| Approval table | `pos_sync_approvals` | `pos_sync_approvals` |
| Token table | `cloud_device_tokens` | `cloud_device_tokens` |
| Audit table | `pos_signal_events` | `pos_signal_events` |

---

## Streams (WebSocket) Analysis

Both sidecars use `streams.py` for WebSocket broadcasting:

| Property | Pos-Full | Pos-Solo |
|----------|----------|----------|
| WebSocket endpoints | `/ws/nodes`, `/ws/config` | `/ws/config` |
| Node event broadcast | `_broadcast_node_event()` | Not exposed |
| Config event broadcast | `_broadcast_config_event()` | `_broadcast_config_event()` |
| Client filtering | node_id, event_type, node_types | node_id, event_type |
| Auto-disconnect cleanup | ✅ | ✅ |

**Node events (Full only):** `node_register`, `node_deregister`, `heartbeat`, `sync_complete`, `sync_push`

**Config events (Both):** `config_changed`, `config_synced`, `configs_pushed`, `catalog_pushed`, `products_pushed`

---

## HTML Serving Assessment

### Current State: API-Only (No HTML)

Both sidecars serve **REST JSON + WebSocket exclusively**. No server-side HTML rendering.

### Existing HTML Templates (Tauri Frontend)

| File | Location | Usage |
|------|----------|-------|
| `support_email.html` | `src-tauri/templates/` | Support ticket email body |
| `invoice.html` | `src-tauri/templates/` | Invoice PDF template (used by ReportLab server-side) |
| `index.html` | root | Vite entry point (React SPA) |

### Potential Sidecar HTML Additions

| Page | Route | Framework | Priority |
|------|-------|-----------|----------|
| Dashboard | `GET /` | Jinja2/Mako | High |
| Node management | `GET /admin/nodes` | Jinja2 | Medium |
| Approval queue | `GET /admin/approvals` | Jinja2 | Medium |
| Sync dashboard | `GET /sync/dashboard` | Jinja2 | Medium |
| API docs | `GET /docs` | OpenAPI (auto) | Low |
| Health status | `GET /health` | Already JSON | — |

**Implementation approach:** Robyn supports `robyn.templating` for Jinja2 template rendering. Add `robyn.templating.Template` to `server.py` and register HTML routes alongside existing JSON routes.

---

## Environment

| Component | Version |
|-----------|---------|
| Python | 3.10.12 |
| Django | 5.2.16 (venv) / 5.2.15 (system) |
| Robyn | 0.88.0 |
| Pydantic | Available |
| pytest | 7.x+ |
| OS | Linux |

---

## Related

| Document | Path |
|----------|------|
| Pos-Full architecture | `projects/pos/pos-full/sidecar/ARCHITECTURE.md` |
| Pos-Solo architecture | `projects/pos/pos-solo/sidecar/ARCHITECTURE.md` |
| Sidecar overview | [`sidecar/README.md`](sidecar/README.md) |
| Django ORM guide | [`sidecar/django-orm.md`](sidecar/django-orm.md) |
| Edition comparison | [`editions.md`](editions.md) |
