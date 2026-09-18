# Bolt API Integration Plan — POS Full Edition

> **Version:** 1.0.0 | **Last Updated:** 20 July 2026 | **Status:** ✅ Complete — bolt_api.py removed, all features ported to routes/

---

## 1. Current State: bolt_api.py

### What it is
`bolt_api.py` (1,010 lines) is a standalone **django-bolt** API module that provides a high-performance REST + WebSocket API backed by Rust's Actix Web engine. It delivers near-native Rust speed (~60k+ RPS) via the `django-bolt` library.

### What endpoints it provides

| Category | Endpoints | Models Used |
|----------|-----------|-------------|
| **Info** | `GET /bolt/`, `GET /bolt/health` | — |
| **Products** | `GET /bolt/products`, `GET /bolt/products/{id}` | `posapp.models.Product` |
| **Customers** | `GET /bolt/customers`, `GET /bolt/customers/{id}` | `posapp.models.Customer` |
| **Sales** | `GET /bolt/sales`, `GET /bolt/sales/{id}` | `posapp.models.Sale` |
| **Inventory** | `GET /bolt/inventory` | `posapp.models.InventoryTransaction` |
| **CRM** | `GET /crm/dashboard`, contacts CRUD, companies, deals, pipelines, activities, notes | `cloud.crm_models.*` |
| **Sync** | `GET /bolt/sync/status`, `POST /bolt/sync/trigger` | `cloud.sync_models.*` |
| **Reports** | `GET /bolt/reports/sales`, `GET /bolt/reports/inventory` | `posapp.models.*` |
| **WebSocket** | `WS /ws/chat/{room_id}`, `WS /ws/notifications` | — |
| **Docs** | `/bolt/docs` (OpenAPI, Swagger, Redoc, Scalar) | — |

### How it's wired (current)

```
Django settings.py:
    INSTALLED_APPS = [..., "django_bolt"]

Django urls.py:
    urlpatterns = [
        path("bolt/", include(bolt.urls)),
    ]
    
    bolt_api.py:
    bolt = BoltAPI(prefix="/bolt", namespace="pos-bolt", ...)
```

### Current problem: NOT integrated with Robyn server

- `server.py` (Robyn) does **not** import or reference `bolt_api.py`
- `bolt_api.py` runs only via Django's `manage.py runserver` (no longer available), separate from the Robyn process
- This means two processes are needed: Robyn (port 8766) + Django (port 8082)
- The Robyn server's `routes/` package already implements similar CRUD endpoints — partial duplication

| Feature | Robyn server.py + routes/ | bolt_api.py (Django) |
|---------|--------------------------|----------------------|
| Products CRUD | ✅ Full CRUD | ✅ Read-only |
| Customers CRUD | ✅ Full CRUD | ✅ Read-only |
| Sales CRUD | ✅ Full CRUD | ✅ Read-only |
| Inventory CRUD | ✅ Full CRUD | ✅ Read-only |
| CRM (contacts, companies, deals) | ❌ Not yet | ✅ Full CRUD |
| Reports (sales, inventory) | ❌ Not yet | ✅ Read-only |
| Sync status/trigger | ✅ via routes/sync.py | ✅ via bolt |
| WebSocket | ✅ /ws/nodes, /ws/config | ✅ /ws/chat, /ws/notifications |
| OpenAPI docs | ❌ | ✅ Swagger/Redoc/Scalar |
| Performance | Good (Robyn async) | Excellent (Rust Actix) |

---

## 2. Integration Plan: Merge bolt into Robyn Server

### Goal
Run a **single process** (Robyn, port 8766) that provides all endpoints — both the current routes/ package and the bolt-specific features (CRM, Reports, Docs).

### Option A: Port bolt endpoints into routes/ (Recommended)

Move bolt_api's unique features into new or existing routes/ modules:

```
New/updated routes/ modules:
├── routes/
│   ├── info.py          # ✅ Already has /, /health
│   ├── nodes.py         # ✅ Already has node CRUD + WS /ws/nodes
│   ├── config.py        # ✅ Already has config CRUD + WS /ws/config
│   ├── sync.py          # ✅ Already has sync CRUD
│   ├── approvals.py     # ✅ Already has approval workflow
│   ├── webhooks.py      # ✅ Already has webhook receiver
│   ├── crm.py           # 🆕 CRM: contacts, companies, deals, pipelines, activities, notes
│   ├── reports.py       # 🆕 Reports: sales report, inventory low-stock report
│   └── docs.py          # 🆕 OpenAPI docs generation endpoint
```

