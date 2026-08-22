pub mod db;
pub mod operations;
pub mod email;
pub mod macros;

use db::{get_db_path, run_migrations};
use operations::*;
use operations::delivery_zones;
use tauri::{AppHandle, Emitter, Manager};
use tauri::tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent};
use tauri::menu::{MenuBuilder, MenuItemBuilder};

// Load environment variables at startup.
// dotenvy::dotenv() looks in cwd, but Tauri runs from src-tauri/ or the
// app bundle — not the project root where .env lives.  Search the cwd and
// every ancestor of the executable (target/debug → target → src-tauri →
// project root) and MERGE every `.env` found.  `dotenvy::from_path` never
// overrides an already-set variable, so the project-root `.env` (auth/SMTP
// credentials) and a closer `src-tauri/.env` (e.g. DATABASE_URL) combine
// instead of one shadowing the other.
fn load_env() {
    let exe_dir = std::env::current_exe()
        .ok()
        .and_then(|e| e.parent().map(|p| p.to_path_buf()));

    let mut candidates: Vec<std::path::PathBuf> = Vec::new();
    if let Ok(cwd) = std::env::current_dir() {
        candidates.push(cwd.join(".env"));
    }

    // Walk up from the exe dir, bounded so we never read stray `~/.env` or
    // `/.env` files outside the project. In dev the exe lives at
    // src-tauri/target/debug/, so depth 0-3 covers target, src-tauri and the
    // project root (formint-pos) where the credentials .env lives.
    let home = std::env::var_os("HOME").map(std::path::PathBuf::from);
    let mut dir = exe_dir;
    let mut depth = 0u32;
    while let Some(d) = dir {
        let at_home = home.as_ref().map_or(false, |h| d == *h);
        if at_home || depth >= 6 {
            break;
        }
        candidates.push(d.join(".env"));
        dir = d.parent().map(|p| p.to_path_buf());
        depth += 1;
    }

    // Load root-most first so closer files only add, never clobber.
    candidates.reverse();
    let mut seen = std::collections::HashSet::new();
    candidates.retain(|p| seen.insert(p.clone()));

    let mut loaded = false;
    for path in &candidates {
        if path.exists() {
            match dotenvy::from_path(path) {
                Ok(_) => {
                    loaded = true;
                    eprintln!("[env] loaded {}", path.display());
                }
                Err(e) => eprintln!("[env] failed {}: {}", path.display(), e),
            }
        }
    }

    if !loaded {
        eprintln!(
            "[env] .env not found (searched: {}). Using OS environment / defaults.",
            candidates
                .iter()
                .map(|p| p.display().to_string())
                .collect::<Vec<_>>()
                .join(", ")
        );
    }
}

// ---- CRUD: products, categories, ingredients, recipes (via macro) ----
register_crud!(products => product, db::models::Product, db::models::NewProduct, db::models::UpdateProduct,
    emit "product-updated");
register_crud!(categories => category, db::models::Category, db::models::NewCategory, db::models::UpdateCategory);
register_crud!(ingredients => ingredient, db::models::Ingredient, db::models::NewIngredient, db::models::UpdateIngredient,
    emit "inventory-changed", filter include_inactive: bool, soft);
register_crud!(recipes => recipe, db::models::Recipe, db::models::NewRecipe, db::models::UpdateRecipe,
    filter include_inactive: bool, soft);

// ---- Custom product commands (beyond standard CRUD) ----
#[tauri::command]
fn mark_product_uploaded(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    products::mark_product_uploaded(&db_path, id)
}

// ---- Sale commands ----
#[tauri::command]
fn add_sale(
    app: AppHandle,
    sale: db::models::NewSale,
    items: Vec<db::models::NewSaleItem>,
) -> Result<db::models::Sale, String> {
    let db_path = get_db_path(&app)?;
    sales::add_sale(&db_path, sale, items)
}

#[tauri::command]
fn get_sales(app: AppHandle) -> Result<Vec<db::models::Sale>, String> {
    let db_path = get_db_path(&app)?;
    sales::get_sales(&db_path)
}

#[tauri::command]
fn update_sale(app: AppHandle, id: i32, update: db::models::UpdateSale) -> Result<db::models::Sale, String> {
    let db_path = get_db_path(&app)?;
    sales::update_sale(&db_path, id, update)
}

#[tauri::command]
fn delete_sale(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    sales::delete_sale(&db_path, id)
}

#[tauri::command]
fn refund_sale(app: AppHandle, sale_id: i32) -> Result<db::models::Sale, String> {
    let db_path = get_db_path(&app)?;
    sales::refund_sale(&db_path, sale_id)
}

#[tauri::command]
fn mark_sale_uploaded(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    sales::mark_sale_uploaded(&db_path, id)
}

// ---- Transaction commands ----
#[tauri::command]
fn get_transactions(app: AppHandle) -> Result<Vec<transactions::Transaction>, String> {
    let db_path = get_db_path(&app)?;
    transactions::get_transactions(&db_path)
}

#[tauri::command]
fn delete_transaction(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    transactions::delete_transaction(&db_path, id)
}

// ---- Settings commands ----
#[tauri::command]
fn get_settings(app: AppHandle) -> Result<db::models::Settings, String> {
    let db_path = get_db_path(&app)?;
    settings::get_settings(&db_path)
}

#[tauri::command]
fn save_settings(app: AppHandle, settings: db::models::UpdateSettings) -> Result<db::models::Settings, String> {
    let db_path = get_db_path(&app)?;
    settings::save_settings(&db_path, settings)
}

// ---- Analytics commands ----
#[tauri::command]
fn get_analytics(app: AppHandle) -> Result<analytics::AnalyticsData, String> {
    let db_path = get_db_path(&app)?;
    analytics::get_analytics(&db_path)
}

#[tauri::command]
fn get_revenue_by_payment_method(app: AppHandle) -> Result<Vec<analytics::PaymentMethodRevenue>, String> {
    let db_path = get_db_path(&app)?;
    analytics::get_revenue_by_payment_method(&db_path)
}

