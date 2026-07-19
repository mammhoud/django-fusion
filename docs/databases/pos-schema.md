# 🗄️ POS Database — Full Schema Reference

> Complete database schema for the POS application built with Rust, Diesel ORM, and SQLite.
>
> <!-- Schema snapshot: July 2026, POS Full Edition. Auto-generated from `diesel print-schema`. Verify against latest migrations before relying on this for development. -->

---

## Architecture

```
┌─────────────────────────────────────┐
│         POS Client (Vue 3)          │
│         Tauri Desktop Shell          │
└────────────┬────────────────────────┘
             │ Tauri invoke()
┌────────────▼────────────────────────┐
│       Rust Backend (Diesel ORM)      │
│  ┌─────────────────────────────────┐│
│  │  db/schema.rs  ← auto-generated  ││
│  │  db/models.rs  ← Rust structs    ││
│  │  db/operations/ ← CRUD per table ││
│  └─────────────────────────────────┘│
└────────────┬────────────────────────┘
             │ SQLite
┌────────────▼────────────────────────┐
│            pos.db (SQLite)           │
│          ~/AppData/pos/             │
└─────────────────────────────────────┘
```

---

## Connection Management

```rust
// db/mod.rs — Connection lifecycle
use diesel::sqlite::SqliteConnection;
use diesel::prelude::*;

pub fn get_db_path() -> PathBuf {
    // 1. Check DATABASE_URL env var
    // 2. Fall back to app data directory
    let app_dir = dirs::data_dir()
        .unwrap()
        .join("com.structa.pos");
    std::fs::create_dir_all(&app_dir).ok();
    app_dir.join("pos.db")
}

pub fn open_conn() -> SqliteConnection {
    let path = get_db_path();
    SqliteConnection::establish(&path.to_string_lossy())
        .expect("Failed to open database")
}

pub fn run_migrations(conn: &mut SqliteConnection) {
    // Embedded migrations at compile time
    embedded_migrations::run(conn)
        .expect("Failed to run migrations");
}
```

---

## Table Reference (29 Tables)

### 🔐 Auth & Users

```sql
-- users: System users (cashiers, managers, admins)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR NOT NULL UNIQUE,
    password_hash VARCHAR NOT NULL,
    full_name VARCHAR NOT NULL,
    pin_code VARCHAR(6),           -- Quick login PIN
    role VARCHAR NOT NULL DEFAULT 'cashier',
    is_active BOOLEAN NOT NULL DEFAULT 1,
    last_login TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- roles: Role definitions
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL UNIQUE,
    permissions TEXT NOT NULL       -- JSON array of permissions
);

-- user_roles: Many-to-many user ↔ role
CREATE TABLE user_roles (
    user_id INTEGER NOT NULL REFERENCES users(id),
    role_id INTEGER NOT NULL REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);
```

### 📦 Products & Inventory

```sql
-- categories: Product categorization (nested)
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    slug VARCHAR NOT NULL UNIQUE,
    parent_id INTEGER REFERENCES categories(id),
    sort_order INTEGER NOT NULL DEFAULT 0,
    image_url VARCHAR,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

-- products: Core product catalog
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku VARCHAR UNIQUE,             -- Stock Keeping Unit
    barcode VARCHAR UNIQUE,         -- UPC/EAN barcode
    name VARCHAR NOT NULL,
    slug VARCHAR NOT NULL UNIQUE,
    description TEXT,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    unit VARCHAR NOT NULL DEFAULT 'piece',  -- piece, kg, liter
    price DECIMAL(10,2) NOT NULL,   -- Selling price
    cost DECIMAL(10,2),             -- Purchase cost
    tax_rate_id INTEGER REFERENCES tax_rates(id),
    image_url VARCHAR,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- product_variants: Size/color/etc.
CREATE TABLE product_variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(id),
    sku VARCHAR UNIQUE,
    barcode VARCHAR UNIQUE,
    name VARCHAR NOT NULL,          -- e.g., "Large, Red"
    price_adjustment DECIMAL(10,2) NOT NULL DEFAULT 0,
    attributes TEXT NOT NULL        -- JSON: {"size":"L","color":"red"}
);

-- inventory: Stock levels per warehouse
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(id),
    variant_id INTEGER REFERENCES product_variants(id),
    warehouse_id INTEGER NOT NULL REFERENCES warehouses(id),
    quantity DECIMAL(10,3) NOT NULL DEFAULT 0,
    low_stock_threshold DECIMAL(10,3),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, variant_id, warehouse_id)
);
```

