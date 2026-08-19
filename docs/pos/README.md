# POS — Restaurant Point of Sale Desktop App

> **Related Names:** `pos`, `POS system`, `desktop app`, `Tauri`, `React`, `Rust`, `SQLite`, `point-of-sale`, `offline-first`, `sidecar`, `Sanic`, `i18n`
> **Tags:** #site #pos #desktop #tauri #rust #react #offline

**Canonical path:** `projects/formints/`  
**Stack:** Tauri 2 + React 19 + Rust (Diesel ORM) + SQLite  
**Platforms:** Windows, macOS, Linux, Android, iOS

---

## Overview

POS is a modern, offline-first desktop point-of-sale application for restaurants, cafes, and food-service businesses. It runs as a native desktop app with a Python/Sanic sidecar server for extended API capabilities.

Unlike the Django-based web sites in this monorepo, POS is a standalone desktop application with its own build system, database, and documentation.

---

## Guide

### Quick Start (Minimal Edition)

```bash
cd projects/formints
cp .env.example .env   # Set SUPERUSER_EMAIL + SUPERUSER_PASSWORD
pnpm install
pnpm dev               # Vite dev server at localhost:1420
pnpm tauri dev         # Full Tauri desktop app
```

### Makefile Commands

```bash
# Development
make dev              # Vite dev server (browser only)
make dev-desktop      # Full Tauri desktop (hot-reload)

# Build
make build            # Production desktop build
make build-android    # Android APK

# Testing
make check            # TypeScript + Rust compilation
make test             # Vitest unit tests
make cargo-test       # Rust tests

# i18n
make i18n-audit       # Regenerate i18n gap report
make i18n-fix         # Apply Arabic translations

# Database
make seed             # Reset DB + seed (PRESET=all|base|gaming|coffee)
```

---

## Code Map

### Project Structure

| Path | Purpose | Customization |
|------|---------|:---:|
| `pos/src/` | React/TypeScript frontend (15 components, 22 pages) | 🟢 customizable |
| `pos/src/api/` | Sidecar API client layer | 🟢 customizable |
| `pos/src/contexts/` | Auth, Theme, Language providers | 🔴 not-customizable |
| `pos/src/hooks/` | Custom React hooks | 🟢 customizable |
| `pos/src/i18n/` | Translations (en/fr/ar via i18next) | 🟢 customizable |
| `pos/src/styles/` | SCSS (utilities, base, components) | 🟢 customizable |
| `pos/src/utils/` | PDF export, CSV export | 🟢 customizable |
| `pos/src-tauri/src/db/` | Database: schema, models, migrations, connection | 🔴 not-customizable |
| `pos/src-tauri/src/operations/` | **25 CRUD modules** (auth, sales, products, inventory...) | 🟢 customizable |
| `pos/src-tauri/src/email.rs` | SMTP email sending | 🟢 customizable |
| `pos/sidecar/server.py` | Robyn REST + WebSocket API (60-70+ endpoints) | 🟢 customizable |
| `pos/sidecar/models/pos.py` | Solo POS models (Category, Product, Customer, Sale...) | 🟢 customizable |
| `pos/sidecar/models/menu.py` | Solo menu models (MenuItem, Menu, Assignment) | 🟢 customizable |
| `pos/sidecar/models/node.py` | Node registry models (Node, Heartbeat, NodeEvent) | 🟢 customizable |
| `pos/sidecar/models/config.py` | Config models (DeviceConfig, MasterDevice, CloudLink) | 🟢 customizable |
| `pos/sidecar/models/sync.py` | Sync audit model (SyncLog) | 🟢 customizable |
| `shared-portal/cloud/` | Standalone Cloud CRM server (Sanic, port 8766) | 🟢 customizable |
| `shared-portal/cloud/sync_proxy.py` | Accepts generic entity pushes from Solo edition | 🟢 customizable |
| `pos-full/src-tauri/src/operations/signals.rs` | Change event broadcast channel (tokio) | 🟡 delegate |
| `pos-full/src-tauri/src/operations/crm.rs` | Rust Diesel CRM CRUD operations | 🟢 customizable |
| `pos/scripts/` | Build, dev, i18n, checksum utilities | 🟡 delegate |

### Three Editions

| Edition | Directory | Contents |
|---------|-----------|----------|
| **Minimal** | `pos-minimal/` | Frontend + Rust backend (no sidecar) |
| **Solo** _(prev. Extended)_ | `pos-solo/` | + Python/Sanic sidecar API + **cloud CRM sync** (`sync_client.py`, `sync_routes.py`) |
| **Full** | `pos-full/` | + Django ORM + WebSocket + **Cloud CRM server** (`cloud/`) + change signals |

```bash
make editions   # Generate editions from canonical source (pos-full)
```