// ---- Recipe child-entity commands (stay manual — complex signatures) ----
#[tauri::command]
fn create_recipe(
    app: AppHandle,
    recipe: db::models::NewRecipe,
    ingredients: Vec<db::models::NewRecipeIngredient>,
) -> Result<db::models::Recipe, String> {
    let db_path = get_db_path(&app)?;
    recipes::create_recipe(&db_path, recipe, ingredients)
}

#[tauri::command]
fn get_recipe_ingredients(app: AppHandle, recipe_id: i32) -> Result<Vec<db::models::RecipeIngredient>, String> {
    let db_path = get_db_path(&app)?;
    let (_, ingredients) = recipes::get_recipe_with_ingredients(&db_path, recipe_id)?;
    Ok(ingredients)
}

#[tauri::command]
fn add_recipe_ingredient(
    app: AppHandle,
    ingredient: db::models::NewRecipeIngredient,
) -> Result<db::models::RecipeIngredient, String> {
    let db_path = get_db_path(&app)?;
    recipes::add_recipe_ingredient(&db_path, ingredient)
}

#[tauri::command]
fn delete_recipe_ingredient(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    recipes::delete_recipe_ingredient(&db_path, id)
}

// ---- Delivery Type commands ----
#[tauri::command]
fn get_delivery_types(app: AppHandle, include_inactive: bool) -> Result<Vec<db::models::DeliveryType>, String> {
    let db_path = get_db_path(&app)?;
    delivery_types::get_delivery_types(&db_path, include_inactive)
}

#[tauri::command]
fn add_delivery_type(app: AppHandle, delivery_type: db::models::NewDeliveryType) -> Result<db::models::DeliveryType, String> {
    let db_path = get_db_path(&app)?;
    delivery_types::add_delivery_type(&db_path, delivery_type)
}

#[tauri::command]
fn update_delivery_type(app: AppHandle, id: i32, update: db::models::UpdateDeliveryType) -> Result<db::models::DeliveryType, String> {
    let db_path = get_db_path(&app)?;
    delivery_types::update_delivery_type(&db_path, id, update)
}

#[tauri::command]
fn soft_delete_delivery_type(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    delivery_types::soft_delete_delivery_type(&db_path, id)
}

// ---- Delivery Zone commands ----
#[tauri::command]
fn get_delivery_zones(app: AppHandle, include_inactive: bool) -> Result<Vec<db::models::DeliveryZone>, String> {
    let db_path = get_db_path(&app)?;
    delivery_zones::get_delivery_zones(&db_path, include_inactive)
}

#[tauri::command]
fn add_delivery_zone(app: AppHandle, zone: db::models::NewDeliveryZone) -> Result<db::models::DeliveryZone, String> {
    let db_path = get_db_path(&app)?;
    delivery_zones::add_delivery_zone(&db_path, zone)
}

#[tauri::command]
fn update_delivery_zone(app: AppHandle, id: i32, update: db::models::UpdateDeliveryZone) -> Result<db::models::DeliveryZone, String> {
    let db_path = get_db_path(&app)?;
    delivery_zones::update_delivery_zone(&db_path, id, update)
}

#[tauri::command]
fn soft_delete_delivery_zone(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    delivery_zones::soft_delete_delivery_zone(&db_path, id)
}

// ---- Employee Type commands ----
#[tauri::command]
fn get_employee_types(app: AppHandle, include_inactive: bool) -> Result<Vec<db::models::EmployeeType>, String> {
    let db_path = get_db_path(&app)?;
    employee_types::get_employee_types(&db_path, include_inactive)
}

#[tauri::command]
fn add_employee_type(app: AppHandle, employee_type: db::models::NewEmployeeType) -> Result<db::models::EmployeeType, String> {
    let db_path = get_db_path(&app)?;
    employee_types::add_employee_type(&db_path, employee_type)
}

#[tauri::command]
fn update_employee_type(app: AppHandle, id: i32, update: db::models::UpdateEmployeeType) -> Result<db::models::EmployeeType, String> {
    let db_path = get_db_path(&app)?;
    employee_types::update_employee_type(&db_path, id, update)
}

#[tauri::command]
fn soft_delete_employee_type(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    employee_types::soft_delete_employee_type(&db_path, id)
}

/// Best-effort audit-log entry. Failures are non-fatal (the primary operation
/// already succeeded); we only log a warning so the audit trail never blocks
/// the caller.
fn log_user_action(db_path: &std::path::PathBuf, action: &str, entity_type: &str, entity_id: i32, details: serde_json::Value) {
    if let Err(e) = user_actions::add_user_action(
        db_path,
        db::models::NewUserAction {
            action: action.to_string(),
            entity_type: Some(entity_type.to_string()),
            entity_id: Some(entity_id),
            details: Some(details.to_string()),
            user_id: None,
        },
    ) {
        eprintln!("[audit] failed to record user action '{action}': {e}");
    }
}

// ---- Employee commands ----
#[tauri::command]
fn get_employees(app: AppHandle, include_inactive: bool) -> Result<Vec<db::models::Employee>, String> {
    let db_path = get_db_path(&app)?;
    employees::get_employees(&db_path, include_inactive)
}

#[tauri::command]
fn add_employee(app: AppHandle, employee: db::models::NewEmployee) -> Result<db::models::Employee, String> {
    let db_path = get_db_path(&app)?;
    let result = employees::add_employee(&db_path, employee)?;
    // Audit trail — record the "addition record" for this user/employee.
    log_user_action(
        &db_path,
        "add_employee",
        "employee",
        result.id,
        serde_json::json!({
            "name": result.name,
            "employee_type_id": result.employee_type_id,
        }),
    );
    if let Err(e) = app.emit("employees-updated", serde_json::json!({"type": "added"})) {
        eprintln!("[events] failed to emit employees-updated: {e}");
    }
    Ok(result)
}

