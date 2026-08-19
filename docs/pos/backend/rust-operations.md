# 🦀 Rust Operations Overview

> **Related Names:** `POS`, `Tauri`, `Diesel`, `SQLite`, `CRUD`, `Rust backend`, `operations`, `database`, `migrations`
> **Tags:** #rust #operations #pos #database #reference

Complete list of all 25 Rust operation modules in `projects/formints/src-tauri/src/operations/`.

> 💡 **Tip:** Every operation follows the same pattern: `pub fn operation_name(db_path: &PathBuf, ...) -> Result<T, String>`. The `db_path` is passed from `lib.rs` which resolves it from `DATABASE_URL` env var or platform app data dir.

---

## Module Index

### Core Business

| Module | Functions | Models | Customizable? |
|--------|-----------|--------|:---:|
| `auth.rs` | `check_auth_required`, `ensure_superuser_exists`, `login`, `verify_user`, `change_password`, `send_confirmation_code`, `has_users`, `get_user_count`, `get_superuser_email` | User, NewUser | 🔴 no |
| `products.rs` | `get_products`, `add_product`, `update_product`, `delete_product`, `mark_product_uploaded` | Product, NewProduct, UpdateProduct | 🟢 yes |
| `sales.rs` | `add_sale`, `get_sales`, `get_sale_with_items`, `update_sale`, `delete_sale`, `mark_sale_uploaded` | Sale, NewSale, SaleItem, NewSaleItem | 🟢 yes |
| `categories.rs` | `get_categories`, `add_category`, `update_category`, `delete_category` | Category, NewCategory, UpdateCategory | 🟢 yes |
| `customers.rs` | `get_customers`, `add_customer`, `update_customer`, `delete_customer`, `get_loyalty_transactions`, `add_loyalty_transaction` | Customer, NewCustomer, UpdateCustomer, LoyaltyTransaction | 🟢 yes |

### Inventory & Kitchen

| Module | Functions | Models | Customizable? |
|--------|-----------|--------|:---:|
| `inventory_transactions.rs` | `add_inventory_transaction`, `get_inventory_transactions`, `get_inventory_adjustments` | InventoryTransaction, NewInventoryTransaction, InventoryAdjustment, NewInventoryAdjustment | 🟢 yes |
| `ingredients.rs` | `get_ingredients`, `add_ingredient`, `update_ingredient`, `soft_delete_ingredient`, `mark_ingredient_uploaded` | Ingredient, NewIngredient, UpdateIngredient | 🟢 yes |
| `recipes.rs` | `get_recipes`, `get_recipe_with_ingredients`, `create_recipe`, `update_recipe`, `soft_delete_recipe`, `mark_recipe_uploaded`, `add_recipe_ingredient`, `update_recipe_ingredient`, `delete_recipe_ingredient` | Recipe, NewRecipe, UpdateRecipe, RecipeIngredient, NewRecipeIngredient, UpdateRecipeIngredient | 🟢 yes |
| `kitchen_tickets.rs` | `get_kitchen_tickets`, `add_kitchen_ticket`, `update_kitchen_ticket`, `delete_kitchen_ticket` | KitchenTicket, NewKitchenTicket, UpdateKitchenTicket | 🟢 yes |
| `delivery_types.rs` | `get_delivery_types`, `add_delivery_type`, `update_delivery_type`, `soft_delete_delivery_type` | DeliveryType, NewDeliveryType, UpdateDeliveryType | 🟢 yes |

### Employees & Scheduling

