# Database — Forge POS

## Overview

Forge POS uses an **embedded SQLite** database managed via **Diesel ORM** migrations. The database file (`restaurant.db`) is created automatically on first launch and stored in the project root.

---

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────┐       ┌───────────────┐
│  settings   │       │  categories  │       │  products     │
│─────────────│       │──────────────│       │───────────────│
│ PK id=1     │       │ PK id        │──┐    │ PK id         │
│ restaurant  │       │ name (UNIQUE)│  └───>│ category_id   │
│ address     │       │ created_at   │       │ name          │
│ phone       │       │ updated_at   │       │ price         │
│ email       │       └──────────────┘       │ unit          │
│ tax_rate    │                              │ image         │
│ currency    │                              │ product_type  │
│ logo        │                              │ border_color  │
│ delivery_*  │                              │ uploaded      │
│ dine_in_*   │                              └───────────────┘
└─────────────┘                                    │
                                                   │ 1
       ┌───────────────────────────────────────────┘
       │
       ▼
┌──────────────┐       ┌─────────────────┐       ┌──────────────────┐
│ sales        │       │ sale_items      │       │ recipes          │
│──────────────│       │─────────────────│       │──────────────────│
│ PK id        │──┐    │ PK id           │       │ PK id            │
│ total_amount │  │    │ FK sale_id      │       │ FK product_id    │
│ currency     │  └───>│ product_name    │       │ FK recipe_type_id│
│ date         │       │ price           │       │ yield_quantity   │
│ time         │       │ quantity        │       │ is_active        │
│ order_type   │       │ unit            │       │ uploaded         │
│ status       │       │ subtotal(GENERATED)   │──────────────────│
│ table_number │       └─────────────────┘       │         │
│ delivery_*   │                                  │         │
│ employee_id  │                                  │         │
└──────────────┘                                  │         │
                                                  │ 1       │ 1
                                                  │         │
                                                  ▼         ▼
                                        ┌──────────────┐  ┌──────────────┐
                                        │recipe_       │  │ recipe_types │
                                        │ingredients   │  │──────────────│
                                        │──────────────│  │ PK id        │
                                        │ PK id        │  │ name (UNIQUE)│
                                        │ FK recipe_id │  │ description  │
                                        │ FK ingredient│  │ is_active    │
                                        │    _id       │  └──────────────┘
                                        │ quantity     │
                                        │ unit         │
                                        │ prep_note    │
                                        └──────────────┘
                                              │
                                              │ *
                                              ▼
┌──────────────┐       ┌─────────────────┐  ┌──────────────────┐
│ ingredients  │       │ inventory_      │  │ inventory_       │
│──────────────│       │ transactions    │  │ adjustments      │
│ PK id        │──┐    │─────────────────│  │──────────────────│
│ name (UNIQUE)│  │    │ PK id           │  │ PK id            │
│ unit         │  └───>│ FK ingredient_id│  │ FK ingredient_id │
│ current_qty  │       │ transaction_type│  │ previous_qty     │
│ reorder_level│       │ quantity_change │  │ new_qty          │
│ reorder_qty  │       │ reference_id    │  │ reason           │
│ cost_per_unit│       │ note            │  │ created_by       │
│ is_active    │       │ uploaded        │  │ uploaded         │
│ uploaded     │       └─────────────────┘  └──────────────────┘
└──────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ employees    │    │ employee_    │    │ delivery_    │
│──────────────│    │ types        │    │ types        │
│ PK id        │───>│──────────────│    │──────────────│
│ name         │    │ PK id        │    │ PK id        │
│ phone        │    │ name (UNIQUE)│    │ name (UNIQUE)│
│ email        │    │ description  │    │ fee_multiplr │
│ employee_    │    │ is_active    │    │ is_active    │
│   type_id    │    └──────────────┘    └──────────────┘
│ salary       │
│ is_active    │    ┌──────────────┐    ┌──────────────┐
│ joined_at    │    │ employee_    │    │ payrolls     │
│ uploaded     │    │ schedules    │    │──────────────│
└──────────────┘    │──────────────│    │ PK id        │
                    │ PK id        │    │ FK employee  │
┌──────────────┐    │ FK employee  │    │ period_start │
│ customers    │    │ shift_start  │    │ period_end   │
│──────────────│    │ shift_end    │    │ regular_hrs  │
│ PK id        │    │ status       │    │ overtime_hrs │
│ name         │    │ notes        │    │ total_pay    │
│ phone        │    └──────────────┘    │ status       │
│ email        │                        └──────────────┘
│ loyalty_pts  │
│ notes        │    ┌──────────────┐    ┌──────────────┐
│ uploaded     │    │ suppliers    │    │ purchase_    │
└──────────────┘    │──────────────│    │ orders       │
                    │ PK id        │    │──────────────│