#[tauri::command]
fn update_employee(app: AppHandle, id: i32, update: db::models::UpdateEmployee) -> Result<db::models::Employee, String> {
    let db_path = get_db_path(&app)?;
    let result = employees::update_employee(&db_path, id, update)?;
    log_user_action(
        &db_path,
        "update_employee",
        "employee",
        id,
        serde_json::json!({
            "name": result.name,
            "is_active": result.is_active,
            "employee_type_id": result.employee_type_id,
        }),
    );
    if let Err(e) = app.emit("employees-updated", serde_json::json!({"type": "updated"})) {
        eprintln!("[events] failed to emit employees-updated: {e}");
    }
    Ok(result)
}

#[tauri::command]
fn soft_delete_employee(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    employees::soft_delete_employee(&db_path, id)?;
    log_user_action(&db_path, "deactivate_employee", "employee", id, serde_json::json!({}));
    if let Err(e) = app.emit("employees-updated", serde_json::json!({"type": "deleted"})) {
        eprintln!("[events] failed to emit employees-updated: {e}");
    }
    Ok(())
}

// ---- Inventory Transaction commands ----
#[tauri::command]
fn get_inventory_transactions(
    app: AppHandle,
    ingredient_id: Option<i32>,
) -> Result<Vec<db::models::InventoryTransaction>, String> {
    let db_path = get_db_path(&app)?;
    inventory_transactions::get_inventory_transactions(&db_path, ingredient_id)
}

#[tauri::command]
fn get_inventory_adjustments(
    app: AppHandle,
    ingredient_id: Option<i32>,
) -> Result<Vec<db::models::InventoryAdjustment>, String> {
    let db_path = get_db_path(&app)?;
    inventory_transactions::get_inventory_adjustments(&db_path, ingredient_id)
}

#[tauri::command]
fn delete_inventory_adjustment(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    let result = inventory_transactions::delete_inventory_adjustment(&db_path, id)?;
    if let Err(e) = app.emit("inventory-changed", serde_json::json!({"type": "adjustment-deleted", "id": id})) {
        eprintln!("[events] failed to emit inventory-changed: {e}");
    }
    Ok(result)
}

#[tauri::command]
fn add_inventory_transaction(
    app: AppHandle,
    transaction: db::models::NewInventoryTransaction,
    adjustment_reason: Option<String>,
    created_by: Option<String>,
) -> Result<db::models::InventoryTransaction, String> {
    let db_path = get_db_path(&app)?;
    let result = inventory_transactions::add_inventory_transaction(&db_path, transaction, adjustment_reason, created_by)?;
    if let Err(e) = app.emit("inventory-changed", serde_json::json!({"type": "transaction"})) {
        eprintln!("[events] failed to emit inventory-changed: {e}");
    }
    Ok(result)
}

// ---- Dump commands ----
#[tauri::command]
fn dump_database(app: AppHandle, only_unuploaded: bool) -> Result<String, String> {
    let db_path = get_db_path(&app)?;
    dump::dump_to_json(&db_path, only_unuploaded)
        .map_err(|e| e.to_string())
}

// ---- Auth commands ----
#[tauri::command]
fn check_auth_required(app: AppHandle) -> Result<bool, String> {
    let db_path = get_db_path(&app)?;
    auth::check_auth_required(&db_path)
}

#[tauri::command]
fn get_superuser_email() -> Option<String> {
    auth::get_superuser_email()
}

#[tauri::command]
fn has_users(app: AppHandle) -> Result<bool, String> {
    let db_path = get_db_path(&app)?;
    auth::has_users(&db_path)
}

#[tauri::command]
fn get_user_count(app: AppHandle) -> Result<i64, String> {
    let db_path = get_db_path(&app)?;
    auth::get_user_count(&db_path)
}

#[tauri::command]
fn verify_user(app: AppHandle, email: String) -> Result<db::models::User, String> {
    let db_path = get_db_path(&app)?;
    auth::verify_user(&db_path, email)
}

#[tauri::command]
fn send_auth_confirmation_code(app: AppHandle, email: String) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    auth::send_confirmation_code(&db_path, email)
}

#[tauri::command]
fn setup_account(
    app: AppHandle,
    email: String,
    code: String,
    password: String,
    name: String,
) -> Result<db::models::User, String> {
    let db_path = get_db_path(&app)?;
    auth::verify_and_setup_account(&db_path, email, code, password, name)
}

#[tauri::command]
fn login_user(
    app: AppHandle,
    email: String,
    password: String,
) -> Result<db::models::User, String> {
    let db_path = get_db_path(&app)?;
    auth::login(&db_path, email, password)
}

#[tauri::command]
fn request_password_reset(app: AppHandle, email: String) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    auth::request_password_reset(&db_path, email)
}

#[tauri::command]
fn reset_password_cmd(
    app: AppHandle,
    email: String,
    code: String,
    new_password: String,
) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    auth::reset_password(&db_path, email, code, new_password)
}

#[tauri::command]
fn change_password_cmd(
    app: AppHandle,
    email: String,
    old_password: String,
    new_password: String,
) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    auth::change_password(&db_path, email, old_password, new_password)
}

// ---- Permission Catalog ----
#[tauri::command]
fn get_permission_catalog() -> Vec<roles::PermissionDef> {
    roles::get_permission_catalog()
}

// ---- Roles commands ----
#[tauri::command]
fn get_roles(app: AppHandle) -> Result<Vec<db::models::Role>, String> {
    let db_path = get_db_path(&app)?;
    roles::get_roles(&db_path)
}

#[tauri::command]
fn add_role(app: AppHandle, role: db::models::NewRole) -> Result<db::models::Role, String> {
    let db_path = get_db_path(&app)?;
    roles::add_role(&db_path, role)
}

#[tauri::command]
fn update_role(app: AppHandle, id: i32, update: db::models::UpdateRole) -> Result<db::models::Role, String> {
    let db_path = get_db_path(&app)?;
    roles::update_role(&db_path, id, update)
}

#[tauri::command]
fn soft_delete_role(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    roles::soft_delete_role(&db_path, id)
}

#[tauri::command]
fn get_user_roles(app: AppHandle, user_id: i32) -> Result<Vec<db::models::Role>, String> {
    let db_path = get_db_path(&app)?;
    roles::get_user_roles(&db_path, user_id)
}

#[tauri::command]
fn assign_role(app: AppHandle, user_id: i32, role_id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    roles::assign_role(&db_path, user_id, role_id)
}