**Pros:** Single process, consistent architecture, no django-bolt dependency, routes/ module pattern already established
**Cons:** Loses Rust-level performance boost, need to reimplement ~500 lines of CRM endpoints

### Option B: Mount bolt_api inside Robyn server

Run the bolt API as a sub-app within the Robyn server process. Robyn can mount external WSGI/ASGI apps.

**Pros:** Keeps bolt's Rust performance, no rewrite, maintains OpenAPI docs
**Cons:** Complex integration, django-bolt may require Django middleware stack, still need separate Django process or hybrid approach

### Option C: Django as primary, Robyn as bolt replacement

Reverse the architecture: make Django the main server and use django-bolt for high-performance endpoints. The routes/ package modules become bolt modules.

**Pros:** Django admin UI available, django-bolt production-ready, full ecosystem
**Cons:** Loses Robyn's async WebSocket, bigger architectural change

### Recommendation: Option A (Port into routes/)

The routes/ package pattern is already proven. Adding `routes/crm.py` and `routes/reports.py` is straightforward. The CRM endpoints bolt_api implements are mostly read-only list/get with one create each — easy to port.

**Estimated effort:** ~2 hours to create crm.py + reports.py, ~1 hour for OpenAPI docs generation.

---

## 3. Node ↔ Server Data Flow (Solo ↔ Full)

```
POS Solo (Node, port 8765)                    POS Full (Server, port 8766)
══════════════════════════                    ══════════════════════════════

┌─────────────────────────┐                   ┌──────────────────────────┐
│  server.py              │                   │  server.py               │
│  routes/                │                   │  routes/                 │
│    info.py              │                   │    info.py               │
│    nodes.py             │                   │    nodes.py              │
│    config.py            │                   │    config.py             │
│    sync.py ←────push────┼──────────────────▶│    sync.py               │
│    approvals.py         │                   │    approvals.py          │
│                         │                   │    webhooks.py           │
│                         │                   │    crm.py (planned)      │
│                         │                   │    reports.py (planned)  │
└─────────────────────────┘                   └──────────────────────────┘
         │                                            │
         │  HTTP REST + WebSocket                     │  HTTP REST + WebSocket
         ▼                                            ▼
    Tauri Desktop App                           Tauri Desktop App
    (local POS)                                 (manager dashboard)
```

### Data streams between Solo (Node) and Full (Server):

| Direction | Endpoint | Payload | Frequency |
|-----------|----------|---------|-----------|
| Solo → Full | `POST /api/sync/push/nodes` | Node registration data | On register/update |
| Solo → Full | `POST /api/sync/push/heartbeats` | Heartbeat data | Periodic (30-60s) |
| Solo → Full | `POST /sync/receive/sales` | Sales batch with approval | On batch/schedule |
| Solo → Full | `POST /sync/receive/reports` | Report data | On schedule |
| Solo → Full | `POST /sync/receive/inventory` | Inventory changes | On stock change |
| Full → Solo | `POST /sync/push/products` | Product catalog push | On catalog update |
| Full → Solo | `POST /sync/push/configs` | Configuration push | On config change |
| Full → Solo | `POST /sync/push/catalog` | Full catalog push | Manual trigger |
| Full → Solo | WebSocket `/ws/config` | Real-time config changes | Continuous |
| Solo → Full | WebSocket `/ws/nodes` (Full only) | Real-time node events | Continuous |

---

## 4. Cloud Architecture Plan (Future)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Cloud Server (port 8767)                             │
│                     Django + django-bolt + PostgreSQL                    │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  django-bolt API (Actix Web, Rust-powered)                        │  │
│  │                                                                    │  │
│  │  /bolt/products, /bolt/customers, /bolt/sales, /bolt/inventory   │  │
│  │  /bolt/crm/contacts, companies, deals, pipelines                 │  │
│  │  /bolt/reports/sales, inventory, analytics, dashboard            │  │
│  │  /bolt/branches, /bolt/integrations                               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │ Branch       │ │ Sync Broker  │ │ Report       │ │ Integration  │  │
│  │ Manager      │ │              │ │ Engine       │ │ Hub          │  │
│  │ • Register   │ │ • Real-time  │ │ • Daily      │ │ • Third-party│  │
│  │   branches   │ │   sync       │ │   reports    │ │   apps       │  │
│  │ • Auth       │ │ • Queue      │ │ • Analytics  │ │ • Webhooks   │  │
│  │ • Health     │ │ • Retry      │ │ • Export     │ │ • Email      │  │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘  │
│         │                │                │                │           │
│  ┌──────┴────────────────┴────────────────┴────────────────┴───────┐  │
│  │                     PostgreSQL Database                           │  │
│  │  Branches, Approvals, Reports, Audit Logs, Integrations           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
          ▲                    ▲                    ▲
          │                    │                    │
    ┌─────┴──────┐      ┌─────┴──────┐      ┌─────┴──────┐
    │ POS Solo   │      │ POS Full   │      │ Third-Party │
    │ (Node)     │      │ (Server)   │      │ Apps        │
    │ port 8765  │      │ port 8766  │      │ (ERP, CRM)  │
    └────────────┘      └────────────┘      └────────────┘
