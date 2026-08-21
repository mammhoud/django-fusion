# Server Migration Guide

> **Diesel → Django ORM:** Moving from Minimal's Rust/Diesel backend to Solo/Full's Python server with Django ORM.

## Overview

The Structa POS stack has two database backends that serve different editions:

| Edition | Database Layer | ORM | Language |
|---------|---------------|-----|----------|
| **Minimal** | Rust + Diesel | `diesel::sqlite` | Rust (compiled) |
| **Solo** | Python server + Django ORM | `django.db.models` | Python (interpreted) |
| **Full** | Python server + Django ORM | `django.db.models` | Python (interpreted) |

When upgrading a Minimal installation to Solo (or Full), the database must be migrated from Diesel's schema to Django ORM's schema. This document covers the architecture, table mapping, migration script, and dev workflow changes required.

---

## Architecture Comparison

### Before (Minimal — Rust/Diesel)

```
┌─────────────────────────────────────────────┐
│                  React UI                    │
├─────────────────────────────────────────────┤
│             Tauri IPC (invoke)               │
├─────────────────────────────────────────────┤
│         Rust Backend (all CRUD)              │
│  ┌───────────┐  ┌────────────────────────┐  │
│  │ Hardware  │  │   Diesel ORM CRUD      │  │
│  │ (printer, │  │   (products, sales,    │  │
│  │  drawer)  │  │   customers, etc.)     │  │
│  └───────────┘  └────────┬───────────────┘  │
│                          │                   │
│                    ┌─────▼──────┐            │
│                    │  SQLite DB │            │
│                    │restaurant.db│           │
│                    └────────────┘            │
└─────────────────────────────────────────────┘
```

### After (Solo/Full — Server Django ORM)

```
┌─────────────────────────────────────────────────┐
│                   React UI                       │
├──────────┬──────────────────────────────────────┤
│ Tauri IPC│    HTTP REST + WebSocket (:8765)      │
├──────────▼──────────────────────────────────────┤
│     Rust Backend (native only)                  │
│  ┌────────────────────┐  ┌───────────────────┐  │
│  │ Hardware (printer, │  │ Server lifecycle │  │
│  │  cash drawer,      │  │ (start/stop,      │  │
│  │  file I/O, dialogs)│  │  health check)    │  │
│  └────────────────────┘  └───────────────────┘  │
├─────────────────────────────────────────────────┤
│          Python Server (primary data layer)     │
│  ┌──────────────────────────────────────────┐   │
│  │  Robyn HTTP Server (:8765)               │   │
│  │  ┌──────────────────────────────────┐    │   │
│  │  │  Django ORM (all CRUD)          │    │   │
│  │  │  ┌───────────┐ ┌─────────────┐ │    │   │
│  │  │  │ POS models │ │ HR/Finance │ │    │   │
│  │  │  │ (products, │ │ (payroll,  │ │    │   │
│  │  │  │  sales,    │ │  schedules)│ │    │   │
│  │  │  │  customers)│ └─────────────┘ │    │   │
│  │  │  └───────────┘ ┌─────────────┐ │    │   │
│  │  │                │ Sync/Config │ │    │   │
│  │  │                │ (node reg,  │ │    │   │
│  │  │                │  cloud link)│ │    │   │
│  │  │                └─────────────┘ │    │   │
│  │  └──────────────────────────────────┘    │   │
│  └──────────────────────────────────────────┘   │
│                      │                            │
│                ┌──────▼──────┐                    │
│                │  SQLite DB  │                    │
│                │restaurant.db│                    │
│                │ (managed by │                    │
│                │  Django ORM)│                    │
│                └─────────────┘                    │
└──────────────────────────────────────────────────┘
```

---

## What Moves to the Server vs What Stays in Rust

### Operations That Move to the Server (Django ORM)

All Diesel-backed CRUD operations move to the Python server. The React frontend communicates with the server over HTTP REST (port 8765) instead of Tauri IPC for these operations:

> **Sync-tracking note:** Every Django model in the server has `is_synced`, `sync_status`, and `synced_at` fields. When migrating data from Diesel, mark all imported records as `is_synced=True`, `sync_status="synced"` to prevent the server from attempting to push historic records to the cloud. Fresh records created after migration will use the normal pending-sync flow.