| Module | Functions | Models | Customizable? |
|--------|-----------|--------|:---:|
| `employees.rs` | `get_employees`, `add_employee`, `update_employee`, `soft_delete_employee`, `mark_employee_uploaded` | Employee, NewEmployee, UpdateEmployee | 🟢 yes |
| `employee_types.rs` | `get_employee_types`, `add_employee_type`, `update_employee_type`, `soft_delete_employee_type` | EmployeeType, NewEmployeeType, UpdateEmployeeType | 🟢 yes |
| `employee_schedules.rs` | `get_employee_schedules`, `add_employee_schedule`, `update_employee_schedule`, `delete_employee_schedule` | EmployeeSchedule, NewEmployeeSchedule, UpdateEmployeeSchedule | 🟢 yes |
| `payrolls.rs` | `get_payrolls`, `add_payroll`, `update_payroll`, `delete_payroll` | Payroll, NewPayroll, UpdatePayroll | 🟢 yes |
| `roles.rs` | `get_roles`, `add_role`, `update_role`, `soft_delete_role`, `get_user_roles`, `assign_role`, `remove_role` | Role, NewRole, UpdateRole | 🟢 yes |

### Reports & Finance

| Module | Functions | Models | Customizable? |
|--------|-----------|--------|:---:|
| `analytics.rs` | `get_analytics` | AnalyticsData, DailyRevenue, TopProduct, ProductDistribution, AnalyticsSummary | 🟢 yes |
| `reports.rs` | `get_report_metadata`, `add_report_metadata`, `delete_report_metadata` | ReportMetadata, NewReportMetadata | 🟢 yes |
| `tax_reports.rs` | `get_tax_reports`, `add_tax_report`, `delete_tax_report` | TaxReport, NewTaxReport | 🟢 yes |
| `transactions.rs` | `get_transactions`, `delete_transaction` | Transaction, TransactionItem | 🟢 yes |

### Supply Chain

| Module | Functions | Models | Customizable? |
|--------|-----------|--------|:---:|
| `suppliers.rs` | `get_suppliers`, `add_supplier`, `update_supplier`, `soft_delete_supplier` | Supplier, NewSupplier, UpdateSupplier | 🟢 yes |
| `purchase_orders.rs` | `get_purchase_orders`, `get_purchase_order_items`, `add_purchase_order`, `update_purchase_order`, `delete_purchase_order` | PurchaseOrder, PurchaseOrderItem, NewPurchaseOrder, NewPurchaseOrderItem | 🟢 yes |

### System

| Module | Functions | Models | Customizable? |
|--------|-----------|--------|:---:|
| `settings.rs` | `get_settings`, `save_settings` | Settings, UpdateSettings | 🟢 yes |
| `sidecar.rs` | `start_sidecar`, `stop_sidecar`, `sidecar_status` | — | 🔴 no |
| `dump.rs` | `dump_all`, `dump_unuploaded`, `dump_to_json` | DumpData | 🟢 yes |
| `receipt_templates.rs` | `get_receipt_templates`, `get_default_receipt_template`, `add_receipt_template`, `update_receipt_template`, `delete_receipt_template` | ReceiptTemplate, NewReceiptTemplate, UpdateReceiptTemplate | 🟢 yes |

> ⚠️ **Warning:** All modules marked 🔴 are security-critical or system-level. Modifying them can break auth, data integrity, or the sidecar lifecycle.

---

## Pattern Reference

### Standard CRUD Pattern

```rust
use crate::db::open_conn;
use crate::db::models::{Product, NewProduct, UpdateProduct};
use diesel::prelude::*;

pub fn get_products(db_path: &PathBuf) -> Result<Vec<Product>, String> {
    let conn = &mut open_conn(db_path)?;
    products::table.load::<Product>(conn).map_err(|e| e.to_string())
}

pub fn add_product(db_path: &PathBuf, new: NewProduct) -> Result<Product, String> {
    let conn = &mut open_conn(db_path)?;
    diesel::insert_into(products::table)
        .values(&new)
        .get_result(conn)
        .map_err(|e| e.to_string())
}
```

> 💡 **Tip:** To add a new operation module: create the `.rs` file → add to `operations/mod.rs` → add Tauri command in `lib.rs` → add TypeScript page.

---

→ [Back to Rust docs](README.md) | [POS Dev Guide](../../../guides/03-dev.md)
