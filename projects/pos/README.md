# POS — Restaurant Point of Sale Desktop App

> **v1.1** — 3 Edition System | Tauri 2 + React 19 + Rust + SQLite

<p align="center">
  <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/version-1.1.0-blue" alt="Version"/></a>
  <a href="../../docs/sites/pos.md"><img src="https://img.shields.io/badge/docs-site-green" alt="Documentation"/></a>
  <a href="PUBLISH.md"><img src="https://img.shields.io/badge/publish-marketplace-orange" alt="Publish"/></a>
  <a href="https://github.com/mammhoud/POS"><img src="https://img.shields.io/badge/support-github-lightgrey" alt="Support"/></a>
</p>

<p align="center">
  <img src="pos-full/docs/screenshots/01_pos_overview.jpg" alt="POS Overview" width="600"/>
</p>

POS is a modern, offline-first desktop point-of-sale application for
restaurants, cafes, and food-service businesses. Built with Tauri, React,
Rust, and SQLite — works on Windows, macOS, Linux, Android, and iOS.

---

## 📦 Three Editions

Choose the edition that fits your needs:

| Feature | Minimal | Solo | Full |
|---------|:-------:|:----:|:----:|
| **React + TypeScript frontend** | ✅ | ✅ | ✅ |
| **Tauri 2 + Rust backend** | ✅ | ✅ | ✅ |
| **SQLite database (29 tables)** | ✅ | ✅ | ✅ |
| **i18n (en/fr/ar)** | ✅ | ✅ | ✅ |
| **POS, inventory, analytics** | ✅ | ✅ | ✅ |
| **Employees, payroll, scheduling** | ✅ | ✅ | ✅ |
| **Kitchen display system** | ✅ | ✅ | ✅ |
| **Python/Sanic sidecar API** | ❌ | ✅ | ✅ |
| **REST API (35+ endpoints)** | ❌ | ✅ | ✅ |
| **Invoice PDF generation** | ❌ | ✅ | ✅ |
| **Chat support widget** | ❌ | ✅ | ✅ |
| **Django ORM models (30 tables)** | ❌ | ❌ | ✅ |
| **WebSocket real-time chat** | ❌ | ❌ | ✅ |
| **Data sync between devices** | ❌ | ❌ | ✅ |
| **JSON seed fixtures** | ❌ | ❌ | ✅ |
| **Django Portal (admin + menu UI)** | ✅ portal/ | ✅ portal/ | ✅ portal/ |
| **Cloud CRM master** | ❌ | ❌ | ✅ portal/cloud/ |
| **Directory size** | ~8M | ~8.5M | ~9M |

---

## 🚀 Quick Start

### Minimal Edition (no sidecar)
```bash
cd pos-minimal
pnpm install
cd src-tauri && cargo fetch && cd ..
pnpm dev          # Vite dev server at localhost:1420
pnpm dev:desktop  # Full Tauri desktop app
```

### Extended Edition (with sidecar API)
```bash
cd pos-solo
pnpm install && cd src-tauri && cargo fetch && cd ..
cd sidecar && pip install -r requirements.txt && cd ..
python3 sidecar/server.py &    # Start sidecar on :8765
pnpm dev                        # Vite dev server
```

### Full Edition (sidecar + Django + WebSocket)
```bash
cd pos-full
pnpm install && cd src-tauri && cargo fetch && cd ..
cd sidecar && pip install -r requirements.txt && cd ..
python3 sidecar/server.py &    # Sidecar + Django + WebSocket
pnpm dev
```

### Using Root Makefile
```bash
make editions          # Generate all 3 editions
make setup-full        # Install full edition deps
make dev-full          # Start full stack
make build-full        # Build everything
make screenshots       # Capture marketplace screenshots
make clean             # Delete all editions
```

### Formint POS Professional (merged package)

