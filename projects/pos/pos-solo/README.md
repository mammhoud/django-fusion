# POS Solo — Branch Device

> Desktop POS + Robyn sidecar API server with cloud CRM sync to pos-full master.

**pos-solo** is the **branch device** edition of POS. It provides a standalone POS terminal with a local REST API, WebSocket real-time events, and cloud sync to the pos-full master manager.

- 🌐 **REST API** — Robyn async sidecar on port `8765` with 60+ CRUD endpoints
- 🔌 **WebSocket config streaming** — real-time configuration push/pull with Redux cache invalidation
- ☁️ **Cloud CRM sync** — push products, sales, customers, and nodes to pos-full master
- 🏗️ **Django ORM** — 17 unified managed models (no Rust DB dependency)
- 🎨 **React + Tailwind** — modern POS terminal UI with Redux RTK Query
- ✅ **155 passing tests** — full CRUD, filtering, pagination, and validation coverage

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
cd sidecar && pip install -r requirements.txt && cd ..
pnpm install
# (Optional for Tauri desktop builds only)
# cd src-tauri && cargo fetch && cd ..

# 2. Start the REST API server (Robyn sidecar)
python3 sidecar/server.py --port 8765

# 3. Start React frontend (in another terminal)
pnpm dev

# 4. (Optional) Start pos-full master for cloud sync
# See ../pos-full/README.md for master setup
```

| Service | URL | Purpose |
|---------|-----|---------|
| **REST API** | `http://localhost:8765` | CRUD endpoints for all entities |
| **Frontend** | `http://localhost:1420` | POS terminal UI (Vite dev) |
| **WebSocket** | `ws://localhost:8765/ws/config` | Real-time config events |
| **Master API** | `http://localhost:8766` | pos-full master (cloud sync target) |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  pos-solo (Branch Device) — port 8765                        │
│                                                              │
│  ┌──────────────────────────────────┐                        │
│  │  React Frontend (Tauri)          │                        │
│  │  ┌────────────────────────────┐  │                        │
│  │  │ Redux Toolkit (RTK Query)  │──│──→ fetch(:8765)        │
│  │  │   ├─ Cache invalidation    │  │                        │
│  │  │   ├─ Pagination            │  │                        │
│  │  │   └─ WS middleware         │←─│─── WS(:8765)           │
│  │  └────────────────────────────┘  │                        │
│  └──────────────────────────────────┘                        │
│                                                              │
│  ┌──────────────────────────────────┐                        │
│  │  Robyn Sidecar :8765             │                        │
│  │  ├─ CRUD endpoints (60+)        │                        │
│  │  ├─ Paginated queries           │                        │
│  │  ├─ WebSocket /ws/config        │                        │
│  │  ├─ Node registration/heartbeat │                        │
│  │  └─ Cloud sync client           │                        │
│  └──────────────────────────────────┘                        │
│                                                              │
│  ┌──────────────────────────────────┐                        │
│  │  Django ORM (SQLite)             │                        │
│  │  ├─ models/pos.py — POS core    │                        │
│  │  ├─ models/menu.py — Menu       │                        │
│  │  ├─ models/node.py — Registry   │                        │
│  │  ├─ models/config.py — Config   │                        │
│  │  └─ models/sync.py — Sync       │                        │
│  └──────────────────────────────────┘                        │
│                                                              │
│       │ HTTP / WS                                            │
│       ▼                                                      │
│  ┌──────────────────────────────────┐                        │
│  │  pos-full Master :8766           │                        │
│  │  (Central management, admin)     │                        │
│  └──────────────────────────────────┘                        │
└──────────────────────────────────────────────────────────────┘
```

---

## 🌐 REST API

The Robyn sidecar serves all CRUD endpoints with **pagination** support.

### Pagination

Every list endpoint supports `?page=` and `?per_page=` query params:

```bash
curl "http://localhost:8765/products?page=1&per_page=20"
```

Response format:
```json
{
  "data": [
    { "id": 1, "name": "Coffee", "price": 4.50, ... }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 532,
    "total_pages": 27
  }
}
```

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET/POST` | `/products` | List (paginated) / Create product |
| `PATCH/DELETE` | `/products/:id` | Update / Delete product |
| `GET/POST` | `/categories` | List / Create category |
| `GET/POST` | `/customers` | List / Create customer |
| `GET/POST` | `/sales` | List / Create sale |
| `GET/POST` | `/sale-items` | List / Create sale item |
| `GET/POST` | `/employees` | List / Create employee |
| `GET/POST` | `/inventory` | List / Create inventory transaction |
| `GET/POST` | `/menu-items` | List / Create menu item |
| `GET/POST` | `/menus` | List / Create menu |
| `GET/POST` | `/suppliers` | List / Create supplier |
| `GET/POST` | `/purchase-orders` | List / Create purchase order |
| `GET/POST` | `/kitchen-tickets` | List / Create kitchen ticket |
| `GET/POST` | `/support-tickets` | List / Create support ticket |
| `GET/POST` | `/nodes/register` | Register as branch device |
| `POST` | `/nodes/heartbeat` | Send heartbeat to master |
| `GET` | `/sync/status` | Cloud sync status |
| `POST` | `/sync/trigger` | Trigger manual sync |

