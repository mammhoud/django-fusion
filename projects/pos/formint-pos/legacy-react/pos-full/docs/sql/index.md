# SQL / Migration Docs — POS Full

> **Directory:** `docs/sql/`
> **Dialect:** SQLite 3.42+
> **ORM:** Diesel (Rust) + Django ORM (Python sidecar)
> **Project:** `projects/pos/pos-full/`

---

## Migration Conventions

### Diesel Migrations (Rust)
```
src-tauri/migrations/YYYY-MM-DD-HHMMSS_description/
├── up.sql       # Forward migration
└── down.sql     # Rollback (optional)
```

### Django ORM Migrations (Python sidecar)
```bash
cd sidecar && python manage.py makemigrations && python manage.py migrate
```

## Safe Migration Patterns

```sql
-- Add column (idempotent)
ALTER TABLE products ADD COLUMN IF NOT EXISTS border_color TEXT;

-- Create table (idempotent)
CREATE TABLE IF NOT EXISTS new_table (...);

-- Add index
CREATE INDEX IF NOT EXISTS idx_name ON table(column);
```

## Key Tables

| Table | Purpose | Managed By |
|-------|---------|------------|
| `products` | Menu items / products | Django ORM + Diesel |
| `categories` | Product categories | Django ORM + Diesel |
| `customers` | Customer records | Django ORM + Diesel |
| `sales` | Sale transactions | Django ORM + Diesel |
| `sale_items` | Individual sale line items | Django ORM + Diesel |

See `../PROMPTS.md#sql-prompts` for code generation templates.