> **`formint-pos/`** is the merged package that consolidates `pos-full` + `pos-solo`
> into one product boundary with the same Tauri architecture. The backend uses
> **Django Ninja + ninja-extra** for the REST API (django-fusion encoder/decoder
> on every response) and **django-fusion data components** (tables + forms) for
> HTMX fragments.

```bash
cd formint-pos/backend && python3 -m venv .venv && . .venv/bin/activate
pip install -e . && python manage.py migrate
python manage.py runserver 127.0.0.1:8000   # API at /api/v1/, HTMX at /htmx/

cd ../frontend && pnpm install && pnpm dev  # Astro shell (proxies /api and /htmx)
```

API surface: `/api/v1/health`, `/api/v1/stats`, `/api/v1/openapi.json`, `/api/v1/docs`,
plus paginated CRUD for 45 resources (products, sales, inventory, suppliers,
purchase orders, loyalty, CRM, HR, …).

See [`formint-pos/README.md`](formint-pos/README.md) and
[`formint-pos/migration/compatibility-manifest.json`](formint-pos/migration/compatibility-manifest.json).

---

## 📸 Screenshots

| | | |
|:---:|:---:|:---:|
| ![Overview](pos-full/docs/screenshots/01_pos_overview.jpg) | ![Dashboard](pos-full/docs/screenshots/02_dashboard.jpg) | ![POS](pos-full/docs/screenshots/03_point_of_sale.jpg) |
| **Home / Overview** | **Dashboard Grid** | **Point of Sale** |
| ![Inventory](pos-full/docs/screenshots/04_inventory.jpg) | ![Reports](pos-full/docs/screenshots/05_reports.jpg) | ![Settings](pos-full/docs/screenshots/06_settings.jpg) |
| **Inventory** | **Reports** | **Settings** |

---

## 🏗️ Architecture

```
pos-{edition}/
├── src/                    # React 19 + TypeScript + Tailwind CSS 4
│   ├── api/                # API client layer (edition-dependent)
│   ├── components/         # 15 reusable UI components
│   ├── contexts/           # Auth, Theme, Language providers
│   ├── hooks/              # Custom React hooks
│   ├── i18n/               # en/fr/ar translations (i18next)
│   ├── pages/              # 22 route-level page components
│   ├── styles/             # SCSS (utilities, base, components)
│   └── utils/              # PDF/Excel export utilities
├── src-tauri/              # Tauri 2 + Rust + Diesel + SQLite
│   ├── src/
│   │   ├── db/             # Schema (29 tables), models, connection
│   │   ├── operations/     # 25 CRUD modules (auth, sales, inventory...)
│   │   └── email.rs        # SMTP email sender
│   ├── migrations/         # Diesel SQLite migrations (6)
│   └── icons/              # App icons (all platforms)├── sidecar/                 # [Solo/Full] Python/Robyn API + Django ORM
│   ├── server.py           # Robyn REST + WebSocket (60-70+ endpoints)
│   ├── models/             # Django ORM models (organized packages)
│   │   ├── pos.py          #   [Solo] Category, Product, Customer, Sale
│   │   ├── menu.py         #   [Solo] MenuItem, Menu, Assignment
│   │   ├── node.py         #   Node, Heartbeat, NodeEvent
│   │   ├── config.py       #   DeviceConfig, MasterDevice, CloudLink
│   │   └── sync.py         #   SyncLog
│   └── tests/              # Pytest suites (155 solo + 63 full)
├── shared/                 # [All] Models, signals, viewsets, templates
│   ├── signals/            #   Django signals (config_changed, etc.)
│   ├── models/             #   SignalEvent, SyncApproval, DeviceToken
│   ├── handlers/           #   Signal handlers (log, webhook, audit)
│   ├── services/           #   ProductSyncEngine
│   ├── middleware/          #   Auth middleware (bearer token + API key)
│   ├── api/                #   CRUD helpers (_ser, _register_crud)
│   ├── portal_viewsets.py  #   Portal viewsets (approvals, sync, menu)
│   └── portal_urls.py      #   Portal URL patterns
├── scripts/
│   ├── dev/                # Build, i18n, checksum utilities (12 scripts)
│   └── github/             # CI/CD scripts
└── docs/                   # Documentation (17 files)
```

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript 5.8, Vite 7, Tailwind CSS 4, Framer Motion |
| Backend | Rust (Tauri 2), Diesel ORM, SQLite |
| Sidecar | Python 3, Sanic, Django ORM (mirror), PyInstaller |
| i18n | i18next (English, French, Arabic) |
| Testing | Vitest (frontend), cargo test (Rust) |
| Build | pnpm, cargo, PyInstaller |