| Rust Module | Operation | Server Endpoint |
|-------------|-----------|-----------------|
| `products` | CRUD + mark_uploaded | `GET/POST/PUT/DELETE /api/products` |
| `categories` | CRUD | `GET/POST/PUT /api/categories` |
| `sales` | CRUD + mark_uploaded | `GET/POST/PUT/DELETE /api/sales` |
| `transactions` | List, delete | `GET/DELETE /api/transactions` |
| `settings` | Get, save | `GET/PUT /api/settings` |
| `analytics` | Aggregate queries | `GET /api/analytics` |
| `ingredients` | CRUD + soft delete | `GET/POST/PUT/DELETE /api/ingredients` |
| `recipes` | CRUD + soft delete | `GET/POST/PUT/DELETE /api/recipes` |
| `inventory_transactions` | CRUD | `GET/POST /api/inventory/transactions` |
| `delivery_types` | CRUD + soft delete | `GET/POST/PUT/DELETE /api/delivery-types` |
| `employee_types` | CRUD + soft delete | `GET/POST/PUT/DELETE /api/employee-types` |
| `employees` | CRUD + soft delete | `GET/POST/PUT/DELETE /api/employees` |
| `customers` | CRUD + loyalty | `GET/POST/PUT/DELETE /api/customers` |
| `suppliers` | CRUD + soft delete | `GET/POST/PUT/DELETE /api/suppliers` |
| `purchase_orders` | CRUD with items | `GET/POST/PUT/DELETE /api/purchase-orders` |
| `kitchen_tickets` | CRUD | `GET/POST/PUT/DELETE /api/kitchen-tickets` |
| `receipt_templates` | CRUD | `GET/POST/PUT/DELETE /api/receipt-templates` |
| `tax_reports` | CRUD | `GET/POST/DELETE /api/tax-reports` |
| `employee_schedules` | CRUD | `GET/POST/PUT/DELETE /api/employee-schedules` |
| `payrolls` | CRUD | `GET/POST/PUT/DELETE /api/payrolls` |
| `report_metadata` | CRUD | `GET/POST/DELETE /api/report-metadata` |
| `auth` | Login, account setup | `POST /api/auth/login`, `POST /api/auth/register` |
| `roles` | CRUD + user assignment | `GET/POST/PUT/DELETE /api/roles` |
| `dump` | Export data | `GET /api/export` |

### Operations That Stay in Rust (Native Only)

These remain as Tauri `invoke()` commands because they require native OS access:

| Rust Module | Operation | Reason to Stay |
|-------------|-----------|----------------|
| `hardware` | Thermal printer (ESC/POS) | Serial/USB port access |
| `hardware` | Cash drawer kick | Hardware I/O via RJ12 connector |
| `server` | Start/stop Python server | Process lifecycle management |
| `lib.rs` | `export_database_cmd` | File I/O (base64 encode/decode) |
| `lib.rs` | `import_database_cmd` | File I/O (write to disk) |
| `lib.rs` | Window state save/load | OS window manager API |
| `lib.rs` | Environment loading | File system access at startup |

---

## Diesel → Django ORM Table Mapping

### Core Tables

| Diesel Table (Minimal) | Django Model (Solo/Full Server) | Django Table | Match |
|------------------------|-----------------------------------|-------------|-------|
| `categories` | `Category` | `full_categories` | ✅ Close |
| `products` | `Product` | `full_products` | ⚠️ Differs |
| `sales` | `Sale` | `full_sales` | ⚠️ Differs |
| `sale_items` | `SaleItem` | `full_sale_items` | ✅ Close |
| `customers` | `Customer` | `full_customers` | ⚠️ Differs |
| `employees` | `Employee` | `full_employees` | ⚠️ Differs |
| `ingredients` | `Ingredient` | `full_ingredients` | ✅ Close |
| `recipes` | `Recipe` | `full_recipes` | ⚠️ Differs |
| `suppliers` | `Supplier` | `full_suppliers` | ✅ Close |
| `purchase_orders` | `PurchaseOrder` | `full_purchase_orders` | ⚠️ Differs |
| `purchase_order_items` | `PurchaseOrderItem` | `full_purchase_order_items` | ✅ Close |
| `kitchen_tickets` | `KitchenTicket` | `full_kitchen_tickets` | ✅ Close |
| `receipt_templates` | `ReceiptTemplate` | `full_receipt_templates` | ⚠️ Differs |
| `inventory_transactions` | `InventoryTransaction` | `full_inventory` | ⚠️ Differs |
| `inventory_adjustments` | `InventoryAdjustment` | `full_inventory_adjustments` | ⚠️ Differs |
| `roles` | `Role` | `full_roles` | ⚠️ Differs |
| `employees` + `employee_schedules` | `EmployeeSchedule` | `full_employee_schedules` | ✅ Close |
| `payrolls` | `Payroll` | `full_payroll` | ⚠️ Differs |
| `users` | — (handled by allauth) | — | ❌ New system |
| `user_roles` | — (handled by allauth groups) | — | ❌ New system |
| `tax_reports` | — (not in server) | — | ❌ No model yet |
| `report_metadata` | — (not in server) | — | ❌ No model yet |
| `delivery_types` | — (not in server) | — | ❌ No model yet |
| `employee_types` | — (not in server) | — | ❌ No model yet |
| `loyalty_transactions` | — (handled by Customer model) | — | 🟡 Integrated |
| `inventory_alerts` | — (not in server) | — | ❌ No model yet |
| `settings` | `DeviceConfig` | `full_device_configs` | ⚠️ Different approach |
| `recipe_ingredients` | — (merged into Recipe) | — | 🟡 Integrated |
| `recipe_types` | — (not in server) | — | ❌ No model yet |

