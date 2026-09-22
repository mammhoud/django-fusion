# 🦀 Rust Backend — Overview

> The Rust backend is the core of the desktop POS editions (Community /
> Standard) — handling all database operations, authentication, and business
> logic via Tauri commands. Pro/Cloud serve their APIs from Django instead.

---

## Architecture

```
React / Vue Frontend
     │ invoke(command, args)
     ▼
Tauri Command Layer (lib.rs)
     │
     ▼
Operations Layer (25+ CRUD modules)
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
| Sidecar architecture (archived) | [`../sidecar/README.md`](../sidecar/README.md) |
| Cloud edition | [`../cloud-edition.md`](../cloud-edition.md) |
| POS database schema | [`../../databases/pos-schema.md`](../../databases/pos-schema.md) |