#[tauri::command]
fn remove_role(app: AppHandle, user_id: i32, role_id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    roles::remove_role(&db_path, user_id, role_id)
}

// ---- Suppliers commands ----
#[tauri::command]
fn get_suppliers(app: AppHandle, include_inactive: bool) -> Result<Vec<db::models::Supplier>, String> {
    let db_path = get_db_path(&app)?;
    suppliers::get_suppliers(&db_path, include_inactive)
}

#[tauri::command]
fn add_supplier(app: AppHandle, supplier: db::models::NewSupplier) -> Result<db::models::Supplier, String> {
    let db_path = get_db_path(&app)?;
    suppliers::add_supplier(&db_path, supplier)
}

#[tauri::command]
fn update_supplier(app: AppHandle, id: i32, update: db::models::UpdateSupplier) -> Result<db::models::Supplier, String> {
    let db_path = get_db_path(&app)?;
    suppliers::update_supplier(&db_path, id, update)
}

#[tauri::command]
fn soft_delete_supplier(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    suppliers::soft_delete_supplier(&db_path, id)
}

// ---- Purchase Orders commands ----
#[tauri::command]
fn get_purchase_orders(app: AppHandle) -> Result<Vec<db::models::PurchaseOrder>, String> {
    let db_path = get_db_path(&app)?;
    purchase_orders::get_purchase_orders(&db_path)
}

#[tauri::command]
fn get_purchase_order_items(app: AppHandle, order_id: i32) -> Result<Vec<db::models::PurchaseOrderItem>, String> {
    let db_path = get_db_path(&app)?;
    purchase_orders::get_purchase_order_items(&db_path, order_id)
}

#[tauri::command]
fn add_purchase_order(
    app: AppHandle,
    order: db::models::NewPurchaseOrder,
    items: Vec<db::models::NewPurchaseOrderItem>,
) -> Result<db::models::PurchaseOrder, String> {
    let db_path = get_db_path(&app)?;
    purchase_orders::add_purchase_order(&db_path, order, items)
}

#[tauri::command]
fn update_purchase_order(app: AppHandle, id: i32, update: db::models::UpdatePurchaseOrder) -> Result<db::models::PurchaseOrder, String> {
    let db_path = get_db_path(&app)?;
    purchase_orders::update_purchase_order(&db_path, id, update)
}

#[tauri::command]
fn delete_purchase_order(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    purchase_orders::delete_purchase_order(&db_path, id)
}

// ---- Customers commands ----
#[tauri::command]
fn get_customers(app: AppHandle) -> Result<Vec<db::models::Customer>, String> {
    let db_path = get_db_path(&app)?;
    customers::get_customers(&db_path)
}

#[tauri::command]
fn add_customer(app: AppHandle, customer: db::models::NewCustomer) -> Result<db::models::Customer, String> {
    let db_path = get_db_path(&app)?;
    let result = customers::add_customer(&db_path, customer)?;
    if let Err(e) = app.emit("customers-updated", serde_json::json!({"type": "added"})) {
        eprintln!("[events] failed to emit customers-updated: {e}");
    }
    Ok(result)
}

#[tauri::command]
fn update_customer(app: AppHandle, id: i32, update: db::models::UpdateCustomer) -> Result<db::models::Customer, String> {
    let db_path = get_db_path(&app)?;
    let result = customers::update_customer(&db_path, id, update)?;
    if let Err(e) = app.emit("customers-updated", serde_json::json!({"type": "updated"})) {
        eprintln!("[events] failed to emit customers-updated: {e}");
    }
    Ok(result)
}

#[tauri::command]
fn delete_customer(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    customers::delete_customer(&db_path, id)?;
    if let Err(e) = app.emit("customers-updated", serde_json::json!({"type": "deleted"})) {
        eprintln!("[events] failed to emit customers-updated: {e}");
    }
    Ok(())
}

#[tauri::command]
fn get_loyalty_transactions(app: AppHandle, customer_id: i32) -> Result<Vec<db::models::LoyaltyTransaction>, String> {
    let db_path = get_db_path(&app)?;
    customers::get_loyalty_transactions(&db_path, customer_id)
}

#[tauri::command]
fn get_all_loyalty_transactions(app: AppHandle, limit: Option<i64>) -> Result<Vec<customers::LoyaltyReportRow>, String> {
    let db_path = get_db_path(&app)?;
    customers::get_all_loyalty_transactions(&db_path, limit)
}

#[tauri::command]
fn add_loyalty_transaction(app: AppHandle, transaction: db::models::NewLoyaltyTransaction) -> Result<db::models::LoyaltyTransaction, String> {
    let db_path = get_db_path(&app)?;
    customers::add_loyalty_transaction(&db_path, transaction)
}

// ---- Receipt Templates commands ----
#[tauri::command]
fn get_notes(app: AppHandle) -> Result<Vec<db::models::Note>, String> {
    let db_path = get_db_path(&app)?;
    notes::get_notes(&db_path)
}

#[tauri::command]
fn get_selectable_notes(app: AppHandle) -> Result<Vec<db::models::Note>, String> {
    let db_path = get_db_path(&app)?;
    notes::get_selectable_notes(&db_path)
}

#[tauri::command]
fn get_default_note(app: AppHandle) -> Result<db::models::Note, String> {
    let db_path = get_db_path(&app)?;
    notes::get_default_note(&db_path)
}

#[tauri::command]
fn add_note(app: AppHandle, template: db::models::NewNote) -> Result<db::models::Note, String> {
    let db_path = get_db_path(&app)?;
    notes::add_note(&db_path, template)
}

#[tauri::command]
fn update_note(app: AppHandle, id: i32, update: db::models::UpdateNote) -> Result<db::models::Note, String> {
    let db_path = get_db_path(&app)?;
    notes::update_note(&db_path, id, update)
}

#[tauri::command]
fn delete_note(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    notes::delete_note(&db_path, id)
}

// ---- Coupon commands ----
#[tauri::command]
fn get_coupons(app: AppHandle) -> Result<Vec<db::models::Coupon>, String> {
    let db_path = get_db_path(&app)?;
    coupons::get_coupons(&db_path)
}