### Tables in Server With No Diesel Equivalent (Solo/Full Only)

These tables exist only in the Server's Django ORM. They have no corresponding Diesel table and do not need migration from Minimal:

| Django Table | Model File | Purpose |
|-------------|-----------|---------|
| `full_menu_items` | `models/menu.py` | Menu item catalog |
| `full_menus` | `models/menu.py` | Named menu collections |
| `full_menu_assignments` | `models/menu.py` | Menu-item link table |
| `full_nodes` | `models/node.py` | Registered POS nodes |
| `full_heartbeats` | `models/node.py` | Node heartbeat log |
| `full_node_events` | `models/node.py` | Node lifecycle events |
| `full_device_configs` | `models/config.py` | Device configuration KV |
| `full_master_devices` | `models/config.py` | Master device registry |
| `full_cloud_links` | `models/config.py` | Cloud connection config |
| `full_sync_logs` | `models/sync.py` | Data sync audit log |
| `full_notes` | `models/notes.py` | User notes with draft |
| `full_support_tickets` | `models/ops.py` | Support ticket system |

---

## Field-Level Mapping (Key Differences)

### `Product`

| Diesel Field | Type | Django Field | Type | Notes |
|-------------|------|-------------|------|-------|
| `id` | `Integer` | `id` | `BigAutoField` | Auto-generated |
| `name` | `Text` | `name` | `CharField(200)` | Same |
| `price` | `Double` | `price` | `DecimalField(10,2)` | Precision change |
| `unit` | `Text` | — | — | Not in Django model |
| `category_id` | `Nullable<Integer>` | `category` | `ForeignKey(Category)` | FK instead of raw ID |
| `image` | `Nullable<Text>` | `image_url` | `URLField` | Differs — URL vs path |
| `product_type` | `Text` | — | — | Not in Django model |
| `border_color` | `Nullable<Text>` | `border_color` | `CharField(7)` | Same |
| — | — | `sku` | `CharField(50)` | New field |
| — | — | `cost_price` | `DecimalField(10,2)` | New field |
| — | — | `tax_rate` | `CharField(20)` | New field |
| — | — | `barcode` | `CharField(100)` | New field |
| — | — | `is_active` | `BooleanField` | New field |
| — | — | `stock_quantity` | `IntegerField` | New field |
| — | — | `low_stock_threshold` | `IntegerField` | New field |
| — | — | `description` | `TextField` | New field |

### `Sale`

| Diesel Field | Type | Django Field | Type | Notes |
|-------------|------|-------------|------|-------|
| `id` | `Integer` | `id` | `BigAutoField` | Auto-generated |
| `total_amount` | `Double` | `total` | `DecimalField` | Renamed |
| `date` | `Text` | `sale_date` | `DateTimeField` | Combined date+time |
| `time` | `Text` | — | — | Merged into `sale_date` |
| `order_type` | `Text` | — | — | Not in Django model |
| `status` | `Text` | `status` | `CharField(20)` | Choices differ |
| `table_number` | `Nullable<Integer>` | — | — | Not in Django model |
| `delivery_type_id` | `Nullable<Integer>` | — | — | No delivery_type in Django |
| `delivery_address` | `Nullable<Text>` | — | — | Not in Django model |
| `employee_id` | `Nullable<Integer>` | — | — | Not linked in Django |
| `customer_id` | `Nullable<Integer>` | `customer` | `ForeignKey` | FK instead of raw ID |
| — | — | `subtotal` | `DecimalField(12,2)` | New field |
| — | — | `tax_amount` | `DecimalField(10,2)` | New field |
| — | — | `discount_amount` | `DecimalField(10,2)` | New field |
| — | — | `payment_method` | `CharField(20)` | New field |
| — | — | `notes` | `TextField` | New field |