```

### Cloud Server Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **API Server** | Django + django-bolt (Rust) | High-performance REST + WS for all branches |
| **Database** | PostgreSQL | Multi-tenant, production-grade |
| **Branch Manager** | Django models + viewsets | Register, authenticate, and monitor branches |
| **Sync Broker** | django-bolt WebSocket | Real-time bidirectional sync between branches |
| **Report Engine** | Django ORM + Celery | Scheduled daily reports, analytics, CSV/PDF export |
| **Integration Hub** | Webhooks + REST | Connect third-party apps (ERP, CRM, accounting) |
| **Auth Gateway** | django-bolt middleware | Token-based auth with role hierarchy |

### Daily Reports (Synced)

| Report | Data Source | Schedule | Format |
|--------|------------|----------|--------|
| Sales Summary | All branch sale records | Daily, midnight | JSON / CSV / PDF |
| Inventory Status | All branch inventory | Daily, midnight | JSON / CSV |
| Branch Health | Heartbeat + node status | Hourly | JSON dashboard |
| Approval Queue | Pending approvals | Real-time | JSON dashboard |
| Sync Audit | SyncLog across branches | Daily | JSON / CSV |
| Revenue Analytics | Aggregated sales | Weekly | JSON dashboard |
| Low Stock Alerts | Inventory below reorder | Real-time | Push notification |

---

## 5. Organization Plan: One Server per Server

Each POS server now has a clear role and organized structure:

### formint-pos/server/ → Merged Robyn server
```
server/
├── server.py         # Thin entry point
├── routes/           # Route handler modules (7+ modules)
├── models/           # Django ORM models (organized packages)
├── bolt_api.py       # django-bolt API (ported from the former pos-full)
├── tests/            # Test suite (171 passing + legacy known-issue failures)
└── Django portal files **removed** — Robyn server.py handles everything
```

> **Note**: The former `pos-solo/server` and `pos-full/server` directories were
> merged into the single `formint-pos/server/` when the editions were consolidated.

### Cloud Server (Future: `projects/pos/cloud/`)
```
cloud/
├── server.py             # Django ASGI entry point
├── bolt_api.py           # django-bolt API (ported from pos-full)
├── models/               # Cloud-specific models
│   ├── branch.py         # CloudBranch, BranchHealth
│   ├── report.py         # DailyReport, ReportSchedule
│   └── integration.py    # ThirdPartyApp, WebhookConfig
├── services/
│   ├── sync_broker.py    # Real-time cross-branch sync
│   ├── report_engine.py  # Daily report generation
│   └── integration.py    # Third-party app connectors
├── tasks/                # Celery scheduled tasks
│   ├── daily_reports.py
│   └── sync_health.py
└── settings/             # Production Django settings
```

---

## 6. Next Steps

### Immediate (this milestone)
- [x] Document bolt_api current state
- [x] Create integration plan (this document)
- [x] Create `routes/crm.py` — port CRM endpoints from bolt_api
- [x] Create `routes/reports.py` — port report endpoints from bolt_api
- [ ] Add OpenAPI docs generation to Robyn server
- [x] Remove `django_bolt` from INSTALLED_APPS — bolt_api.py and Django files deleted

### Short-term (next milestone)
- [x] Full integration test: Robyn serving CRM + Reports (63/63 tests pass)
- [x] Deprecate and remove bolt_api.py — all endpoints now in routes/ package
- [x] Document solo↔full data flow in POS_ARCHITECTURE.md + BOLT_INTEGRATION.md

### Long-term (cloud server)
- [ ] Create `projects/pos/cloud/` directory
- [ ] Port bolt_api.py to cloud server
- [ ] Implement branch manager
- [ ] Implement sync broker with WebSocket
- [ ] Implement daily reports with Celery
- [ ] Implement integration hub for third-party apps