### 🛒 Orders & Sales

```sql
-- orders: Sales transactions
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number VARCHAR NOT NULL UNIQUE,  -- e.g., "ORD-20260719-0001"
    customer_id INTEGER REFERENCES customers(id),
    register_id INTEGER NOT NULL REFERENCES registers(id),
    user_id INTEGER NOT NULL REFERENCES users(id),  -- Cashier
    status VARCHAR NOT NULL DEFAULT 'pending',
        -- pending, completed, cancelled, refunded
    subtotal DECIMAL(10,2) NOT NULL,
    tax_total DECIMAL(10,2) NOT NULL DEFAULT 0,
    discount_total DECIMAL(10,2) NOT NULL DEFAULT 0,
    grand_total DECIMAL(10,2) NOT NULL,
    payment_method_id INTEGER REFERENCES payment_methods(id),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- order_items: Line items per order
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    variant_id INTEGER REFERENCES product_variants(id),
    quantity DECIMAL(10,3) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    tax_rate DECIMAL(5,2) NOT NULL DEFAULT 0,
    discount_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    total DECIMAL(10,2) NOT NULL
);

-- customers: Customer profiles
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    email VARCHAR,
    phone VARCHAR,
    address TEXT,
    loyalty_points INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 💰 Payments

```sql
-- payment_methods: Accepted payment types
CREATE TABLE payment_methods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,          -- Cash, Card, Mada, STC Pay
    type VARCHAR NOT NULL,          -- cash, card, digital_wallet
    is_active BOOLEAN NOT NULL DEFAULT 1,
    settings TEXT                   -- JSON: terminal config
);

-- payments: Payment records
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    method_id INTEGER NOT NULL REFERENCES payment_methods(id),
    amount DECIMAL(10,2) NOT NULL,
    reference VARCHAR,              -- Card transaction ID
    status VARCHAR NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- refunds: Refund transactions
CREATE TABLE refunds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    payment_id INTEGER NOT NULL REFERENCES payments(id),
    amount DECIMAL(10,2) NOT NULL,
    reason VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 🏪 Operations

```sql
-- warehouses: Multi-warehouse/location support
CREATE TABLE warehouses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    code VARCHAR NOT NULL UNIQUE,   -- WH-001
    address TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

-- stock_movements: Inventory adjustments
CREATE TABLE stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(id),
    variant_id INTEGER REFERENCES product_variants(id),
    warehouse_id INTEGER NOT NULL REFERENCES warehouses(id),
    movement_type VARCHAR NOT NULL,
        -- purchase, sale, return, adjustment, transfer_in, transfer_out
    quantity DECIMAL(10,3) NOT NULL,
    reference_id INTEGER,           -- Order or PO ID
    notes TEXT,
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- registers: Cash register sessions
CREATE TABLE registers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    warehouse_id INTEGER NOT NULL REFERENCES warehouses(id),
    is_active BOOLEAN NOT NULL DEFAULT 1
);

-- register_sessions: Open/close tracking
CREATE TABLE register_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    register_id INTEGER NOT NULL REFERENCES registers(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    opened_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    opening_balance DECIMAL(10,2) NOT NULL DEFAULT 0,
    closing_balance DECIMAL(10,2),
    expected_cash DECIMAL(10,2),
    actual_cash DECIMAL(10,2),
    difference DECIMAL(10,2)
);
```

### 🔧 Settings & Config

