# Formint — Rust Backend Documentation

> **Path:** `src-tauri/src/` | **Language:** Rust (Edition 2021) | **ORM:** Diesel 2.x | **DB:** SQLite  
> **No sidecar** — all data directly through Diesel ORM in-process

---

## Architecture

```
main.rs (Tauri app builder)
  └── lib.rs (80+ #[tauri::command] registrations)
        └── operations/ (27 CRUD modules)
              ├── direct Diesel SQL queries
              └── db/ (Diesel ORM — connection, schema, models)
```

forge-pos is the **only edition** where the Rust backend handles ALL data operations directly. No Python sidecar, no HTTP layer — just Tauri IPC → Rust → Diesel → SQLite.

## Database Schema (37 Tables)

### Core POS (18 tables)

| Table | Key Fields | Description |
|-------|-----------|-------------|
| `settings` | restaurant_name, address, phone, currency, tax_rate, delivery_fee | Restaurant configuration |
| `categories` | id, name | Product categories |
| `products` | name, price, unit, category_id, image, border_color, product_type, uploaded | Menu products |
| `delivery_types` | name, fee_multiplier, is_active | Delivery methods |
| `employees` | name, phone, email, employee_type_id, salary, is_active | Staff records |
| `sales` | total_amount, currency, date, time, order_type, status, table_number | Sales transactions |
| `sale_items` | sale_id, product_name, price, quantity, unit, subtotal | Line items |
| `ingredients` | name, unit, current_quantity, reorder_level, cost_per_unit | Stock items |
| `recipes` | product_id, recipe_type_id, yield_quantity | Product recipes |
| `recipe_ingredients` | recipe_id, ingredient_id, quantity, preparation_note | Recipe components |
| `inventory_transactions` | ingredient_id, transaction_type, quantity_change | Stock movements |
| `inventory_adjustments` | ingredient_id, previous_quantity, new_quantity, reason | Manual corrections |
| `inventory_alerts` | ingredient_id, alert_type, alert_message, is_resolved | Low-stock alerts |
| `receipt_templates` | name, template_body, is_default | Custom receipt designs |
| `tax_reports` | period_start, period_end, total_sales, total_tax | Tax period reports |
| `report_metadata` | report_type, format, file_path | Report file tracking |

### Auth & Access (3 tables)

| Table | Key Fields | Description |
|-------|-----------|-------------|
| `users` | email, password_hash (bcrypt), name | User accounts |
| `roles` | name, permissions (JSON text), is_active | Role definitions |
| `user_roles` | user_id, role_id | Role assignments |

### Supply Chain (3 tables)

| Table | Key Fields | Description |
|-------|-----------|-------------|
| `suppliers` | name, contact_name, email, phone, payment_terms | Supplier records |
| `purchase_orders` | supplier_id, reference_number, status, total_amount | Purchase orders |
| `purchase_order_items` | purchase_order_id, ingredient_id, quantity, cost_per_unit | PO line items |

### Customers & Kitchen (3 tables)

| Table | Key Fields | Description |
|-------|-----------|-------------|
| `customers` | name, phone, email, loyalty_points | Customer records |
| `loyalty_transactions` | customer_id, sale_id, points_change, reason | Loyalty history |
| `kitchen_tickets` | sale_id, status, priority, notes, completed_at | Kitchen display |

### HR & Payroll (3 tables)

| Table | Key Fields | Description |
|-------|-----------|-------------|
| `employee_types` | name, description, is_active | Staff categories |
| `employee_schedules` | employee_id, shift_start, shift_end, status | Shift schedules |
| `payrolls` | employee_id, period_start, period_end, regular_hours, overtime_hours, total_pay | Payroll records |

## Command Registration Pattern

