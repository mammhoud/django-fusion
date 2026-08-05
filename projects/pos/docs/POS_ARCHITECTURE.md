# POS Architecture — Master Design Document

> **⚠️ Superseded (August 2026):** `pos-full` and `pos-solo` have been merged
> into the single **Formint POS Professional** package — see
> [FORMINT_ARCHITECTURE.md](FORMINT_ARCHITECTURE.md) for the canonical,
> current architecture. The `pos-solo` / `pos-full` directories no longer
> exist; their merged home is [`../formint-pos/`](../formint-pos/).
>
> This document is kept as the historical design record for the pre-merge
> three-edition layout (Solo → Full → Cloud Server). Sections describing
> deleted paths (`pos-solo/`, `pos-full/`) refer to the pre-merge state.
>
> **Version:** 2.0.0 (historical)  
> **Last Updated:** 20 July 2026  
> **Editions:** Solo (standalone) → Full (cloud master) → Cloud Server (enterprise)  
> **Related:** [Bolt API Integration Plan](BOLT_INTEGRATION.md) — django-bolt integration strategy

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Edition Architecture](#2-edition-architecture)
3. [Server Layer: Robyn + Django ORM](#3-server-layer-robyn--django-orm)
4. [API Organization](#4-api-organization)
5. [Model Maps](#5-model-maps)
6. [Data Flow & Streaming](#6-data-flow--streaming)
7. [Sync & Approval Pipeline](#7-sync--approval-pipeline)
8. [Shared Module Map](#8-shared-module-map)
9. [Rust Integration Points](#9-rust-integration-points)
10. [Frontend API Integration (Redux RTK Query)](#10-frontend-api-integration-redux-rtk-query)
11. [Cloud Server Plan (Next Phase)](#11-cloud-server-plan-next-phase)
12. [Unfold Admin Dashboard (pos-full)](#12-unfold-admin-dashboard-pos-full)
13. [Roadmap & Next Steps](#13-roadmap--next-steps)

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         POS System Architecture                          │
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │  Tauri App    │    │  Tauri App   │    │  Web / Mobile Clients   │  │
│  │  (React 19)  │    │  (React 19)  │    │  (Pinia stores ↔ API)  │  │
│  └──────┬───────┘    └──────┬───────┘    └──────────┬───────────────┘  │
│         │                   │                        │                  │
│         │  HTTP REST        │  HTTP REST             │  HTTP REST       │
│         │  + WebSocket      │  + WebSocket           │  + WebSocket     │
│         ▼                   ▼                        ▼                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │               Robyn Server (Python, async)                       │  │
│  │                                                                  │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌──────────┐ ┌─────────────┐ │  │
│  │  │  POS API    │ │  Node API    │ │ Config   │ │  Sync API   │ │  │
│  │  │  (CRUD)     │ │  (register,  │ │ API      │ │  (status,   │ │  │
│  │  │  products,  │ │   heartbeat, │ │(devices, │ │   push,     │ │  │
│  │  │  sales,     │ │   events)    │ │ master,  │ │   approval, │ │  │
│  │  │  customers) │ │              │ │ cloud)   │ │   webhook)  │ │  │
│  │  └──────▲──────┘ └──────▲───────┘ └────▲─────┘ └──────▲──────┘ │  │
│  │         │               │               │              │        │  │
│  │         └───────────────┴───────────────┴──────────────┘        │  │
│  │                           │                                     │  │
│  │                Django ORM (SQLite)                               │  │
│  │  ┌──────────────────────────────────────────────────────────┐  │  │
│  │  │  models/     — Node, Heartbeat, NodeEvent, SyncLog       │  │  │
│  │  │                DeviceConfig, MasterDevice, CloudLink     │  │  │
│  │  │  unified_    — Category, Product, Customer, Sale,        │  │  │
│  │  │  models.py     SaleItem, InventoryTransaction, Employee,  │  │  │
│  │  │  (Solo)        MenuItem, Menu, MenuItemAssignment         │  │  │
│  │  │  posapp/     — Product, Category, Customer, Sale, +30    │  │  │
│  │  │  models.py     (Rust-backed, managed=False, Full only)    │  │  │
│  │  │  shared/     — SyncApproval, DeviceToken, SignalEvent    │  │  │
│  │  └──────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  WebSocket Streams                                                │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │  │
│  │  │ /ws/nodes    │  │ /ws/config   │  │ (future) /ws/sync    │  │  │
│  │  │ Node events  │  │ Config       │  │ Cross-bridge sync    │  │  │
│  │  │ (Full only)  │  │ changes      │  │ broker               │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Server** | Robyn (Rust-powered Python async) | HTTP REST + WebSocket API server |
| **ORM** | Django ORM (via Django) | Database access, migrations, signals |
| **Database** | SQLite (file-based) | Local data storage |
| **Validation** | Pydantic v2 | Request/response validation |
| **Auth** | Bearer tokens (SHA-256) + API Key | Device authentication |
| **Signals** | Django's `django.dispatch.Signal` | Event-driven notifications |
| **Frontend** | React 19 + TypeScript + Vite (Tauri) | Desktop UI |
| **Desktop** | Tauri 2 + Rust + Diesel | Desktop shell + local CRUD |

### What is a Sidecar?

A **sidecar** is a companion process that runs alongside the Tauri desktop application to provide HTTP REST + WebSocket APIs. It uses Robyn as the async server and Django ORM for database access.

```
┌──────────────────────────────────────┐
│         Tauri Desktop App             │
│  ┌──────────────┐ ┌────────────────┐ │
│  │ Rust Backend │ │ React Frontend │ │
│  │ (Diesel CRUD)│ │ (Pinia stores) │ │
│  └──────┬───────┘ └───────┬────────┘ │
│         │                  │          │
│         │  Tauri IPC       │ HTTP API │
│         │  (invoke)        │ :8765/66 │
│         ▼                  ▼          │
│  ┌──────────────────────────────────┐ │
│  │     Sidecar Process (Robyn)      │ │
│  │  ┌────────────────────────────┐ │ │
│  │  │  Django ORM (SQLite)       │ │ │
│  │  │  models/ + shared/         │ │ │
│  │  └────────────────────────────┘ │ │
│  └──────────────────────────────────┘ │
└──────────────────────────────────────┘
```

---

## 2. Edition Architecture

### 2.1 POS Mini (Standalone Terminal)

```
┌─────────────────────────────────────────────────┐
│           POS Mini (Standalone Terminal)         │
│                                                   │
│  Backend: Rust/Diesel (no sidecar)                │
│  Frontend: Tauri + React + TypeScript            │
│  Database: SQLite via Diesel ORM                 │
│  Data ops: Tauri IPC `invoke()` commands         │
│  Network: Fully offline-capable                   │
│  Use case: Single terminal / minimal POS         │
└─────────────────────────────────────────────────┘
```

**Key characteristics:**
- No Python sidecar — pure Rust/Diesel backend
- Data accessed via Tauri `invoke()` (not HTTP REST)
- No cloud sync, no node registry, no admin panel
- Smallest footprint, fastest startup

### 2.2 POS Solo (Branch Device)

```
┌─────────────────────────────────────────────────┐
│           POS Solo Server (port 8765)            │
│                                                   │
│  Database: restaurant.db                         │
│  Models: all managed=True (models/ package)      │
│  WebSocket: /ws/config only                      │
│  Cloud: Push client → Full master                │
│  Frontend: React + Redux RTK Query               │
│  Use case: Branch device / single restaurant     │
└─────────────────────────────────────────────────┘
```

**Directory Structure:**
```
pos-solo/sidecar/
├── server.py              # Robyn entry point: bootstrap + middleware + CRUD
├── routes/                # Route handler modules
│   ├── __init__.py        # register_all(app)
│   ├── state.py           # Shared state, SyncClient, WS broadcast
│   ├── info.py            # /, /health, /stats
│   ├── nodes.py           # Node CRUD, register, heartbeat, WS
│   ├── config.py          # Device/Master/Cloud config, WS /ws/config
│   ├── sync.py            # Sync status, trigger, push, cloud push
│   └── approvals.py       # Approve, reject, pending
├── models/                # Django ORM models (pos_unified)
│   ├── pos.py             # Product, Customer, Sale, etc.
│   ├── menu.py            # MenuItem, Menu, MenuItemAssignment
│   ├── node.py            # Node, Heartbeat, NodeEvent
│   ├── config.py          # DeviceConfig, MasterDevice, CloudLink
│   └── sync.py            # SyncLog
├── tests/
│   └── test_unified_api.py  # 155 tests
├── Makefile               # Sidecar commands
├── pyproject.toml          # Python project metadata
└── requirements.txt        # Dependencies
```

### 2.3 POS Full (Master Manager)

```
┌─────────────────────────────────────────────────┐
│           POS Full Server (port 8766)            │
│                                                   │
│  Database: restaurant.db                         │
│  Admin Panel: Django Unfold (port 8000)          │
│  Dashboard: 9 KPI cards, 5 charts, 2 tables     │
│  WebSocket: /ws/entities + /ws/nodes + /ws/config │
│  Cloud: Master ↔ Children sync                   │
│  Features: Admin panel, node registry, sync      │
│  Use case: Multi-branch management / cloud master │
└─────────────────────────────────────────────────┘
```

**Directory Structure:**
```
pos-full/sidecar/
├── configs/               # Centralized Django settings
│   ├── __init__.py        # Django + Unfold settings
│   ├── admin.py           # 17+ model admin registrations
│   ├── dashboard.py       # Custom dashboard (9 KPI + 5 charts + 2 tables)
│   └── urls.py            # Django URL configuration
├── server.py              # Robyn entry point: bootstrap + middleware + CRUD
├── manage.py              # Django CLI with --ensure-superuser flag
├── handlers.py            # CRUD factory with WS broadcast
├── streams.py             # WebSocket broadcast functions
├── routes/                # Route handler modules
│   ├── nodes.py           # Node registration/heartbeat/WS
│   ├── config.py          # Device config/WS
│   ├── sync.py            # Sync status/trigger
│   └── approvals.py       # Sync approval workflow
├── models/                # Django ORM models (pos_full)
│   ├── pos.py             # Category, Product, Customer, Sale...
│   ├── node.py            # Node, Heartbeat, NodeEvent
│   ├── config.py          # DeviceConfig, MasterDevice, CloudLink
│   ├── inventory.py       # Supplier, PurchaseOrder
│   ├── ops.py             # KitchenTicket, SupportTicket
│   └── menu.py            # MenuItem, Menu
├── tests/
│   └── test_server.py     # 53 tests
├── Makefile               # Admin bootstrap + screenshot targets
├── pyproject.toml          # Python project metadata
└── requirements.txt        # Dependencies
```

### 2.3 Edition Comparison

| Feature | pos-mini | pos-solo | pos-full |
|---------|:--------:|:--------:|:--------:|
| **Backend** | Rust/Diesel | Robyn + Django ORM | Robyn + Django ORM |
| **Port** | N/A (Tauri IPC) | 8765 | 8766 |
| **Admin Panel** | ❌ | ❌ | ✅ Unfold dashboard |
| **Data Layer** | `invoke()` (Rust) | Redux RTK Query | Redux RTK Query |
| **POS Models** | Rust/Diesel | managed (`pos_unified`) | managed (`pos_full`) |
| **Manage.py** | ❌ | ✅ | ✅ |
| **Configs/** | ❌ | ❌ | ✅ Django + Unfold |
| **Dashboard** | ❌ | ❌ | ✅ 9 KPI + 5 charts + 2 tables |
| **Node WebSocket** | ❌ | ❌ | ✅ `/ws/entities` + `/ws/nodes` |
| **Config WebSocket** | ❌ | ✅ `/ws/config` | ✅ `/ws/config` |
| **Paginated API** | ❌ | ✅ (60+ endpoints) | ✅ (30+ endpoints) |
| **Approval Workflow** | ❌ | ✅ | ✅ |
| **Product Sync Engine** | ❌ | ✅ | ✅ |
| **Token Auth** | ❌ | ✅ | ✅ |
| **Cloud Sync** | ❌ | ✅ (child→master) | ✅ (master↔children) |
| **Webhook Receiver** | ❌ | ❌ | ✅ |
| **Architecture Role** | Standalone | Branch device | Master manager |
| **Tests** | — | 155 | 53 |

**Key distinctions:**
- **pos-mini** is a minimal Tauri desktop app with Rust/Diesel local CRUD — no sidecar, no API, no cloud sync.
- **pos-solo** is a branch device with a local Robyn sidecar (port 8765), Redux frontend, and cloud sync pushing data to pos-full master.
- **pos-full** is the master manager with a Robyn sidecar (port 8766), Unfold Django admin dashboard (port 8000), node registry, and full cloud sync in both directions.

---

## 3. Server Layer: Robyn + Django ORM

The server uses **Robyn** (a Rust-powered Python async web framework) as the HTTP/WS server with **Django ORM** for database access. This eliminates the need for a full Django portal process — Robyn handles everything.

### Server Bootstrap Flow

```
1. Python imports server.py
2. Django ORM configures (settings.configure)
3. django.setup() — loads apps, discovers models via AppConfig
4. Models are imported and registered
5. init_state() — passes models/config/services to routes/state.py
6. Robyn app created, middleware configured
7. Generic CRUD endpoints registered via _register_crud (from routes.state)
8. register_all(app) — wires all route handlers from routes/ package
9. main(): _ensure_tables(args.migrate) — schema_editor or migrations
10. Server starts: app.start(host, port)
```

**Table creation options:**
- `python server.py` — schema_editor.create_model() (fast, dev-friendly)
- `python server.py --migrate` — Django migration system (production-ready, tracks changes)
- `python manage.py migrate` — CLI migration management (makemigrations, showmigrations)

### Architecture Pattern: Thin Entry Point + Routes Package

`server.py` is now a thin entry point (~400 lines). All route handlers live in the `routes/` package and access shared state via `init_state()`:

```
server.py                         routes/state.py
─────────                        ───────────────
 Django bootstrap                 _ser, _ser_node, _paginate, _error
 Model imports                    _list, _get, _create, _update, _delete
 init_state(...)  ─────────────►  Node, Heartbeat, SyncLog, ...
                     passes       SyncClient, _register_crud
 app = Robyn(...)    models       _ws_clients, _broadcast_node_event
 middleware          config       _config_ws_clients, _broadcast_config_event
 CRUD registration   services     fire_config_changed, fire_config_synced
 register_all(app) ───────────►  routes/*.py: import state as S; S._list(...)
 main(): start()     routes
```

### Key Modules

| File | Lines | Responsibility |
|------|-------|---------------|
| `server.py` | ~415 | Django bootstrap, middleware, CRUD registration, `init_state()`, `register_all()`, `main()` |
| `manage.py` | ~45 | Django CLI — migrate, makemigrations, showmigrations |
| `models/apps.py` | ~12 | PosFullConfig / PosSoloConfig AppConfig |
| `models/models.py` | ~20 | Django models_module — imports all managed models |
| `models/posapp_app/` (Solo) | ~30 | PosappConfig + models.py for ~30 Rust-mirror models |
| `routes/state.py` | ~450 | Shared helpers (`_ser`, `_list`), `SyncClient`, WebSocket state, `_register_crud` (consolidated from both editions) |
| `routes/info.py` | ~60 | `GET /`, `/health`, `/stats` — service info + health checks |
| `routes/nodes.py` | ~350 | Node CRUD, register, heartbeat, update, delete, history, WS `/ws/nodes` (Full) |
| `routes/config.py` | ~140 | Per-node config, master config sync, cloud link test, WS `/ws/config` |
| `routes/sync.py` | ~300 | Sync status, config, trigger, push/receive, cloud push |
| `routes/approvals.py` | ~70 | Approve, reject, stats, pending, receive endpoints |
| `routes/webhooks.py` | ~80 (Full) | Webhook receive, list, stats |
| `tests/test_server.py` | — | 53 tests (Full); server bootstrap + CRUD coverage |
| `tests/test_webhook_e2e.py` | — | 10 tests (Full); signal → webhook end-to-end |
| `tests/django_setup.py` | ~95 (Full) | Standalone Django bootstrap helper (decoupled from server.py) |

### Test Helpers

Each sidecar's test suite includes a standalone Django bootstrap helper that decouples tests from server.py:

```python
# tests/django_setup.py — standalone Django ORM bootstrap for tests
# Does NOT import server.py; no Robyn app creation, middleware, or route wiring.
# Sets up: Django ORM, model tables, signal handlers, webhook helpers.

from tests.django_setup import _DJANGO_READY
assert _DJANGO_READY, "Django ORM bootstrap failed"
```

This keeps tests robust — a failure in server.py won't crash the test suite,
and test imports don't trigger server.py side effects.

### Migration Infrastructure

Both editions use Django's built-in migration system for database schema management. The `--migrate` flag controls which table-creation strategy is used at startup.

#### Two Modes

| Mode | Command | Mechanism | Use Case |
|------|---------|-----------|----------|
| **Dev** | `python server.py` (default) | `schema_editor.create_model()` — creates tables directly from model definitions | Fast iteration, no migration files needed |
| **Production** | `python server.py --migrate` | `call_command("migrate")` — applies Django migration files | Tracked schema changes, reproducible deployments |

Under the hood, `_ensure_tables(use_migrations: bool)` in `server.py` branches:

```python
def _ensure_tables(use_migrations=False):
    if use_migrations:
        call_command("migrate", verbosity=1)     # Apply all Django migrations
    else:
        for model in _ALL_MODELS:                # Dev: create tables inline
            schema_editor.create_model(model)
```

#### CLI Management

```bash
# All migration management goes through manage.py (Django's standard CLI)
cd sidecar/

python3 manage.py makemigrations          # Generate migration files from models
python3 manage.py migrate                 # Apply all pending migrations
python3 manage.py showmigrations          # List migration status for each app
python3 manage.py migrate pos_unified     # Apply migrations for a specific app
python3 manage.py migrate posapp zero     # Rollback all posapp migrations
```

#### AppConfig Structure

Each edition uses Django `AppConfig` subclasses to register models with the migration system:

| Edition | Config | Label | Models | Details |
|---------|--------|-------|--------|---------|
| **Solo** | `PosSoloConfig` (models/apps.py) | `pos_unified` | 16 managed | Node, Heartbeat, Product, Customer, Sale, MenuItem, etc. |
| **Solo** | `PosappConfig` (models/posapp_app/apps.py) | `posapp` | ~30 managed | AppSettings, Employee, Payroll, InventoryTransaction, Supplier, KitchenTicket, etc. |
| **Full** | `PosFullConfig` (models/apps.py) | `pos_full` | 16 managed | Node, Heartbeat, DeviceConfig, Product, Customer, Sale, etc. |

Each AppConfig uses `models_module` to point to a dedicated module (e.g., `models/models.py`) that imports all managed models. This keeps Django's model discovery clean without polluting `__init__.py`.

#### Migration Files

```
pos-solo/sidecar/models/
├── apps.py                    # PosSoloConfig (label=pos_unified)
├── models.py                  # models_module — imports all ~16 models
├── pos.py, menu.py, node.py, config.py, sync.py  # Model definitions
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py        # pos_unified: 16 models
└── posapp_app/
    ├── apps.py                # PosappConfig (label=posapp)
    ├── models.py              # models_module — imports ~30 posapp models
    └── migrations/
        ├── __init__.py
        └── 0001_initial.py    # posapp: ~30 models (~560 lines)

pos-full/sidecar/models/
├── apps.py                    # PosFullConfig (label=pos_full)
├── models.py                  # models_module — imports all ~16 models
├── pos.py, menu.py, node.py, config.py, sync.py  # Model definitions
├── core.py, sales.py, people.py, inventory.py, ops.py, crm.py  # Rust-backed
└── migrations/
    ├── __init__.py
    └── 0001_initial.py        # pos_full: 16 models
```

#### Startup Flow with --migrate

```
python server.py --migrate
  │
  ├── 1. Django bootstrap: settings.configure(), django.setup()
  ├── 2. AppConfig discovery via INSTALLED_APPS
  ├── 3. Models imported via models_module on each AppConfig
  ├── 4. init_state() — passes models to routes/state.py
  ├── 5. Robyn app + middleware + CRUD registration
  ├── 6. main() → _ensure_tables(use_migrations=True)
  │     ├── call_command("migrate") for all registered apps
  │     │   ├── django.contrib.contenttypes  (system)
  │     │   ├── pos_unified / pos_full       (registry models)
  │     │   └── posapp                       (Solo only, ~30 models)
  │     └── All tables created in restaurant.db
  └── 7. app.start(host, port) — server ready
```

### Why Robyn + Django ORM (Not Full Django)

| Approach | Pros | Cons |
|----------|------|------|
| **Robyn + Django ORM** | Async, high-performance, WebSocket native, lightweight | Must bootstrap Django manually |
| **Robyn only** | Max performance, full control | No ORM, must build SQL layer from scratch |

---

## 4. API Organization

All APIs are organized under the Robyn server with a consistent URL structure:

```
/{version}/{entity}              # List/Create
/{version}/{entity}/:id          # Read/Update/Delete
/{version}/{entity}/:id/:action  # Custom actions
```

Currently at version 1 (no prefix), future: `/v1/prefix`.

### API Categories

| Category | Prefix | Server | Description |
|----------|--------|--------|-------------|
| **Info** | `/`, `/health`, `/stats` | Both | Service info, health checks, statistics |
| **POS Core** | `/products`, `/categories`, `/customers`, etc. | Both (Solo: unified, Full: posapp) | Generic CRUD via `_register_crud()` |
| **Sales** | `/sales`, `/sales/with-items`, `/sale-items` | Both | Sales + line items |
| **Inventory** | `/inventory`, `/ingredients`, `/suppliers`, `/purchase-orders` | Both | Inventory management |
| **Employees** | `/employees` | Both | Employee management |
| **Menus** | `/menu-items`, `/menus`, `/menu-assignments` | Solo only | Menu management |
| **Kitchen** | `/kitchen-tickets`, `/support-tickets` | Full only | Kitchen display, support |
| **Nodes** | `/nodes`, `/nodes/register`, `/nodes/heartbeat` | Both | Node registration & lifecycle |
| **Config** | `/config/devices`, `/config/master`, `/config/cloud-links` | Both | Device/Master/Cloud config |
| **Events** | `/events` | Both | Node event audit trail |
| **Sync** | `/sync/status`, `/sync/trigger`, `/sync/log`, `/sync/config` | Both | Data sync to cloud |
| **Approvals** | `/approvals`, `/approvals/:pk/approve\|reject` | Both | Approval workflow |
| **Product Sync** | `/sync/push/*`, `/sync/receive/*` | Both | Master↔Child data exchange |
| **Auth** | `/auth/token`, `/auth/refresh`, `/auth/verify`, `/auth/status` | Both | Token-based auth |
| **Webhooks** | `/webhooks/receive/*` | Full only | Signal webhook receiver |
| **Cloud** | `/cloud/push/:type`, `/api/sync/push/:type` | Both | Cloud push/receive |

### Full Endpoint List (Full edition)

```
GET/POST    /products, /categories, /customers, /sales, /sale-items,
            /employees, /ingredients, /inventory, /suppliers,
            /purchase-orders, /kitchen-tickets, /support-tickets,
            /heartbeats, /sync-logs, /config/devices, /config/master,
            /config/cloud-links, /approvals
GET/PATCH/DELETE  /{entity}/:id
POST        /sales/with-items
POST        /nodes/register
POST        /nodes/heartbeat
PATCH/DELETE/nodes/:node_id
GET/POST/DELETE /nodes/:node_id/config
POST        /config/cloud-links/:pk/test
POST        /config/master/:pk/sync
POST        /approvals/:pk/approve | /approvals/:pk/reject
POST        /sync/receive/sales | reports | inventory
POST        /sync/push/products | configs | catalog
GET         /sync/status | /sync/log | /sync/trigger
POST        /cloud/push/:type | /api/sync/push/:type
POST        /webhooks/receive/:signal_name
POST        /auth/token | /auth/refresh
GET         /auth/verify | /auth/status
WS          /ws/nodes | /ws/config
```

---

## 5. Model Maps

### 5.1 Solo Edition Models

| Model | File | DB Table | Type | Purpose |
|-------|------|----------|------|---------|
| Category | `models/pos.py` | `unified_categories` | Managed | Product categories |
| Product | `models/pos.py` | `unified_products` | Managed | POS products |
| Customer | `models/pos.py` | `unified_customers` | Managed | Customer data |
| Sale | `models/pos.py` | `unified_sales` | Managed | Sales transactions |
| SaleItem | `models/pos.py` | `unified_sale_items` | Managed | Line items |
| InventoryTransaction | `models/pos.py` | `unified_inventory` | Managed | Stock changes |
| Employee | `models/pos.py` | `unified_employees` | Managed | Staff records |
| MenuItem | `models/menu.py` | `unified_menu_items` | Managed | Menu items |
| Menu | `models/menu.py` | `unified_menus` | Managed | Menu groups |
| MenuItemAssignment | `models/menu.py` | `unified_menu_assignments` | Managed | Menu↔Item mapping |
| Node | `models/node.py` | `unified_nodes` | Managed | Registered POS nodes |
| Heartbeat | `models/node.py` | `unified_heartbeats` | Managed | Heartbeat audit log |
| NodeEvent | `models/node.py` | `unified_node_events` | Managed | Node lifecycle events |
| SyncLog | `models/sync.py` | `unified_sync_logs` | Managed | Sync audit trail |
| DeviceConfig | `models/config.py` | `unified_device_configs` | Managed | Per-node config |
| MasterDevice | `models/config.py` | `unified_master_devices` | Managed | Master devices |
| CloudLink | `models/config.py` | `unified_cloud_links` | Managed | Cloud connections |
| SyncApproval | shared | `pos_sync_approvals` | Managed | Approval queue |
| DeviceToken | shared | `pos_device_tokens` | Managed | Auth tokens |
| SignalEvent | shared | `pos_signal_events` | Managed | Signal audit trail |

### 5.2 Full Edition Models

| Model | File | DB Table | Type | Purpose |
|-------|------|----------|------|---------|
| Product | `posapp/models.py` | `posapp_products` | Rust-backed (managed=False) | POS products |
| Category | `posapp/models.py` | `posapp_categories` | Rust-backed | Product categories |
| Customer | `posapp/models.py` | `posapp_customers` | Rust-backed | Customer data |
| Sale | `posapp/models.py` | `posapp_sales` | Rust-backed | Sales transactions |
| SaleItem | `posapp/models.py` | `posapp_sale_items` | Rust-backed | Line items |
| Employee | `posapp/models.py` | `posapp_employees` | Rust-backed | Staff records |
| +25 more | `posapp/models.py` | `posapp_*` | Rust-backed | Inventory, recipes, etc. |
| Node | `models/node.py` | `full_nodes` | Managed | Registered POS nodes |
| Heartbeat | `models/node.py` | `full_heartbeats` | Managed | Heartbeat audit log |
| NodeEvent | `models/node.py` | `full_node_events` | Managed | Node lifecycle events |
| SyncLog | `models/sync.py` | `full_sync_logs` | Managed | Sync audit trail |
| DeviceConfig | `models/config.py` | `full_device_configs` | Managed | Per-node config |
| MasterDevice | `models/config.py` | `full_master_devices` | Managed | Master devices |
| CloudLink | `models/config.py` | `full_cloud_links` | Managed | Cloud connections |
| SyncApproval | shared | `pos_sync_approvals` | Managed | Approval queue |
| DeviceToken | shared | `pos_device_tokens` | Managed | Auth tokens |
| SignalEvent | shared | `pos_signal_events` | Managed | Signal audit trail |

---

## 6. Data Flow & Streaming

### 6.1 HTTP REST Flow

```
Client                          Robyn Server                    Django ORM
  │                                 │                              │
  ├── HTTP Request ───────────────►│                              │
  │                                 │── sync_to_async ────────────►│
  │                                 │                              │── query
  │                                 │◄── queryset results ────────┤
  │                                 │── serialize ────────────────►│
  │◄── JSON Response ──────────────┤                              │
```

All database operations use `@sync_to_async` to bridge Django's synchronous ORM with Robyn's async event loop.

### 6.2 WebSocket Streaming

```
Client                          Robyn Server
  │                                 │
  ├── WS Connect (/ws/nodes) ──────►│  _ws_clients.add(ws)
  │                                 │  _ws_filters[id] = {}
  │                                 │
  │◄── { type: "connected", ... } ──┤
  │                                 │
  ├── { filter: { node_id: "X" } }─►│  _ws_filters[id] = filter
  │◄── { type: "filter_updated" } ──┤
  │                                 │
  │      ... event occurs ...       │
  │                                 │── _broadcast_node_event()
  │◄── { type: "node_event", ... } ─┤
  │                                 │
  ├── Disconnect ──────────────────►│  _ws_clients.discard(ws)
```

### 6.3 Sync Data Flow

```
POS Solo (port 8765)               POS Full (port 8766)              Cloud CRM
      │                                   │                              │
      │  push node data                   │                              │
      ├── POST /api/sync/push/nodes ─────►│                              │
      │                                   │  record in SyncLog          │
      │                                   │  broadcast to /ws/nodes     │
      │                                   │                              │
      │                                   │  push to upstream CRM        │
      │                                   ├── POST /api/crm/* ─────────►│
      │                                   │                              │
      │                                   │  pull/push products          │
      │◄── POST /sync/push/products ─────┤                              │
      │                                   │                              │
      │  health check                     │                              │
      ├── GET /health ──────────────────►│                              │
```

### 6.4 Local Device Usage

For local POS devices (cash registers, tablets):

```
┌────────────────────────────────────────────┐
│  Local POS Device (e.g., iPad at counter)    │
│                                              │
│  ┌──────────┐  ┌─────────────┐              │
│  │  Browser  │  │  Tauri App  │              │
│  └────┬─────┘  └──────┬──────┘              │
│       │               │                      │
│       │ HTTP API      │ Tauri IPC            │
│       ▼               ▼                      │
│  ┌──────────────────────────────────────┐   │
│  │  Sidecar (Robyn, port 8765/8766)     │   │
│  │  Django ORM → SQLite                 │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  Network: localhost only (no external)       │
│  Offline: fully functional                   │
└──────────────────────────────────────────────┘
```

---

## 7. Sync & Approval Pipeline

### 7.1 Approval Workflow

```
Child Node                          Master Server
     │                                     │
     ├── POST /sync/receive/sales ────────►│
     │   { sales: [...], node_id }         │── SyncApproval.create()
     │                                     │   status: pending
     │◄── 201 { approval_id, status } ─────┤
     │                                     │
     │                            Manager reviews
     │                                     │
     │◄── POST /approvals/:pk/approve ─────┤── approve()
     │◄── OR /approvals/:pk/reject ────────┤── reject()
     │                                     │
     │                                     │── mark_applied()
     │                                     │── fire_config_changed()
     │                                     │── broadcast WS event
```

### 7.2 Product Sync Engine

```
Master Node                         Target Node(s)
     │                                     │
     │── push_products_to_node() ─────────►│
     │   { products: [...], target_node }  │── DeviceConfig.update_or_create()
     │   (approval: optional)              │   for each product config
     │                                     │
     │── push_config_to_node() ───────────►│
     │   { configs: {...}, target_node }   │── DeviceConfig.update_or_create()
     │                                     │   for each config key
     │                                     │
     │── push_catalog_to_node() ──────────►│
     │   { products, categories, settings }│── Bulk upsert
     │                                     │
     │   receive_sales_from_node() ◄───────┤
     │   receive_reports_from_node() ◄─────┤
     │   receive_inventory_changes() ◄─────┤
```

---

## 8. Shared Module Map

**Directory:** `projects/pos/shared/`

```
shared/
├── __init__.py                     # Module docstring
├── __about__.py                    # Shared version metadata (__version__, __title_*__)
├── signals/
│   └── __init__.py                 # Signal definitions + fire_* helpers
│       fire_config_changed()
│       fire_config_synced()
│       fire_master_device_changed()
│       fire_cloud_link_changed()
│       fire_device_status_changed()
├── models/
│   ├── __init__.py                 # Re-exports
│   ├── audit.py                    # SignalEvent (audit trail)
│   ├── approval.py                 # SyncApproval (approve/reject/mark_applied)
│   └── token.py                    # DeviceToken (issue/validate/refresh)
├── handlers/
│   ├── __init__.py
│   └── signal.py                   # @receiver — log, webhook, audit
├── services/
│   ├── __init__.py
│   └── sync.py                     # ProductSyncEngine class
├── middleware/
│   ├── __init__.py
│   └── auth.py                     # create_auth_middleware, register_auth_routes
└── api/
    ├── __init__.py
    └── crud.py                     # Legacy helpers (routes use routes/state.py now)
```

### Backward Compatibility

Old import paths are preserved as re-export shims:

| Old Path | New Path |
|----------|----------|
| `shared.signals` | `shared.signals.__init__` |
| `shared.signal_models` | `shared.models.audit` |
| `shared.approval_models` | `shared.models.approval` |
| `shared.models.token` | `shared.models.token` |
| `shared.signal_handlers` | `shared.handlers.signal` |
| `shared.product_sync` | `shared.services.sync` |
| `shared.server_base` | `shared.api.crud` (legacy) or `routes.state` (preferred for route modules) |
| `shared.auth` | `shared.middleware.auth` |

---

## 9. Rust Integration Points

### 9.1 Current Architecture

The Rust backend (Tauri) manages its own SQLite tables via Diesel for local CRUD operations. The sidecar provides additional API endpoints for cloud sync, node management, and approval workflows.

```
┌────────────────────────────────────────────────────────┐
│               Rust Backend (Diesel)                     │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  operations/                                    │  │
│  │  ├── products.rs    → products table            │  │
│  │  ├── sales.rs       → sales table               │  │
│  │  ├── customers.rs   → customers table           │  │
│  │  ├── categories.rs  → categories table          │  │
│  │  ├── inventory.rs   → inventory table           │  │
│  │  ├── employees.rs   → employees table           │  │
│  │  ├── auth.rs        → users table               │  │
│  │  ├── sidecar.rs     → sidecar process lifecycle │  │
│  │  └── ...                                         │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  Database: posapp.db (Diesel SQLite, separate)          │
│  Tables: managed by Rust (same schema as posapp)        │
└─────────────────────────────────────────────────────────┘
```

### 9.2 What to Add to Rust Code for Sidecar Linking

To link the Rust backend with the sidecar, add these modules to `src-tauri/src/operations/`:

| Module | Purpose | Added To |
|--------|---------|----------|
| `sidecar.rs` | Start/stop/status of Robyn sidecar process | ✅ Already exists |
| `sync.rs` | Push local data to sidecar `/api/sync/push/*` | ⬜ **Not yet** |
| `tokens.rs` | Request device tokens from sidecar `/auth/token` | ⬜ **Not yet** |
| `config.rs` | Pull device config from sidecar `/nodes/:id/config` | ⬜ **Not yet** |
| `approvals.rs` | Check approval queue status `/approvals/pending` | ⬜ **Not yet** |

### 9.3 Sync Module (Proposed)

```rust
// src-tauri/src/operations/sync.rs
// 🟢 Customizable — add new sync entity types

use tauri::State;
use crate::db::DbPool;

#[tauri::command]
pub async fn push_products_to_sidecar(
    pool: State<'_, DbPool>,
    sidecar_url: String,
) -> Result<SyncResult, String> {
    let conn = pool.get().map_err(|e| e.to_string())?;
    let products: Vec<Product> = products::table.load(&conn).map_err(|e| e.to_string())?;

    let client = reqwest::Client::new();
    let resp = client
        .post(format!("{}/api/sync/push/products", sidecar_url))
        .json(&serde_json::json!({ "products": products }))
        .send()
        .await
        .map_err(|e| format!("Sidecar push failed: {}", e))?;

    Ok(resp.json().await.unwrap_or_default())
}

#[tauri::command]
pub async fn sync_sales_after_offline(
    pool: State<'_, DbPool>,
    sidecar_url: String,
) -> Result<SyncResult, String> {
    // Fetch unsynced sales from local DB
    // Push to sidecar /sync/receive/sales
    // Update local sync status
    todo!()
}
```

### 9.4 Token Module (Proposed)

```rust
// src-tauri/src/operations/tokens.rs
// 🟢 Customizable

#[tauri::command]
pub async fn get_device_token(
    sidecar_url: String,
    device_id: String,
    role: String,
) -> Result<String, String> {
    let client = reqwest::Client::new();
    let resp = client
        .post(format!("{}/auth/token", sidecar_url))
        .json(&serde_json::json!({
            "device_id": device_id,
            "role": role
        }))
        .send()
        .await
        .map_err(|e| format!("Token request failed: {}", e))?;

    let body: serde_json::Value = resp.json().await.map_err(|e| e.to_string())?;
    Ok(body["token"].as_str().unwrap_or("").to_string())
}
```

---

## 10. Frontend API Integration (Redux RTK Query)

> **Note:** Both pos-solo and pos-full use **Redux Toolkit (RTK Query)** for API state management, not Pinia. The Pinia examples below are preserved for reference if migrating from a Vue.js frontend.

### 10.1 Redux Store Structure

Both editions use Redux Toolkit with RTK Query for API caching:

```
src/store/
├── api/
│   ├── baseApi.ts        # createApi with tag types for cache invalidation
│   └── endpoints/        # Entity endpoint slices (products, sales, customers)
└── middleware/
    └── websocket.ts      # WS entity cache invalidation (full) / config (solo)
```

### 10.2 Legacy Pinia Stores (Vue.js Reference)

For a Vue.js frontend, create Pinia stores that wrap the Robyn sidecar API:

```
src/stores/
├── index.ts              # Barrel exports
├── sidecar.ts            # Base API client (fetch + auth)
├── products.ts           # Product CRUD store
├── sales.ts              # Sales store
├── nodes.ts              # Node registry store
├── sync.ts               # Sync status store
├── approvals.ts          # Approval workflow store
├── auth.ts               # Auth token store
├── websocket.ts          # WebSocket connection manager
└── config.ts             # Device/Master/Cloud config store
```

### 10.2 Base API Client

```typescript
// src/stores/sidecar.ts
// Base HTTP + WebSocket client for Robyn sidecar API

export interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  ok: boolean;
  status: number;
}

class SidecarClient {
  private baseUrl: string;
  private token: string | null = null;
  private wsConnections: Map<string, WebSocket> = new Map();

  constructor(baseUrl: string = 'http://localhost:8765') {
    this.baseUrl = baseUrl;
  }

  setToken(token: string | null) {
    this.token = token;
    localStorage.setItem('pos_device_token', token || '');
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (this.token) h['Authorization'] = `Bearer ${this.token}`;
    return h;
  }

  async get<T>(path: string): Promise<ApiResponse<T>> { /* ... */ }
  async post<T>(path: string, body: unknown): Promise<ApiResponse<T>> { /* ... */ }
  async patch<T>(path: string, body: unknown): Promise<ApiResponse<T>> { /* ... */ }
  async delete(path: string): Promise<ApiResponse<void>> { /* ... */ }

  async healthCheck(): Promise<boolean> { /* ... */ }
  async getToken(deviceId: string, role: string): Promise<string> { /* ... */ }

  connectWebSocket(
    path: string,
    onMessage: (data: unknown) => void,
    onStateChange?: (state: string) => void,
  ): WebSocket { /* ... */ }
}

export const sidecar = new SidecarClient();
```

### 10.3 Pinia Store Examples

```typescript
// src/stores/nodes.ts
import { defineStore } from 'pinia';
import { sidecar } from './sidecar';

interface Node {
  node_id: string;
  status: string;
  hostname: string;
  version: string;
  last_seen: string;
  product_count: number;
}

export const useNodeStore = defineStore('nodes', {
  state: () => ({
    nodes: [] as Node[],
    loading: false,
    error: null as string | null,
    wsConnected: false,
  }),

  getters: {
    onlineNodes: (state) => state.nodes.filter(n => n.status === 'online'),
    offlineNodes: (state) => state.nodes.filter(n => n.status === 'offline'),
    nodeCount: (state) => state.nodes.length,
  },

  actions: {
    async fetchNodes() {
      this.loading = true;
      const { data, error } = await sidecar.get<Node[]>('/nodes');
      if (data) this.nodes = data;
      if (error) this.error = error;
      this.loading = false;
    },

    connectNodeStream() {
      const ws = sidecar.connectWebSocket('/ws/nodes', (msg: any) => {
        if (msg.type === 'node_event') {
          // Update node in state or add new
          const idx = this.nodes.findIndex(n => n.node_id === msg.node_id);
          if (idx >= 0) {
            this.nodes[idx] = { ...this.nodes[idx], ...msg.data };
          } else if (msg.event === 'registered') {
            this.nodes.push(msg.data);
          }
        }
      });
      this.wsConnected = true;
      return ws;
    },

    async registerNode(nodeData: Partial<Node>) {
      return sidecar.post<Node>('/nodes/register', nodeData);
    },

    async sendHeartbeat(nodeId: string) {
      return sidecar.post('/nodes/heartbeat', { node_id: nodeId });
    },
  },
});
```

```typescript
// src/stores/sync.ts
import { defineStore } from 'pinia';

export const useSyncStore = defineStore('sync', {
  state: () => ({
    status: 'idle' as string,
    cloudUrl: '',
    lastSync: null as string | null,
    itemsSynced: 0,
    errors: 0,
    log: [] as SyncLogEntry[],
    wsConnected: false,
  }),

  actions: {
    async fetchStatus() { /* GET /sync/status */ },
    async triggerSync() { /* POST /sync/trigger */ },
    async updateConfig(config: Partial<SyncConfig>) { /* PATCH /sync/config */ },
    connectConfigStream() { /* WS /ws/config */ },
  },
});
```

```typescript
// src/stores/approvals.ts
import { defineStore } from 'pinia';

export const useApprovalStore = defineStore('approvals', {
  state: () => ({
    pending: [] as Approval[],
    stats: { pending: 0, approved: 0, rejected: 0 },
  }),

  actions: {
    async fetchPending() { /* GET /approvals/pending */ },
    async fetchStats() { /* GET /approvals/stats */ },
    async approve(id: number, reviewer: string) { /* POST /approvals/:id/approve */ },
    async reject(id: number, reviewer: string, notes: string) { /* POST /approvals/:id/reject */ },
  },
});
```

### 10.4 React Hooks Wrapper

```typescript
// src/hooks/useSidecarStore.ts
import { useNodeStore } from '../stores/nodes';
import { useSyncStore } from '../stores/sync';
import { useApprovalStore } from '../stores/approvals';

export function useSidecarStores() {
  const nodes = useNodeStore();
  const sync = useSyncStore();
  const approvals = useApprovalStore();

  return {
    nodes,
    sync,
    approvals,
    initialize: async () => {
      await Promise.all([
        nodes.fetchNodes(),
        sync.fetchStatus(),
        approvals.fetchPending(),
        approvals.fetchStats(),
      ]);
      nodes.connectNodeStream();
      sync.connectConfigStream();
    },
  };
}
```

### 10.5 WebSocket Manager

```typescript
// src/stores/websocket.ts
type WsHandler = (data: any) => void;

class WebSocketManager {
  private connections: Map<string, { ws: WebSocket; handlers: Set<WsHandler> }> = new Map();
  private reconnectTimers: Map<string, ReturnType<typeof setTimeout>> = new Map();
  private maxRetries = 5;

  connect(url: string, handler: WsHandler): void {
    // Get or create connection
    if (!this.connections.has(url)) {
      this.createConnection(url);
    }
    this.connections.get(url)!.handlers.add(handler);
  }

  private createConnection(url: string, retryCount = 0): void {
    const ws = new WebSocket(url);
    const entry = { ws, handlers: new Set<WsHandler>() };
    this.connections.set(url, entry);

    ws.onopen = () => {
      console.log(`WS connected: ${url}`);
      retryCount = 0;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        entry.handlers.forEach(h => h(data));
      } catch { /* ignore parse errors */ }
    };

    ws.onclose = () => {
      if (retryCount < this.maxRetries) {
        this.reconnectTimers.set(url, setTimeout(() => {
          this.createConnection(url, retryCount + 1);
        }, Math.min(1000 * Math.pow(2, retryCount), 30000)));
      }
    };
  }

  disconnect(url: string, handler: WsHandler): void {
    const entry = this.connections.get(url);
    if (!entry) return;
    entry.handlers.delete(handler);
    if (entry.handlers.size === 0) {
      entry.ws.close();
      this.connections.delete(url);
      clearTimeout(this.reconnectTimers.get(url));
      this.reconnectTimers.delete(url);
    }
  }
}

export const wsManager = new WebSocketManager();
```

---

## 11. Cloud Server Plan (Next Phase)

### 11.1 Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      Cloud Server (port 8767)                     │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Token Auth Gateway                                        │  │
│  │  • Bearer token validation (SHA-256)                       │  │
│  │  • Role-based access (admin, manager, cashier, viewer)     │  │
│  │  • Device identity + branch type routing                   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐    │
│  │ Branch Router │ │ Sync Broker  │ │ Approval Manager    │    │
│  │ • Route by    │ │ • Bidirect-  │ │ • Cross-branch      │    │
│  │   device_id   │ │   tional     │ │   approval queue    │    │
│  │ • Multi-      │ │   streaming  │ │ • Moderator         │    │
│  │   tenant      │ │   to all     │ │   dashboard         │    │
│  │ • Load bal    │ │   branches   │ │ • Email/push        │    │
│  └──────┬───────┘ └──────┬───────┘ └──────────────────────┘    │
│         │                │                                      │
└─────────┼────────────────┼──────────────────────────────────────┘
          │                │
    ┌─────┴──────┐  ┌─────┴──────┐  ┌─────┴──────┐
    │ POS Solo   │  │ POS Full   │  │ POS Minimal│
    │ (8765)     │  │ (8766)     │  │ (no side-  │
    │ Sync client│  │ Cloud mas- │  │  car →     │
    │ → push     │  │ ter → push │  │ node API)  │
    └────────────┘  └────────────┘  └────────────┘
```

### 11.2 API Types

| API Type | Method | Description | Stream Type |
|----------|--------|-------------|-------------|
| **REST CRUD** | GET/POST/PATCH/DELETE | Standard CRUD operations | Request/Response |
| **REST Action** | POST /{entity}/:id/{action} | Custom actions (approve, reject, sync, test) | Request/Response |
| **WebSocket Event** | WS /ws/{stream} | Real-time events (node, config, sync) | Server→Client push |
| **WebSocket Command** | WS /ws/{stream} | Client filters | Client→Server |
| **Signal Webhook** | POST /webhooks/receive/{signal} | Django signal → HTTP callback | Server→Server |
| **Sync Push** | POST /sync/push/{type} | Data sync between nodes | Server→Server |
| **Health** | GET /health | Service health check | Request/Response |

### 11.3 Streaming Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Streaming Pipeline                        │
│                                                                │
│  Source Event → Signal → Webhook/WS → Target(s)              │
│                                                                │
│  ┌─────────┐    ┌──────────┐    ┌────────────┐               │
│  │ Config   │───►│ fire_    │───►│ Webhook    │──► Cloud CRM │
│  │ Changed  │    │ config_  │    │ HTTP POST  │               │
│  └─────────┘    │ changed  │    └────────────┘               │
│                 └──────────┘                                 │
│  ┌─────────┐    ┌──────────┐    ┌────────────┐               │
│  │ Node     │───►│ fire_    │───►│ /ws/nodes  │──► Dashboard │
│  │ Heartbeat│    │ device_  │    │ WebSocket  │               │
│  └─────────┘    │ status_  │    └────────────┘               │
│                 │ changed  │                                  │
│                 └──────────┘    ┌────────────┐               │
│  ┌─────────┐    ┌──────────┐   │ /ws/config  │──► Config UI │
│  │ Approval │───►│ fire_    │──►│ WebSocket   │               │
│  │ Action   │    │ config_  │   └────────────┘               │
│  └─────────┘    │ changed  │                                  │
│                 └──────────┘                                  │
└──────────────────────────────────────────────────────────────┘
```

### 11.4 Cloud Server Endpoints (Proposed)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register device, get token |
| POST | `/auth/refresh` | Refresh token |
| GET | `/branches` | List all connected branches |
| GET | `/branches/:id/status` | Branch health + stats |
| POST | `/sync/broker/connect` | Establish WS bridge |
| WS | `/ws/broker` | Cross-branch sync stream |
| GET | `/approvals/cross-branch` | Cross-branch approval queue |
| POST | `/approvals/:id/forward` | Forward approval to another branch |
| GET | `/analytics/global` | Cross-branch analytics |
| GET | `/monitor/health` | Cluster health dashboard |

### 11.5 Local Device Integration

```
Local POS Device (offline-capable):
┌─────────────────────────────────────┐
│  Tauri App                           │
│  ┌────────────┐ ┌─────────────────┐ │
│  │ Rust Local │ │ Pinia Store     │ │
│  │ DB (Diesel)│ │ (WebSocket      │ │
│  │ CRUD       │ │  connection)    │ │
│  └─────┬──────┘ └────────┬────────┘ │
│        │                 │          │
│        │                 │          │
│  ┌─────▼─────────────────▼────────┐ │
│  │  Sidecar (Robyn, port 8765)    │ │
│  │  • REST API for all entities   │ │
│  │  • WebSocket /ws/config        │ │
│  │  • Sync client → Cloud Server  │ │
│  │  • Offline: all features work  │ │
│  │  • Online: sync to cloud       │ │
│  └────────────────────────────────┘ │
│                                      │
│  Network: localhost (offline)        │
│  Network: internet (online → cloud)  │
└──────────────────────────────────────┘
```

---

## 12. Unfold Admin Dashboard (pos-full)

pos-full includes a **Django Unfold** admin dashboard — a modern, dark-themed admin panel with real-time KPIs, charts, and CRUD management for all 17+ managed models.

### Dashboard Features

| Component | Count | Details |
|-----------|:-----:|---------|
| KPI Cards | 9 | Today's Sales, Monthly Revenue, Avg Order Value, MTD Revenue, YTD Revenue, Active Products, Customers, Branch Nodes, Open Alerts |
| Charts | 5 | Revenue 7-day bar, Top Products pie, Payment doughnut, Hourly Revenue bar, Hourly Transactions bar |
| Tables | 2 | Recent Sales (5 rows), Node Status (5 rows) |
| Registered Models | 17+ | Product, Category, Customer, Sale, SaleItem, Employee, Inventory, Menu, Node, Config, Sync, etc. |

### Access (current — merged package)

```bash
cd formint-pos/sidecar
python3 manage.py migrate
python3 manage.py --ensure-superuser   # Auto-create admin from env vars
python3 manage.py runserver 0.0.0.0:8767
# → http://localhost:8767/admin/
```

Or use the one-command bootstrap:

```bash
cd formint-pos && make seed && make env
```

### Screenshots

| Dashboard | Products |
|:---:|:---:|
| ![Dashboard](screenshots/admin/03_admin_dashboard.jpg) | ![Products](screenshots/admin/04_admin_products.jpg) |

Admin panel ships with the merged **Formint POS** package (pos-mini has no admin interface).
Screenshots live in `docs/screenshots/` (see `FORMINT_ARCHITECTURE.md` §3.6 for the full set).

---

## 13. Roadmap & Next Steps

### ✅ Phase 1: Foundation (Complete)
- [x] Robyn + Django ORM server for both editions
- [x] Node registry models (Node, Heartbeat, NodeEvent, SyncLog)
- [x] Generic CRUD router factory (`_register_crud`)
- [x] Configuration models (DeviceConfig, MasterDevice, CloudLink)
- [x] WebSocket config stream (/ws/config)
- [x] WebSocket node stream (/ws/nodes, Full only)
- [x] Shared module map with backward-compat shims
- [x] Django migration infrastructure (AppConfig, models.py, migrations/, manage.py, --migrate)
- [x] PosappConfig for Solo posapp models (models/posapp_app/ with ~30 managed=True, migrations)
- [x] Shared version metadata (`shared/__about__.py` — single source for version strings)

### ✅ Phase 2: Sync & Moderation (Complete)
- [x] SyncApproval model with approve/reject workflow
- [x] ProductSyncEngine (Master→Child, Child→Master)
- [x] Approval API endpoints
- [x] Product sync API endpoints
- [x] Django signals + wiring into all endpoints
- [x] 🔄 Pending: Signal receivers for logging/notifications

### ✅ Phase 3: Cloud Bridge (Complete)
- [x] DeviceToken model (SHA-256 hashing, roles, expiry)
- [x] Auth middleware (Bearer token + API key fallback)
- [x] Auth endpoints (/auth/token, /auth/refresh, /auth/verify)
- [x] Role hierarchy (viewer < cashier < manager < admin)
- [x] 🔄 Pending: Unified cloud server cluster

### 🎯 Phase 4: Enterprise (Planned)
- [ ] **Cloud Server** — Standalone Robyn server (port 8767) for multi-branch management
- [ ] **Branch Router** — Route requests by device token to correct branch
- [ ] **Sync Broker** — Bidirectional WebSocket stream between all branches
- [ ] **Cross-Branch Approvals** — Approve/reject across branches
- [ ] **Multi-Tenant Support** — Isolate data per organization
- [ ] **RBAC** — Full role-based access control with permissions matrix
- [ ] **Audit Log** — Signal-driven persistence with search/filter UI
- [ ] **Webhook Notifications** — Configurable webhooks for all signal types
- [ ] **Email/Push Notifications** — Pending approval alerts
- [ ] **Monitoring Dashboard** — Cluster health, branch status, sync analytics
- [ ] **Export/Import** — Bulk device configuration
- [ ] **Failover** — Automated cloud link failover

### 🔧 Recommended: Rust Integration (Next)
- [ ] Add `sync.rs` to Rust operations — push local data to sidecar
- [ ] Add `tokens.rs` — request device tokens from sidecar
- [ ] Add `config.rs` — pull device config from sidecar
- [ ] Add `approvals.rs` — check approval queue from sidecar
- [ ] Create Pinia stores for all sidecar API categories
- [ ] Add WebSocket manager for auto-reconnecting streams