---

## ✨ Key Features

- **Cross-platform desktop POS** — Windows, macOS, Linux, Android, iOS
- **Offline-first SQLite** — No internet required for core POS operations
- **3 Editions** — Minimal (core), Solo (+API), Full (+Django+CRM+Sync)
- **Role-based auth** — Superuser with 2FA support
- **Inventory tracking** — Low-stock alerts, purchase orders, supplier management
- **Kitchen display system** — Ticket flow: pending → preparing → ready → delivered
- **POS-KO Gaming Center** — Token-based gaming sessions with time tracking
- **Customer database** — Loyalty points, purchase history
- **Advanced receipts** — Tax, commercial, proforma, credit invoice templates
- **Automated tax reports** — PDF and Excel export
- **Employee management** — Scheduling, payroll, role assignments
- **i18n (3 languages)** — English, French, Arabic with i18next
- **Dark & Light mode** — CSS custom properties theme system
- **REST API (Solo/Full)** — 35+ endpoints via Python/Sanic sidecar
- **WebSocket chat** — Real-time support chat with auto-reconnect
- **Cloud CRM sync** — Push sales, products, customers to cloud (Solo edition)
- **Django Portal** — Web-based admin UI with django-fusion viewsets

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [`SIDECAR_V2.md`](docs/SIDECAR_V2.md) | **Sidecar v2 reference** — Robyn + Django ORM, 70+ APIs, WS streams, signals, approval, sync, cloud plan |
| [`CHANGELOG.md`](CHANGELOG.md) | Full version history |
| [`PUBLISH.md`](PUBLISH.md) | Marketplace publish kit (ThemeForest, CodeCanyon, Gumroad) |
| [`docs/README.md`](docs/README.md) | Editions overview & architecture |
| [`docs/START_HERE.md`](docs/START_HERE.md) | Getting started guide |
| [`docs/commands.md`](docs/commands.md) | All CLI commands reference |
| [`docs/project-tree.md`](docs/project-tree.md) | Full project tree |
| [`docs/rust-code.md`](docs/rust-code.md) | Rust backend documentation |
| [`docs/customization-react.md`](docs/customization-react.md) | React customization guide |
| [`docs/customization-tauri.md`](docs/customization-tauri.md) | Tauri customization guide |
| [`docs/i18n-conventions.md`](docs/i18n-conventions.md) | Translation conventions |
| [`docs/server/README.md`](docs/server/README.md) | Sidecar API reference [Solo/Full] |
| [`docs/back-env/README.md`](docs/back-env/README.md) | Backend environment setup [Full] |

---

## 🏷️ Environment

Copy `.env.example` to `.env`:

```bash
SUPERUSER_EMAIL=admin@pos.local
SUPERUSER_PASSWORD=changeme
SUPERUSER_NAME=Admin
DATABASE_URL=restaurant.db
SIDECAR_HOST=127.0.0.1
SIDECAR_PORT=8765
```

---

## 📄 License

AGPL-3.0 — See [LICENSE](LICENSE)

---

## 🔗 Links

- **Website**: [structa.cloud](https://structa.cloud)
- **GitHub**: [github.com/mammhoud/POS](https://github.com/mammhoud/POS)
- **Marketplace**: See [`PUBLISH.md`](PUBLISH.md) for listing instructions
