# 🦀 Rust — Data Flow

> **Related Names:** `data flow`, `architecture`, `SQLite`, `Tauri invoke`, `sidecar`, `React`, `HTTP`, `WebSocket`, `IPC`, `read-only`
> **Tags:** #rust #data-flow #architecture #cross-layer

How data moves between Rust, SQLite, the Python sidecar, and the React frontend in POS.

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
│  │  src/api/*.ts                    │    │  Diesel ORM ────────┐       ││
│  │    │ sidecar.get/post()          │    │                     │       ││
│  │    ▼                             │    │    ┌────────────────▼──────┐ ││
│  │  HTTP/WS to 127.0.0.1:8765 ─────┼────┼───►│  SQLite (restaurant.db) │ ││
│  └──────────────────────────────────┘    │    │  Read/Write via Diesel  │ ││
│                                          │    └────────┬───────────────┘ ││
│                                          │             │ read-only        ││
│  ┌──────────────────────────────────┐    │    ┌────────▼───────────────┐ ││
│  │    Python Sidecar (Sanic)        │    │    │  Sidecar SQLite access  │ ││
│  │    projects/pos/sidecar/server.py      │    │    │  file:path?mode=ro      │ ││
│  │                                  │    │    └────────────────────────┘ ││
│  │  HTTP Routes                     │    │                               ││
│  │    GET  /api/sales               │    │    ┌─────────────────────────┐││
│  │    GET  /api/products            │    │    │  Migration System        │││
│  │    GET  /api/settings            │    │    │  embed_migrations!()     │││
│  │    GET  /invoice/render/:id      │    │    │  run_pending_migrations()│││
│  │  WebSocket                       │    │    └─────────────────────────┘││
│  │    WS   /ws/chat/:room           │    │                               ││
│  │                                  │    │    ┌─────────────────────────┐││
│  │  JSON File Storage               │    │    │  Seed Binary             │││
│  │    data/chat_*.json              │    │    │  bin/seed.rs              │││
│  │    data/tickets_*.json           │    │    │  PRESET=all|base|gaming   │││
│  └──────────────────────────────────┘    │    │  |coffee                  │││
│                                          │    └─────────────────────────┘││
│                                          └─────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
```

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

### Path 2: React ↔ Sidecar (HTTP/WS)

```
React component
  └── sidecar.get('/api/sales')
       └── HTTP GET 127.0.0.1:8765/api/sales
            └── Sanic handler → SQLite read-only → JSON response
```

> 💡 **Tip:** The sidecar only READS from SQLite (`?mode=ro`). All writes go through Rust via Tauri invoke.

### Path 3: Sidecar ↔ JSON Files (Chat/Tickets)

```
ChatSupport.tsx
  └── createChatWs({ room: 'support' })
       └── WebSocket 127.0.0.1:8765/ws/chat/support
            └── Sanic handler → read/write data/chat_support.json
```

> 🟢 **Customizable:** Chat and ticket data is stored in JSON files. You can replace with a real database.

---

## Read/Write Split

| Data Category | Write Path | Read Path |
|--------------|------------|-----------|
| Products | Tauri invoke → Rust → Diesel → SQLite | Tauri invoke OR Sidecar GET /api/products |
| Sales | Tauri invoke → Rust → Diesel → SQLite | Tauri invoke OR Sidecar GET /api/sales |
| Inventory | Tauri invoke → Rust → Diesel → SQLite | Tauri invoke only |
| Settings | Tauri invoke → Rust → Diesel → SQLite | Tauri invoke OR Sidecar GET /api/settings |
| Chat messages | WebSocket → Sidecar → JSON file | WebSocket OR Sidecar GET /chat/:room |
| Support tickets | Sidecar POST /api/support/ticket | Sidecar GET /api/support/tickets |
| Invoice render | — | Sidecar GET /invoice/render/:id (reads SQLite) |

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

### Sidecar HTTP

```typescript
import { sidecar, data } from '../api';

// Health check before making calls
const ok = await sidecar.healthCheck();

// Typed responses
const sales = await data.listSales();
const products = await data.listProducts();
const invoiceUrl = data.getInvoiceUrl(42, { type: 'commercial', design: 'modern' });
```

---

## Startup Sequence

```
1. Rust main() starts
     ├── get_db_path(app) → resolves restaurant.db path
     ├── run_migrations(&db_path) → applies pending migrations
     ├── check_auth_required(&db_path) → determines auth mode
     └── ensure_superuser_exists(&db_path) → creates superuser from env

2. Sidecar spawns (if configured)
     └── start_sidecar(app) → python server.py --db <path> --port 8765

3. React loads
     ├── App.tsx → Auth gate (login screen or Home)
     ├── sidecar.healthCheck() → verify sidecar running
     └── Pages invoke Rust commands as needed
```

---

## Customization Guide

### 🟢 Customizable
| What | How |
|------|-----|
| Add a Tauri command | Create ops function → register in lib.rs → invoke from React |
| Add sidecar endpoint | Add route in server.py → add client in src/api/ |
| Sidecar data storage | Replace JSON files with database |
| Read pattern | Use sidecar for read-heavy pages, Tauri for writes |

### 🔴 Not Customizable
| What | Why not |
|------|---------|
| Tauri IPC protocol | Must use `invoke()` — the bridge between JS and Rust |
| Sidecar read-only SQLite | `?mode=ro` prevents write conflicts with Rust |
| Command naming | Must match between lib.rs and React invoke() calls |
| Startup order | Rust → Sidecar → React — changing breaks initialization |

---

→ [Back to Rust docs](README.md) | [Database Layer](../backend/rust-database.md) | [Sidecar Docs](../sidecar/README.md)
