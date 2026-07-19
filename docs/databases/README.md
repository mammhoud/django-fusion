# 🗄️ Databases

> Database architecture across all Structa Cloud projects — PostgreSQL for production, SQLite for development, and the 37-table POS schema.

---

## Architecture

```
                    ┌──────────────────────┐
                    │   PostgreSQL 16       │
                    │   (shared cluster)    │
                    │   :5432               │
                    └────┬─────┬─────┬─────┘
                         │     │     │
              ┌──────────┼─────┼─────┼──────────┐
              │          │     │     │          │
         db_ctc    db_lms  db_vresume  db_cypercloud
         (site 1)  (site 2) (site 3)   (site 4)
```

Each Django project uses its own database within the shared PostgreSQL cluster for production isolation.

---

## Per-Project Databases

| Project | DB Name | Engine (Prod) | Engine (Dev) |
|---------|---------|---------------|--------------|
| CTC Research | `db_ctc` | PostgreSQL 16 | SQLite |
| LMS | `db_lms` | PostgreSQL 16 | SQLite |
| Portfolio | `db_vresume` | PostgreSQL 16 | SQLite |
| Cypercloud | `db_cypercloud` | PostgreSQL 16 | SQLite |
| POS | `pos.db` | SQLite (embedded) | SQLite |

---

## POS Database Schema (37 Tables)

The POS application (`projects/pos/`) uses an embedded SQLite database managed by Diesel ORM (Rust):

### Core Domain
- `products` — Product catalog with variants
- `categories` — Product categorization
- `inventory` — Stock levels per product/variant
- `orders` — Sales orders with status tracking
- `order_items` — Line items per order
- `customers` — Customer profiles
- `payments` — Payment records per order

### Operations
- `warehouses` — Multi-warehouse support
- `stock_movements` — Inventory adjustments
- `suppliers` — Supplier management
- `purchase_orders` — Procurement tracking
- `registers` — Cash register sessions
- `register_transactions` — Open/close/float

### Settings & Config
- `settings` — Store configuration
- `tax_rates` — Tax rules
- `currencies` — Currency definitions
- `payment_methods` — Accepted payment types
- `discounts` — Discount rules

### See Full Schema

→ [`../projects/pos/rust-backend.md`](../projects/pos/rust-backend.md)

---

## Migrations

Django migrations are managed per-project:

```bash
cd projects
make migrate WEBSITE=lms          # Run LMS migrations
make makemigrations WEBSITE=lms   # Create new migrations
```

POS migrations are handled by Diesel:

```bash
cd projects/pos/pos-full
diesel migration run
```

---

## Backups

```bash
# PostgreSQL dump
docker exec postgres pg_dump -U postgres db_lms > lms_backup.sql

# POS SQLite backup (just copy the file)
cp projects/pos/pos-full/pos.db backups/pos_backup_$(date +%Y%m%d).db
```

---

## Related

| Topic | Path |
|-------|------|
| POS Rust backend | [`../projects/pos/rust-backend.md`](../projects/pos/rust-backend.md) |
| Backend env | [`../back-env/`](../back-env/) |
| Infrastructure | [`../infrastructure/`](../infrastructure/) |
| Repo overview | [`../repo-overview.md`](../repo-overview.md) |