```sql
-- settings: Store configuration (key-value)
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR NOT NULL UNIQUE,
    value TEXT NOT NULL,
    description VARCHAR,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Common settings keys:
--   store.name, store.currency, store.timezone
--   store.receipt_header, store.receipt_footer
--   tax.default_rate, tax.number
--   receipt.logo_url, receipt.show_barcode
--   cloud.sync_enabled, cloud.sync_interval

-- tax_rates: Tax definitions
CREATE TABLE tax_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,          -- VAT, GST, Sales Tax
    rate DECIMAL(5,2) NOT NULL,     -- 0.15 = 15%
    is_default BOOLEAN NOT NULL DEFAULT 0
);

-- discounts: Discount rules
CREATE TABLE discounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    type VARCHAR NOT NULL,          -- percentage, fixed
    value DECIMAL(10,2) NOT NULL,
    min_order_amount DECIMAL(10,2),
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

-- suppliers: Supplier management
CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    contact_person VARCHAR,
    email VARCHAR,
    phone VARCHAR,
    address TEXT,
    notes TEXT
);

-- purchase_orders: Procurement
CREATE TABLE purchase_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
    warehouse_id INTEGER NOT NULL REFERENCES warehouses(id),
    status VARCHAR NOT NULL DEFAULT 'draft',
        -- draft, sent, received, cancelled
    expected_date DATE,
    notes TEXT,
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

## Rust Model Example

```rust
// db/models.rs
use diesel::prelude::*;
use serde::{Serialize, Deserialize};

#[derive(Queryable, Selectable, Serialize, Deserialize, Debug)]
#[diesel(table_name = crate::db::schema::products)]
#[diesel(check_for_backend(diesel::sqlite::Sqlite))]
pub struct Product {
    pub id: i32,
    pub sku: Option<String>,
    pub barcode: Option<String>,
    pub name: String,
    pub slug: String,
    pub description: Option<String>,
    pub category_id: i32,
    pub unit: String,
    pub price: f64,
    pub cost: Option<f64>,
    pub tax_rate_id: Option<i32>,
    pub image_url: Option<String>,
    pub is_active: bool,
    pub created_at: chrono::NaiveDateTime,
    pub updated_at: chrono::NaiveDateTime,
}

#[derive(Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::products)]
pub struct NewProduct {
    pub sku: Option<String>,
    pub barcode: Option<String>,
    pub name: String,
    pub slug: String,
    pub category_id: i32,
    pub price: f64,
    pub cost: Option<f64>,
}
```

---

## Seed Data

```json
// sidecar/posapp/fixtures/seed_data.json (example)
{
  "categories": [
    {"name": "Beverages", "slug": "beverages"},
    {"name": "Snacks", "slug": "snacks"},
    {"name": "Dairy", "slug": "dairy"}
  ],
  "products": [
    {
      "sku": "BEV-001",
      "name": "Water 500ml",
      "slug": "water-500ml",
      "category": "beverages",
      "price": 1.00,
      "cost": 0.50,
      "unit": "piece"
    }
  ],
  "payment_methods": [
    {"name": "Cash", "type": "cash"},
    {"name": "Card", "type": "card"},
    {"name": "Mada", "type": "card"},
    {"name": "STC Pay", "type": "digital_wallet"}
  ]
}
```

---

## Edition Differences

| Feature | Minimal | Solo | Full |
|---------|:---:|:---:|:---:|
| Products | ✅ | ✅ | ✅ |
| Categories | ✅ | ✅ | ✅ |
| Inventory | ❌ | ✅ | ✅ |
| Orders | ✅ | ✅ | ✅ |
| Customers | ❌ | ✅ | ✅ |
| Payments | ✅ (Cash) | ✅ | ✅ |
| Warehouses | ❌ | ❌ | ✅ |
| Stock Movements | ❌ | ❌ | ✅ |
| Suppliers | ❌ | ❌ | ✅ |
| Purchase Orders | ❌ | ❌ | ✅ |
| Registers | ❌ | ✅ | ✅ |
| Tax Rates | ❌ | ✅ | ✅ |
| Discounts | ❌ | ✅ | ✅ |
| Cloud CRM Sync | ❌ | ✅ | ✅ |

---

## Related

| Topic | Path |
|-------|------|
| POS Rust backend | [`../projects/pos/backend/rust-backend.md`](../projects/pos/backend/rust-backend.md) |
| POS infrastructure | [`../projects/pos/infrastructure.md`](../projects/pos/infrastructure.md) |
| POS editions | [`../projects/pos/editions.md`](../projects/pos/editions.md) |
| Database overview | [`README.md`](README.md) |