┌──────────────┐    │ name         │───>│ PK id        │
│ roles        │    │ contact_name │    │ FK supplier  │
│──────────────│    │ phone        │    │ total_amount │
│ PK id        │    │ email        │    │ status       │
│ name         │    │ tax_id       │    │ notes        │
│ permissions  │    │ payment_terms│    └──────────────┘
│ is_active    │    │ is_active    │
└──────────────┘    └──────────────┘
```

---

## Table Reference

### `settings` (Singleton)

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| `id` | INTEGER PK | `1` (CHECK) | Singleton row enforced by CHECK constraint |
| `restaurant_name` | TEXT | — | Restaurant display name |
| `address` | TEXT | — | Physical address |
| `phone` | TEXT | — | Contact phone |
| `email` | TEXT | — | Contact email |
| `tax_rate` | TEXT | — | Tax percentage (stored as text for formatting) |
| `currency` | TEXT | `'PKR'` | Default currency code |
| `opening_time` | TEXT | — | Business opening time |
| `closing_time` | TEXT | — | Business closing time |
| `receipt_footer` | TEXT | — | Custom message on receipts |
| `logo` | TEXT | — | Base64-encoded logo image |
| `dine_in_tables` | INTEGER | `0` | Number of dine-in tables |
| `delivery_fee` | REAL | `0.0` | Flat delivery fee |
| `delivery_fee_per_km` | REAL | `0.0` | Per-km delivery surcharge |

### `categories`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `name` | TEXT | UNIQUE NOT NULL |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### `products`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `name` | TEXT | NOT NULL |
| `price` | REAL | NOT NULL |
| `unit` | TEXT | NOT NULL DEFAULT 'item' |
| `category_id` | INTEGER | REFERENCES `categories(id)` ON DELETE SET NULL |
| `image` | TEXT | — |
| `product_type` | TEXT | NOT NULL DEFAULT 'product' |
| `border_color` | TEXT | — |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| `uploaded` | BOOLEAN | DEFAULT 0 |

### `sales`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `total_amount` | REAL | NOT NULL |
| `currency` | TEXT | NOT NULL |
| `date` | TEXT | DEFAULT (date('now')) |
| `time` | TEXT | DEFAULT (time('now')) |
| `order_type` | TEXT | DEFAULT 'dine_in' |
| `status` | TEXT | DEFAULT 'completed' |
| `table_number` | INTEGER | — |
| `delivery_type_id` | INTEGER | REFERENCES `delivery_types(id)` |
| `delivery_address` | TEXT | — |
| `employee_id` | INTEGER | REFERENCES `employees(id)` |

### `sale_items`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `sale_id` | INTEGER | NOT NULL REFERENCES `sales(id)` ON DELETE CASCADE |
| `product_name` | TEXT | NOT NULL |
| `price` | REAL | NOT NULL |
| `quantity` | REAL | NOT NULL |
| `unit` | TEXT | NOT NULL |
| `subtotal` | REAL | GENERATED ALWAYS AS (price * quantity) STORED |

### `ingredients`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `name` | TEXT | UNIQUE NOT NULL |
| `unit` | TEXT | NOT NULL |
| `current_quantity` | REAL | DEFAULT 0.0 |
| `reorder_level` | REAL | DEFAULT 0.0 |
| `reorder_quantity` | REAL | DEFAULT 0.0 |
| `cost_per_unit` | REAL | DEFAULT 0.0 |
| `is_active` | BOOLEAN | DEFAULT 1 |

### `inventory_transactions`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `ingredient_id` | INTEGER | NOT NULL REFERENCES `ingredients(id)` ON DELETE CASCADE |
| `transaction_type` | TEXT | CHECK IN ('purchase', 'usage', 'waste', 'adjustment', 'return', 'goods_transfer') |
| `quantity_change` | REAL | NOT NULL (positive = addition, negative = removal) |
| `reference_id` | INTEGER | — |
| `note` | TEXT | — |

### `recipes`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `product_id` | INTEGER | NOT NULL REFERENCES `products(id)` ON DELETE CASCADE |
| `recipe_type_id` | INTEGER | NOT NULL REFERENCES `recipe_types(id)` |
| `yield_quantity` | REAL | DEFAULT 1.0 |
| `is_active` | BOOLEAN | DEFAULT 1 |
| | | UNIQUE(product_id, recipe_type_id) |

### `employees`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `name` | TEXT | NOT NULL |
| `phone` | TEXT | — |
| `email` | TEXT | — |
| `employee_type_id` | INTEGER | NOT NULL REFERENCES `employee_types(id)` |
| `salary` | REAL | DEFAULT 0.0 |
| `is_active` | BOOLEAN | DEFAULT 1 |
| `joined_at` | TEXT | DEFAULT (date('now')) |

---

## Triggers

All tables with `updated_at` columns have an `AFTER UPDATE` trigger:

```sql
CREATE TRIGGER IF NOT EXISTS update_products_updated_at 
AFTER UPDATE ON products
BEGIN 
  UPDATE products SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; 
END;
```

---

## Migrations

Migrations are managed via Diesel in `src-tauri/migrations/`.

### File Structure

```
src-tauri/migrations/
└── 2026-01-01-000000_create_all/
    ├── up.sql      # Full schema + seed data
    └── down.sql    # DROP TABLE statements
```

### Running Migrations

```bash
# Apply all migrations
cd src-tauri
diesel migration run

# Revert last migration
diesel migration revert

# Redo migration
diesel migration redo
```

### Seed Data

The `up.sql` migration includes comprehensive seed data with:

- **Settings:** Restaurant defaults (name, address, tax rate, etc.)
- **Categories:** 10 menu categories (Burgers, Pizza, BBQ, Biryani, etc.)
- **Products:** 47 menu items with prices
- **Ingredients:** 55 ingredients with stock levels and costs
- **Recipes:** 41 recipes with ingredient mappings
- **Employees:** 12 sample staff members
- **Sales:** 12 sample transactions with sale items
- **Inventory Transactions:** 30+ stock movements

### Seed Presets

```bash
make seed                  # Full seed (all data)
make seed PRESET=base      # Base restaurant preset (47 products)
make seed PRESET=gaming    # Gaming lounge preset
make seed PRESET=coffee    # Coffee shop preset
```

---

## Database Maintenance

### Backup

```bash
cp restaurant.db restaurant.db.backup
```

### Reset

```bash
make seed                  # Delete + remigrate + reseed
make clean-db              # Delete database file only
```

### File Location

Default: `forge-pos/restaurant.db`

Override via `.env`:
```env
DATABASE_URL=custom/path/database.db
```
