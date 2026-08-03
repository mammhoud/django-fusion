# ARCHIVED — COMPLETED (as of 2026-08-02)

> This plan has been fully implemented (see forge-pos CHANGELOG).
> Moved from `docs/plans/pos/` on 2026-08-02. Kept for historical reference only.

---

# POS Mini — Enhancement Plan
> **Tags:** #pos #forge-pos #enhancement #tauri

> **Plan file:** `projects/pos/pos-mini/plan/ENHANCEMENT_PLAN.md`
> **Created:** 2026-07-25 | **Branch:** `generic`

---

## Overview

POS Mini is the lightweight Tauri edition with direct Rust + Diesel + SQLite
access — **no Python sidecar**. This plan covers Mini-specific enhancements.

---

## Plan 1 — Component Reorganization

**Reference:** `../pos-full/plan/COMPONENT_REORGANIZATION.md`

Minimal reorganization — Mini has fewer components:

```
src/components/
  ui/         # Modal, Skeleton (from POS Full)
  layout/     # PageLayout, SideNav
  pos/        # ProductCard

src/pages/
  pos/        # Sale, ProductManager
  customers/  # Customers
  reports/    # Reports, Analytics
  admin/      # Settings, Notes, About
  auth/       # Auth
```

### Mini-Specific Differences

- **No Python sidecar** — no `sidecar/` directory, no `lib/fusion-*.ts`
- **`stores/` directory** (plural) — existing convention, keep as-is
- **No `store/` Redux** — uses simpler state if RTK Query is not needed
- **SQL migrations** are raw SQL files in `src-tauri/migrations/` (no Diesel migration runner)

---

## Plan 2 — Rust Data Layer Improvements

Since POS Mini has no Python sidecar, all data logic is in Rust. Improvements:

### 2.1 Direct Diesel Query Helper

```rust
// src-tauri/src/db/helpers.rs
pub fn get_products_by_category(conn: &SqliteConnection, category_id: i32) -> Vec<Product> {
    use crate::db::schema::products::dsl::*;
    products.filter(category_id.eq(category_id)).load(conn).unwrap_or_default()
}
```

### 2.2 Transaction Safety

Wrap all Tauri commands in transactions:

```rust
#[tauri::command]
fn add_product(state: tauri::State<AppState>, product: NewProduct) -> Result<Product, String> {
    let conn = &mut *state.db.lock().map_err(|e| e.to_string())?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(products::table)
            .values(&product)
            .get_result(conn)
    }).map_err(|e| e.to_string())
}
```

### 2.3 WAL Mode Optimization

SQLite's Write-Ahead Logging (WAL) is the best approach for a single-user
desktop app — no connection pooling needed. The current `Mutex<SqliteConnection>`
+ WAL mode handles concurrent reads natively.

```rust
// src-tauri/src/main.rs — enable WAL mode on startup
conn.execute_batch("PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;")?;
```

Benefits: concurrent reads + writes without locking, faster than connection pooling
for single-user apps, and built into SQLite with zero dependencies.

---

## Plan 3 — SQL Migration System

Mini uses raw SQL files for migrations (no Diesel migration runner). Improve:

### 3.1 Migration Runner (Compile-Time Embedded)

Migrations must be embedded at compile time — the `src-tauri/migrations/`
source directory doesn't exist in a bundled/released Tauri app.

```rust
// src-tauri/src/db/migration.rs
// Embed migration SQL at compile time using include_str!
pub fn run_migrations(conn: &SqliteConnection) -> Result<(), String> {
    // Each migration is embedded via build.rs or include_str!
    const MIGRATIONS: &[(&str, &str)] = &[
        ("2026-01-01-000000_create_all", include_str!("../migrations/2026-01-01-000000_create_all/up.sql")),
        ("2026-07-25-000000_add_border_color", include_str!("../migrations/2026-07-25-000000_add_border_color/up.sql")),
    ];

    // Track applied migrations
    conn.execute_batch("CREATE TABLE IF NOT EXISTS _migrations (name TEXT PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        .map_err(|e| e.to_string())?;

    for (name, sql) in MIGRATIONS {
        let already_applied: bool = conn
            .query_row("SELECT COUNT(*) FROM _migrations WHERE name = ?1", [name], |row| row.get::<_, i32>(0))
            .unwrap_or(0) > 0;
        if !already_applied {
            conn.execute_batch(sql).map_err(|e| e.to_string())?;
            conn.execute("INSERT INTO _migrations (name) VALUES (?1)", [name])
                .map_err(|e| e.to_string())?;
        }
    }
    Ok(())
}
```

### 3.2 Migration Tracking Table

```sql
-- Track which migrations have been applied
CREATE TABLE IF NOT EXISTS _migrations (
    name TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Documentation

| Doc | Content |
|-----|---------|
| `AGENTS.md` | Mini-specific: no sidecar, Rust+Diesel only, `stores/` dir |
| `PROMPTS.md` | Rust-only prompts, raw SQL patterns |
| `docs/typescript/index.md` | No Fusion, direct Tauri invoke |
| `docs/rust/index.md` | Direct Diesel, no HTTP layer |
| `docs/sql/index.md` | Raw SQL migrations, no Django ORM |

---

## Progress

| Plan | Status | Effort |
|------|:------:|:------:|
| 1 — Component Reorganization | ⬜ | 3s |
| 2 — Rust Data Layer Improvements | ⬜ | 4s |
| 3 — SQL Migration System | ⬜ | 3s |