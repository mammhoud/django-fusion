# POS System — Comprehensive Architecture Audit

> **Generated:** 2026-07-23  
> **Scope:** `pos-mini`, `pos-solo`, `pos-full` (historical)  
> **Stack:** Tauri v2 (Rust backend) + React (TypeScript frontend) + SQLite (Diesel ORM) + Python/Sanic server

> ⚠️ **Archived reference**: pos-solo and pos-full were merged into
> `formint-pos/`; the Robyn server now lives at `formint-pos/server/` and the
> legacy React UIs under `formint-pos/legacy-react/`.

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        POS VERSION MATRIX                           │
├──────────────┬────────────────┬────────────────┬───────────────────┤
│              │   pos-mini     │   pos-solo     │    pos-full       │
├──────────────┼────────────────┼────────────────┼───────────────────┤
│ Backend      │ Rust (Tauri)   │ Python Server │ Python Server    │
│ DB Access    │ Diesel ORM     │ Server HTTP   │ Server HTTP      │
│ Frontend→BE  │ Tauri invoke() │ REST API       │ REST API + RTK-Q  │
│ Sync         │ N/A (local)    │ Server WebSocket sync             │
│ Tables       │ 15             │ 15             │ 15                │
├──────────────┼────────────────┼────────────────┼───────────────────┤
│ Pages        │ 22             │ 23 (+ Notes)   │ 23 (+ Notes)      │
│ Tauri Cmds   │ 100+           │ N/A            │ N/A               │
│ Server APIs │ N/A            │ 84+ CRUD       │ 84+ CRUD          │
└──────────────┴────────────────┴────────────────┴───────────────────┘
```

### Data Flow per Version

**pos-mini:** `React → invoke("get_products") → Tauri IPC → Rust (Diesel) → SQLite`

**pos-solo:** `React → fetch("/api/products") → Server (Python/Sanic) → SQLite`

**pos-full:** `React → RTK Query → fetch("/api/products") → Server (Python/Sanic) → SQLite`

---

## 2. Database Models

### 2.1 Shared Tables (All 3 Versions)

All three versions share an identical set of **15 tables** (14 business + users):

| # | Table | Key Fields | Relations | Usage |
|---|-------|-----------|-----------|-------|
| 1 | `settings` | id, restaurant_name, address, phone, email, tax_rate, currency, opening_time, closing_time, receipt_footer, logo, dine_in_tables, delivery_fee, delivery_fee_per_km | — | App configuration |
| 2 | `categories` | id, name, created_at, updated_at | products.category_id → categories.id | Product grouping |
| 3 | `products` | id, name, price, unit, category_id, image, product_type, **border_color**, created_at, updated_at, uploaded | sale_items ref by name | Menu items |
| 4 | `delivery_types` | id, name, description, fee_multiplier, is_active, created_at, updated_at | sales.delivery_type_id → delivery_types.id | Delivery options |
| 5 | `employee_types` | id, name, description, is_active, created_at, updated_at | employees.employee_type_id → employee_types.id | Staff roles |
| 6 | `employees` | id, name, phone, email, employee_type_id, salary, is_active, joined_at, created_at, updated_at, uploaded | — | Staff records |
| 7 | `sales` | id, total_amount, currency, date, time, order_type, status, table_number, delivery_type_id, delivery_address, employee_id, customer_id, created_at, updated_at, uploaded | → delivery_types, → employees, → customers | Transactions |
| 8 | `sale_items` | id, sale_id, product_name, price, quantity, unit, subtotal, created_at | sale_id → sales.id | Line items |
| 9 | `ingredients` | id, name, unit, current_quantity, reorder_level, reorder_quantity, cost_per_unit, is_active, created_at, updated_at, uploaded | — | Stock items |
| 10 | `recipe_types` | id, name, description, is_active, created_at, updated_at | recipes.recipe_type_id → recipe_types.id | Recipe categories |
| 11 | `recipes` | id, product_id, recipe_type_id, yield_quantity, is_active, created_at, updated_at, uploaded | → products, → recipe_types | Product recipes |
| 12 | `recipe_ingredients` | id, recipe_id, ingredient_id, quantity, unit, preparation_note, created_at, updated_at | → recipes, → ingredients | Recipe BOM |
| 13 | `inventory_transactions` | id, ingredient_id, transaction_type, quantity_change, reference_id, note, created_at, uploaded | → ingredients | Stock movements |
| 14 | `inventory_adjustments` | id, ingredient_id, previous_quantity, new_quantity, reason, created_by, created_at, uploaded | → ingredients | Manual stock corrections |
| 15 | `users` | id, email, password_hash, name, created_at, updated_at | — (user_roles → roles) | Authentication |

### 2.2 Additional Tables (Enterprise — pos-mini only via Rust)

These tables exist in the Rust codebase (models + operations + lib.rs commands) but are **not in the SQL migration** for solo/full:

| # | Table | Key Fields | Module | Tauri Command |
|---|-------|-----------|--------|---------------|
| E1 | `roles` | id, name, permissions (JSON string), is_active | roles.rs | get_roles, add_role, update_role, soft_delete_role |
| E2 | `user_roles` | user_id, role_id, created_at | roles.rs | assign_role, remove_role, get_user_roles |
| E3 | `suppliers` | id, name, contact_name, email, phone, address, tax_id, payment_terms, is_active | suppliers.rs | 4 CRUD commands |
| E4 | `purchase_orders` | id, supplier_id, reference_number, status, total_amount, expected_date, notes | purchase_orders.rs | 5 CRUD commands |
| E5 | `purchase_order_items` | id, purchase_order_id, ingredient_id, quantity, cost_per_unit, received_quantity | purchase_orders.rs | (nested in PO) |
| E6 | `kitchen_tickets` | id, sale_id, status, priority, notes, created_at, completed_at | kitchen_tickets.rs | 4 CRUD commands |
| E7 | `customers` | id, name, phone, email, loyalty_points, notes | customers.rs | 4 CRUD + 2 loyalty |
| E8 | `loyalty_transactions` | id, customer_id, sale_id, points_change, reason | customers.rs | get/add |
| E9 | `receipt_templates` | id, name, template_body, is_default | receipt_templates.rs | 5 CRUD commands |
| E10 | `tax_reports` | id, period_start, period_end, total_sales, total_tax, transaction_count | tax_reports.rs | 3 CRUD commands |
| E11 | `employee_schedules` | id, employee_id, shift_start, shift_end, status, notes | employee_schedules.rs | 4 CRUD commands |
| E12 | `payrolls` | id, employee_id, period_start, period_end, regular_hours, overtime_hours, total_pay, status | payrolls.rs | 4 CRUD commands |
| E13 | `report_metadata` | id, report_type, format, file_path, parameters, generated_by | reports.rs | 3 CRUD commands |
| E14 | `inventory_alerts` | id, ingredient_id, alert_type, alert_message, is_resolved, created_at, resolved_at | (model only) | — (no Tauri cmd) |

> ⚠️ **NOTE:** `inventory_alerts` has Rust model structs but **no Tauri command registered** in lib.rs and **no operations module**. It exists in schema/models but is unreachable from the frontend.

### 2.3 border_color Field — Full Stack Trace

The `border_color` column is **fully implemented across all layers in all 3 versions**:

```
┌──────────────────────────────────────────────────────────────────────┐
│                        border_color Stack                            │
├──────────┬───────────────────────────────────────────────────────────┤
│ DB       │ SQL migration: border_color TEXT (in products table)      │
│          │ pos-mini: ✅  pos-solo: ✅  pos-full: ✅                   │
├──────────┼───────────────────────────────────────────────────────────┤
│ Schema   │ diesel schema.rs: border_color -> Nullable<Text>          │
├──────────┼───────────────────────────────────────────────────────────┤
│ Rust     │ Product: border_color: Option<String>                     │
│ Models   │ NewProduct: border_color: Option<String>                  │
│          │ UpdateProduct: border_color: Option<Option<String>>       │
├──────────┼───────────────────────────────────────────────────────────┤
│ TS Types │ Product: border_color?: string | null                     │
│          │ NewProduct: border_color?: string | null                  │
│          │ UpdateProductPayload: border_color?: string | null        │
│          │ pos-mini: ✅  pos-solo: ✅  pos-full: ✅                   │
├──────────┼───────────────────────────────────────────────────────────┤
│ Frontend │ ProductCard.tsx: reads border_color → applies inline      │
│          │   style with borderColor + rgba background tint            │
│          │ ProductManager.tsx: color picker input + 8-color palette  │
│          │   preset buttons, saved with add/update payload            │
│          │ pos-mini: ✅  pos-solo: ✅  pos-full: ✅                   │
├──────────┼───────────────────────────────────────────────────────────┤
│ i18n     │ en.json: "productManager.borderColor": "Border Color"     │
│          │ pos-mini: ✅  pos-solo: ✅  pos-full: ✅                   │
└──────────┴───────────────────────────────────────────────────────────┘
```

---

## 3. TypeScript Types

### 3.1 Complete Type Inventory (pos-mini — 30 interfaces/types)

| Interface | Fields | Used By |
|-----------|--------|---------|
| `Product` | id, name, price, unit, category_id, image, border_color | ProductManager, Sale, ProductCard |
| `NewProduct` | name, price, unit, category_id, image, border_color | ProductManager (add) |
| `UpdateProductPayload` | name?, price?, unit?, category_id?, image?, border_color? | ProductManager (edit) |
| `Category` | id, name, created_at?, updated_at? | ProductManager |
| `Settings` | restaurant_name?, address?, phone?, email?, tax_rate?, currency?, opening_time?, closing_time?, receipt_footer?, logo?, dine_in_tables?, delivery_fee?, delivery_fee_per_km? | Settings |
| `DeliveryType` | id, name, description?, fee_multiplier, is_active | Sale, Settings |
| `EmployeeType` | id, name, description?, is_active | Employees |
| `Employee` | id, name, phone?, email?, employee_type_id, salary, is_active, joined_at? | Employees, Sale |
| `Sale` | id, total_amount, currency, date, time, order_type, status, table_number, delivery_type_id, delivery_address, employee_id, customer_id? | Transactions, Sale |
| `SaleItem` | name, price, quantity, unit | Sale (cart) |
| `Transaction` | id, items[], total_amount, currency, date, time, order_type, status | Transactions |
| `AnalyticsData` | daily_revenue[], top_products[], product_distribution[], summary | Analytics |
| `Recipe` | id, product_id, recipe_type_id, yield_quantity, is_active | Recipes |
| `RecipeIngredient` | id, recipe_id, ingredient_id, quantity, unit?, preparation_note? | Recipes |
| `Ingredient` | id, name, unit, current_quantity, reorder_level, reorder_quantity, cost_per_unit, is_active | Inventory, Recipes |
| `InventoryTransaction` | id, ingredient_id, transaction_type, quantity_change, reference_id?, note?, created_at | Inventory |
| `InventoryAdjustment` | id, ingredient_id, previous_quantity, new_quantity, reason, created_by?, created_at | Inventory |
| `Role` | id, name, permissions (string), is_active | Roles |
| `Supplier` | id, name, contact_name?, email?, phone?, address?, tax_id?, payment_terms?, is_active | Suppliers |
| `PurchaseOrder` | id, supplier_id, reference_number?, status, total_amount, expected_date?, notes? | PurchaseOrders |
| `KitchenTicket` | id, sale_id, status, priority, notes?, created_at, completed_at? | KitchenDisplay |
| `Customer` | id, name, phone?, email?, loyalty_points, notes? | Customers |
| `LoyaltyTransaction` | id, customer_id, sale_id?, points_change, reason | Customers |
| `ReceiptTemplate` | id, name, template_body, is_default | ReceiptTemplates |
| `TaxReport` | id, period_start, period_end, total_sales, total_tax, transaction_count | TaxReports |
| `EmployeeSchedule` | id, employee_id, shift_start, shift_end, status, notes? | EmployeeSchedule |
| `Payroll` | id, employee_id, period_start, period_end, regular_hours, overtime_hours, total_pay, status | Payroll |
| `ReportMetadata` | id, report_type, format, file_path, parameters?, generated_by? | Reports |
| `InventoryAlert` | id, ingredient_id, alert_type, alert_message, is_resolved, resolved_at? | (unused) |
| `InvoiceType` | 'tax' \| 'commercial' \| 'proforma' \| 'credit' \| 'receipt' | InvoicePage |

### 3.2 Cross-Version Type Differences

All three versions share **identical type definitions** in `types.ts`. The only differences are:

- **pos-full** has additional RTK Query API endpoint types in `store/api/endpoints/*.ts` that shadow the canonical types.ts — these were aligned in a previous fix session
- **pos-solo** and **pos-mini** have identical type files
- All versions: `InventoryAlert` type exists but no UI page uses it

---

## 4. Rust Backend (pos-mini)

### 4.1 Operations Modules → Tauri Commands

| Operations Module | Functions | Tauri Commands | DB Tables Touched |
|-------------------|-----------|----------------|-------------------|
| `products.rs` | get_products, add_product, update_product, delete_product, mark_product_uploaded | ✅ 5 | products |
| `categories.rs` | get_categories, add_category, update_category, delete_category | get, add (2/4) | categories |
| `sales.rs` | add_sale, get_sales, update_sale, delete_sale, mark_sale_uploaded, get_sale_with_items | ✅ 5 (missing get_sale_with_items) | sales, sale_items |
| `transactions.rs` | get_transactions, delete_transaction | ✅ 2 | sales, sale_items (JOIN) |
| `settings.rs` | get_settings, save_settings | ✅ 2 | settings |
| `analytics.rs` | get_analytics | ✅ 1 | sales, sale_items |
| `ingredients.rs` | get_ingredients, add_ingredient, update_ingredient, soft_delete_ingredient, mark_ingredient_uploaded | ✅ 4 (missing mark) | ingredients |
| `recipes.rs` | get_recipes, create_recipe, update_recipe, soft_delete_recipe, mark_recipe_uploaded, get_recipe_with_ingredients, add_recipe_ingredient, update_recipe_ingredient, delete_recipe_ingredient | ✅ 9 | recipes, recipe_ingredients |
| `inventory_transactions.rs` | get_inventory_transactions, get_inventory_adjustments, add_inventory_transaction | ✅ 3 | inventory_transactions, inventory_adjustments |
| `delivery_types.rs` | get_delivery_types, add_delivery_type, update_delivery_type, soft_delete_delivery_type | ✅ 4 | delivery_types |
| `employee_types.rs` | get_employee_types, add_employee_type, update_employee_type, soft_delete_employee_type | ✅ 4 | employee_types |
| `employees.rs` | get_employees, add_employee, update_employee, soft_delete_employee, mark_employee_uploaded | ✅ 4 (missing mark) | employees |
| `roles.rs` | get_roles, add_role, update_role, soft_delete_role, get_user_roles, assign_role, remove_role | ✅ 7 | roles, user_roles |
| `suppliers.rs` | get_suppliers, add_supplier, update_supplier, soft_delete_supplier | ✅ 4 | suppliers |
| `purchase_orders.rs` | get_purchase_orders, get_purchase_order_items, add_purchase_order, update_purchase_order, delete_purchase_order | ✅ 5 | purchase_orders, purchase_order_items |
| `kitchen_tickets.rs` | get_kitchen_tickets, add_kitchen_ticket, update_kitchen_ticket, delete_kitchen_ticket | ✅ 4 | kitchen_tickets |
| `customers.rs` | get_customers, add_customer, update_customer, delete_customer, get_loyalty_transactions, add_loyalty_transaction | ✅ 6 | customers, loyalty_transactions |
| `receipt_templates.rs` | get_receipt_templates, get_default_receipt_template, add_receipt_template, update_receipt_template, delete_receipt_template | ✅ 5 | receipt_templates |
| `tax_reports.rs` | get_tax_reports, add_tax_report, delete_tax_report | ✅ 3 | tax_reports |
| `employee_schedules.rs` | get_employee_schedules, add_employee_schedule, update_employee_schedule, delete_employee_schedule | ✅ 4 | employee_schedules |
| `payrolls.rs` | get_payrolls, add_payroll, update_payroll, delete_payroll | ✅ 4 | payrolls |
| `reports.rs` | get_report_metadata, add_report_metadata, delete_report_metadata | ✅ 3 | report_metadata |
| `shifts.rs` | open_shift, close_shift, get_shifts, get_active_shift | ❌ **0 registered!** | shifts (not in migration!) |
| `hardware.rs` | print_thermal_receipt, trigger_cash_drawer, check_printer_status | ❌ **0 registered!** | N/A (ESC/POS, serial) |
| `auth.rs` | check_auth_required, has_users, verify_user, login, send_confirmation_code, verify_and_setup_account, change_password, ensure_superuser_exists, get_superuser_email | ✅ 9 | users |
| `dump.rs` | dump_to_json, dump_all, dump_unuploaded | ✅ 1 (dump_database) | all tables |
| `server.rs` | start_server, stop_server, server_status | ✅ 3 | — |
| `email.rs` | send_support_email | ✅ 1 | — |
| `db.rs` | export_database_cmd, import_database_cmd | ✅ 2 | — (file I/O) |

### 4.2 Critical Gaps

| Issue | Severity | Detail |
|-------|----------|--------|
| `shifts.rs` — 0 Tauri commands | 🔴 CRITICAL | open_shift, close_shift, get_shifts, get_active_shift all defined but **never registered** in `invoke_handler![]`. Frontend cannot call them. |
| `hardware.rs` — 0 Tauri commands | 🔴 CRITICAL | print_thermal_receipt, trigger_cash_drawer, check_printer_status defined but **never registered**. Thermal printing and cash drawer are dead code. |
| `shifts` table missing from migration | 🔴 CRITICAL | The shifts module references a `shifts` table that **doesn't exist** in the SQL migration. DB will error at runtime. |
| `get_sale_with_items` not registered | 🟡 MEDIUM | Exists in operations but no Tauri command — frontend can't fetch a sale with its items |
| `update_category` not registered | 🟡 LOW | Only get/add categories exposed; update/delete are internal |
| `delete_category` not registered | 🟡 LOW | Same as above |
| `inventory_alerts` no operations module | 🟡 LOW | Model + schema exist but no CRUD operations or Tauri commands |
| Missing `mark_*_uploaded` commands | 🟡 LOW | ingredients and employees have mark_uploaded in ops but not in commands |

---

## 5. Server API (pos-solo & pos-full)

Both pos-solo and pos-full use an **identical** Python/Sanic server with `_register_crud()` for automatic REST endpoints.

### 5.1 Registered CRUD Endpoints

| Resource | Route Pattern | HTTP Verbs |
|----------|--------------|------------|
| `products` | `/api/products` | GET, POST, PATCH, DELETE |
| `categories` | `/api/categories` | GET, POST, PATCH, DELETE |
| `customers` | `/api/customers` | GET, POST, PATCH, DELETE |
| `sales` | `/api/sales` | GET, POST, PATCH, DELETE |
| `sale-items` | `/api/sale-items` | GET, POST, PATCH, DELETE |
| `employees` | `/api/employees` | GET, POST, PATCH, DELETE |
| `inventory` | `/api/inventory` | GET, POST, PATCH, DELETE |
| `suppliers` | `/api/suppliers` | GET, POST, PATCH, DELETE |
| `purchase-orders` | `/api/purchase-orders` | GET, POST, PATCH, DELETE |
| `purchase-order-items` | `/api/purchase-order-items` | GET, POST, PATCH, DELETE |
| `kitchen-tickets` | `/api/kitchen-tickets` | GET, POST, PATCH, DELETE |
| `support-tickets` | `/api/support-tickets` | GET, POST, PATCH, DELETE |
| `payroll` | `/api/payroll` | GET, POST, PATCH, DELETE |
| `employee-schedules` | `/api/employee-schedules` | GET, POST, PATCH, DELETE |
| `tax-reports` | `/api/tax-reports` | GET, POST, PATCH, DELETE |
| `notes` | `/api/notes` | GET, POST, PATCH, DELETE |
| `ingredients` | `/api/ingredients` | GET, POST, PATCH, DELETE |
| `recipes` | `/api/recipes` | GET, POST, PATCH, DELETE |
| `receipt-templates` | `/api/receipt-templates` | GET, POST, PATCH, DELETE |
| `roles` | `/api/roles` | GET, POST, PATCH, DELETE |
| `inventory-adjustments` | `/api/inventory-adjustments` | GET, POST, PATCH, DELETE |
| **Managed variants** | `/api/managed/*` | GET, POST, PATCH, DELETE |
| **Sync specials** | `/api/heartbeats`, `/api/sync-logs`, `/api/sync-approvals` | GET, POST |
| **Config** | `/api/config/devices`, `/api/config/master`, `/api/config/cloud-links` | GET, POST, PATCH |

### 5.2 WebSocket

Both solo and full have `/ws/entities` for real-time entity streaming.

### 5.3 pos-mini vs pos-solo/full API Gap

| Feature | pos-mini (Tauri) | pos-solo/full (Server) |
|---------|-----------------|------------------------|
| `notes` | ❌ No module | ✅ `/api/notes` |
| `support-tickets` | ❌ | ✅ `/api/support-tickets` |
| `menu-items` / `menus` | ❌ | ✅ `/api/managed/menu-items` |
| `config/devices` | ❌ | ✅ with cloud links |
| `shifts` | ⚠️ ops exist, no cmd | ❌ No endpoint |
| `hardware` (printer/drawer) | ⚠️ ops exist, no cmd | ❌ No endpoint |
| WebSocket sync | ❌ | ✅ `/ws/entities` |

---

## 6. Frontend Pages

### 6.1 Complete Page Inventory

| Page | Route | pos-mini | pos-solo | pos-full | i18n Key | SideNav | Home Card |
|------|-------|:--------:|:--------:|:--------:|----------|:-------:|:---------:|
| Home | `/` | ✅ | ✅ | ✅ | `nav.home` | ✅ | — |
| Auth | `/auth` | ✅ | ✅ | ✅ | `auth.*` | — | — |
| Sale | `/sale` | ✅ | ✅ | ✅ | `sale.*` (156) | ✅ | ✅ |
| ProductManager | `/manager` | ✅ | ✅ | ✅ | `productManager.*` (48) | ✅ | ✅ |
| KitchenDisplay | `/kitchen` | ✅ | ✅ | ✅ | ❌ MISSING | ✅ | ✅ |
| Transactions | `/transactions` | ✅ | ✅ | ✅ | `transactions.*` (73) | ✅ | ✅ |
| InvoicePage | `/invoice` | ✅ | ✅ | ✅ | ❌ MISSING | ✅ | ✅ |
| Analytics | `/analytics` | ✅ | ✅ | ✅ | `analytics.*` (9) | ✅ | ✅ |
| Inventory | `/inventory` | ✅ | ✅ | ✅ | `inventory.*` (26) | ✅ | ✅ |
| Recipes | `/recipes` | ✅ | ✅ | ✅ | `recipes.*` (19) | ✅ | ✅ |
| Suppliers | `/suppliers` | ✅ | ✅ | ✅ | `suppliers.*` (7) | ✅ | ✅ |
| Customers | `/customers` | ✅ | ✅ | ✅ | `customers.*` (18) | ✅ | ✅ |
| Employees | `/employees` | ✅ | ✅ | ✅ | `employees.*` (12) | ✅ | ✅ |
| EmployeeSchedule | `/schedule` | ✅ | ✅ | ✅ | ❌ MISSING | ✅ | ✅ |
| Payroll | `/payroll` | ✅ | ✅ | ✅ | `payroll.*` (5) | ✅ | ✅ |
| Roles | `/roles` | ✅ | ✅ | ✅ | `roles.*` (11) | ✅ | ✅ |
| Reports | `/reports` | ✅ | ✅ | ✅ | `reports.*` (8) | ✅ | ✅ |
| TaxReports | `/tax-reports` | ✅ | ✅ | ✅ | `taxReports.*` (5) | ✅ | ✅ |
| ReceiptTemplates | `/receipt-templates` | ✅ | ✅ | ✅ | `receiptTemplates.*` (11) | ✅ | ✅ |
| Settings | `/settings` | ✅ | ✅ | ✅ | `settings.*` (62) | ✅ | ✅ |
| SupportChat | `/support-chat` | ✅ | ✅ | ✅ | `supportChat.*` (8) | ✅ | ✅ |
| About | `/about` | ✅ | ✅ | ✅ | `about.*` (3) | ✅ | ✅ |
| Notes | `/notes` | ❌ | ✅ | ✅ | `notes.*` (12) | — | ✅ |

### 6.2 i18n Coverage Gaps

| Page | Status | Notes |
|------|--------|-------|
| **KitchenDisplay** | ❌ No i18n group | All strings are hardcoded or use `nav.kitchen` |
| **InvoicePage** | ❌ No i18n group | Uses hardcoded English strings |
| **EmployeeSchedule** | ❌ No i18n group | Uses `employeeSchedule.*` which doesn't exist |
| All others | ✅ | Have dedicated i18n groups with 3–156 sub-keys |

---

## 7. Icon Audit

### 7.1 Icon Imports per Page (pos-mini)

| Page | react-icons/md | react-icons/fa | Total |
|------|---------------|----------------|-------|
| **Home** | MdPointOfSale, MdPeople, MdLocalShipping, MdKitchen, MdEvent, MdReceiptLong, MdAccountBalance, MdSecurity, MdDashboard | FaClipboardList, FaChartBar, FaHistory, FaCog, FaHeart, FaBoxes, FaUsers, FaMortarPestle, FaFileAlt, FaMoneyBillWave, FaComments, FaFileInvoiceDollar | 21 |
| **SideNav** | MdClose, MdPointOfSale, MdLogout, MdHelpOutline, MdPeople, MdLocalShipping, MdKitchen, MdEvent, MdReceiptLong, MdAccountBalance, MdSecurity | FaClipboardList, FaChartBar, FaHistory, FaBoxes, FaUsers, FaMortarPestle, FaFileAlt, FaCog, FaHeart, FaHome, FaMoneyBillWave, FaComments, FaFileInvoiceDollar | 24 |
| **Sale** | MdShoppingCart, MdCheckCircle, MdLocalPrintshop, MdFileDownload, MdSearch, MdClose, MdChevronRight, MdChevronLeft, MdTune | FaPlus, FaStore, FaTruck, FaHandPaper, FaUserTie, FaDoorOpen, FaMapMarkerAlt, FaFileInvoiceDollar | 17 |
| **Auth** | — | FaEnvelope, FaLock, FaUser, FaKey, FaCheck, FaArrowRight, FaShieldAlt, FaEye, FaEyeSlash | 9 |
| **ProductManager** | — | FaPlus, FaTrash, FaCheck, FaExclamationTriangle, FaImage, FaTimes, FaEdit, FaSearch | 8 |
| **Settings** | (imported as destructured group) | FaCog, FaPalette, FaGlobe, FaDatabase, FaSave, FaTrash, FaExclamationTriangle, FaInfoCircle, FaDownload, FaUpload, FaCheck, FaMoon, FaSun, FaPaintBrush, FaBuilding, FaStore, FaLeaf | 17 |
| **Inventory** | MdInventory, MdEdit, MdDelete, MdSearch, MdClose | FaBoxes, FaHistory, FaExclamationTriangle, FaPlus, FaSave | 10 |
| **Employees** | MdPeople, MdEdit, MdDelete, MdWork | FaUsers, FaUserTag, FaMoneyBillWave, FaPlus, FaSave, FaSearch, FaPhone, FaEnvelope, FaCalendarAlt | 13 |
| **Recipes** | MdRestaurantMenu, MdEdit, MdDelete, MdAdd, MdRemove | FaPlus, FaSave, FaSearch, FaCubes, FaUtensils | 10 |
| **Transactions** | MdReceipt, MdClose, MdSearch, MdEdit, MdDelete, MdFilterList | FaFileInvoiceDollar, FaDownload | 8 |
| **KitchenDisplay** | MdRestaurant, MdCheckCircle, MdAccessTime, MdSearch, MdClose | — | 5 |
| **Suppliers** | MdBusiness, MdPhone, MdEmail, MdLocationOn, MdAdd, MdEdit, MdDelete, MdSearch, MdClose | — | 9 |
| **Customers** | MdPerson, MdPhone, MdEmail, MdStars, MdAdd, MdEdit, MdDelete, MdSearch, MdClose | — | 9 |
| **Reports** | MdBarChart, MdAttachMoney, MdShoppingCart, MdTrendingUp, MdFileDownload, MdPictureAsPdf, MdDelete | FaFilePdf, FaDownload | 9 |
| **Payroll** | MdAttachMoney, MdAdd, MdDelete | — | 3 |
| **EmployeeSchedule** | MdSchedule, MdAdd, MdDelete | — | 3 |
| **TaxReports** | MdAccountBalance, MdAdd, MdDelete, MdSearch, MdClose | — | 5 |
| **Roles** | MdSecurity, MdAdd, MdEdit, MdDelete, MdSearch, MdClose | — | 6 |
| **ReceiptTemplates** | MdReceipt, MdAdd, MdEdit, MdDelete, MdSearch, MdClose | — | 6 |
| **SupportChat** | MdSupportAgent, MdInbox, MdRefresh, MdCircle | FaHeadset | 5 |
| **About** | — | FaCode, FaHeart, FaEnvelope, FaPaperPlane, FaCheck, FaExclamationTriangle | 6 |
| **InvoicePage** | MdDownload, MdPrint, MdAdd, MdDelete, MdClose, MdSearch, MdEdit | FaFileInvoiceDollar | 8 |
| **Notes** (solo/full) | MdNoteAdd, MdEdit, MdDelete, MdDrafts, MdSave, MdRestore, MdArchive, MdClose, MdSearch | FaStickyNote, FaSave, FaPlus, FaTrash, FaUndo | 14 |
| **Analytics** | MdTrendingUp, MdAttachMoney, MdShoppingCart | — | 3 |

### 7.2 SideNav Gradient Clash Audit

The 21 SideNav items use 16 unique gradient values, with **5 clashes**:

| Gradient | Used By | Clash? |
|----------|---------|--------|
| `from-teal-400 to-teal-500` | Home, Invoice | ⚠️ 2-way |
| `from-blue-400 to-blue-500` | productManager | ✅ Unique |
| `from-green-400 to-green-500` | newSale | ✅ Unique |
| `from-purple-400 to-purple-500` | analytics | ✅ Unique |
| `from-orange-400 to-orange-500` | **transactions, recipes, kitchen** | 🔴 3-way! |
| `from-emerald-400 to-emerald-500` | **inventory, payroll** | ⚠️ 2-way |
| `from-indigo-400 to-indigo-500` | **employees, taxReports** | ⚠️ 2-way |
| `from-rose-400 to-rose-500` | reports | ✅ Unique |
| `from-cyan-400 to-cyan-500` | **customers, supportChat** | ⚠️ 2-way |
| `from-amber-400 to-amber-500` | suppliers | ✅ Unique |
| `from-violet-400 to-violet-500` | schedule | ✅ Unique |
| `from-lime-400 to-lime-500` | receiptTemplates | ✅ Unique |
| `from-pink-400 to-pink-500` | about | ✅ Unique |
| `from-red-400 to-red-500` | roles | ✅ Unique |
| `from-gray-400 to-gray-500` | settings | ✅ Unique |

### 7.3 Home vs SideNav Completeness

**SideNav** has 21 items (including `home` which is the current page). **Home** has 20 cards organized in 5 categories. Every SideNav item (except `home`) has a corresponding card on the Home screen — **no missing items**:

| Home Category | SideNav Items Covered |
|---------------|----------------------|
| Sales & Operations | newSale, kitchen, transactions, invoice |
| Inventory & Products | productManager, inventory, recipes, suppliers |
| Staff & Customers | employees, schedule, payroll, customers, roles |
| Reports & Analytics | analytics, reports, taxReports |
| System | settings, receiptTemplates, supportChat, about |

> **Note:** `nav.notes` is only present in pos-solo and pos-full (added to the System category).

---

## 8. Data Flow Diagrams

### 8.1 pos-mini — Tauri Invoke Flow

```
┌──────────┐    invoke("get_products")    ┌──────────────┐
│ React    │ ──────────────────────────▶  │ Tauri IPC     │
│ (TSX)    │                              │ (Rust bridge) │
└──────────┘                              └──────┬───────┘
                                                 │
                              ┌──────────────────┘
                              ▼
                    ┌──────────────────┐
                    │ lib.rs           │
                    │ #[tauri::command]│
                    │ fn get_products()│
                    └──────┬───────────┘
                           │
                           ▼
                    ┌──────────────────┐
                    │ operations/      │
                    │ products.rs      │
                    │ get_products()   │
                    └──────┬───────────┘
                           │
                           ▼
                    ┌──────────────────┐
                    │ Diesel ORM       │
                    │ products::table  │
                    │ .load::<Product>()│
                    └──────┬───────────┘
                           │
                           ▼
                    ┌──────────────────┐
                    │ SQLite           │
                    │ pos.db           │
                    └──────────────────┘
```

### 8.2 pos-solo — REST API Flow

```
┌──────────┐   fetch("/api/products")   ┌──────────────┐
│ React    │ ────────────────────────▶  │ HTTP          │
│ (TSX)    │ ◀────────────────────────  │ localhost:8082│
└──────────┘   JSON response           └──────┬───────┘
                                               │
                              ┌────────────────┘
                              ▼
                    ┌──────────────────┐
                    │ Python Server   │
                    │ Sanic server     │
                    │ _register_crud() │
                    └──────┬───────────┘
                           │
                           ▼
                    ┌──────────────────┐
                    │ SQLite           │
                    │ pos.db           │
                    └──────────────────┘
```

### 8.3 pos-full — RTK Query Flow

```
┌──────────┐  RTK Query hook          ┌──────────────┐
│ React    │  useGetProductsQuery()   │ Redux Store  │
│ (TSX)    │ ◀─────────────────────── │ (cache)      │
└──────────┘                          └──────┬───────┘
                                              │ cache miss
                              ┌───────────────┘
                              ▼
                    ┌──────────────────┐
                    │ RTK Query        │
                    │ baseApi          │
                    │ fetch("/api/") │
                    └──────┬───────────┘
                           │
                           ▼
                    ┌──────────────────┐
                    │ Python Server   │
                    │ Sanic server     │
                    │ (same as solo)   │
                    └──────┬───────────┘
                           │
                           ▼
                    ┌──────────────────┐
                    │ SQLite           │
                    │ pos.db           │
                    └──────────────────┘
```

---

## 9. Seed Data Documentation

### 9.1 Seed Data Files

| File | Location | Tables Seeded | Brands |
|------|----------|---------------|--------|
| `up.sql` | `pos-mini/src-tauri/migrations/2026-01-01-000000_create_all/` | All 15 tables | POS KO |
| `up.sql` | `pos-solo/src-tauri/migrations/2026-01-01-000000_create_all/` | All 15 tables | POS KO |
| `up.sql` | `pos-full/src-tauri/migrations/2026-01-01-000000_create_all/` | All 15 tables | POS KO |
| `seed.rs` | `pos-mini/src-tauri/src/bin/` | Uses presets: all/base/gaming/coffee | 3 brands |
| `sync_state.json` | `pos-full/server/` | Runtime sync tracking (solo/full only) | — |

### 9.2 Seed Presets (seed.rs)

| Preset | Brand Name | Description |
|--------|-----------|-------------|
| `all` | Level Up Gaming Center | Layered: base + gaming + coffee |
| `base` | POS KO | Core restaurant data only |
| `gaming` | Level Up Gaming Center | Gaming center menu + stations |
| `coffee` | The Daily Grind | Coffee shop menu |

---

## 10. Summary of Issues Found

### Critical (🔴)

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | `shifts` Tauri commands not registered | lib.rs invoke_handler | Shift open/close broken |
| 2 | `shifts` table missing from SQL migration | up.sql | Runtime DB error |
| 3 | `hardware` (printer/drawer) commands not registered | lib.rs | Thermal printing dead code |

### Medium (🟡)

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 4 | `get_sale_with_items` not exposed as Tauri command | lib.rs | Can't fetch sale details |
| 5 | `update_category`/`delete_category` not exposed | lib.rs | Can't edit categories |
| 6 | `inventory_alerts` no operations module | ops/ | Feature inaccessible |

### Low (🟢)

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 7 | SideNav gradient color clashes (recipes, payroll, support) | SideNav.tsx | Visual inconsistency |
| 8 | Reports icon mismatch (FaFileAlt in nav vs MdBarChart in page) | SideNav.tsx, Reports.tsx | Navigation confusion |
| 9 | 3 pages missing i18n groups (KitchenDisplay, InvoicePage, EmployeeSchedule) | en.json | Hardcoded English strings |
| 10 | `notes` page in solo/full but not in mini | — | Feature gap |
| 11 | `support-tickets` API in server but not in mini Rust | — | Feature gap |

---

## 11. Recommendations

### Immediate Fixes

1. **Register shifts Tauri commands** in `invoke_handler![]` and add shifts table to migration
2. **Register hardware Tauri commands** in `invoke_handler![]`
3. **Register `get_sale_with_items`** as a Tauri command

### Quick Wins

4. Add i18n groups for KitchenDisplay, InvoicePage, EmployeeSchedule
5. Fix SideNav gradient color clashes for unique visual identity
6. Add `update_category`/`delete_category` Tauri commands
7. Either implement `inventory_alerts` operations or remove the dead model/schema

### Future Work

8. Add `notes` feature to pos-mini (port from solo/full)
9. Add `support-tickets` endpoint to pos-mini server
10. Unify Home card border colors across all pages (currently consistent but could use the theme system)

---

## 12. Version Comparison Quick Reference

```
                    pos-mini        pos-solo        pos-full
─────────────────────────────────────────────────────────────
Backend             Rust Tauri      Python Server  Python Server
Frontend→Backend    invoke() IPC    fetch() REST    RTK Query REST
DB Access           Diesel ORM      Server SQL     Server SQL
Total Tables        15              15              15
Rust Op Modules     26              N/A             N/A
Tauri Commands      100+            N/A             N/A
Server Endpoints   N/A             50+ CRUD        50+ CRUD
TS Pages            22              23 (+Notes)     23 (+Notes)
TS Types            30              30              30 (+RTK types)
i18n Groups         20/23           20/23           20/23
TypeScript Errors   0               0               0 (fixed)
```

---

*Audit generated by automated code analysis. All file paths relative to `projects/pos/`.*