#[tauri::command]
fn get_active_coupons(app: AppHandle) -> Result<Vec<db::models::Coupon>, String> {
    let db_path = get_db_path(&app)?;
    coupons::get_active_coupons(&db_path)
}

#[tauri::command]
fn add_coupon(app: AppHandle, template: db::models::NewCoupon) -> Result<db::models::Coupon, String> {
    let db_path = get_db_path(&app)?;
    coupons::add_coupon(&db_path, template)
}

#[tauri::command]
fn update_coupon(app: AppHandle, id: i32, update: db::models::UpdateCoupon) -> Result<db::models::Coupon, String> {
    let db_path = get_db_path(&app)?;
    coupons::update_coupon(&db_path, id, update)
}

#[tauri::command]
fn delete_coupon(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    coupons::delete_coupon(&db_path, id)
}

// ---- Badge (loyalty rewards) commands ----
#[tauri::command]
fn get_badges(app: AppHandle) -> Result<Vec<db::models::Badge>, String> {
    let db_path = get_db_path(&app)?;
    badges::get_badges(&db_path)
}

#[tauri::command]
fn add_badge(app: AppHandle, badge: db::models::NewBadge) -> Result<db::models::Badge, String> {
    let db_path = get_db_path(&app)?;
    badges::add_badge(&db_path, badge)
}

#[tauri::command]
fn update_badge(app: AppHandle, id: i32, update: db::models::UpdateBadge) -> Result<db::models::Badge, String> {
    let db_path = get_db_path(&app)?;
    badges::update_badge(&db_path, id, update)
}

#[tauri::command]
fn delete_badge(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    badges::delete_badge(&db_path, id)
}

// ---- User Action audit log commands ----
#[tauri::command]
fn add_user_action(app: AppHandle, action: db::models::NewUserAction) -> Result<db::models::UserAction, String> {
    let db_path = get_db_path(&app)?;
    user_actions::add_user_action(&db_path, action)
}

#[tauri::command]
fn get_user_actions(app: AppHandle, limit: Option<i64>) -> Result<Vec<db::models::UserAction>, String> {
    let db_path = get_db_path(&app)?;
    user_actions::get_user_actions(&db_path, limit)
}

#[tauri::command]
fn get_user_actions_for_entity(
    app: AppHandle,
    entity_type: String,
    entity_id: i32,
    limit: Option<i64>,
) -> Result<Vec<db::models::UserAction>, String> {
    let db_path = get_db_path(&app)?;
    user_actions::get_user_actions_for_entity(&db_path, &entity_type, entity_id, limit)
}

// ---- Recipe Notes commands ----
#[tauri::command]
fn get_recipe_notes(app: AppHandle, recipe_id: i32) -> Result<Vec<db::models::Note>, String> {
    let db_path = get_db_path(&app)?;
    notes::get_recipe_notes(&db_path, recipe_id)
}

#[tauri::command]
fn add_recipe_note(app: AppHandle, template: db::models::NewNote) -> Result<db::models::Note, String> {
    let db_path = get_db_path(&app)?;
    notes::add_recipe_note(&db_path, template)
}

// ---- Tax Reports commands ----
#[tauri::command]
fn get_tax_reports(app: AppHandle) -> Result<Vec<db::models::TaxReport>, String> {
    let db_path = get_db_path(&app)?;
    tax_reports::get_tax_reports(&db_path)
}

#[tauri::command]
fn add_tax_report(app: AppHandle, report: db::models::NewTaxReport) -> Result<db::models::TaxReport, String> {
    let db_path = get_db_path(&app)?;
    tax_reports::add_tax_report(&db_path, report)
}

#[tauri::command]
fn delete_tax_report(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    tax_reports::delete_tax_report(&db_path, id)
}

// ---- Employee Schedules commands ----
#[tauri::command]
fn get_employee_schedules(app: AppHandle, employee_id: Option<i32>) -> Result<Vec<db::models::EmployeeSchedule>, String> {
    let db_path = get_db_path(&app)?;
    employee_schedules::get_employee_schedules(&db_path, employee_id)
}

#[tauri::command]
fn add_employee_schedule(app: AppHandle, schedule: db::models::NewEmployeeSchedule) -> Result<db::models::EmployeeSchedule, String> {
    let db_path = get_db_path(&app)?;
    employee_schedules::add_employee_schedule(&db_path, schedule)
}

#[tauri::command]
fn update_employee_schedule(app: AppHandle, id: i32, update: db::models::UpdateEmployeeSchedule) -> Result<db::models::EmployeeSchedule, String> {
    let db_path = get_db_path(&app)?;
    employee_schedules::update_employee_schedule(&db_path, id, update)
}

#[tauri::command]
fn delete_employee_schedule(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    employee_schedules::delete_employee_schedule(&db_path, id)
}

// ---- Finance & Budget commands ----
#[tauri::command]
fn get_finance_transactions(app: AppHandle) -> Result<Vec<db::models::FinanceTransaction>, String> {
    let db_path = get_db_path(&app)?;
    finance::get_finance_transactions(&db_path)
}

#[tauri::command]
fn add_finance_transaction(app: AppHandle, tx: db::models::NewFinanceTransaction) -> Result<db::models::FinanceTransaction, String> {
    let db_path = get_db_path(&app)?;
    let created = finance::add_finance_transaction(&db_path, tx)?;
    log_user_action(
        &db_path,
        "add_finance_transaction",
        "finance",
        created.id,
        serde_json::json!({ "direction": created.direction, "amount": created.amount, "category": created.category_id }),
    );
    Ok(created)
}

#[tauri::command]
fn update_finance_transaction(app: AppHandle, id: i32, update: db::models::UpdateFinanceTransaction) -> Result<db::models::FinanceTransaction, String> {
    let db_path = get_db_path(&app)?;
    finance::update_finance_transaction(&db_path, id, update)
}

#[tauri::command]
fn delete_finance_transaction(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    finance::delete_finance_transaction(&db_path, id)
}