> **Full endpoint list:** ~60+ CRUD routes + 10+ custom routes

---

## 🔌 WebSocket Streams

The sidecar provides one WebSocket endpoint for real-time features:

### `/ws/config` — Configuration Events

Broadcasts whenever configuration is changed, synced, or pushed:

```json
{
  "type": "config_changed",
  "node_id": "NODE-A",
  "config_key": "sync_interval",
  "data": { "value": 60 },
  "timestamp": "2026-07-20T12:00:00+00:00"
}
```

**Used by**: Redux RTK Query middleware to auto-invalidate caches.

---

## ☁️ Cloud Sync

pos-solo can push local data to the pos-full master manager:

```bash
# Configure sync target
curl -X POST http://127.0.0.1:8765/sync/config \
  -H "Content-Type: application/json" \
  -d '{"cloud_url": "http://localhost:8766", "sync_interval": 60}'

# Check sync status
curl http://127.0.0.1:8765/sync/status

# Trigger manual sync
curl -X POST http://127.0.0.1:8765/sync/trigger
```

| Sync Direction | Payload | Endpoint |
|----------------|---------|----------|
| Solo → Master | Products, sales, customers | `POST /sync/push/:type` (type=products, sales, customers) |
| Solo → Master | Nodes, heartbeats | `POST /sync/push/:type` (type=nodes, heartbeats) |
| Master → Solo | Config, approved changes | `GET /sync/pull/:type` (type=config, approvals) |

---

## 📁 Directory Structure

```
pos-solo/
├── src/                          # React + TypeScript + Tailwind
│   ├── store/                    # Redux Toolkit (RTK Query)
│   │   ├── api/
│   │   │   ├── baseApi.ts        # createApi with tag types
│   │   │   └── endpoints/        # Entity endpoint slices
│   │   └── middleware/
│   │       └── websocket.ts      # WS config cache invalidation
│   ├── pages/                    # POS page components
│   ├── components/               # Shared UI components
│   ├── hooks/                    # Custom React hooks
│   ├── i18n/                     # Internationalization
│   └── utils/                    # Utility functions
├── sidecar/
│   ├── server.py                 # Robyn async server entry point
│   ├── routes/                   # Custom route handlers
│   │   ├── info.py               # /, /health, /stats
│   │   ├── nodes.py              # Node registration/heartbeat/WS
│   │   ├── config.py             # Device config/WS
│   │   ├── sync.py               # Cloud sync client
│   │   └── approvals.py          # Sync approval workflow
│   ├── models/                   # Django ORM models
│   │   ├── pos.py                # Category, Product, Customer, Sale...
│   │   ├── menu.py               # MenuItem, Menu
│   │   ├── node.py               # Node, Heartbeat, NodeEvent
│   │   ├── config.py             # DeviceConfig, MasterDevice, CloudLink
│   │   └── sync.py               # SyncLog
│   ├── tests/
│   │   └── test_unified_api.py   # 155 pytest tests
│   ├── streams.py                # WebSocket broadcast functions
│   ├── handlers.py               # CRUD factory with WS broadcast
│   └── ARCHITECTURE.md           # Detailed architecture docs
├── src-tauri/                    # Tauri/Rust shell
└── scripts/                      # Dev/build utilities
```

