# POS — Desktop Point-of-Sale Application

> **Edition System:** Minimal | Solo | Full  
> **Stack:** Tauri 2 + React 19 + Rust + SQLite (+ Robyn + Django ORM sidecar)  
> **Shared Assets:** `projects/pos/assets/css/pos-theme.css`

---

## ▶️ What's New — Sidecar v2 (July 2026)

The POS sidecar has been modernised from Sanic → **Robyn** (high-performance async Python server) with **Django ORM** for database access. All APIs are served through a single Robyn process — no separate Django portal needed.

## 📚 Documentation Library

| Document | Description |
|----------|-------------|
| [`POS_ARCHITECTURE.md`](POS_ARCHITECTURE.md) | **Master design doc** — full architecture diagrams, API organization, model maps, data flow, streaming, cloud plan |
| [`SIDECAR_V2.md`](SIDECAR_V2.md) | Sidecar v2 full reference — models, 70+ APIs, WebSocket, signals, approval, sync, token system |
| [`CLOUD_PLAN.md`](CLOUD_PLAN.md) | Cloud server integration plan — multi-branch streaming, offline-first, cross-branch approvals |
| [`RUST_INTEGRATION.md`](RUST_INTEGRATION.md) | Rust backend linking — sync, tokens, config, approval modules, Tauri command registration |
| [`PINIA_API.md`](PINIA_API.md) | Frontend Pinia stores — base API client, WebSocket manager, store examples for all API categories |

### Key Features

| Capability | Description |
|-----------|-------------|
| 🚀 **Robyn + Django ORM** | Single async server — no Django portal needed |
| 🔄 **Product Sync Engine** | Master→Child product/config push + Child→Master sales/reports with approval queue |
| ✅ **Moderated Approvals** | `SyncApproval` model with approve/reject workflow for cross-branch data changes |
| 🔌 **Django Signals** | `config_changed`, `config_synced`, `device_status_changed` wired into all endpoints |
| 🌐 **WebSocket Streams** | `/ws/nodes` (node events) + `/ws/config` (config changes) with client-side filters |
| 🔑 **Device Token Auth** | SHA-256 bearer tokens with role hierarchy (viewer < cashier < manager < admin) |
| 🔗 **Cloud Bridge Plan** | Unified cloud server linking all branches via token keys |
| 📱 **Pinia Stores** | Full frontend integration — HTTP client + WebSocket manager + reactive stores |

---

## Edition Overview

| Edition | Sidecar | Django ORM | WebSocket | Cloud Sync | Use Case |
|---------|---------|-----------|-----------|------------|----------|
| **Minimal** | ❌ | ❌ | ❌ | ❌ | Core POS — fast, lightweight, offline-first |
| **Solo** | ✅ Robyn | ✅ `models/` (pos, menu, node, config, sync) | ✅ `/ws/config` | ✅ sync client | Standalone POS node with API |
| **Full** | ✅ Robyn | ✅ `models/` (node, config, sync) + posapp (Rust-backed) | ✅ `/ws/config` + `/ws/nodes` | ✅ cloud master + CRM | Enterprise POS with multi-node orchestration |

---

## Edition Plans

### Minimal — Core POS App

**Directory:** `projects/pos/pos-minimal/`

The minimal edition is the foundational point-of-sale desktop application built with **Tauri 2 + React 19 + Rust + SQLite**. It runs fully offline with no external dependencies.

**Architecture:**
```
pos-minimal/
├── src/                # React/TypeScript frontend
│   ├── api/            # Tauri invoke API layer
│   ├── components/     # 15 reusable UI components
│   ├── contexts/       # Auth, Theme, Language providers
│   ├── hooks/          # Custom React hooks
│   ├── i18n/           # en/fr/ar translations
│   ├── pages/          # 22 route-level page components
│   ├── styles/         # SCSS (utilities, base, components)
│   └── utils/          # PDF export, data utilities
├── src-tauri/          # Rust/Tauri backend
│   ├── src/
│   │   ├── db/         # Database (schema, models, migrations)
│   │   ├── operations/ # CRUD operations (25+ modules)
│   │   └── email.rs    # SMTP email sender
│   ├── migrations/     # Diesel SQLite migrations
│   └── icons/          # App icons
├── assets/             # Shared design system (symlinked from ../assets/)
└── Makefile            # Build & dev commands
```

**Commands:**
```bash
cd projects/pos/pos-minimal
pnpm install
pnpm tauri dev    # Development
pnpm build        # Production build
```

---

### Solo — POS + Sidecar API + Django ORM

**Directory:** `projects/pos/pos-solo/`

The solo edition adds a **Robyn async Python server** with **Django ORM** for REST + WebSocket APIs on top of the core POS SQLite database.

**Additional Architecture:**
```
pos-solo/
├── ...core POS files (same as minimal)...
├── sidecar/
│   ├── server.py           # Robyn REST + WebSocket API (60+ endpoints)
│   ├── models/             # Django ORM models (managed=True) — organized packages
│   │   ├── pos.py          #   Category, Product, Customer, Sale, etc.
│   │   ├── menu.py         #   MenuItem, Menu, MenuItemAssignment
│   │   ├── node.py         #   Node, Heartbeat, NodeEvent
│   │   ├── config.py       #   DeviceConfig, MasterDevice, CloudLink
│   │   └── sync.py         #   SyncLog
│   ├── requirements.txt    # Python deps
│   ├── Makefile            # Sidecar commands
│   └── tests/              # 155 pytest tests
└── assets/                 # Shared design system
```