#[tauri::command]
fn get_budgets(app: AppHandle) -> Result<Vec<db::models::Budget>, String> {
    let db_path = get_db_path(&app)?;
    finance::get_budgets(&db_path)
}

#[tauri::command]
fn add_budget(app: AppHandle, budget: db::models::NewBudget) -> Result<db::models::Budget, String> {
    let db_path = get_db_path(&app)?;
    finance::add_budget(&db_path, budget)
}

#[tauri::command]
fn update_budget(app: AppHandle, id: i32, update: db::models::UpdateBudget) -> Result<db::models::Budget, String> {
    let db_path = get_db_path(&app)?;
    finance::update_budget(&db_path, id, update)
}

#[tauri::command]
fn delete_budget(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    finance::delete_budget(&db_path, id)
}

#[tauri::command]
fn get_finance_summary(app: AppHandle) -> Result<db::models::FinanceSummary, String> {
    let db_path = get_db_path(&app)?;
    finance::get_finance_summary(&db_path)
}

// ---- Report Metadata commands ----
#[tauri::command]
fn get_report_metadata(app: AppHandle) -> Result<Vec<db::models::ReportMetadata>, String> {
    let db_path = get_db_path(&app)?;
    reports::get_report_metadata(&db_path)
}

#[tauri::command]
fn add_report_metadata(app: AppHandle, report: db::models::NewReportMetadata) -> Result<db::models::ReportMetadata, String> {
    let db_path = get_db_path(&app)?;
    reports::add_report_metadata(&db_path, report)
}

#[tauri::command]
fn delete_report_metadata(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    reports::delete_report_metadata(&db_path, id)
}

// ---- Support email ----
#[tauri::command]
fn send_support_email(
    app: AppHandle,
    name: String,
    email: String,
    subject: String,
    message: String,
) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    email::send_support_email(&db_path, name, email, subject, message)
}

#[tauri::command]
fn get_smtp_config(app: AppHandle) -> Result<serde_json::Value, String> {
    let db_path = get_db_path(&app)?;
    let cfg = email::load_smtp_config(&db_path);
    // NOTE: username/password are deliberately not exposed to the frontend.
    Ok(serde_json::json!({
        "configured": cfg.is_configured(),
        "support_email": if cfg.has_recipient() { Some(cfg.recipient) } else { None },
        "server": cfg.server,
        "port": cfg.port,
        "from_name": cfg.from_name,
    }))
}

// ---- Support messages (contact/ticket persistence) ----
#[tauri::command]
fn get_support_messages(app: AppHandle) -> Result<Vec<db::models::SupportMessage>, String> {
    let db_path = get_db_path(&app)?;
    support_messages::get_support_messages(&db_path)
}

#[tauri::command]
fn submit_support_message(
    app: AppHandle,
    name: String,
    email: String,
    phone: Option<String>,
    subject: Option<String>,
    category: Option<String>,
    priority: Option<String>,
    message: String,
) -> Result<db::models::SupportMessage, String> {
    let db_path = get_db_path(&app)?;

    let priority = priority.unwrap_or_else(|| "normal".to_string());
    let subject = subject.unwrap_or_else(|| "Formint — Support Request".to_string());
    let status = "new".to_string();

    let new_message = db::models::NewSupportMessage {
        name: name.clone(),
        email: email.clone(),
        phone,
        subject: Some(subject.clone()),
        category,
        priority: priority.clone(),
        message: message.clone(),
        status: status.clone(),
    };

    // Persist first — the DB is the source of truth for the ticket.
    let saved = support_messages::add_support_message(&db_path, new_message)?;

    // Then best-effort email notification (failure is non-fatal; ticket is saved).
    if let Err(e) = email::send_support_ticket_email(
        &db_path,
        name,
        email,
        None,
        saved.category.clone(),
        saved.priority.clone(),
        saved.subject.clone().unwrap_or_default(),
        saved.message.clone(),
        saved.status.clone(),
    ) {
        eprintln!("[support] email send failed (message saved): {e}");
    }

    Ok(saved)
}

#[tauri::command]
fn update_support_message_status(
    app: AppHandle,
    id: i32,
    status: String,
) -> Result<db::models::SupportMessage, String> {
    let db_path = get_db_path(&app)?;
    support_messages::update_support_message(
        &db_path,
        id,
        db::models::UpdateSupportMessage {
            status: Some(status),
            priority: None,
        },
    )
}

#[tauri::command]
fn delete_support_message(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    support_messages::delete_support_message(&db_path, id)
}

// ---- Database commands (import/export/reset) ----
#[tauri::command]
fn reset_database_cmd(app: AppHandle) -> Result<(), String> {
    let db_path = get_db_path(&app)?;

    eprintln!("[db] reset_database: deleting {}", db_path.display());

    // Delete the existing database file
    if db_path.exists() {
        std::fs::remove_file(&db_path)
            .map_err(|e| format!("Failed to delete database file: {}", e))?;
        eprintln!("[db] reset_database: deleted {}", db_path.display());
    }

    // Also delete WAL and SHM files if they exist
    let wal_path = db_path.with_extension("db-wal");
    if wal_path.exists() {
        let _ = std::fs::remove_file(&wal_path);
    }
    let shm_path = db_path.with_extension("db-shm");
    if shm_path.exists() {
        let _ = std::fs::remove_file(&shm_path);
    }

    // Re-run migrations to create fresh tables
    run_migrations(&db_path)?;
    eprintln!("[db] reset_database: migrations re-applied successfully");

    // Recreate superuser if auth is configured
    if let Err(e) = auth::ensure_superuser_exists(&db_path) {
        eprintln!("[db] reset_database: superuser ensure failed (non-fatal): {e}");
    }

    Ok(())
}

#[tauri::command]
fn export_database_cmd(app: AppHandle) -> Result<String, String> {
    let db_path = get_db_path(&app)?;
    let data = std::fs::read(&db_path)
        .map_err(|e| format!("Failed to read database file: {}", e))?;
    use base64::Engine;
    Ok(base64::engine::general_purpose::STANDARD.encode(&data))
}

