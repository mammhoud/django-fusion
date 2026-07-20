# POS Mini Edition — Rust/Diesel Only (No Sidecar)

The **pos-mini** edition is the lightest POS variant. It uses only the Rust backend
(Diesel ORM + SQLite) with a Tauri desktop shell. No Python sidecar process.

## Architecture

```
┌──────────────────────────────────────┐
│         Tauri Desktop App             │
│  ┌──────────────┐ ┌────────────────┐ │
│  │ Rust Backend │ │ React Frontend │ │
│  │ (Diesel CRUD)│ │ (Vue/Pinia)    │ │
│  └──────┬───────┘ └───────┬────────┘ │
│         │                  │          │
│         │  Tauri IPC       │          │
│         │  (invoke)        │          │
│         ▼                  │          │
│  ┌──────────────────────┐  │          │
│  │ Diesel ORM (SQLite)  │  │          │
│  │ restaurant.db        │  │          │
│  └──────────────────────┘  │          │
└─────────────────────────────┴─────────┘
```

## Comparison

| Feature | pos-mini | pos-solo | pos-full |
|---------|----------|----------|----------|
| **Backend** | Rust/Diesel only | Robyn + Django ORM | Robyn + Django ORM |
| **Sidecar** | ❌ None | ✅ Robyn (8765) | ✅ Robyn (8766) |
| **API** | Tauri IPC only | HTTP REST + WS | HTTP REST + WS |
| **Database** | Diesel SQLite | Django ORM SQLite | Django ORM + Rust DB |
| **Port** | — | 8765 | 8766 |
| **Node Registry** | ❌ | ✅ | ✅ |
| **Sync** | ❌ | ✅ (client) | ✅ (master) |
| **Use case** | Single terminal | Standalone POS | Multi-node cloud |

## Build & Run

```bash
cd projects/pos/pos-mini
make setup    # Install dependencies
make dev      # Development mode
make build    # Production build
```

## Adding Features

To add a new CRUD operation, add a `#[tauri::command]` in `src-tauri/src/operations/`:

```rust
#[tauri::command]
async fn get_products(pool: State<'_, DbPool>) -> Result<Vec<Product>, String> {
    let conn = pool.get().map_err(|e| e.to_string())?;
    products::table.load(&conn).map_err(|e| e.to_string())
}
```

Then register it in `src-tauri/src/main.rs`:

```rust
.invoke_handler(tauri::generate_handler![get_products])
```
