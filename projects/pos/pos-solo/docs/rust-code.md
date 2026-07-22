# POS — Rust Backend Documentation

> **Path:** `src-tauri/src/` | **Language:** Rust (Edition 2021) | **ORM:** Diesel 2.x | **DB:** SQLite

---

## Architecture Overview

The Rust backend is a Tauri 2 application with a layered architecture:

```
main.rs (Tauri app builder)
  └── lib.rs (command registrations — 80+ #[tauri::command])
        └── operations/ (27 CRUD modules)
              └── db/ (Diesel ORM — connection, schema, models)
```

---

## Database Schema

The database has **37 tables** organized into functional groups:

### Core POS (18 tables)

| Table | Fields | Purpose |
|-------|--------|---------|
| `settings` | restaurant_name, address, phone, tax_rate, currency, receipt_footer, logo, dine_in_tables, delivery_fee | Restaurant configuration |
| `categories` | name | Product categories |
| `products` | name, price, unit, category_id, image, uploaded | Menu products |
| `delivery_types` | name, fee_multiplier, is_active | Delivery methods |
| `employee_types` | name, description, is_active | Staff role categories |
| `employees` | name, phone, email, employee_type_id, salary, is_active | Staff records |
| `sales` | total_amount, currency, date, time, order_type, status, table_number, delivery_type_id, employee_id, customer_id | Sales transactions |
| `sale_items` | sale_id, product_name, price, quantity, unit, subtotal | Line items |
| `ingredients` | name, unit, current_quantity, reorder_level, reorder_quantity, cost_per_unit | Stock items |
| `recipe_types` | name, description, is_active | Recipe categories |
| `recipes` | product_id, recipe_type_id, yield_quantity | Product recipes |
| `recipe_ingredients` | recipe_id, ingredient_id, quantity, unit, preparation_note | Recipe components |
| `inventory_transactions` | ingredient_id, transaction_type, quantity_change, reference_id, note | Stock movements |
| `inventory_adjustments` | ingredient_id, previous_quantity, new_quantity, reason, created_by | Manual stock corrections |
| `inventory_alerts` | ingredient_id, alert_type, alert_message, is_resolved | Low-stock alerts |
| `receipt_templates` | name, template_body, is_default | Custom receipt designs |
| `tax_reports` | period_start, period_end, total_sales, total_tax, transaction_count | Tax period reports |
| `report_metadata` | report_type, format, file_path, parameters, generated_by | Report file tracking |

### Auth & Access (3 tables)

| Table | Fields | Purpose |
|-------|--------|---------|
| `users` | email, password_hash, name | User accounts |
| `roles` | name, permissions (JSON), is_active | Role definitions |
| `user_roles` | user_id, role_id | Role assignments |

### Supply Chain (3 tables)

| Table | Fields | Purpose |
|-------|--------|---------|
| `suppliers` | name, contact_name, email, phone, address, tax_id, payment_terms | Supplier records |
| `purchase_orders` | supplier_id, reference_number, status, total_amount, expected_date | Purchase orders |
| `purchase_order_items` | purchase_order_id, ingredient_id, quantity, cost_per_unit, received_quantity | PO line items |

### Kitchen & Customers (3 tables)

| Table | Fields | Purpose |
|-------|--------|---------|
| `kitchen_tickets` | sale_id, status, priority, notes, completed_at | Kitchen display tickets |
| `customers` | name, phone, email, loyalty_points, notes | Customer records |
| `loyalty_transactions` | customer_id, sale_id, points_change, reason | Loyalty point history |

### HR & Payroll (2 tables)

| Table | Fields | Purpose |
|-------|--------|---------|
| `employee_schedules` | employee_id, shift_start, shift_end, status, notes | Shift schedules |
| `payrolls` | employee_id, period_start, period_end, regular_hours, overtime_hours, total_pay, status | Payroll records |

### Cloud CRM (8 tables) — Full Edition only

| Table | Fields | Purpose |
|-------|--------|---------|
| `crm_companies` | name, website, phone, email, address, industry, tax_id, tags | Company records |
| `crm_contacts` | salutation, first_name, last_name, email, phone, job_title, company_id, pos_customer_id | Contact records |
| `crm_pipelines` | name, description, is_default, is_active | Sales pipelines |
| `crm_stages` | pipeline_id, name, display_order, probability, color | Pipeline stages |
| `crm_deals` | title, value, currency, priority, pipeline_id, stage_id, contact_id, company_id, pos_sale_id, expected_close_date | Sales deals |
| `crm_activities` | activity_type, subject, description, outcome, contact_id, deal_id, company_id, due_date | Activity log |
| `crm_notes` | content, contact_id, deal_id, company_id, is_pinned | Note records |
| `crm_sync_log` / `crm_sync_queue` / `crm_cloud_config` | Sync infrastructure | Cloud sync management |

---

## Command Registration Pattern

All frontend-to-backend communication uses Tauri's `#[tauri::command]` pattern. Commands are registered in `lib.rs`:

```rust
#[tauri::command]
fn get_products(app: AppHandle) -> Result<Vec<db::models::Product>, String> {
    let db_path = get_db_path(&app)?;
    products::get_products(&db_path)
}
```

The Tauri `AppHandle` is used to resolve the app data directory for the SQLite database path.