/// Tables merged into the live database when importing in "append" mode.
/// Auth tables (`users`, `roles`, `user_roles`) and the singleton `settings`
/// row are intentionally excluded — those are only restored via "replace".
const IMPORT_APPEND_TABLES: &[&str] = &[
    "categories",
    "products",
    "delivery_types",
    "employee_types",
    "employees",
    "customers",
    "delivery_zones",
    "coupons",
    "badges",
    "sales",
    "sale_items",
    "ingredients",
    "recipe_types",
    "recipes",
    "recipe_ingredients",
    "inventory_transactions",
    "inventory_adjustments",
    "inventory_alerts",
    "suppliers",
    "purchase_orders",
    "purchase_order_items",
    "loyalty_transactions",
    "receipt_templates",
    "tax_reports",
    "employee_schedules",
    "support_messages",
    "report_metadata",
];

/// Merge records from an imported backup file into the live database.
/// Both databases share the same schema, so each table present in the backup
/// is copied with `INSERT OR IGNORE` — existing rows (by primary key) stay
/// untouched and new rows are appended. The whole merge runs in one
/// transaction so a failure rolls everything back.
fn import_database_append(db_path: &std::path::Path, decoded: &[u8]) -> Result<(), String> {
    use diesel::{sql_query, Connection, RunQueryDsl};

    let tmp_path = std::env::temp_dir().join(format!(
        "formint-pos-import-{}-{}.db",
        std::process::id(),
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_millis())
            .unwrap_or(0)
    ));
    std::fs::write(&tmp_path, decoded)
        .map_err(|e| format!("Failed to write temporary database: {}", e))?;

    let result = (|| -> Result<(), String> {
        let mut conn = db::establish_connection(db_path)
            .map_err(|e| format!("Failed to connect to database: {}", e))?;

        // ATTACH requires the path as a literal — escape single quotes for SQL.
        let src_path = tmp_path.to_string_lossy().replace('\'', "''");
        sql_query(format!("ATTACH DATABASE '{}' AS src", src_path))
            .execute(&mut conn)
            .map_err(|e| format!("Failed to attach backup database: {}", e))?;

        // FK enforcement must be changed outside a transaction (SQLite rule).
        let _ = sql_query("PRAGMA foreign_keys = OFF").execute(&mut conn);

        conn.transaction::<_, diesel::result::Error, _>(|conn| {
            for table in IMPORT_APPEND_TABLES {
                // Skip tables that don't exist in the backup (schema drift).
                let exists: i64 = diesel::dsl::sql::<diesel::sql_types::BigInt>(&format!(
                    "SELECT count(*) FROM src.sqlite_master WHERE type='table' AND name='{}'",
                    table
                ))
                .get_result(conn)
                .map_err(|e| {
                    eprintln!("[db] append merge: could not inspect {}: {}", table, e);
                    e
                })?;
                if exists == 0 {
                    eprintln!("[db] append merge: {} not present in backup, skipping", table);
                    continue;
                }
                sql_query(format!(
                    "INSERT OR IGNORE INTO {} SELECT * FROM src.{}",
                    table, table
                ))
                .execute(conn)
                .map_err(|e| {
                    eprintln!("[db] append merge failed on {}: {}", table, e);
                    e
                })?;
            }
            Ok(())
        })
        .map_err(|e| format!("Failed to merge backup data: {}", e))?;

        let _ = sql_query("DETACH DATABASE src").execute(&mut conn);
        Ok(())
    })();

    let _ = std::fs::remove_file(&tmp_path);
    result
}

#[tauri::command]
fn import_database_cmd(app: AppHandle, data: String, mode: Option<String>) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    use base64::Engine;
    let decoded = base64::engine::general_purpose::STANDARD
        .decode(&data)
        .map_err(|e| e.to_string())?;

    // mode: "replace" (default) overwrites the whole database;
    // "append" merges the backup data into the existing database.
    if mode.as_deref() == Some("append") {
        return import_database_append(&db_path, &decoded);
    }

    if db_path.exists() {
        let backup_path = db_path.with_extension("db.backup");
        std::fs::copy(&db_path, &backup_path)
            .map_err(|e| format!("Failed to create backup: {}", e))?;
    }

    std::fs::write(&db_path, decoded)
        .map_err(|e| format!("Failed to write database: {}", e))?;
    Ok(())
}

// Helper function to get window state file path (desktop only)
fn get_window_state_path(app: &AppHandle) -> Result<std::path::PathBuf, String> {

    let app_dir = app.path().app_data_dir().map_err(|e| e.to_string())?;
    std::fs::create_dir_all(&app_dir).map_err(|e| e.to_string())?;
    Ok(app_dir.join("window_state.json"))
}

// Helper function to save window state (desktop only)
fn save_window_state(app: &AppHandle, is_maximized: bool) -> Result<(), String> {
    let path = get_window_state_path(app)?;
    let state = serde_json::json!({
        "is_maximized": is_maximized
    });
    std::fs::write(path, serde_json::to_string_pretty(&state).unwrap())
        .map_err(|e| e.to_string())
}

// Helper function to load window state (desktop only)
fn load_window_state(app: &AppHandle) -> Result<bool, String> {
    let path = get_window_state_path(app)?;
    if path.exists() {
        let content = std::fs::read_to_string(path).map_err(|e| e.to_string())?;
        let state: serde_json::Value = serde_json::from_str(&content).map_err(|e| e.to_string())?;
        Ok(state.get("is_maximized").and_then(|v| v.as_bool()).unwrap_or(false))
    } else {
        Ok(false)
    }
}

