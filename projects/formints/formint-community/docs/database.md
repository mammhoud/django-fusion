# Database — Formint

## Overview

Formint uses an **embedded SQLite** database managed via **Diesel ORM** migrations. The database file (`restaurant.db`) is created automatically on first launch and stored in the project root.

---

## Entity Relationship Diagram

> 💡 **Interactive ERD (Formint Standard edition):** the [interactive ERD with
> per-entity operations logic](../formint-standard/docs/erd/README.md) — searchable
> viewer (`docs/erd/index.html`) plus a printable/PDF export. This static ASCII
> diagram below is kept for quick reference.

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

See also: [Full interactive ERD + operations logic (40 tables, Formint Standard edition)](../formint-standard/docs/erd/README.md)

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
├── 2026-01-01-000000_create_all/
│   ├── up.sql      # Schema only — CREATE TABLE, TRIGGER, essential defaults
│   ├── down.sql    # DROP TABLE statements
│   └── seed.sql    # Unified seed data with section markers
├── 2026-07-17-000000_gaming_center_seed/
│   ├── up.sql      # Gaming center preset data (categories 11-16, products 51-76, …)
│   └── down.sql    # Reverts gaming data + resets settings to defaults
└── 2026-08-01-000000_coffee_shop_seed/
    ├── up.sql      # Coffee shop preset data (categories 17-21, products 77-108, …)
    └── down.sql    # Reverts coffee data + resets settings to defaults
```

### Schema vs Seed Separation

As of July 2026, the schema and seed data have been **separated**:

- **`up.sql`** — Contains ONLY schema definitions (CREATE TABLE, CREATE TRIGGER, ALTER TABLE) plus essential reference defaults (delivery_types, employee_types, recipe_types, roles, receipt_template). No demo data.
- **`seed.sql`** — Contains ALL demo/seed data in a **unified file** with **section markers** that the seed binary parses to select preset-specific data.

### Unified Seed Architecture

The `seed.sql` file uses section markers to organize data by preset:

```sql
-- [SECTION:shared]   — Data for ALL presets (suppliers, customers, tax_reports)
-- [SECTION:base]     — Restaurant demo data (categories 1-10, products 1-47, …)
-- [SECTION:gaming]   — Gaming center data (categories 11-16, products 51-76, …)
-- [SECTION:coffee]   — Coffee shop data (categories 17-21, products 77-108, …)
```

### How Presets Work

The seed binary (`src-tauri/src/bin/seed.rs`) parses the section markers and runs only the relevant sections based on the requested preset:

| Preset | Sections Seeded | Data |
|--------|-----------------|------|
| `all` | shared + gaming + coffee | Gaming center + coffee shop (comprehensive demo) |
| `base` | shared + base | Restaurant demo (47 products, 12 employees) |
| `gaming` | shared + gaming | Gaming center (26 products, 7 employees, USD) |
| `coffee` | shared + base + coffee | Restaurant + coffee shop (55 products total) |

### Seed Presets

```bash
make seed                  # PRESET=all (default — gaming + coffee)
make seed PRESET=base      # Base restaurant only
make seed PRESET=gaming    # Gaming lounge only
make seed PRESET=coffee    # Coffee shop only
```

### Seed Data by Preset

#### Section: shared (all presets)
- Suppliers (6), Customers (10), Tax Reports (3)

#### Section: base (restaurant)
- **Settings:** Restaurant defaults (Formint, PKR, Lahore address)
- **Categories:** 10 (Burgers, Pizza, BBQ, Biryani, Karahi, Fast Food, Beverages, Desserts, Chinese, Breakfast)
- **Products:** 47 menu items with prices ($1–$22)
- **Ingredients:** 55 stock items with levels and costs
- **Recipes:** 41 recipe mappings with 200+ ingredient lines
- **Employees:** 12 staff (Manager, Chefs, Waiters, Cashier, Drivers, Cleaner)
- **Sales:** 12 sample transactions with items (PKR)
- **Inventory Transactions:** 31 stock movements (purchase, usage, waste, adjustment)
- **Employee Schedules:** 12 shifts
- **Payrolls:** 8 bi-weekly records
- **Purchase Orders:** 6 orders with 22 line items

#### Section: gaming
- **Settings:** Level Up Gaming Center, USD currency, 10AM-2AM hours
- **Categories:** 6 (PS5, PS4, VR, Game Modes, Accessories, Snacks)
- **Products:** 26 (gaming sessions & snacks, $1–$45)
- **Employee Types:** 5 (Manager, Attendant, Cashier, Technician, Security)
- **Employees:** 7 ($2,600–$4,500/month)
- **Delivery Types:** 2 (Walk-in, Pre-booked)
- **Sales:** 20 transactions (USD)
- **Logo:** Gaming-themed SVG

#### Section: coffee
- **Settings:** The Daily Grind, PKR, 7AM-11PM hours
- **Categories:** 5 (Espresso, Teas, Pastries, Cold Brews, Signature)
- **Products:** 32 (coffee drinks & pastries, PKR 120–520)
- **Employee Types:** 3 (Barista, Pastry Chef, Shift Manager)
- **Employees:** 5
- **Sales:** 8 transactions (PKR)
- **Ingredients:** 14 (coffee-specific: espresso beans, matcha, syrups)
- **Inventory Transactions:** 10
- **Logo:** Coffee-themed SVG

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

### Seed Binary (`seed.rs`)

The standalone seed binary (`src-tauri/src/bin/seed.rs`) handles seeding:

```bash
# Via Make
make seed
make seed PRESET=coffee

# Direct
cargo run --manifest-path src-tauri/Cargo.toml --bin seed
PRESET=coffee cargo run --manifest-path src-tauri/Cargo.toml --bin seed
```

**Flow:**
1. Deletes existing database
2. Runs all Diesel migrations (creates schema)
3. Parses `seed.sql` section markers
4. Executes only the relevant sections for the chosen preset
5. Forces the correct `settings.restaurant_name` brand

### Additive Design

The seed binary always **deletes + recreates** the database before seeding, so fresh runs are always clean. As an additional safety net, most sections use `INSERT OR IGNORE` and `UPDATE ... WHERE`, making it safe to re-run specific sections on an already-seeded database without data duplication or constraint errors.
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

Default: `projects/formints/formintA/restaurant.db`

Override via `.env`:
```env
DATABASE_URL=custom/path/database.db
```
