# POS Mini

> Minimal desktop POS — Tauri + React + Rust/Diesel ORM (embedded SQLite). No sidecar.

This is the **mini edition** of POS. It includes the full React frontend with
the **Rust/Diesel ORM** backend running directly inside the Tauri process — no
external Python sidecar needed. All data operations use `invoke()` to call
Tauri commands backed by Diesel.

## Architecture

```
┌──────────────────────────────────────────────┐
│  Tauri Desktop App                           │
│  ┌──────────────┐    invoke()    ┌─────────┐ │
│  │  React UI    │ ────────────── │  Rust   │ │
│  │  (TypeScript)│                │  Backend│ │
│  │              │                │         │ │
│  │  Pages:      │                │  Diesel │ │
│  │  ProductMgr  │                │  ORM    │ │
│  │  Customers   │                │         │ │
│  │  Sale        │                │  SQLite │ │
│  │  Employees   │                │  (local)│ │
│  │  Settings    │                │         │ │
│  │  ...         │                │         │ │
│  └──────────────┘                └─────────┘ │
└──────────────────────────────────────────────┘
```

## What's Included

- **React frontend** (TypeScript, Tailwind CSS, Framer Motion)
- **Rust/Diesel ORM** — 30+ Tauri `#[command]` functions for full CRUD
- **Embedded SQLite** — `restaurant.db` managed by Diesel migrations
- **Tauri shell** — window management, file dialogs, native menus
- **Invoice PDF generation** (jspdf-based, saved via Tauri file dialogs)
- **Product image support** (Tauri file picker + base64 encoding)
- **i18n** — multi-language support via react-i18next

## What's NOT Included

- Python/Robyn sidecar server (use [`pos-solo`](../pos-solo/) for that)
- Zustand API stores (pos-mini uses `invoke()` directly)
- Django ORM models
- Cloud CRM sync

> Need a sidecar API + cloud sync? Use [`pos-solo`](../pos-solo/) or [`pos-full`](../pos-full/).

## Quick Start

```bash
# Install dependencies
pnpm install
cd src-tauri && cargo fetch && cd ..

# Run dev server (React + Tauri)
pnpm dev

# Or run Tauri desktop app
pnpm tauri dev
```

## Database

Diesel manages the embedded SQLite database:

```bash
# Run Diesel migrations
cd src-tauri
diesel migration run --database-url ../restaurant.db

# The DB is created automatically on first launch
```

## Tauri Commands (Rust Backend)

All data operations use `invoke()` from `@tauri-apps/api/core`:

| Command | Description |
|---------|-------------|
| `get_products` | List all products |
| `add_product` | Create a product |
| `update_product` | Update a product |
| `delete_product` | Delete a product |
| `get_customers` | List all customers |
| `add_customer` | Create a customer |
| `update_customer` | Update a customer |
| `delete_customer` | Soft-delete a customer |
| `get_sales` | List all sales |
| `add_sale` | Create a sale with items |
| `get_employees` | List employees |
| `add_employee` | Create an employee |
| `get_settings` | Get app settings |
| `save_settings` | Save app settings |
| ... | (30+ commands total) |

## Environment

```bash
SUPERUSER_EMAIL=admin@pos.local
SUPERUSER_PASSWORD=changeme
DATABASE_URL=restaurant.db
```

## Build

```bash
pnpm build:desktop     # Production desktop app (Tauri bundle)
```

## Editions Comparison

| Feature | pos-mini | pos-solo | pos-full |
|---------|----------|----------|----------|
| Rust/Diesel ORM | ✅ | ❌ (removed) | ❌ (removed) |
| Robyn sidecar | ❌ | ✅ | ✅ |
| Cloud CRM sync | ❌ | ✅ | ✅ |
| WebSocket support | ❌ | ✅ | ✅ |
| Django ORM models | ❌ | ✅ | ✅ |
| Node registry | ❌ | ✅ | ✅ |
| invoke() data ops | ✅ | ❌ (Zustand) | ❌ (Zustand) |
| Database | SQLite (Diesel) | SQLite (Django) | SQLite (Django) |