// The runtime entry point is not needed by library tests. Keeping it out of
// the test crate avoids forcing Tauri's bundle icon/resource validation into
// Rust unit-test compilation.
#[cfg(not(test))]
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // Load environment variables
    load_env();

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .setup(|app| {
            let db_path = get_db_path(&app.handle())?;
            run_migrations(&db_path)?;

            // Ensure superuser exists from env vars (SUPERUSER_EMAIL + SUPERUSER_PASSWORD)
            if let Err(e) = auth::ensure_superuser_exists(&db_path) {
                eprintln!("[setup] superuser ensure failed (non-fatal): {e}");
            }

            // ── System tray icon ──
            #[cfg(not(any(target_os = "android", target_os = "ios")))]
            {
                let show_item = MenuItemBuilder::with_id("show", "Show Formint")
                    .build(app)?;
                let quit_item = MenuItemBuilder::with_id("quit", "Quit")
                    .build(app)?;

                let menu = MenuBuilder::new(app)
                    .item(&show_item)
                    .separator()
                    .item(&quit_item)
                    .build()?;

                // The standalone Community bundle carries ICO/ICNS assets, not
                // a PNG tray image. Tauri uses the application icon for the
                // window; leave the tray icon optional so Rust tests and
                // headless builds do not depend on a missing generated PNG.
                let tray = TrayIconBuilder::new()
                    .tooltip("Formint")
                    .menu(&menu)
                    .on_menu_event(|app, event| {
                        match event.id().as_ref() {
                            "show" => {
                                if let Some(window) = app.get_webview_window("main") {
                                    let _ = window.show();
                                    let _ = window.set_focus();
                                }
                            }
                            "quit" => {
                                app.exit(0);
                            }
                            _ => {}
                        }
                    })
                    .on_tray_icon_event(|tray, event| {
                        if let TrayIconEvent::Click {
                            button: MouseButton::Left,
                            button_state: MouseButtonState::Up,
                            ..
                        } = event
                        {
                            let app = tray.app_handle();
                            if let Some(window) = app.get_webview_window("main") {
                                let _ = window.show();
                                let _ = window.set_focus();
                            }
                        }
                    })
                    .build(app)?;

            }

            // Setup window state management (desktop only)
            #[cfg(not(any(target_os = "android", target_os = "ios")))]
            {
                let window = app.get_webview_window("main").unwrap();

                // Restore maximize state
                let is_maximized = load_window_state(&app.handle()).unwrap_or(false);
                if is_maximized {
                    let _ = window.maximize();
                }

                // Listen for window resize events to save maximize state
                let window_clone = window.clone();
                let app_handle = app.handle().clone();
                window.on_window_event(move |event| {
                    if let tauri::WindowEvent::Resized(_) = event {
                        if let Ok(is_maximized) = window_clone.is_maximized() {
                            let _ = save_window_state(&app_handle, is_maximized);
                        }
                    }
                });
            }

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            // Products
            get_products,
            add_product,
            update_product,
            delete_product,
            mark_product_uploaded,
            // Categories
            get_categories,
            add_category,
            update_category,
            delete_category,
            // Sales
            add_sale,
            get_sales,
            update_sale,
            delete_sale,
            refund_sale,
            mark_sale_uploaded,
            // Transactions
            get_transactions,
            delete_transaction,
            // Settings
            get_settings,
            save_settings,
            // Analytics
            get_analytics,
            get_revenue_by_payment_method,
            // Ingredients
            get_ingredients,
            add_ingredient,
            update_ingredient,
            soft_delete_ingredient,
            // Recipes
            get_recipes,
            create_recipe,
            update_recipe,
            soft_delete_recipe,
            get_recipe_ingredients,
            add_recipe_ingredient,
            delete_recipe_ingredient,
            // Delivery Types
            get_delivery_types,
            add_delivery_type,
            update_delivery_type,
            soft_delete_delivery_type,
            // Employee Types
            get_employee_types,
            add_employee_type,
            update_employee_type,
            soft_delete_employee_type,
            // Employees
            get_employees,
            add_employee,
            update_employee,
            soft_delete_employee,
            // Inventory
            get_inventory_transactions,
            get_inventory_adjustments,
            add_inventory_transaction,
            delete_inventory_adjustment,
            // Dump
            dump_database,
            // Database
            reset_database_cmd,
            export_database_cmd,
            import_database_cmd,
            // Auth
            check_auth_required,
            has_users,
            get_user_count,
            verify_user,
            send_auth_confirmation_code,
            setup_account,
            login_user,
            change_password_cmd,
            request_password_reset,
            reset_password_cmd,
            get_superuser_email,
            // Email
            send_support_email,
            get_smtp_config,
            // Support messages (contact/ticket persistence)
            get_support_messages,
            submit_support_message,
            update_support_message_status,
            delete_support_message,
            // Permission Catalog
            get_permission_catalog,
            // Roles
            get_roles,
            add_role,
            update_role,
            soft_delete_role,
            get_user_roles,
            assign_role,
            remove_role,
            // Suppliers
            get_suppliers,
            add_supplier,
            update_supplier,
            soft_delete_supplier,
            // Purchase Orders
            get_purchase_orders,
            get_purchase_order_items,
            add_purchase_order,
            update_purchase_order,
            delete_purchase_order,
            // Customers
            get_customers,
            add_customer,
            update_customer,
            delete_customer,
            get_loyalty_transactions,
            get_all_loyalty_transactions,
            add_loyalty_transaction,
            // Receipt Templates
            get_notes,
            get_selectable_notes,
            get_default_note,
            add_note,
            update_note,
            add_recipe_note,
            get_recipe_notes,
            delete_note,
            // Coupons
            get_coupons,
            get_active_coupons,
            add_coupon,
            update_coupon,
            delete_coupon,
            // Badges (loyalty rewards)
            get_badges,
            add_badge,
            update_badge,
            delete_badge,
            // User Action audit log
            add_user_action,
            get_user_actions,
            get_user_actions_for_entity,
            // Tax Reports
            get_tax_reports,
            add_tax_report,
            delete_tax_report,
            // Employee Schedules
            get_employee_schedules,
            add_employee_schedule,
            update_employee_schedule,
            delete_employee_schedule,
            // Finance & Budget
            get_finance_transactions,
            add_finance_transaction,
            update_finance_transaction,
            delete_finance_transaction,
            get_budgets,
            add_budget,
            update_budget,
            delete_budget,
            get_finance_summary,
            // Report Metadata
            get_report_metadata,
            add_report_metadata,
            delete_report_metadata,
            // Delivery Zones
            get_delivery_zones,
            add_delivery_zone,
            update_delivery_zone,
            soft_delete_delivery_zone,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