---

## 📊 Models Package

All models use `app_label=pos_unified` and `db_table` prefix `unified_`:

| Model | Module | Table | Purpose |
|-------|--------|-------|---------|
| `Category` | `models/pos.py` | `unified_categories` | Product categories |
| `Product` | `models/pos.py` | `unified_products` | POS products |
| `Customer` | `models/pos.py` | `unified_customers` | Customer records |
| `Sale` | `models/pos.py` | `unified_sales` | POS transactions |
| `SaleItem` | `models/pos.py` | `unified_sale_items` | Line items |
| `InventoryTransaction` | `models/pos.py` | `unified_inventory` | Stock movements |
| `Employee` | `models/pos.py` | `unified_employees` | Staff records |
| `MenuItem` | `models/menu.py` | `unified_menu_items` | Menu items |
| `Menu` | `models/menu.py` | `unified_menus` | Named menus |
| `MenuItemAssignment` | `models/menu.py` | `unified_menu_assignments` | Through table |
| `Node` | `models/node.py` | `unified_nodes` | Registered nodes |
| `Heartbeat` | `models/node.py` | `unified_heartbeats` | Heartbeat audit |
| `NodeEvent` | `models/node.py` | `unified_node_events` | Lifecycle events |
| `SyncLog` | `models/sync.py` | `unified_sync_logs` | Sync audit trail |
| `DeviceConfig` | `models/config.py` | `unified_device_configs` | Per-node config |
| `MasterDevice` | `models/config.py` | `unified_master_devices` | Master devices |
| `CloudLink` | `models/config.py` | `unified_cloud_links` | Cloud connections |

---

## 🧪 Testing

```bash
cd sidecar
DJANGO_SETTINGS_MODULE='' python3 -m pytest tests/test_unified_api.py -v --tb=short --import-mode=importlib
# → 155 tests pass (CRUD, filtering, pagination, validation)
```

---

## 🛠️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POS_HOST` | `0.0.0.0` | Sidecar bind address |
| `POS_PORT` | `8765` | Sidecar port |
| `POS_API_KEY` | `None` | API authentication key |
| `MASTER_URL` | `http://localhost:8766` | pos-full master URL |
| `MASTER_API_KEY` | `None` | Master API key for auth |
| `CLOUD_CRM_URL` | `""` | Upstream CRM API URL |
| `CLOUD_API_KEY` | `None` | CRM API key |
| `SYNC_INTERVAL` | `60` | Auto-sync interval (seconds) |

### Sidecar Arguments

```bash
python3 server.py --host 0.0.0.0 --port 8765 --verbose
python3 server.py --version          # Show version
```

---

## 📚 Edition Comparison

| Feature | pos-mini | pos-solo | pos-full |
|---------|:--------:|:--------:|:--------:|
| Backend | Rust/Diesel | Robyn + Django | Robyn + Django |
| Admin panel | ❌ | ❌ | ✅ Unfold dashboard |
| Data ops | `invoke()` | Redux RTK Query | Redux RTK Query |
| Paginated API | ❌ | ✅ 60+ endpoints | ✅ 30+ endpoints |
| Entity WS events | ❌ | ✅ `/ws/config` | ✅ `/ws/entities` |
| Node registry | ❌ | ✅ (child) | ✅ (master) |
| Cloud sync | ❌ | ✅ (child→master) | ✅ (master↔children) |
| WebSocket chat | ❌ | ❌ | ✅ |
| Architecture role | Standalone | Branch device | Master manager |

---

## 🔗 Related

- **pos-full**: Master manager with admin dashboard — [../pos-full/](../pos-full/)
- **pos-mini**: Minimal Rust/Diesel edition — [../pos-mini/](../pos-mini/)
- **Sidecar architecture**: [sidecar/ARCHITECTURE.md](sidecar/ARCHITECTURE.md)
- **Architecture overview**: [../../docs/POS_ARCHITECTURE.md](../../docs/POS_ARCHITECTURE.md)
