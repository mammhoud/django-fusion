# 🦀 Rust Backend — Overview

> The Rust backend is the core of the POS system — handling all database operations, authentication, and business logic via Tauri commands.

---

## Architecture

```
Vue Frontend
     │ invoke(command, args)
     ▼
Tauri Command Layer (lib.rs)
     │
     ▼
Operations Layer (25 CRUD modules)
     │
     ▼
Diesel ORM (SQLite)
```

---

## Files

| File | Purpose |
|------|---------|
| [`rust-backend.md`](../backend/rust-backend.md) | Overall backend architecture and Tauri commands |
| [`rust-database.md`](../backend/rust-database.md) | SQLite schema (29 tables), Diesel ORM setup, migrations |
| [`rust-data-flow.md`](../backend/rust-data-flow.md) | Data flow: Vue → Tauri → Rust → SQLite |
| [`rust-operations.md`](../backend/rust-operations.md) | 25 CRUD modules: auth, products, orders, inventory |
| [`rust-auth.md`](../backend/rust-auth.md) | Authentication: JWT, PIN code, role-based access |
| [`rust-seed-data.md`](../backend/rust-seed-data.md) | Seed data: products, categories, payment methods |

---

## Related

| Topic | Path |
|-------|------|
| Sidecar architecture | [`../sidecar/README.md`](../sidecar/README.md) |
| Cloud sync | [`../cloud/README.md`](../cloud/README.md) |
| POS database schema | [`../../databases/pos-schema.md`](../../databases/pos-schema.md) |
