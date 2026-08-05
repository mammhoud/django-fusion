# 📁 POS-KO Operations (`src-tauri/src/operations/`)

> **Related Names:** `operations`, `business logic`, `CRUD`, `Rust`, `Diesel`, `tauri commands`
> **Tags:** #rust #operations #business-logic #crud

25 business-logic modules, each following a uniform CRUD pattern. Every module connects to SQLite via `open_conn(&db_path)` and returns `Result<T, String>`.

```
operations/
├── auth.rs                  # 🔴 Account setup, login, password, superuser
├── analytics.rs             # 🟢 Dashboard aggregations
├── categories.rs            # 🟢 Product categories
├── products.rs              # 🟢 Product CRUD
├── sales.rs                 # 🔴 Sale + sale_items (atomic insert)
├── transactions.rs          # 🟢 Transaction history
├── settings.rs              # 🟢 Restaurant configuration
├── ingredients.rs           # 🟢 Ingredient CRUD (soft-delete)
├── recipes.rs               # 🟢 Recipe + recipe_ingredients
├── inventory_transactions.rs # 🔴 Stock movements + adjustments
├── delivery_types.rs        # 🟢 Delivery type CRUD (soft-delete)
├── employee_types.rs        # 🟢 Employee type CRUD (soft-delete)
├── employees.rs             # 🟢 Employee CRUD (soft-delete)
├── employee_schedules.rs    # 🟢 Shift scheduling
├── payrolls.rs              # 🟢 Payslip generation
├── roles.rs                 # 🟢 RBAC management
├── suppliers.rs             # 🟢 Supplier CRUD (soft-delete)
├── purchase_orders.rs       # 🟢 Procurement workflow
├── customers.rs             # 🟢 Customer + loyalty CRUD
├── kitchen_tickets.rs       # 🟢 Kitchen display workflow
├── receipt_templates.rs     # 🟢 Receipt template CRUD
├── tax_reports.rs           # 🟢 Tax report CRUD
├── reports.rs               # 🟢 Report metadata
├── dump.rs                  # 🟢 JSON dump for backup/cloud sync
└── sidecar.rs               # 🔴 Sidecar lifecycle (start/stop/status)
```

## Customization Tags

| Tag | Modules | Notes |
|-----|---------|-------|
| 🔴 `not-customizable` | auth, sales, inventory_transactions, sidecar | Core infrastructure |
| 🟢 `customizable` | All other 21 modules | Freely modify CRUD logic |

## Uniform CRUD Pattern

```rust
pub fn get_entities(db_path: &PathBuf) -> Result<Vec<Entity>, String> { ... }
pub fn add_entity(db_path: &PathBuf, input: NewEntity) -> Result<Entity, String> { ... }
pub fn update_entity(db_path: &PathBuf, id: i32, update: UpdateEntity) -> Result<Entity, String> { ... }
pub fn delete_entity(db_path: &PathBuf, id: i32) -> Result<(), String> { ... }
```

## Soft-Delete Modules

These modules use `is_active` boolean instead of hard deletes:

`ingredients`, `recipes`, `delivery_types`, `employee_types`, `employees`, `roles`, `suppliers`

```rust
pub fn get_entities(db_path: &PathBuf, include_inactive: bool) -> Result<Vec<Entity>, String>
pub fn soft_delete_entity(db_path: &PathBuf, id: i32) -> Result<(), String>
```

## Command Registration

Each operation is exposed as a Tauri command in `lib.rs`:

```rust
#[tauri::command]
fn get_products(app: AppHandle) -> Result<Vec<Product>, String> {
    let db_path = get_db_path(&app)?;
    products::get_products(&db_path)
}
```

## Adding a New Operation

1. Create `operations/my_domain.rs` with CRUD functions
2. Add `pub mod my_domain;` to `operations/mod.rs`
3. Register command in `lib.rs` with `#[tauri::command]`
4. Add to `invoke_handler` list
5. Call from React: `const data = await invoke('get_data');`

## Reference

- [Rust Code Reference →](../../docs/rust-code.md)
- [Operations Docs →](../../../docs/rust/operations.md)
- [Database Layer →](../db/README.md)
