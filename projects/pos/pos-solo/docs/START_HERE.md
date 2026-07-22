# POS — Getting Started Guide

> **Edition:** Full | **Stack:** Tauri 2 + React 19 + Rust + SQLite + Python/Sanic

Welcome to the POS Full Edition! This guide walks you through your first launch.

---

## Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| **Node.js** | ≥ 20 | `node --version` |
| **pnpm** | ≥ 9 | `pnpm --version` |
| **Rust** | ≥ 1.80 | `rustc --version` |
| **Tauri CLI** | ≥ 2.0 | `cargo install tauri-cli` |
| **Python** | ≥ 3.11 | `python3 --version` |
| **SQLite** | ≥ 3.35 | `sqlite3 --version` |

### Platform-Specific

| Platform | Extra Requirements |
|----------|-------------------|
| **Linux** | `libwebkit2gtk-4.1-dev`, `libgtk-3-dev`, `libayatana-appindicator3-dev` |
| **macOS** | Xcode Command Line Tools |
| **Windows** | Visual Studio Build Tools, WebView2 Runtime |

---

## Installation

```bash
# 1. Clone the repo (if not already)
cd projects/pos/pos-full

# 2. Install all dependencies
make install

# 3a. Copy environment config
cp .env.example .env

# 3b. Edit .env with your settings
# SUPERUSER_EMAIL=admin@pos.local
# SUPERUSER_PASSWORD=changeme
# SUPERUSER_NAME=Admin
```

---

## First Launch

### Option 1: Browser-only Dev (fastest)

```bash
make dev
# Opens http://localhost:1420 in your browser
```

This starts the Vite dev server with hot module replacement. No Rust backend needed for UI work.

### Option 2: Full Tauri Desktop (with backend)

```bash
make dev-desktop
# Launches the native desktop app with Rust backend
```

This starts Tauri in development mode — hot-reload for both frontend and backend changes.

### Option 3: Full Stack (sidecar + Django + desktop)

```bash
# Terminal 1: Start the Python sidecar
cd sidecar
pip install -r requirements.txt
python3 server.py --db ../restaurant.db --port 8765 &

# Terminal 2: Start the Django portal
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8080 &

# Terminal 3: Start the desktop app
cd ..
make dev-desktop
```

---

## Seeding the Database

The app ships with 4 preset datasets:

```bash
make seed PRESET=all       # All 100+ items (default)
make seed PRESET=base      # Basic restaurant (30 items)
make seed PRESET=gaming    # POS-KO Gaming Center preset
make seed PRESET=coffee    # Coffee shop preset
```

Seeding resets the database (`restaurant.db`) and populates it with products, categories, ingredients, recipes, and settings.

---

## Exploring the App

The POS has **22 page routes** accessible from the sidebar navigation:

| Route | Page | Description |
|-------|------|-------------|
| `/` | Home | Dashboard overview with KPIs |
| `/manager` | Product Manager | Product & category management |
| `/sale` | Point of Sale | Sales terminal with cart |
| `/analytics` | Analytics | Charts, revenue, trends |
| `/transactions` | Transactions | Sale history & refunds |
| `/inventory` | Inventory | Stock tracking & low-stock alerts |
| `/employees` | Employees | Staff management |
| `/recipes` | Recipes | Recipe & ingredient management |
| `/reports` | Reports | Exportable PDF/Excel reports |
| `/settings` | Settings | Restaurant, tax, display config |
| `/customers` | Customers | Customer DB & loyalty points |
| `/suppliers` | Suppliers | Supplier & purchase orders |
| `/kitchen` | Kitchen Display | Ticket flow board |
| `/schedule` | Employee Schedule | Shift scheduling |
| `/payroll` | Payroll | Payroll processing |
| `/receipt-templates` | Receipt Templates | Custom receipt designs |
| `/tax-reports` | Tax Reports | Tax period reporting |
| `/roles` | Roles | User roles & permissions |
| `/support-chat` | Support Chat | Real-time support chat |
| `/invoice` | Invoice | Invoice viewer & print |
| `/about` | About | App info & version |

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `src-tauri/src/lib.rs` | All Tauri command registrations |
| `src-tauri/src/operations/` | 27 CRUD operation modules |
| `src-tauri/src/db/schema.rs` | 29+ table schema definitions |
| `src/App.tsx` | Route definitions & page transitions |
| `src/main.tsx` | App entry point & providers |
| `src/i18n/` | English, French, Arabic translations |
| `sidecar/server.py` | Sanic REST API (when using sidecar) |
| `Makefile` | Build, test, dev, and seed commands |

---

## Next Steps

- **[commands.md](commands.md)** — Complete CLI reference
- **[rust-code.md](rust-code.md)** — Rust backend architecture
- **[customization-react.md](customization-react.md)** — Customize the frontend
- **[customization-tauri.md](customization-tauri.md)** — Customize the desktop app
- **[i18n-conventions.md](i18n-conventions.md)** — Translation workflow
