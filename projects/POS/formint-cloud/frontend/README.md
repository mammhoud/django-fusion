# Formint

> **Product:** Formints (site slug `formint-pos`) · Minimal desktop POS — Tauri + React + Rust/Diesel ORM (embedded SQLite). No server.

This is the **formint-pos edition** of POS (formerly pos-mini / forge-pos). It includes the full React frontend with
the **Rust/Diesel ORM** backend running directly inside the Tauri process — no
external Python server needed. All data operations use `invoke()` to call
Tauri commands backed by Diesel.

> **Edition identity on the landing site:** this project is marketed as the
> **Formints** desktop POS at `/products/formint-pos/` — Community (this
> edition), Standard, Pro and Cloud. Keep the landing product page and this
> repo's README/docs in sync (features, comparison rows, snippets, roadmap).

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

- Python/Robyn server server (use [`formint`](../../formint/) for that)
- Zustand API stores (forge-pos uses `invoke()` directly)
- Django ORM models
- Cloud CRM sync

> Need a server API + cloud sync? Use [`formint`](../../formint/) (the merged Pro package, formerly pos-full + pos-solo).

## Documentation

| Document | Description |
|----------|-------------|
| [Commands](docs/commands.md) | Complete CLI reference for dev, build, test, seed |
| [Project Tree](docs/project-tree.md) | Full directory structure with descriptions |
| [Rust Backend](docs/rust-code.md) | Diesel ORM schema, 27 operation modules, hardware integration |
| [Calculations](docs/calculations.md) | All formulas: sales, tax, delivery, payroll, loyalty |
| [Roles & Permissions](docs/roles-permissions.md) | Permission flags, default roles, UI hiding rules |
| [Customization](docs/customization.md) | Theme variants, product colors, receipts, i18n, presets |
| [Editions & features](../../docs/architecture/editions.md) | Cross-edition architecture & API documentation |

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

| Feature | Mini (formint-pos, this edition) | Merged (formint-pos) |
|---------|:---------:|:-----------:|
| Rust/Diesel ORM | ✅ | ❌ (Django is data authority) |
| Robyn server | ❌ | ✅ |
| Django Ninja backend | ❌ | ✅ |
| Cloud CRM sync | ❌ | ✅ |
| WebSocket support | ❌ | ✅ |

> **Note**: The former `pos-solo` and `pos-full` editions were merged into
> `formint-pos/` (see [`../../formint/README.md`](../../formint/README.md)).
| Django ORM models | ❌ | ✅ | ✅ |
| Node registry | ❌ | ✅ | ✅ |
| invoke() data ops | ✅ | ❌ (Zustand) | ❌ (Zustand) |
| Hardware printer | ✅ Direct ESC/POS | ❌ | ❌ |
| Database | SQLite (Diesel) | SQLite (Django) | SQLite (Django) |

## New features (landing-site sync — August 2026)

Feature additions shipped to the Formints product page (`/products/formint-pos/`)
and mirrored here:

- **Expanded feature-comparison table** — the edition matrix now covers
  offline-first mode, refunds & returns, loyalty & rewards program,
  multi-currency & tax profiles, custom roles & permissions, data export
  (CSV/JSON) and automatic cloud backups across Community · Standard · Pro · Cloud.
- **Edition capabilities** — Community gained offline-first mode + refunds;
  Standard gained loyalty, multi-currency, roles and data export; Cloud gained
  automatic backups + monitoring.
- **New reference snippets** — `Diesel migration (up.sql)` (loyalty points +
  refunds tables) and a `Tauri command (invoice PDF)` example joined the
  existing SQLite schema + Rust model snippets on the product page.
- **Product roadmap** — a dedicated roadmap band (loyalty engine,
  multi-currency & tax profiles, automatic cloud backups) is published on the
  landing page and tracked here.
