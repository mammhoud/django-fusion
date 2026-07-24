# POS Sidecar v2 — Robyn + Django ORM Architecture

> **Status:** Production Ready (with known test issues)  
> **Last Updated:** 2026-07-24 (fusion audit)  
> **Editions:** pos-solo (standalone) + pos-full (cloud master)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Edition Comparison](#2-edition-comparison)
3. [Model Reference](#3-model-reference)
4. [API Endpoint Catalog](#4-api-endpoint-catalog)
5. [WebSocket Streams](#5-websocket-streams)
6. [Django Signals](#6-django-signals)
7. [Approval Workflow](#7-approval-workflow)
8. [Product Sync Engine](#8-product-sync-engine)
9. [Django Portal Pages — Removed](#9-django-portal-pages--removed)
10. [Shared Module Map](#10-shared-module-map)
11. [Cloud Server Plan](#11-cloud-server-plan)
12. [django-fusion Token System](#12-django-fusion-token-system)
13. [Testing & Validation](#13-testing--validation)
14. [Recommendations](#14-recommendations)
15. [Roadmap](#15-roadmap)

---

## 1. Architecture Overview

Both POS editions now use a **Robyn** async Python web server with **Django ORM** for database access. This replaces the old Sanic-based sidecar architecture.

```
┌──────────────────────────────────────────────────────────────┐
│  POS Server (Robyn, async)                                   │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌──────────┐      │
│  │ POS API  │ │  Node API │ │ Config   │ │ Sync     │      │
│  │ (CRUD)   │ │(register, │ │ (devices, │ │ (status, │      │
│  │          │ │ heartbeat)│ │ master,  │ │ push,    │      │
│  │          │ │           │ │ cloud)   │ │ approval)│      │
│  └────▲─────┘ └────▲──────┘ └────▲─────┘ └────▲─────┘      │
│       │            │             │            │             │
│       └────────────┴─────────────┴────────────┘             │
│                         │                                   │
│              Django ORM (SQLite)                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ posapp/models.py  (Rust-backed, read-only, Full)     │    │
│  │ models/ package (pos.py, menu.py) (managed=True, Solo)               │    │
│  │ models.py         (managed=True, Node Registry)      │    ││  │  shared/           (signals, models, services, middleware)│    │
│  │ approval_models.py (SyncApproval workflow)            │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘

                         │  WebSockets
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  /ws/nodes   — Node event stream (register, heartbeat, ...)  │
│  /ws/config  — Config change stream (config, approval, sync) │
└──────────────────────────────────────────────────────────────┘

                         │  Portal Removed
                         ▼
           All functionality served by Robyn server only
```

### Server Startup

```bash
# Solo edition (standalone)
cd projects/pos/pos-solo/sidecar
python3 server.py --port 8765               # schema_editor tables (dev)
python3 server.py --port 8765 --migrate     # Django migrations (production)

# Full edition (cloud master)
cd projects/pos/pos-full/sidecar
python3 server.py --port 8766               # schema_editor tables (dev)
python3 server.py --port 8766 --migrate     # Django migrations (production)

# Django CLI for migration management
python3 manage.py makemigrations            # Create migration files
python3 manage.py migrate                   # Apply all migrations
python3 manage.py showmigrations            # List migration status

# Django Portal removed — Robyn server handles everything
```

### Migration Infrastructure & `--migrate` Flag

The `--migrate` flag controls how database tables are created at startup:

| Mode | Command | Mechanism | When to Use |
|------|---------|-----------|-------------|
| **Dev (default)** | `python server.py` | `schema_editor.create_model()` — inline table creation | Rapid development, no migration files needed |
| **Production** | `python server.py --migrate` | `call_command("migrate")` — Django migration system | Tracked schema changes, reproducible deployments |

#### How `_ensure_tables()` Works

Both `server.py` files implement a shared pattern:

```python
def _ensure_tables(use_migrations=False):
    """Create database tables — dev (schema_editor) or production (migrations)."""
    if use_migrations:
        from django.core.management import call_command
        call_command("migrate", verbosity=1)
        logger.info("Tables created via Django migrations")
    else:
        from django.db import connection
        with connection.schema_editor() as editor:
            for model in _ALL_MODELS:
                editor.create_model(model)
        logger.info("Tables created via schema_editor (%d models)", len(_ALL_MODELS))
```

#### AppConfig Registration

Each edition registers Django `AppConfig` subclasses so the migration system can discover models:

```python
# server.py — INSTALLED_APPS
INSTALLED_APPS = [
    "django.contrib.contenttypes",  # Required: ContentType framework
    "models.PosSoloConfig",         # pos_unified: 16 managed models (Solo)
    "models.posapp_app.PosappConfig", # posapp: ~30 managed models (Solo only)
    # Full: "models.PosFullConfig"  # pos_full: 16 managed models
]
```

#### manage.py CLI

Both sidecars ship a `manage.py` for Django migration management:

```bash
cd sidecar/
python3 manage.py makemigrations      # Generate migration files
python3 manage.py migrate             # Apply all migrations
python3 manage.py showmigrations      # List migration status
python3 manage.py migrate posapp zero # Rollback a specific app
```

#### Migration File Layout

```
(Solo) models/
├── apps.py                  ── PosSoloConfig(label="pos_unified")
├── models.py                ── models_module → all ~16 models
├── migrations/
│   └── 0001_initial.py      ── pos_unified migration
└── posapp_app/
    ├── apps.py              ── PosappConfig(label="posapp")
    ├── models.py            ── models_module → ~30 posapp models
    └── migrations/
        └── 0001_initial.py  ── posapp migration (~560 lines)

(Full) models/
├── apps.py                  ── PosFullConfig(label="pos_full")
├── models.py                ── models_module → all ~16 models
└── migrations/
    └── 0001_initial.py      ── pos_full migration
```

#### Why `posapp_app/` Is a Separate Sub-Package (Solo Only)

Two `AppConfig` instances can't share the same `name` because their `migrations/` directories would collide. By using `name = "models.posapp_app"` for `PosappConfig` (vs `name = "models"` for `PosSoloConfig`), each app gets its own isolated `migrations/` directory.

---

## 2. Edition Comparison

| Feature | pos-solo | pos-full |
|---------|----------|----------|
| **Server file** | `sidecar/server.py` | `sidecar/server.py` |
| **Models** | `models/` package (16 unified + 30 posapp, all managed=True) | `models/` package (16 registry, managed=True) + posapp (30+, managed=False) |
| **Database** | `restaurant.db` | `restaurant.db` |
| **Default port** | 8765 | 8766 |
| **Migrations** | ✅ 3 apps: pos_unified + posapp + contenttypes | ✅ 1 app: pos_full + contenttypes + auth |
| **manage.py** | ✅ migrate, makemigrations, showmigrations | ✅ migrate, makemigrations, showmigrations |
| **--migrate flag** | ✅ `call_command("migrate")` at startup | ✅ `call_command("migrate")` at startup |
| **Rust POS tables** | ❌ (unified only) | ✅ (posapp, managed=False) |
| **Node WebSocket** | ❌ | ✅ `/ws/nodes` |
| **Config WebSocket** | ✅ `/ws/config` | ✅ `/ws/config` |
| **Django Portal** | Removed | Removed |
| **Bolt API** | ❌ | ❌ (removed) |
| **Use case** | Standalone POS node | Cloud master / multi-node |

---

## 3. Model Reference

### 3.1 Node Registry (both editions)

| Model | Table (Full) | Table (Solo) | Purpose |
|-------|-------------|-------------|---------|
| `Node` | `full_nodes` | `unified_nodes` | Registered POS nodes with status, capabilities, metadata |
| `Heartbeat` | `full_heartbeats` | `unified_heartbeats` | Heartbeat audit log per node |
| `NodeEvent` | `full_node_events` | `unified_node_events` | Node lifecycle events (register, config_change, etc.) |
| `SyncLog` | `full_sync_logs` | `unified_sync_logs` | Data sync operation audit trail |

### 3.2 Configuration Models (both editions)

| Model | Table (Full) | Table (Solo) | Purpose |
|-------|-------------|-------------|---------|
| `DeviceConfig` | `full_device_configs` | `unified_device_configs` | Per-node key-value config entries |
| `MasterDevice` | `full_master_devices` | `unified_master_devices` | Master devices managing child nodes |
| `CloudLink` | `full_cloud_links` | `unified_cloud_links` | Cloud connection config (URL, API key, status) |

### 3.3 Approval Model (shared)

| Model | Table | Purpose |
|-------|-------|---------|
| `SyncApproval` | `pos_sync_approvals` | Pending data changes requiring moderation |

**Entity types:** sale, product, config, report, inventory, customer, employee, category, sync, other  
**Statuses:** pending, approved, rejected, applied, failed  
**Methods:** `approve(reviewer, notes)`, `reject(reviewer, notes)`, `mark_applied(error)`

### 3.4 POS Core Models

**Solo edition** (`models/pos.py`, `models/menu.py` — all managed=True, app_label=pos_unified):
Category, Product, Customer, Sale, SaleItem, InventoryTransaction, Employee, MenuItem, Menu, MenuItemAssignment

**Solo posapp** (`models/core.py`, `models/sales.py`, etc. — managed=True, app_label=posapp, PosappConfig):
AppSettings, Category, Product, DeliveryType, EmployeeType, Customer, Sale, SaleItem, LoyaltyTransaction, Employee, EmployeeSchedule, Payroll, User, Role, UserRole, Ingredient, RecipeType, Recipe, RecipeIngredient, InventoryTransaction, InventoryAdjustment, InventoryAlert, Supplier, PurchaseOrder, PurchaseOrderItem, KitchenTicket, SupportTicket, ReceiptTemplate, TaxReport, ReportMetadata (~30 models)

**Full edition** (`models/core.py`, etc. — managed=False, Rust-owned):
Same schema as Solo posapp, but managed=False (read-only via Django ORM)

---

## 4. API Endpoint Catalog

### 4.1 Info & Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service info, model counts |
| GET | `/health` | Health check with uptime |
| GET | `/stats` | Cross-model statistics |

### 4.2 POS Core CRUD (Generic)

| Method | Path | Models |
|--------|------|--------|
| GET/POST | `/{entity}` | List/Create |
| GET/PATCH/DELETE | `/{entity}/:id` | Read/Update/Delete |

**Full edition entities:** products, categories, customers, sales, sale-items, employees, ingredients, inventory, suppliers, purchase-orders, kitchen-tickets, support-tickets, heartbeats, sync-logs

**Solo edition entities:** products, customers, sales, sale-items, inventory, employees, categories, menu-items, menus, menu-assignments, nodes, heartbeats, sync-logs

### 4.3 Node API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/nodes` | List all registered nodes (paginated) |
| GET | `/nodes/:node_id` | Get node by node_id |
| POST | `/nodes/register` | Register or update a node |
| POST | `/nodes/heartbeat` | Record node heartbeat |
| PATCH | `/nodes/:node_id` | Update node metadata |
| DELETE | `/nodes/:node_id` | Delete a node |
| GET | `/nodes/:node_id/history` | Detailed device history (events, heartbeats, configs, syncs) |
| GET | `/nodes/:node_id/config` | Get per-node config entries |
| POST | `/nodes/:node_id/config` | Set per-node config entry |
| DELETE | `/nodes/:node_id/config/:key` | Delete per-node config entry |

### 4.4 Configuration API

| Method | Path | Description |
|--------|------|-------------|
| GET/POST/PATCH/DELETE | `/config/devices` | DeviceConfig CRUD |
| GET/POST/PATCH/DELETE | `/config/master` | MasterDevice CRUD |
| GET/POST/PATCH/DELETE | `/config/cloud-links` | CloudLink CRUD |
| POST | `/config/cloud-links/:pk/test` | Test cloud connection |
| POST | `/config/master/:pk/sync` | Push master config to managed nodes |

### 4.5 Events & Sync

| Method | Path | Description |
|--------|------|-------------|
| GET | `/events` | List node events (filtered) |
| GET | `/sync/status` | Sync config + local logs + cloud health |
| PATCH | `/sync/config` | Update sync configuration |
| GET | `/sync/log` | Sync history |
| POST | `/sync/trigger` | Trigger sync of all active nodes |
| POST | `/cloud/push/:entity_type` | Proxy push to upstream CRM |

### 4.6 Approval API

| Method | Path | Description |
|--------|------|-------------|
| GET/POST/PATCH/DELETE | `/approvals` | SyncApproval CRUD |
| POST | `/approvals/:pk/approve` | Approve a pending change |
| POST | `/approvals/:pk/reject` | Reject a pending change |
| GET | `/approvals/stats` | Approval queue statistics |
| GET | `/approvals/pending` | List pending approvals (filtered) |

### 4.7 Product Sync API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/sync/receive/sales` | Receive sales from child node → approval queue |
| POST | `/sync/receive/reports` | Receive reports from child node → approval queue |
| POST | `/sync/receive/inventory` | Receive inventory changes → approval queue |
| POST | `/sync/push/products` | Master pushes products to child node(s) |
| POST | `/sync/push/configs` | Master pushes config to child node(s) |
| POST | `/sync/push/catalog` | Master pushes full catalog (products + categories + settings) |

### 4.8 Sales (Full edition only)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/sales/with-items` | Create sale with line items (uses posapp models) |
| POST | `/api/sync/push/:entity_type` | Receive push from POS node (cloud master) |

---

## 5. WebSocket Streams

### 5.1 Node Event Stream (`/ws/nodes`)

**Available in:** Full edition only  
**Purpose:** Real-time node lifecycle events

```json
{
  "type": "node_event",
  "event": "registered|heartbeat|config_change|deleted|sync_push|sync_complete",
  "node_id": "NODE-001",
  "data": { ... serialized node ... },
  "timestamp": "2026-07-19T12:00:00+00:00"
}
```

**Client filters:** `{"filter": {"node_id": "NODE-001"}}`, `{"filter": {"event_type": "registered"}}`, `{"filter": {"node_types": ["pos-solo", "pos-minimal"]}}`

### 5.2 Config Stream (`/ws/config`)

**Available in:** Both editions  
**Purpose:** Real-time configuration change events

```json
{
  "type": "config_event",
  "event": "config_created|config_updated|config_deleted|master_synced|cloud_link_changed|approval_approved|approval_rejected|products_pushed|configs_pushed|catalog_pushed",
  "node_id": "NODE-001",
  "data": { ... payload ... },
  "timestamp": "2026-07-19T12:00:00+00:00"
}
```

**Client filters:** `{"filter": {"node_id": "NODE-001"}}`, `{"filter": {"event_type": "config_updated"}}`

### 5.3 Portal Polling Fallback

Since the Robyn server provides WebSocket endpoints directly, the sync_status page concept is no longer applicable.
See the WebSocket Streams section for real-time event delivery.

---

## 6. Django Signals

**File:** `projects/pos/shared/signals.py`

### 6.1 Signal Definitions

| Signal | Fired When | Payload |
|--------|-----------|---------|
| `config_changed` | Device config created/updated/deleted | node_id, config_key, action, old_value, new_value, category |
| `master_device_changed` | Master device registered/updated/deactivated | device_id, action, status, metadata |
| `cloud_link_changed` | Cloud link status changes | link_id, action, status, cloud_url |
| `config_synced` | Config pushed from master to child | source_device_id, target_device_ids, config_keys, status |
| `device_status_changed` | Device heartbeat / status change | node_id, old_status, new_status, reason |

### 6.2 Wiring Map

| Endpoint | Signal | Call |
|----------|--------|------|
| `approve_change` | `config_changed` | `fire_config_changed(node_id="__approval__", ...)` |
| `reject_change` | `config_changed` | `fire_config_changed(node_id="__approval__", ...)` |
| `set_node_config` | `config_changed` | `fire_config_changed(node_id, config_key, action, ...)` |
| `delete_node_config` | `config_changed` | `fire_config_changed(node_id, config_key, action="deleted")` |
| `sync_master_config` | `config_synced` | `fire_config_synced(source, targets, keys, status)` |
| `push_products` | `config_synced` | `fire_config_synced(source, [target], keys, status)` |
| `push_configs` | `config_synced` | `fire_config_synced(source, [target], keys, status)` |
| `receive_sales` | `device_status_changed` | `fire_device_status_changed(node_id, old, new, reason)` |
| `register_node` | `device_status_changed` | `fire_device_status_changed(node_id, "", online, "registered")` |
| `heartbeat_node` | `device_status_changed` | `fire_device_status_changed(node_id, offline, online, "restored")` |

### 6.3 Adding Receivers

```python
from django.dispatch import receiver
from shared.signals import config_changed, device_status_changed

@receiver(config_changed)
def on_config_changed(sender, **kwargs):
    node_id = kwargs.get("node_id")
    config_key = kwargs.get("config_key")
    action = kwargs.get("action")
    print(f"Config {config_key} {action} on {node_id}")
    # → Send notification, log to file, trigger webhook, etc.
```

---

## 7. Approval Workflow

**File:** `projects/pos/shared/approval_models.py`  
**Engine:** `projects/pos/shared/product_sync.py` → `ProductSyncEngine`

### 7.1 Flow

```
Child Node                    Master/Cloud Server
    │                               │
    ├── POST /sync/receive/sales ───►  SyncApproval created (pending)
    ├── POST /sync/receive/reports ──►  SyncApproval created (pending)
    │                               │
    │                           Manager reviews
    │                               │
    │◄── POST /approvals/:pk/approve ─┤  approve()
    │◄── POST /approvals/:pk/reject ──┤  reject()
    │                               │
    │                           Status: approved / rejected
    │                           If approved: mark_applied()
```

### 7.2 Approval Endpoints

| Endpoint | Function | Description |
|----------|----------|-------------|
| `POST /approvals/:pk/approve` | `sync_engine.approve_changes([pk])` | Approve + fire signal |
| `POST /approvals/:pk/reject` | `sync_engine.reject_changes([pk])` | Reject + fire signal |
| `GET /approvals/stats` | `sync_engine.get_approval_stats()` | Queue stats |
| `GET /approvals/pending` | `sync_engine.get_pending_approvals()` | Pending list |

---

## 8. Product Sync Engine

**File:** `projects/pos/shared/product_sync.py`  
**Class:** `ProductSyncEngine`

### 8.1 Methods

| Method | Direction | Purpose |
|--------|-----------|---------|
| `push_products_to_node()` | Master → Child | Push product catalog (direct or via approval) |
| `push_config_to_node()` | Master → Child | Push configuration entries |
| `push_catalog_to_node()` | Master → Child | Push full catalog (products + categories + settings) |
| `receive_sales_from_node()` | Child → Master | Receive sales (via approval queue) |
| `receive_reports_from_node()` | Child → Master | Receive reports (via approval queue) |
| `receive_inventory_changes()` | Child → Master | Receive inventory changes (via approval queue) |
| `approve_changes()` | Moderation | Approve multiple pending approvals |
| `reject_changes()` | Moderation | Reject multiple pending approvals |
| `get_pending_approvals()` | Query | List pending approvals (filtered) |
| `get_approval_stats()` | Query | Approval queue statistics |

### 8.2 Engine Initialization

```python
sync_engine = ProductSyncEngine(
    sync_log_model=SyncLog,
    node_model=Node,
    device_config_model=DeviceConfig,
    node_event_model=NodeEvent,
    sync_approval_model=SyncApproval,
    cloud_link_model=CloudLink,
)
```

---

## 9. Django Portal Pages — REMOVED

The Django portal (`manage.py runserver`) and all associated files (portal_viewsets.py,
portal_urls.py, portal_models.py, admin.py, templates/portal/, static/portal.*, seed_menu)
were removed in July 2026. The Robyn server handles everything — no separate Django
process is needed.

See [POS_ARCHITECTURE.md](POS_ARCHITECTURE.md) for the current single-server architecture.

---

## 10. Shared Module Map

**Directory:** `projects/pos/shared/`

```
shared/
├── __init__.py
├── signals/               # Signal definitions (package replaces old signals.py)
│   └── __init__.py        #   Signal definitions + fire_* helper functions
├── models/                # Shared Django models (package replaces old _models.py files)
│   ├── __init__.py        #   Re-exports all shared models
│   ├── audit.py            #   SignalEvent (audit trail)
│   ├── approval.py         #   SyncApproval (approve, reject, mark_applied)
│   └── token.py            #   DeviceToken (SHA-256 auth, issue/validate/refresh)
├── handlers/              # Signal handlers (package replaces old signal_handlers.py)
│   ├── __init__.py
│   └── signal.py          #   @receiver — log, webhook, audit persistence
├── services/              # POS services (package replaces old product_sync.py)
│   ├── __init__.py
│   └── sync.py            #   ProductSyncEngine class
├── middleware/            # Robyn middleware (package replaces old auth.py)
│   ├── __init__.py
│   └── auth.py            #   create_auth_middleware, register_auth_routes, require_role
├── api/                   # CRUD helpers (package replaces old server_base.py)
│   ├── __init__.py
│   └── crud.py            #   _ser(), _ser_node(), _paginate(), _error(),
│                           #   _list(), _get(), _create(), _update(), _delete(), _count()
│                           #   _register_crud(app, prefix, model, name)
├── node_base.py           # Base Node agent for management commands

### Backward Compatibility

Old file paths (`shared.server_base`, `shared.auth`, `shared.signal_models`, etc.)
are preserved as backward-compatible shims that re-export from the new package
locations. Existing imports in server.py files and tests continue to work.


---

## 11. Cloud Server Plan

### 11.1 Current Architecture

```
POS Solo (port 8765)          POS Full (port 8766)          Cloud CRM (Django, port 8082)
    │                              │                              │
    ├── sync client ───► push ───► │                              │
    │                              ├── cloud master ───► push ───►│
    │                              │                              │
    │                              │◄── health check ─────────────┤
    │                              │                              │
```

### 11.2 Planned: Unified Cloud Bridge

The goal is to link all POS branches (solo, full, minimal) through a unified cloud server with django-fusion authentication tokens:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cloud Server (port 8767)                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Django-fusion Auth Token System                          │  │
│  │  • Token-based device authentication                      │  │
│  │  • Role-based access (admin, manager, cashier, viewer)    │  │
│  │  • JWT tokens with refresh rotation                       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐    │
│  │ Branch Router │ │ Sync Broker  │ │ Approval Manager    │    │
│  │ • Route by    │ │ • Bidirect-  │ │ • Cross-branch      │    │
│  │   device_id   │ │   tional     │ │   approval queue    │    │
│  │ • Load bal-   │ │   streaming  │ │ • Moderator         │    │
│  │   ance        │ │   to all     │ │   dashboard         │    │
│  │ • Failover    │ │   branches   │ │ • Email/push        │    │
│  └──────┬───────┘ └──────┬───────┘ └──────────────────────┘    │
│         │                │                                      │
└─────────┼────────────────┼──────────────────────────────────────┘
          │                │
    ┌─────┴──────┐  ┌─────┴──────┐  ┌─────┴──────┐
    │ POS Solo   │  │ POS Full   │  │ Minimal    │
    │ (port 8765)│  │ (port 8766)│  │ (no sidecar│
    │            │  │            │  │  → uses    │
    │            │  │            │  │  node API) │
    └────────────┘  └────────────┘  └────────────┘
```

### 11.3 Token-Based Authentication (django-fusion)

```python
# Proposed Token model (shared/models/token.py)
class DeviceToken(models.Model):
    """django-fusion token for device authentication across branches."""
    device_id = models.CharField(max_length=100, unique=True)
    token = models.CharField(max_length=256, unique=True)
    node = models.ForeignKey(Node, on_delete=models.CASCADE, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="viewer")
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(blank=True, null=True)
```

**Token flow:**
1. Device registers with cloud server → receives JWT token
2. Subsequent API calls include `Authorization: Bearer <token>`
3. Token encodes device_id, role, permissions, branch type
4. Cloud server validates token before routing requests
5. Token refresh via `/auth/refresh` endpoint

### 11.4 Key Linking

All branches link through the cloud using these keys from the models:

| Model Key | Used For | Linked Via |
|-----------|----------|------------|
| `node_id` | Device identification | Token + device registration |
| `device_id` (MasterDevice) | Master device routing | Token role + config sync |
| `cloud_url` (CloudLink) | Cloud endpoint discovery | Health check + sync target |
| `api_key` (CloudLink) | API authentication | Header-based auth |
| `managed_node_ids` (MasterDevice) | Multi-node orchestration | Master→child push |

---

## 12. django-fusion Token System### 12.1 Current Usage
The django-fusion framework was used for the now-removed Django Portal UI:

```python
from django_fusion.comp.routes import Viewset, route

class PortalDashboard(Viewset):
    @route(path="", methods=["GET"])
    def dashboard(self, request):
        return self.render_template("portal/dashboard.html", context)
```

**Note:** The Django portal has been removed. These viewsets no longer exist.
Robyn `routes/` package is the canonical server now.

### 12.2 Token System — Implemented ✅

The token system is now fully implemented and wired into both server editions:

**Model:** `shared/models/token.py` — `DeviceToken`
- Cryptographically secure token generation (`secrets.token_urlsafe(32)`)
- SHA-256 token hashing for storage (raw token shown only once)
- Role hierarchy: viewer < cashier < manager < admin
- Token TTL with automatic expiry
- Capability scoping (JSON dict) + entity allow-listing
- Link to Node registry via optional FK
- `validate_token()` classmethod with last_used_at tracking
- `issue_token()` classmethod with configurable TTL
- `refresh()` with automatic old token revocation
- `has_role_at_least()` + `has_entity_access()` helper methods

**Middleware:** `shared/auth.py` — `create_auth_middleware()`
- Priority: Bearer token → X-API-Key fallback → public path bypass
- Sets `contextvars.ContextVar` for request-scoped token info
- `get_token_info()` helper for route handlers
- `require_role()` decorator for RBAC on routes
- `register_auth_routes()` registers 4 endpoints

**Auth Endpoints:**
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/token` | Issue a new device token (requires device_id) |
| POST | `/auth/refresh` | Refresh an existing token (revokes old, issues new) |
| GET | `/auth/verify` | Verify the current token and return its payload |
| GET | `/auth/status` | Get auth system status and configuration |

**Token Flow:**
```
Device                          Robyn Server
  │                                    │
  ├── POST /auth/token ───────────────►│  Issue token (shown once)
  │◄── { token: "abc123...", device } ─┤
  │                                    │
  ├── GET /products ──────────────────►│  Authorization: Bearer abc123...
  │    (with header)                   │  Middleware validates hash + expiry
  │◄── { data: [...] } ───────────────┤
  │                                    │
  ├── POST /auth/refresh ─────────────►│  Old token revoked, new issued
  │◄── { token: "xyz789..." } ────────┤
```

**Usage in route handlers:**
```python
from shared.auth import get_token_info, require_role

@require_role("manager")
@app.get("/approvals/pending")
async def list_pending(request: Request):
    token = get_token_info()
    if token and token["device_id"] != "__api_key__":
        # Token-authenticated device
        logger.info("Request from %s (role: %s)", token["device_id"], token["role"])
    return jsonify(...)
```

### 12.3 Token Model Integration (Implemented)

```python
# shared/models/token.py
from django.db import models

class DeviceToken(models.Model):
    device_id = models.CharField(max_length=100, unique=True, db_index=True)
    token_hash = models.CharField(max_length=128, unique=True)    # SHA-256
    token_prefix = models.CharField(max_length=8)                 # Display only
    node = models.ForeignKey("Node", on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="viewer")
    node_type = models.CharField(max_length=20, choices=NODE_TYPE_CHOICES, default="pos-solo")
    capabilities = models.JSONField(default=dict, blank=True)
    allowed_entities = models.JSONField(default=list, blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()                           # Configurable TTL
    last_used_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    @classmethod
    def issue_token(cls, device_id, role="viewer", node_type="pos-solo", 
                     ttl_days=90, **kwargs) -> tuple["DeviceToken", str]: ...
    
    @classmethod
    def validate_token(cls, raw_token: str) -> "DeviceToken | None": ...
    
    def refresh(self, ttl_days=90) -> tuple["DeviceToken", str]: ...
```

**Role Hierarchy:** `viewer` (0) < `cashier` (1) < `manager` (2) < `admin` (3)

---

## 13. Testing & Validation *(audited 2026-07-24)*

### 13.1 Current Test Suite

| Test File | Location | Tests | Status |
|-----------|----------|-------|--------|
| `test_server.py` | `pos-full/sidecar/tests/` | ~63 | 🟡 Collection errors |
| `test_unified_api.py` | `pos-solo/sidecar/tests/` | ~155 | 🟡 Collection errors |
| `test_fragments.py` | `pos-full/sidecar/tests/` | 8 | ✅ Added |
| `test_fusion.py` | `pos-full/sidecar/tests/` | ~25 | ✅ Added |
| `test_fusion_integration.py` | `pos-full/sidecar/tests/` | ~20 | 🟡 Collection errors |
| `test_webhook_e2e.py` | `pos-full/sidecar/tests/` | — | 🔴 **3 collection errors** |

**pos-full total:** 75 tests collected, 3 errors  
**pos-solo total:** 74 tests collected, 3 errors

### 13.2 Known Issues

- **3 test files have collection errors** in both editions:
  - `test_webhook_e2e.py` — `AssertionError` during collection.
  - `test_fusion_integration.py` — `AssertionError` during collection, likely a Django settings/import issue.
  - `test_server.py` — `RuntimeError: Model...` during module import.
  These 3 errors block the full test suite from running (75/74 tests collected but none execute).
- **`RequestsDependencyWarning`** — incompatible `urllib3` (2.7.0) or `chardet` (4.0.0) versions with the installed `requests` library.

### 13.3 Test Commands

```bash
# Full edition tests (all)
cd projects/pos/pos-full/sidecar
DJANGO_SETTINGS_MODULE='' python3 -m pytest tests/ -v --tb=short

# Solo edition tests (all)
cd projects/pos/pos-solo/sidecar
DJANGO_SETTINGS_MODULE='' python3 -m pytest tests/ -v --tb=short

# Only fusion tests (passing subset)
DJANGO_SETTINGS_MODULE='' python3 -m pytest tests/test_fragments.py tests/test_fusion.py -v

# Import check
DJANGO_SETTINGS_MODULE='' python3 -c "from server import _DJANGO_READY, app; print(f'OK: Django={_DJANGO_READY}')"
```

---

## 14. Recommendations

### 14.1 Immediate

1. **Add Pydantic validation** — Add request/response validation models for all endpoints
2. **Improve error handling** — Standardize error responses across all route modules
3. **Add rate limiting** — Per-token rate limiting for auth-protected endpoints

### 14.2 Short-term

1. **Database migrations** — ✅ Complete. Both editions now have proper Django AppConfig (`PosSoloConfig`, `PosFullConfig`, `PosappConfig`), `models/models.py` for model discovery, `migrations/` directories with auto-generated `0001_initial.py` files (16 unified + 30 posapp models), `manage.py` CLI, and `--migrate` flag on server.py.
2. **Add @receiver handlers** — Wire up signal receivers in `shared/signal_handlers.py` for real notification/logging
3. **Cloud server token auth** — Implement the token model and authentication flow in `shared/models/token.py`
4. **API versioning** — Add `/v1/` prefix to all endpoints for future compatibility

### 14.3 Medium-term

1. **Unified cloud server** — Create a standalone Robyn cloud server at `projects/pos/cloud-server/` that all branches connect to
2. **Branch router** — Route requests to the correct branch based on device token
3. **Cross-branch approval** — An approval created on one branch can be reviewed on any other branch
4. **Real-time sync broker** — WebSocket bridge between all connected branches for instant updates
5. **Monitoring dashboard** — django-fusion pages for cloud server health, branch status, and sync analytics

### 14.4 Architecture Improvements

1. **Extract middleware to shared** — The `log_req`, `cors_preflight`, `add_cors`, and `auth` middleware are identical in both server.py files
2. **Extract Pydantic models to shared** — `NodeRegisterRequest` and `HeartbeatRequest` are duplicated in both editions
3. **SyncClient consolidation** — The `SyncClient` class and state management functions (`_load_sync_state`, `_save_sync_state`) are nearly identical in both editions
4. **Module-level vs dynamic routes** — Standardize on either `:param` or `<param:type>` syntax (both are used inconsistently)

---

## 15. Roadmap

### Phase 1: Foundation ✅ (Complete)
- [x] Robyn + Django ORM server consolidation
- [x] Node registry models (Node, Heartbeat, NodeEvent, SyncLog)
- [x] Generic CRUD router factory
- [x] Shared server base with deduplicated helpers
- [x] Configuration models (DeviceConfig, MasterDevice, CloudLink)
- [x] Config WebSocket stream (/ws/config)
- [x] Node WebSocket stream (/ws/nodes, Full only)
- [x] Django migration infrastructure (AppConfig, models.py, migrations/, manage.py, --migrate)
- [x] PosappConfig for Solo posapp models (models/posapp_app/ with ~30 managed=True models)
- [x] Shared version metadata (`__about__.py` — single source for version strings)

### Phase 2: Sync & Moderation ✅ (Complete)
- [x] SyncApproval model with approve/reject workflow
- [x] ProductSyncEngine (Master→Child push + Child→Master receive)
- [x] Approval API endpoints
- [x] Product sync API endpoints
- [x] Django signals (config_changed, config_synced, device_status_changed)
- [x] Signal wiring into all endpoints
- [x] django-fusion approval dashboard (removed — portal deleted)
- [x] django-fusion sync status page (removed — portal deleted)
- [x] Real-time WS + polling fallback on portal pages (removed — portal deleted)

### Phase 3: Cloud Bridge ✅ (Implemented)
- [x] django-fusion token model — `shared/models/token.py` (DeviceToken with SHA-256 hashing, roles, expiry, capabilities)
- [x] Device authentication middleware — `shared/auth.py` (Bearer token validation + API key fallback)
- [x] Token auth endpoints — `POST /auth/token`, `POST /auth/refresh`, `GET /auth/verify`, `GET /auth/status`
- [x] Role hierarchy — viewer < cashier < manager < admin
- [x] Token scoping — capabilities dict + allowed_entities list
- [x] Token-based API security — `require_role()` decorator for route handlers
- [x] Token refresh flow — revoke old + issue new with configurable TTL
- [ ] Unified cloud server
- [ ] Branch router
- [ ] Cross-branch sync broker

### Phase 3.5: Fusion Infrastructure ✅ (Completed — unplanned)

> **Note:** This phase was **not in the original roadmap**. All items were implemented as
> necessary prerequisites for fragment-rendering support across the POS ecosystem and are
> now documented here for completeness.

- [x] **8 `FragmentComponent` classes** per edition — `fragments/` package: Dashboard, Suppliers, About, Customers, Inventory, Employees, ProductList, ProductDetail
- [x] **Fragment registry** — `fragments/__init__.py` with `register()` decorator, `get_all_fragments()`, `get_context()`
- [x] **Fusion health endpoint** — `GET /fusion/health` via `middleware/fusion.py` → `RobynFusionChecker` + `register_fusion_health_routes()`
- [x] **Fusion fragment routes** — `routes/fusion_fragments.py` exposing `/fragments/*` endpoints with `fusion_render_first` support
- [x] **React fusion bridge** — `FusionMiddleware` (mode context), `FusionPage` (page-level wrapper), `FusionProxy` (HTML fetch & render)
- [x] **Fusion utility libraries** — `fusion-types.ts`, `fusion-decoder.ts`, `fusion-store.ts`
- [x] **FusionPage wiring** — 13/24 pos-full pages, 11/24 pos-solo pages
- [x] **E2E fusion tests** — `fusion-e2e.test.tsx`, `FusionDecoder.test.ts`, `FusionMiddleware.test.tsx`, `FusionPage.test.tsx`, `FusionProxy.test.tsx`, `fusion-store.test.ts`
- [x] **Sidecar fusion tests** — `test_fragments.py`, `test_fusion.py`, `test_fusion_integration.py`
- [ ] **Remaining page wiring** — 10 pos-full pages, 12 pos-solo pages not yet using FusionPage

### Phase 4: Enterprise 🎯 (Planned)
- [ ] Multi-tenant support
- [ ] Role-based access control (RBAC)
- [ ] Audit log with signal-driven persistence
- [ ] Webhook notifications for config changes
- [ ] Email/push notifications for pending approvals
- [ ] Monitoring dashboard with real-time charts
- [ ] Export/import for bulk device configuration
- [ ] Automated failover between cloud links