### `Customer`

| Diesel Field | Type | Django Field | Type | Notes |
|-------------|------|-------------|------|-------|
| `id` | `Integer` | `id` | `BigAutoField` | |
| `name` | `Text` | `first_name` | `CharField(100)` | Split into first/last |
| — | — | `last_name` | `CharField(100)` | Will be empty if single name |
| `phone` | `Nullable<Text>` | `phone` | `CharField(20)` | Same |
| `email` | `Nullable<Text>` | `email` | `EmailField` | Same |
| `loyalty_points` | `Double` | `loyalty_points` | `IntegerField` | Type change |
| `notes` | `Nullable<Text>` | `notes` | `TextField` | Same |
| — | — | `total_spent` | `DecimalField(12,2)` | New field |

### `Employee`

| Diesel Field | Type | Django Field | Type | Notes |
|-------------|------|-------------|------|-------|
| `id` | `Integer` | `id` | `BigAutoField` | |
| `name` | `Text` | `first_name` | `CharField(100)` | Split into first/last |
| — | — | `last_name` | `CharField(100)` | Will be empty if single name |
| `phone` | `Nullable<Text>` | `phone` | `CharField(20)` | Same |
| `email` | `Nullable<Text>` | `email` | `EmailField` | Same |
| `employee_type_id` | `Integer` | `role` | `CharField(20)` | Different approach |
| `salary` | `Double` | `hourly_rate` | `DecimalField(8,2)` | Renamed + precision |
| — | — | `pin_code` | `CharField(6)` | New field |

### `InventoryTransaction`

| Diesel Field | Type | Django Field | Type | Notes |
|-------------|------|-------------|------|-------|
| `id` | `Integer` | `id` | `BigAutoField` | |
| `ingredient_id` | `Integer` | `product` | `ForeignKey(Product)` | Points to Product now |
| `transaction_type` | `Text` | `transaction_type` | `CharField(20)` | Same |
| `quantity_change` | `Double` | `quantity` | `IntegerField` | Renamed, type change |
| `reference_id` | `Nullable<Integer>` | `reference` | `CharField(100)` | Different approach |
| `note` | `Nullable<Text>` | `notes` | `TextField` | Same |
| — | — | `created_by` | `CharField(100)` | New field |
| — | — | `shipping_fee` | `DecimalField(10,2)` | New field |

---

## Data Migration Strategy

### Approach: Read Diesel DB → Transform → Write to Django DB