---

## Operation Module Pattern

Each module in `operations/` follows a consistent pattern:

```rust
// operations/products.rs
use crate::db::models::{Product, NewProduct, UpdateProduct};
use crate::db; // for establish_connection()

pub fn get_products(db_path: &str) -> Result<Vec<Product>, String> { ... }
pub fn add_product(db_path: &str, product: NewProduct) -> Result<Product, String> { ... }
pub fn update_product(db_path: &str, id: i32, update: UpdateProduct) -> Result<Product, String> { ... }
pub fn delete_product(db_path: &str, id: i32) -> Result<(), String> { ... }
pub fn mark_product_uploaded(db_path: &str, id: i32) -> Result<(), String> { ... }
```

### All 27 Operation Modules

| Module | Functions | Responsibility |
|--------|-----------|---------------|
| `auth.rs` | `check_auth_required`, `get_superuser_email`, `ensure_superuser_exists`, `login`, `change_password`, `send_confirmation_code`, `verify_user` | Authentication & user management |
| `products.rs` | CRUD + `mark_product_uploaded` | Product lifecycle |
| `categories.rs` | CRUD | Product categories |
| `sales.rs` | `add_sale` (with items), CRUD | Sales transactions |
| `transactions.rs` | `get_transactions`, `delete_transaction` | Transaction history |
| `analytics.rs` | `get_analytics` | Dashboard metrics |
| `settings.rs` | `get_settings`, `save_settings` | Restaurant config |
| `ingredients.rs` | CRUD + soft delete | Ingredient management |
| `recipes.rs` | CRUD + ingredient management + soft delete | Recipe lifecycle |
| `inventory_transactions.rs` | CRUD + adjustments | Stock tracking |
| `dump.rs` | `dump_to_json` | Database export |
| `delivery_types.rs` | CRUD + soft delete | Delivery methods |
| `employee_types.rs` | CRUD + soft delete | Staff categories |
| `employees.rs` | CRUD + soft delete | Staff records |
| `roles.rs` | CRUD + user role assignment | Access control |
| `suppliers.rs` | CRUD + soft delete | Supplier records |
| `purchase_orders.rs` | CRUD (order + items) | Procurement |
| `kitchen_tickets.rs` | CRUD | Kitchen display |
| `customers.rs` | CRUD + loyalty transactions | Customer management |
| `receipt_templates.rs` | CRUD + default template | Receipt designs |
| `tax_reports.rs` | CRUD | Tax reporting |
| `employee_schedules.rs` | CRUD | Shift management |
| `payrolls.rs` | CRUD | Payroll |
| `reports.rs` | CRUD (metadata) | Report tracking |
| `sidecar.rs` | `start_sidecar`, `stop_sidecar`, `sidecar_status` | Sidecar lifecycle |
| `signals.rs` | Broadcast channel | Change events (Full only) |
| `crm.rs` | CRUD (companies, contacts, deals, pipelines, activities, notes) | Cloud CRM (Full only) |

---

## Database Connection

```rust
// db/mod.rs
use diesel::prelude::*;
use diesel::sqlite::SqliteConnection;

pub fn establish_connection(db_path: &str) -> SqliteConnection {
    SqliteConnection::establish(db_path)
        .unwrap_or_else(|_| panic!("Error connecting to {}", db_path))
}

pub fn get_db_path(app: &AppHandle) -> Result<String, String> {
    let app_dir = app.path().app_data_dir().map_err(|e| e.to_string())?;
    std::fs::create_dir_all(&app_dir).map_err(|e| e.to_string())?;
    Ok(app_dir.join("restaurant.db").to_string_lossy().to_string())
}

pub fn run_migrations(db_path: &str) -> Result<(), String> {
    let mut conn = establish_connection(db_path);
    // Run Diesel migrations
    // Ensure superuser exists if configured
    Ok(())
}
```

---

## Seed System

The seed binary (`src/bin/seed.rs`) supports 4 presets:

```bash
# Run via Makefile
make seed PRESET=all      # All 100+ items
make seed PRESET=base     # Basic restaurant
make seed PRESET=gaming   # POS-KO Gaming Center
make seed PRESET=coffee   # Coffee shop

# Or directly
DATABASE_URL=restaurant.db PRESET=all cargo run --bin seed
```

Seeds populate: `settings`, `categories`, `products`, `ingredients`, `recipes`, `recipe_ingredients`, `employees`, `customers`, and more.

---

## Email System (`email.rs`)

SMTP email sending using `lettre`:

```rust
pub fn send_support_email(name: &str, email: &str, subject: &str, message: &str) -> Result<(), String>
```

Configured via `SMTP_*` environment variables. Uses the `support_email.html` template from `src-tauri/templates/`.

---

## Error Handling

All Tauri commands return `Result<T, String>` for consistent error propagation to the frontend:

```typescript
// Frontend receives errors as plain strings
try {
  const products = await invoke('get_products');
} catch (err) {
  console.error('Failed to load products:', err);
}
```

---

## Related Docs

- **[Tauri Documentation](https://v2.tauri.app/)**
- **[Diesel ORM Guide](https://diesel.rs/guides/)**
- [`customization-tauri.md`](customization-tauri.md) — Customizing the Rust backend
