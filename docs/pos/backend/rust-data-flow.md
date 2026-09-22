# 🦀 Rust — Data Flow

> **Related Names:** `data flow`, `architecture`, `SQLite`, `Tauri invoke`, `React`, `IPC`, `read-only`
> **Tags:** #rust #data-flow #architecture #cross-layer

How data moves between Rust, SQLite, and the React frontend in POS
(Community / Standard editions — offline-first, no sidecar). Pro and Cloud
serve their APIs from Django; see [editions](../editions.md).

---

## Full Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        POS Desktop Application                       │
│                                                                         │
│  ┌──────────────────────────────────┐    ┌─────────────────────────────┐│
│  │       React Frontend              │    │     Tauri/Rust Backend       ││
│  │       (TypeScript/Vite)           │    │     (src-tauri/)             ││
│  │                                  │    │                             ││
│  │  src/pages/*.tsx                 │    │  lib.rs                     ││
│  │    │ invoke('command', {args})    │◄──►│    │ #[tauri::command]       ││
│  │    ▼                             │IPC │    ▼                        ││
│  │  Rust command returns JSON ──────┼───►│  operations/*.rs            ││
│  │                                  │    │    │ open_conn(&db_path)     ││
│  │                                  │    │    ▼                        ││
│  │                                  │    │  Diesel ORM ────────┐       ││
│  │                                  │    │                     │       ││
│  │                                  │    │    ┌────────────────▼──────┐ ││
│  │                                  │    └───►│  SQLite (restaurant.db) │ ││
│  │                                  │    │    │  Read/Write via Diesel  │ ││
│  └──────────────────────────────────┘    │    └────────────────────────┘ ││
│                                          │    ┌─────────────────────────┐││
│                                          │    │  Migration System        │││
│                                          │    │  embed_migrations!()     │││
│                                          │    │  run_pending_migrations()│││
│                                          │    └─────────────────────────┘││
│                                          │    ┌─────────────────────────┐││
│                                          │    │  Seed Binary             │││
│                                          │    │  bin/seed.rs              │││
│                                          │    │  PRESET=all|base|gaming   │││
│                                          │    │  |coffee                  │││
│                                          │    └─────────────────────────┘││
│                                          └─────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
```

> **⛔ Sidecar paths removed:** the former Python/Sanic sidecar (`sidecar/server.py`,
> `127.0.0.1:8765`, JSON-file chat/tickets) no longer exists. Community/Standard
> do all data access through Tauri `invoke()` → Rust/Diesel; Pro/Cloud use Django.

---

## Communication Paths

### Path 1: Rust ↔ SQLite (Primary)

```
React page
  └── invoke('get_products')
       └── #[tauri::command] get_products
            └── operations::products::get_products(&db_path)
                 └── open_conn(&db_path) → Diesel query
                      └── SQLite → Vec<Product> → JSON → React
```

> 🔴 **Not customizable:** This is the core Tauri IPC path. All CRUD operations use this pattern.

### Path 2: React ↔ Sidecar (HTTP/WS) — ⛔ removed

```
React component
  └── sidecar.get('/api/sales')      # no longer exists
       └── HTTP GET 127.0.0.1:8765/api/sales
```

> The sidecar paths are historical. In current editions every read and write
> goes through `invoke()` → Rust/Diesel (Community/Standard) or the Django API
> (Pro/Cloud).

---

## Read/Write Split

| Data Category | Write Path | Read Path |
|--------------|------------|-----------|
| Products | Tauri invoke → Rust → Diesel → SQLite | Tauri invoke |
| Sales | Tauri invoke → Rust → Diesel → SQLite | Tauri invoke |
| Inventory | Tauri invoke → Rust → Diesel → SQLite | Tauri invoke |
| Settings | Tauri invoke → Rust → Diesel → SQLite | Tauri invoke |

---

## Tauri Command Registration

All Rust operations are registered as Tauri commands in `lib.rs`:

```rust
#[tauri::command]
fn get_products(state: tauri::State<AppState>) -> Result<Vec<Product>, String> {
    operations::products::get_products(&state.db_path)
}

// Registered in main:
tauri::Builder::default()
    .invoke_handler(tauri::generate_handler![
        get_products,
        add_product,
        update_product,
        // ... all commands ...
    ])
```

> 🔴 **Not customizable:** Command registration must match the frontend `invoke()` calls exactly by name.

---

## Frontend Invoke Patterns

### Direct Rust Invoke

```typescript
import { invoke } from '@tauri-apps/api/core';

// Queryable types mirror Rust structs exactly
const products = await invoke<Product[]>('get_products');
const sale = await invoke<Sale>('add_sale', { newSale, items });
```

### Pro/Cloud HTTP (Django)

Pro and Cloud serve their API from Django (daphne ASGI); the frontend uses
`@formints/client` or the fusion render-mode contract. See
[Pro README](../../projects/formints/formint-pro/README.md) and
[Cloud README](../../projects/formints/formint-cloud/README.md).

---

## Startup Sequence

```
1. Rust main() starts
     ├── get_db_path(app) → resolves restaurant.db path
     ├── run_migrations(&db_path) → applies pending migrations
     ├── check_auth_required(&db_path) → determines auth mode
     └── ensure_superuser_exists(&db_path) → creates superuser from env

2. React loads
     └── App.tsx → Auth gate (login screen or Home) → Pages invoke Rust commands
```

---

## Customization Guide

### 🟢 Customizable
| What | How |
|------|-----|
| Add a Tauri command | Create ops function → register in lib.rs → invoke from React |
| Add a Django endpoint (Pro/Cloud) | Add a service/route in the edition's backend → frontend type |
| Read pattern | Tauri invoke (Community/Standard) or Django API (Pro/Cloud) |

### 🔴 Not Customizable
| What | Why not |
|------|---------|
| Tauri IPC protocol | Must use `invoke()` — the bridge between JS and Rust |
| Command naming | Must match between lib.rs and React invoke() calls |

---

→ [Back to Rust docs](README.md) | [Database Layer](../backend/rust-database.md) | [Editions](../editions.md)