```rust
// lib.rs — every frontend→backend call uses #[tauri::command]
#[tauri::command]
fn get_products(app: AppHandle) -> Result<Vec<db::models::Product>, String> {
    let db_path = get_db_path(&app)?;
    products::get_products(&db_path)
}

#[tauri::command]
fn add_product(app: AppHandle, product: db::models::NewProduct) -> Result<db::models::Product, String> {
    let db_path = get_db_path(&app)?;
    products::add_product(&db_path, product)
}
```

## All 27 Operation Modules

| Module | Functions | Responsibility |
|--------|-----------|---------------|
| `auth.rs` | check_auth_required, login, change_password, setup_account | Authentication |
| `products.rs` | CRUD + mark_product_uploaded | Product lifecycle |
| `categories.rs` | CRUD | Product categories |
| `sales.rs` | add_sale (with items), CRUD | Sales transactions |
| `transactions.rs` | get_transactions, delete_transaction | Transaction history |
| `analytics.rs` | get_analytics | Dashboard metrics |
| `settings.rs` | get_settings, save_settings | Restaurant config |
| `ingredients.rs` | CRUD + soft delete | Ingredient management |
| `recipes.rs` | CRUD + ingredient management | Recipe lifecycle |
| `inventory_transactions.rs` | CRUD + adjustments | Stock tracking |
| `dump.rs` | dump_to_json | Database export |
| `delivery_types.rs` | CRUD + soft delete | Delivery methods |
| `employee_types.rs` | CRUD + soft delete | Staff categories |
| `employees.rs` | CRUD + soft delete | Staff records |
| `roles.rs` | CRUD + user assignment | Access control |
| `suppliers.rs` | CRUD + soft delete | Supplier records |
| `purchase_orders.rs` | CRUD (order + items) | Procurement |
| `kitchen_tickets.rs` | CRUD | Kitchen display |
| `customers.rs` | CRUD + loyalty transactions | Customer management |
| `receipt_templates.rs` | CRUD + default template | Receipt designs |
| `tax_reports.rs` | CRUD | Tax reporting |
| `employee_schedules.rs` | CRUD | Shift management |
| `payrolls.rs` | CRUD | Payroll |
| `reports.rs` | CRUD (metadata) | Report tracking |
| `sidecar.rs` | start_sidecar, stop_sidecar, sidecar_status | Sidecar lifecycle |
| `hardware.rs` | trigger_cash_drawer, print_thermal_receipt, check_printer_status | Thermal printer |
| `email.rs` | send_support_email | SMTP email |

## Hardware Integration (`hardware.rs`)

forge-pos includes built-in ESC/POS thermal printer support:

| Function | Description |
|----------|-------------|
| `trigger_cash_drawer()` | Opens cash drawer via printer RJ12 port |
| `print_thermal_receipt()` | Prints formatted receipt with bold/center/alignment |
| `check_printer_status()` | Verifies printer port connectivity |

**ESC/POS commands used:** Init, bold on/off, double-width, center/left align, paper cut, drawer kick.

## Seed System

```bash
make seed PRESET=all      # All 100+ items (default)
make seed PRESET=base     # Basic restaurant
make seed PRESET=gaming   # POS-KO Gaming Center
make seed PRESET=coffee   # Coffee shop
```

The seed binary uses Diesel's `embed_migrations!` for schema and layered SQL seed scripts.

## Error Handling

All commands return `Result<T, String>` — errors propagate as strings to the frontend:

```typescript
// Frontend
try {
  const products = await invoke('get_products');
} catch (err) {
  console.error('Failed:', err); // err is a string
}
```

## Key Differences from the merged package

| Feature | forge-pos | formint-pos |
|---------|:--------:|:-----------:|
| Data access | `invoke()` → Rust/Diesel | Django Ninja API → HTTP |
| Python sidecar | ❌ | ✅ Robyn |
| Django ORM | ❌ (Diesel) | ✅ |
| Admin panel | ❌ | ✅ Unfold |
| Cloud sync | ❌ | ✅ Child→Master |
| WebSocket | ❌ | ✅ /ws/entities |
| Hardware printer | ✅ Direct ESC/POS | ❌ (sidecar) |