**Key APIs (see full catalog in SIDECAR_V2.md §4):**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check with uptime |
| `/nodes/register` | POST | Register a POS node |
| `/nodes/heartbeat` | POST | Record node heartbeat |
| `/{entity}` | GET/POST | CRUD for 15 entity types |
| `/approvals/pending` | GET | Pending approval queue |
| `/sync/status` | GET | Sync health & logs |
| `/ws/config` | WS | Config change stream |

**Commands:**
```bash
cd projects/pos/pos-solo/sidecar
python3 server.py --port 8765          # Start Robyn server
DJANGO_SETTINGS_MODULE='' python3 -m pytest tests/ -v  # 155 tests
```

---

### Full — POS + Sidecar + Django ORM + Cloud Master

**Directory:** `projects/pos/pos-full/`

The full edition adds **Rust-backed POS tables** (posapp, managed=False) and serves as the **Cloud Master** for multi-node orchestration.

**Additional Architecture:**
```
pos-full/
├── ...core POS files (same as solo)...
├── sidecar/
│   ├── server.py           # Robyn REST + WebSocket API (70+ endpoints)
│   ├── models/             # Django ORM models (managed=True) — organized packages
│   │   ├── node.py         #   Node, Heartbeat, NodeEvent
│   │   ├── config.py       #   DeviceConfig, MasterDevice, CloudLink
│   │   └── sync.py         #   SyncLog
│   ├── posapp/models.py    # Rust-backed POS tables (30+, managed=False)
│   ├── bolt_api.py         # django-bolt high-performance API (60k+ RPS) [deprecated — removed]
│   ├── requirements.txt    # Python deps
│   ├── .env.example        # Environment variable template
│   ├── Makefile            # Sidecar commands
│   └── tests/              # 63 pytest tests (server + webhook E2E)
└── assets/                 # Shared design system
```

**Commands:**
```bash
cd projects/pos/pos-full/sidecar
python3 server.py --port 8766          # Start Robyn server
DJANGO_SETTINGS_MODULE='' python3 -m pytest tests/ -v  # 63 tests
```

---

## Shared Module Map

**Directory:** `projects/pos/shared/`

```
shared/
├── signals/               # Django signals (__init__.py — config_changed, config_synced, etc.)
├── models/                # Shared Django models
│   ├── audit.py           #   SignalEvent (audit trail)
│   ├── approval.py        #   SyncApproval (approve/reject workflow)
│   └── token.py           #   DeviceToken (SHA-256 auth)
├── handlers/              # Signal handlers
│   └── signal.py          #   @receiver — log, webhook, audit persistence
├── services/              # POS services
│   └── sync.py            #   ProductSyncEngine (Master↔Child sync + approval)
├── middleware/            # Robyn middleware
│   └── auth.py            #   create_auth_middleware, register_auth_routes
└── api/                   # CRUD helpers
    └── crud.py            #   _ser, _paginate, _register_crud (legacy — routes/state.py preferred)
```

---

## Shared Design System

**Location:** `projects/pos/assets/css/pos-theme.css`

All editions share a common design system through CSS custom properties:

```css
:root {
  --pos-primary: #2563eb;
  --pos-secondary: #059669;
  --pos-accent: #f59e0b;
  --pos-danger: #dc2626;
  --pos-bg: #f8fafc;
  --pos-surface: #ffffff;
  --pos-border: #e2e8f0;
  --pos-text: #1e293b;
  --pos-radius: 8px;
  --pos-font: 'Inter', sans-serif;
}
```

**Components:** buttons (`.pos-btn`), cards (`.pos-card`), tables (`.pos-table`), forms (`.pos-input`), badges (`.pos-badge`), layout (`.pos-layout`, `.pos-sidebar`, `.pos-main`), navigation (`.pos-nav-item`).

---

## Related Documentation

| Document | Description | Path |
|----------|-------------|------|
| **Sidecar v2 (Full Reference)** | Architecture, models, 70+ APIs, WS, signals, approval, sync, cloud plan | [`docs/SIDECAR_V2.md`](SIDECAR_V2.md) |
| **Main README** | Edition overview, quick start, feature table | [`README.md`](../README.md) |
| **Changelog** | Version history | [`CHANGELOG.md`](../CHANGELOG.md) |
| **Backend Environment** | Dev environment setup | [`../../docs/back-env/`](../../docs/back-env/) |
| **Deployment Guide** | Production deployment | [`../../docs/guides/04-deploy.md`](../../docs/guides/04-deploy.md) |
| **Customization Guide** | How to customise | [`../../docs/guides/05-customize.md`](../../docs/guides/05-customize.md) |
| **Rust Backend** | Tauri/Rust internals | [`../../docs/rust/`](../../docs/rust/) |
| **TypeScript Frontend** | React/TS docs | [`../../docs/typescript/`](../../docs/typescript/) |