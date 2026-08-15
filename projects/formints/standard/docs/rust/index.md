# Rust / Diesel Docs — POS Mini

> **Directory:** `docs/rust/`
> **Language:** Rust (2021 edition)
> **Framework:** Tauri 2.x + Diesel ORM (direct — no server)

---

POS Mini uses Rust/Tauri with direct Diesel + SQLite access — **no Python server**.

See the archived **`../../formint-pos/legacy-react/pos-full/docs/rust/index.md`** for the base Rust conventions.

## POS Mini Specific

- **No Python server** — all data logic lives in Rust
- **Direct Diesel access** — no intermediary HTTP layer
- **SQL migrations are raw SQL files** embedded at compile time via `include_str!`
- **Simpler command set** — no sync, no multi-store, no employee commands

## Direct Diesel Query Pattern

```rust
// src-tauri/src/commands/products.rs
use crate::db::models::Product;
use crate::db::schema::products;
use diesel::prelude::*;

#[tauri::command]
pub fn get_products(
    state: tauri::State<'_, AppState>,
    search: Option<String>,
) -> Result<Vec<Product>, String> {
    let conn = &mut *state.db.lock().map_err(|e| e.to_string())?;

    let mut query = products::table
        .filter(products::is_active.eq(true))
        .into_boxed();

    if let Some(q) = search {
        query = query.filter(products::name.like(format!("%{}%", q)));
    }

    query
        .order(products::name.asc())
        .load::<Product>(conn)
        .map_err(|e| e.to_string())
}
```

## Tauri Command Registration

```rust
// src-tauri/src/main.rs
fn main() {
    tauri::Builder::default()
        .manage(AppState::new())
        .invoke_handler(tauri::generate_handler![
            get_products,
            add_product,
            update_product,
            delete_product,
            get_customers,
            add_customer,
            // ... more commands
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

## WAL Mode + SQLite Optimization

```rust
// Enable Write-Ahead Logging for concurrent reads
conn.execute_batch(
    "PRAGMA journal_mode=WAL;
     PRAGMA synchronous=NORMAL;
     PRAGMA foreign_keys=ON;"
).map_err(|e| e.to_string())?;
```

## Migrations (Compile-Time Embedded)

```rust
use crate::db::migration::run_migrations;

fn main() {
    let state = AppState::new();
    let conn = &mut *state.db.lock().unwrap();
    run_migrations(conn).expect("Failed to run migrations");
}
```

See `../PROMPTS.md#rust--tauri-prompts` for code generation templates.