The migration runs as a one-time Python script executed by the server on first launch when it detects a legacy Diesel database.

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│ restaurant.db│────▶│ migration.py │────▶│ restaurant.db│
│ (Diesel)     │     │ (Python)     │     │ (Django ORM) │
│              │     │              │     │              │
│ products     │     │ Read Diesel  │     │ full_products│
│ sales        │     │ Transform    │     │ full_sales   │
│ categories   │────▶│ Write Django │────▶│ full_categories
│ ...          │     │              │     │ ...          │
└──────────────┘     └──────────────┘     └──────────────┘
```

### Detection Logic

The server checks for a legacy Diesel database on startup:

1. Check if `restaurant.db` exists and has Diesel migration metadata (`__diesel_schema_migrations` table)
2. Check if Django tables exist (`full_products`, `full_categories`, etc.)
3. If Diesel DB exists AND Django tables are empty → run migration
4. If Diesel DB exists AND Django tables have data → skip (already migrated)
5. If no Diesel DB → skip (fresh Solo install, no migration needed)

### Migration Order

Tables must be migrated in dependency order to preserve foreign key relationships:

```
1. categories          → full_categories   (no dependencies)
2. delivery_types      → skip (no Django model — data preserved in Diesel DB)
3. employee_types      → skip (no Django model — mapped to role field)
4. settings            → DeviceConfig      (transform to KV pairs)
5. ingredients         → full_ingredients
6. products            → full_products     (depends on categories)
7. employees           → full_employees    (depends on employee_types → role mapping)
8. customers           → full_customers
9. suppliers           → full_suppliers
10. recipes            → full_recipes      (depends on products)
11. recipe_ingredients → merged into Recipe model
12. inventory_transactions → full_inventory (depends on products now, not ingredients)
13. inventory_adjustments → full_inventory_adjustments
14. sales              → full_sales        (depends on customers)
15. sale_items         → full_sale_items   (depends on sales + products)
16. purchase_orders    → full_purchase_orders (depends on suppliers)
17. purchase_order_items → full_purchase_order_items
18. kitchen_tickets    → full_kitchen_tickets (depends on sales)
19. receipt_templates  → full_receipt_templates
20. employee_schedules → full_employee_schedules (depends on employees)
21. payrolls           → full_payroll       (depends on employees)
22. roles              → full_roles
23. users + user_roles → skip (handled by allauth — see auth migration)
24. loyalty_transactions → integrated into Customer model
25. remaining tables with no Django model → preserve data in Diesel DB backup
```

### Data Transformations

Key transformations the migration script must handle:

**Product:**
- `price: f64` → `price: Decimal` — round to 2 decimal places
- `image: Option<String>` (file path) → `image_url: str` (URL or empty)
- `unit: String` → drop (not in Django model)
- `product_type: String` → drop (not in Django model)
- Set defaults for new fields: `sku=""`, `cost_price=0`, `tax_rate="standard"`, `is_active=True`, `stock_quantity=0`, `low_stock_threshold=10`

**Sale:**
- `total_amount: f64` → `total: Decimal`
- `date: String` + `time: String` → `sale_date: DateTime` (parse and combine)
- `subtotal` = `total_amount` (approximation since Diesel model doesn't have subtotal)
- Set `tax_amount=0`, `discount_amount=0`, `payment_method="cash"`
- `order_type: String` → drop
- `delivery_type_id`, `delivery_address`, `table_number`, `employee_id` → drop

**Customer:**
- `name: String` → `first_name` (whole string), `last_name=""`
- `loyalty_points: f64` → `loyalty_points: int` (truncate)
- Set `total_spent=0`

**Employee:**
- `name: String` → `first_name` (whole string), `last_name=""`
- `employee_type_id: i32` → `role` (map: 1→"cashier", 2→"server", 3→"manager", 4→"admin", 5→"kitchen", default→"cashier")
- `salary: f64` → `hourly_rate: Decimal` (divide by 2080 work hours/year for approximation)
- Set `pin_code=""`

**InventoryTransaction:**
- `ingredient_id: i32` → `product` (FK to Product — find product by name or leave null)
- `quantity_change: f64` → `quantity: int` (round to nearest integer)
- `reference_id: Option<i32>` → `reference: str`
- Set `created_by=""`, `shipping_fee=0`

**Recipe:**
- New `Recipe.name` = "Recipe: {product_name}"
- `recipe_ingredients` → drop (merge logic TBD — store as JSON in instructions if needed)

**Settings:**
- Transform each setting field into a `DeviceConfig` KV pair with category="system"
- E.g., `restaurant_name` → `{"key": "restaurant_name", "value": "My Restaurant"}`

### Auth Migration

The Diesel auth system uses a simple `users` table with bcrypt password hashes. The Django server uses `django-allauth`. Migration:

1. Read all users from Diesel `users` table
2. Create corresponding `User` records via Django's `get_user_model()` — custom user model or allauth's
3. Preserve `password_hash` directly in the database (Django uses the same bcrypt format `$2b$...`)
4. Create allauth `EmailAddress` records for each user
5. Map `user_roles` to allauth `Group` assignments

> **Important:** bcrypt hashes from Diesel's `bcrypt` crate use the same format as Django's `bcrypt` hasher. The hash can be copied directly into Django's `password` field with the prefix `bcrypt$$` or written as-is if the default hasher is bcrypt. Verify the hash format before migration.

### Backup Strategy

### Sync-Tracking on Migrated Records

All Django models in the server include sync-tracking fields for cloud replication:

| Field | Purpose | Migration Value |
|-------|---------|----------------|
| `is_synced` | Whether the record has been synced to cloud | `True` (was created during migration, not user action) |
| `sync_status` | Sync state machine | `"synced"` (skip cloud push) |
| `synced_at` | Timestamp of last sync | `timezone.now()` (migration timestamp) |

This is critical: without marking migrated records as synced, the server's sync scheduler will attempt to push all historic data to the cloud on first run, potentially causing duplicates or stale-data conflicts.

### Backup Strategy

Before any migration, the script must:

1. **Copy** `restaurant.db` → `restaurant.db.diesel-backup` (full file copy)
2. Only then begin the migration transaction
3. If any step fails → log the error, restore from backup, and exit with exit code 1

```
mkdir -p /path/to/app/data/backups/
cp restaurant.db restaurant.db.diesel-backup  # timestamped
# ... run migration ...
# if success: keep backup as fallback
# if failure: cp restaurant.db.diesel-backup restaurant.db; exit 1
```

---

## Migration Script Outline

The migration script lives at `server/management/commands/migrate_from_diesel.py` (Django management command).

```
server/
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── migrate_from_diesel.py    ◄── NEW
├── management_utils/
│   ├── __init__.py
│   └── diesel_reader.py              ◄── NEW (SQLite reader for Diesel schema)
└── migrations/
    └── ...