### Sidecar Architecture

Both Solo and Full editions use **Robyn** (Rust-powered async Python server) with **Django ORM** for REST + WebSocket APIs.

### Shared Package Structure

```
projects/formints/shared/
├── signals/               # Signal definitions (config_changed, config_synced, device_status_changed)
├── models/                # Shared Django models
│   ├── audit.py           #   SignalEvent (audit trail)
│   ├── approval.py        #   SyncApproval (approve/reject workflow)
│   └── token.py           #   DeviceToken (SHA-256 auth)
├── handlers/              # Signal @receiver handlers
│   └── signal.py          #   Logging, webhook delivery, audit persistence
├── services/              # POS services
│   └── sync.py            #   ProductSyncEngine
├── middleware/             # Robyn middleware
│   └── auth.py            #   create_auth_middleware, register_auth_routes
├── api/                   # CRUD helpers
│   └── crud.py            #   _ser, _paginate, _register_crud
├── portal_viewsets.py     # Django Portal viewsets
└── portal_urls.py         # Portal URL patterns
```

### Solo Edition Models (`pos-solo/sidecar/models/`)

| Module | Models |
|--------|--------|
| `pos.py` | Category, Product, Customer, Sale, SaleItem, InventoryTransaction, Employee |
| `menu.py` | MenuItem, Menu, MenuItemAssignment |
| `node.py` | Node, Heartbeat, NodeEvent |
| `config.py` | DeviceConfig, MasterDevice, CloudLink |
| `sync.py` | SyncLog |

### Full Edition Models (`pos-full/sidecar/models/`)

| Module | Models |
|--------|--------|
| `node.py` | Node, Heartbeat, NodeEvent |
| `config.py` | DeviceConfig, MasterDevice, CloudLink |
| `sync.py` | SyncLog |

Plus 30+ Rust-backed tables in `posapp/models.py` (managed=False).

### Sync Architecture

```
+-------------------+       Robyn REST       +---------------------+
|  pos-solo         |  ──────────────────>  |  pos-full (master)  |
|  sidecar/server.py|  push products, sales |  port 8766          |
|  port 8765        |  <──────────────────  |  + approval queue   |
+-------------------+       status, config   +---------------------+
```

### Change Signals

The Rust backend (Full Edition) includes a broadcast-based change signal system (`operations/signals.rs`) that emits events when:
- **Settings** are saved (`ChangeEvent::SettingsChanged`)
- **Products** are created/updated/deleted (`ChangeEvent::ProductCreated`, `ProductUpdated`, `ProductDeleted`)
- **CRM entities** are modified (`ChangeEvent::EntityChanged`)

---

## Remarks

| # | Note |
|---|------|
| ⚠️ | POS requires **Rust toolchain** + Tauri CLI (`cargo install tauri-cli`) |
| ⚠️ | Auth is optional — configure via `SUPERUSER_EMAIL` + `SUPERUSER_PASSWORD` env vars |
| 💡 | The sidecar is auto-spawned by Rust on app start — no manual launch needed |
| 🔌 | Sidecar can be developed standalone: `python server.py --db ../restaurant.db --port 8765` |
| 🌐 | i18n supports **English, French, Arabic** — add more locales in `src/i18n/` |

---

## Customization Key

| Tag | Scope | What it means here |
|-----|-------|-------------------|
| 🟢 `customizable` | UI & operations | Pages, components, styles, translations, CRUD modules (25 ops) |
| 🟡 `delegate` | Extensions | Add Tauri command → register in `lib.rs`, add sidecar endpoint → register in `server.py` |
| 🔴 `not-customizable` | Core infra | Auth (`auth.rs`), database (`db/`), `AuthContext.tsx`, `App.tsx`, sidecar lifecycle (`sidecar.rs`) |
| 🔵 `template` | Templates | Invoice HTML template in `server.py`, SCSS variables |
| ⚪ `config` | Settings | `SUPERUSER_*`, `DATABASE_URL`, `SMTP_*` env vars |

---

## Related Documentation

| Area | Path |
|------|------|
| POS docs (in-project) | [POS docs](./) |
| Editions guide | [`editions.md`](editions.md) |
| Rust backend | [`rust-backend.md`](backend/rust-backend.md) |
| TypeScript frontend | [`typescript-frontend.md`](frontend/typescript-frontend.md) |
| Sidecar API | [`sidecar-readme.md`](sidecar/README.md) |
| POS changelog | [`changelog.md`](changelog.md) |
| Development guide | [`../../guides/03-dev.md`](../../guides/03-dev.md) |
| Customization | [`../../customization/`](../../customization/) |
| POS README | [POS source](https://github.com/mammhoud/structa.cloud/tree/generic/projects/formints) |