```

### `diesel_reader.py` — Read-Only SQLite Access

```python
"""Read-only access to a legacy Diesel-managed SQLite database.

Uses Python's built-in `sqlite3` module — no Diesel dependencies needed.
All relationship columns use Diesel's naming (e.g., `category_id`, not Django's FK).
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional


@dataclass
class DieselProduct:
    id: int
    name: str
    price: float
    unit: str
    category_id: Optional[int]
    image: Optional[str]
    product_type: str
    border_color: Optional[str]
    uploaded: bool


@dataclass
class DieselSale:
    id: int
    total_amount: float
    date: str       # YYYY-MM-DD
    time: str       # HH:MM:SS
    order_type: str
    status: str
    table_number: Optional[int]
    delivery_type_id: Optional[int]
    delivery_address: Optional[str]
    employee_id: Optional[int]
    customer_id: Optional[int]


@dataclass
class DieselCustomer:
    id: int
    name: str
    phone: Optional[str]
    email: Optional[str]
    loyalty_points: float
    notes: Optional[str]


@dataclass
class DieselEmployee:
    id: int
    name: str
    phone: Optional[str]
    email: Optional[str]
    employee_type_id: int
    salary: float
    is_active: bool
    joined_at: Optional[str]


@dataclass
class DieselSetting:
    id: int
    restaurant_name: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    tax_rate: Optional[str]
    currency: str
    # ... additional fields


class DieselDatabase:
    """Read-only interface to a Diesel-managed SQLite database.

    Example:
        db = DieselDatabase(Path("/path/to/restaurant.db"))
        for p in db.get_products():
            print(p.name, p.price)
        db.close()
    """

    def __init__(self, path: Path):
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row

    def has_diesel_schema(self) -> bool:
        """Check if this DB has Diesel migration metadata."""
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='__diesel_schema_migrations'"
        )
        return cursor.fetchone() is not None

    def get_products(self) -> list[DieselProduct]:
        cursor = self.conn.execute("SELECT * FROM products")
        return [DieselProduct(**dict(row)) for row in cursor.fetchall()]

    def get_categories(self) -> list[dict]:
        cursor = self.conn.execute("SELECT * FROM categories")
        return [dict(row) for row in cursor.fetchall()]

    def get_sales(self) -> list[DieselSale]:
        cursor = self.conn.execute("SELECT * FROM sales")
        return [DieselSale(**dict(row)) for row in cursor.fetchall()]

    def get_sale_items(self) -> list[dict]:
        cursor = self.conn.execute("SELECT * FROM sale_items")
        return [dict(row) for row in cursor.fetchall()]

    def get_customers(self) -> list[DieselCustomer]:
        cursor = self.conn.execute("SELECT * FROM customers")
        return [DieselCustomer(**dict(row)) for row in cursor.fetchall()]

    def get_employees(self) -> list[DieselEmployee]:
        cursor = self.conn.execute("SELECT * FROM employees")
        return [DieselEmployee(**dict(row)) for row in cursor.fetchall()]

    def get_settings(self) -> Optional[DieselSetting]:
        cursor = self.conn.execute("SELECT * FROM settings WHERE id = 1")
        row = cursor.fetchone()
        return DieselSetting(**dict(row)) if row else None

    # ... additional getters for all migrated tables ...

    def close(self):
        self.conn.close()
```

### `migrate_from_diesel.py` — Django Management Command

```python
"""Django management command: migrate legacy Diesel data to Django ORM.

Usage:
    python manage.py migrate_from_diesel --diesel-db /path/to/restaurant.db

The command:
  1. Backs up the Diesel DB
  2. Reads all data from Diesel tables (read-only)
  3. Transforms and writes to Django ORM models
  4. Validates the migration
  5. Reports summary
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from typing import Any, Optional


EMPLOYEE_TYPE_TO_ROLE = {
    1: "cashier",
    2: "server",
    3: "manager",
    4: "admin",
    5: "kitchen",
}


class Command(BaseCommand):
    help = "Migrate data from a legacy Diesel-managed SQLite DB to Django ORM"

    def add_arguments(self, parser):
        parser.add_argument(
            "--diesel-db",
            required=True,
            help="Path to the legacy Diesel SQLite database file (restaurant.db)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Read and validate Diesel data but do not write to Django ORM",
        )

    def handle(self, *args, **options):
        diesel_path = Path(options["diesel_db"])
        dry_run = options["dry_run"]

        if not diesel_path.exists():
            raise CommandError(f"Diesel database not found: {diesel_path}")

        # ── Back up ──
        backup_path = diesel_path.with_suffix(".db.diesel-backup")
        import shutil
        shutil.copy2(diesel_path, backup_path)
        self.stdout.write(f"✅ Backed up to {backup_path}")

        # ── Read ──
        reader = DieselDatabase(diesel_path)
        if not reader.has_diesel_schema():
            self.stdout.write(self.style.WARNING("No Diesel schema found — nothing to migrate."))
            return

        # Read all data
        categories = reader.get_categories()
        products_raw = reader.get_products()
        sales_raw = reader.get_sales()
        sale_items_raw = reader.get_sale_items()
        customers_raw = reader.get_customers()
        employees_raw = reader.get_employees()
        settings_raw = reader.get_settings()
        # ... read remaining tables ...

        reader.close()

        if dry_run:
            self.stdout.write(f"📊 Dry run: found {len(products_raw)} products, "
                            f"{len(sales_raw)} sales, {len(customers_raw)} customers")
            return

        # ── Transform & Write ──
        with transaction.atomic():
            stats = {"categories": 0, "products": 0, "sales": 0, "customers": 0, "employees": 0}

            # 1. Categories (no dependencies)
            diesel_to_django_ids = {}  # map Diesel PK → Django PK
            for cat in categories:
                django_obj = Category.objects.create(
                    name=cat["name"],
                    slug=self._slugify(cat["name"]),
                    display_order=cat.get("id", 0),
                    is_active=True,
                    created_at=cat.get("created_at", timezone.now()),
                    updated_at=cat.get("updated_at", timezone.now()),
                )
                diesel_to_django_ids[("category", cat["id"])] = django_obj.id
                stats["categories"] += 1

            # 2. Products (depends on categories)
            for p in products_raw:
                category_id = diesel_to_django_ids.get(("category", p.category_id))
                django_obj = Product.objects.create(
                    name=p.name,
                    price=Decimal(str(p.price)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                    category_id=category_id,
                    border_color=p.border_color or "",
                    is_active=True,
                    stock_quantity=0,
                    low_stock_threshold=10,
                    tax_rate="standard",
                )
                diesel_to_django_ids[("product", p.id)] = django_obj.id
                stats["products"] += 1

            # 3. Customers
            for c in customers_raw:
                Customer.objects.create(
                    first_name=c.name,
                    last_name="",
                    phone=c.phone or "",
                    email=c.email or "",
                    loyalty_points=int(c.loyalty_points),
                    notes=c.notes or "",
                    is_active=True,
                )
                stats["customers"] += 1

            # 4. Employees (depends on employee_type → role mapping)
            for e in employees_raw:
                role = EMPLOYEE_TYPE_TO_ROLE.get(e.employee_type_id, "cashier")
                Employee.objects.create(
                    first_name=e.name,
                    last_name="",
                    phone=e.phone or "",
                    email=e.email or "",
                    role=role,
                    hourly_rate=Decimal(str(e.salary / 2080)).quantize(Decimal("0.01")),
                    is_active=e.is_active,
                )
                stats["employees"] += 1

            # 5. Sales (depends on customers)
            for s in sales_raw:
                django_obj = Sale.objects.create(
                    sale_date=self._parse_diesel_datetime(s.date, s.time),
                    subtotal=Decimal(str(s.total_amount)).quantize(Decimal("0.01")),
                    total=Decimal(str(s.total_amount)).quantize(Decimal("0.01")),
                    tax_amount=Decimal("0"),
                    discount_amount=Decimal("0"),
                    payment_method="cash",
                    status=s.status if s.status in ["pending", "completed", "refunded", "cancelled"] else "completed",
                )
                diesel_to_django_ids[("sale", s.id)] = django_obj.id
                stats["sales"] += 1

                # SaleItems
                for si in [si for si in sale_items_raw if si["sale_id"] == s.id]:
                    product_id = diesel_to_django_ids.get(("product", si["product_id"])) if "product_id" in si else None
                    SaleItem.objects.create(
                        sale_id=django_obj.id,
                        product_id=product_id,
                        product_name=si["product_name"],
                        quantity=int(si["quantity"]),
                        unit_price=Decimal(str(si["price"])).quantize(Decimal("0.01")),
                        line_total=Decimal(str(si["subtotal"])).quantize(Decimal("0.01")),
                    )

            self.stdout.write(self.style.SUCCESS(
                f"✅ Migration complete: {stats}"
            ))
```

---

## Development Workflow Changes

### Before Migration (Minimal)

```
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│ Write Rust   │───▶│ cargo build      │───▶│ cargo run    │
│ (Diesel CRUD)│    │                  │    │              │
└──────────────┘    └──────────────────┘    └──────────────┘
```

### After Migration (Solo/Full)

```
┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Write Python │───▶│ uv sync          │───▶│ python -m server │
│ (Django ORM) │    │ + server runs   │    │ (hot-reload)     │
└──────────────┘    └──────────────────┘    └──────────────────┘
                        │
┌──────────────┐    ┌───┴────────────────┐    ┌──────────────────┐
│ Edit Rust    │───▶│ cargo build (only  │───▶│ Tauri app with  │
│ (native ops) │    │ hardware module)   │    │ server running │
└──────────────┘    └──────────────────┘    └──────────────────┘
```

### Makefile Targets

| Target | Before (Minimal) | After (Solo/Full) |
|--------|------------------|--------------------|
| Build app | `cargo tauri build` | `make build-server && cargo tauri build` |
| Run dev | `cargo tauri dev` | `make dev-desktop` (starts server + Tauri) |
| Test | `cargo test` | `uv run pytest` (Python) + `cargo test` (Rust) |
| DB migration | `diesel migration run` | `python manage.py migrate` |
| Seed data | `cargo run --bin seed` | `python manage.py seed_data` |

### Testing Strategy

| Test Type | What to Test | Command |
|-----------|-------------|---------|
| Python unit | Django model methods, validation | `uv run pytest server/tests/` |
| Python integration | REST API endpoints | `uv run pytest server/tests/ -k "api"` |
| Python migration | Diesel→Django data fidelity | `uv run pytest server/tests/test_migration.py` |
| Rust unit | Hardware ops (printer, drawer) | `cargo test -- --nocapture` |
| Rust integration | Server lifecycle commands | `cargo test --test integration` |
| E2E | Full app with server running | `make test-e2e` |

### Data Fidelity Verification

After migration, verify by running:

```python
# Verify row counts match
diesel_count = diesel_db.conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
django_count = Product.objects.count()
assert diesel_count == django_count, f"Product count mismatch: {diesel_count} vs {django_count}"

# Verify critical fields match (sampling)
diesel_product = diesel_db.get_products()[0]
django_product = Product.objects.get(id=1)
assert float(django_product.price) == round(diesel_product.price, 2)
```

---

## Rollback Plan

If the migration fails or produces incorrect data:

1. Stop the server: `kill <server-pid>` or `invoke("stop_server")`
2. Restore from backup: `cp restaurant.db.diesel-backup restaurant.db`
3. Delete or truncate all Django-managed tables:
   ```sql
   DELETE FROM full_products;
   DELETE FROM full_categories;
   DELETE FROM full_sales;
   -- ... all full_* tables ...
   ```
4. Restart Minimal (Tauri app with Diesel backend) — it will read the restored backup
5. Debug and fix the migration script
6. Run the migration again

---

## Development Checklist

When adding a new feature that touches data:

- [ ] **Does the feature need database access?** → Implement in Python server (Django ORM)
- [ ] **Does it need native hardware access?** → Implement in Rust (Tauri `invoke`)
- [ ] **If in Python:** Add Django model → Create REST endpoint → Update frontend to call `http://127.0.0.1:8765/api/...`
- [ ] **If in Rust:** Add Tauri command → Update frontend to call `invoke("command_name")`
- [ ] **Does the Diesel schema have an equivalent?** → Add to migration script
- [ ] **Does the Diesel schema differ in field names/types?** → Add transformation logic
- [ ] **Have you run the migration on a copy of real data?** → Test before deploying to users

---

## Related Documentation

- [Edition Comparison](editions.md) — per-edition feature matrix
- [POS Architecture](./pos-architecture.md) — System architecture overview
- [legacy Server Architecture](../legacy/POS_ARCHITECTURE.md) — archived server process lifecycle details
- [Pro ↔ Cloud Sync Contract](pro-cloud-sync-contract.md) — cloud sync architecture
