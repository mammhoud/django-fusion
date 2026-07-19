pub mod db;
pub mod operations;
pub mod email;

use db::{get_db_path, run_migrations};
use operations::*;
use operations::sidecar::{start_sidecar, stop_sidecar, sidecar_status};
use tauri::{AppHandle, Manager};
use tauri_plugin_shell::ShellExt;
use chrono::NaiveDateTime;

// Load environment variables at startup
fn load_env() {
    if let Err(e) = dotenvy::dotenv() {
        eprintln!("Warning: Could not load .env file: {}", e);
    }
}

// ---- Product commands ----
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

#[tauri::command]
fn update_product(app: AppHandle, id: i32, update: db::models::UpdateProduct) -> Result<db::models::Product, String> {
    let db_path = get_db_path(&app)?;
    products::update_product(&db_path, id, update)
}

#[tauri::command]
fn delete_product(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    products::delete_product(&db_path, id)
}

#[tauri::command]
fn mark_product_uploaded(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    products::mark_product_uploaded(&db_path, id)
}

// ---- Category commands ----
#[tauri::command]
fn get_categories(app: AppHandle) -> Result<Vec<db::models::Category>, String> {
    let db_path = get_db_path(&app)?;
    categories::get_categories(&db_path)
}

#[tauri::command]
fn add_category(app: AppHandle, category: db::models::NewCategory) -> Result<db::models::Category, String> {
    let db_path = get_db_path(&app)?;
    categories::add_category(&db_path, category)
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

// ---- Ingredient commands ----
#[tauri::command]
fn get_ingredients(app: AppHandle, include_inactive: bool) -> Result<Vec<db::models::Ingredient>, String> {
    let db_path = get_db_path(&app)?;
    ingredients::get_ingredients(&db_path, include_inactive)
}

#[tauri::command]
fn add_ingredient(app: AppHandle, ingredient: db::models::NewIngredient) -> Result<db::models::Ingredient, String> {
    let db_path = get_db_path(&app)?;
    ingredients::add_ingredient(&db_path, ingredient)
}

#[tauri::command]
fn update_ingredient(app: AppHandle, id: i32, update: db::models::UpdateIngredient) -> Result<db::models::Ingredient, String> {
    let db_path = get_db_path(&app)?;
    ingredients::update_ingredient(&db_path, id, update)
}

#[tauri::command]
fn soft_delete_ingredient(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    ingredients::soft_delete_ingredient(&db_path, id)
}

// ---- Recipe commands ----
#[tauri::command]
fn get_recipes(app: AppHandle, include_inactive: bool) -> Result<Vec<db::models::Recipe>, String> {
    let db_path = get_db_path(&app)?;
    recipes::get_recipes(&db_path, include_inactive)
}

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
fn update_recipe(app: AppHandle, id: i32, update: db::models::UpdateRecipe) -> Result<db::models::Recipe, String> {
    let db_path = get_db_path(&app)?;
    recipes::update_recipe(&db_path, id, update)
}

#[tauri::command]
fn soft_delete_recipe(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    recipes::soft_delete_recipe(&db_path, id)
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

// ---- Employee commands ----
#[tauri::command]
fn get_employees(app: AppHandle, include_inactive: bool) -> Result<Vec<db::models::Employee>, String> {
    let db_path = get_db_path(&app)?;
    employees::get_employees(&db_path, include_inactive)
}

#[tauri::command]
fn add_employee(app: AppHandle, employee: db::models::NewEmployee) -> Result<db::models::Employee, String> {
    let db_path = get_db_path(&app)?;
    employees::add_employee(&db_path, employee)
}

#[tauri::command]
fn update_employee(app: AppHandle, id: i32, update: db::models::UpdateEmployee) -> Result<db::models::Employee, String> {
    let db_path = get_db_path(&app)?;
    employees::update_employee(&db_path, id, update)
}

#[tauri::command]
fn soft_delete_employee(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    employees::soft_delete_employee(&db_path, id)
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
fn add_inventory_transaction(
    app: AppHandle,
    transaction: db::models::NewInventoryTransaction,
    adjustment_reason: Option<String>,
    created_by: Option<String>,
) -> Result<db::models::InventoryTransaction, String> {
    let db_path = get_db_path(&app)?;
    inventory_transactions::add_inventory_transaction(&db_path, transaction, adjustment_reason, created_by)
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
fn verify_user(app: AppHandle, email: String) -> Result<db::models::User, String> {
    let db_path = get_db_path(&app)?;
    auth::verify_user(&db_path, email)
}

#[tauri::command]
fn start_support_sidecar(app: AppHandle) -> Result<String, String> {
    operations::sidecar::start_sidecar(app)
}

#[tauri::command]
fn send_auth_confirmation_code(email: String) -> Result<(), String> {
    auth::send_confirmation_code(email)
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
fn change_password_cmd(
    app: AppHandle,
    email: String,
    old_password: String,
    new_password: String,
) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    auth::change_password(&db_path, email, old_password, new_password)
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

// ---- Kitchen Tickets commands ----
#[tauri::command]
fn get_kitchen_tickets(app: AppHandle, status: Option<String>) -> Result<Vec<db::models::KitchenTicket>, String> {
    let db_path = get_db_path(&app)?;
    kitchen_tickets::get_kitchen_tickets(&db_path, status)
}

#[tauri::command]
fn add_kitchen_ticket(app: AppHandle, ticket: db::models::NewKitchenTicket) -> Result<db::models::KitchenTicket, String> {
    let db_path = get_db_path(&app)?;
    kitchen_tickets::add_kitchen_ticket(&db_path, ticket)
}

#[tauri::command]
fn update_kitchen_ticket(app: AppHandle, id: i32, update: db::models::UpdateKitchenTicket) -> Result<db::models::KitchenTicket, String> {
    let db_path = get_db_path(&app)?;
    kitchen_tickets::update_kitchen_ticket(&db_path, id, update)
}

#[tauri::command]
fn delete_kitchen_ticket(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    kitchen_tickets::delete_kitchen_ticket(&db_path, id)
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
    customers::add_customer(&db_path, customer)
}

#[tauri::command]
fn update_customer(app: AppHandle, id: i32, update: db::models::UpdateCustomer) -> Result<db::models::Customer, String> {
    let db_path = get_db_path(&app)?;
    customers::update_customer(&db_path, id, update)
}

#[tauri::command]
fn delete_customer(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    customers::delete_customer(&db_path, id)
}

#[tauri::command]
fn get_loyalty_transactions(app: AppHandle, customer_id: i32) -> Result<Vec<db::models::LoyaltyTransaction>, String> {
    let db_path = get_db_path(&app)?;
    customers::get_loyalty_transactions(&db_path, customer_id)
}

#[tauri::command]
fn add_loyalty_transaction(app: AppHandle, transaction: db::models::NewLoyaltyTransaction) -> Result<db::models::LoyaltyTransaction, String> {
    let db_path = get_db_path(&app)?;
    customers::add_loyalty_transaction(&db_path, transaction)
}

// ---- Receipt Templates commands ----
#[tauri::command]
fn get_receipt_templates(app: AppHandle) -> Result<Vec<db::models::ReceiptTemplate>, String> {
    let db_path = get_db_path(&app)?;
    receipt_templates::get_receipt_templates(&db_path)
}

#[tauri::command]
fn get_default_receipt_template(app: AppHandle) -> Result<db::models::ReceiptTemplate, String> {
    let db_path = get_db_path(&app)?;
    receipt_templates::get_default_receipt_template(&db_path)
}

#[tauri::command]
fn add_receipt_template(app: AppHandle, template: db::models::NewReceiptTemplate) -> Result<db::models::ReceiptTemplate, String> {
    let db_path = get_db_path(&app)?;
    receipt_templates::add_receipt_template(&db_path, template)
}

#[tauri::command]
fn update_receipt_template(app: AppHandle, id: i32, update: db::models::UpdateReceiptTemplate) -> Result<db::models::ReceiptTemplate, String> {
    let db_path = get_db_path(&app)?;
    receipt_templates::update_receipt_template(&db_path, id, update)
}

#[tauri::command]
fn delete_receipt_template(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    receipt_templates::delete_receipt_template(&db_path, id)
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

// ---- Payrolls commands ----
#[tauri::command]
fn get_payrolls(app: AppHandle, employee_id: Option<i32>) -> Result<Vec<db::models::Payroll>, String> {
    let db_path = get_db_path(&app)?;
    payrolls::get_payrolls(&db_path, employee_id)
}

#[tauri::command]
fn add_payroll(app: AppHandle, payroll: db::models::NewPayroll) -> Result<db::models::Payroll, String> {
    let db_path = get_db_path(&app)?;
    payrolls::add_payroll(&db_path, payroll)
}

#[tauri::command]
fn update_payroll(app: AppHandle, id: i32, update: db::models::UpdatePayroll) -> Result<db::models::Payroll, String> {
    let db_path = get_db_path(&app)?;
    payrolls::update_payroll(&db_path, id, update)
}

#[tauri::command]
fn delete_payroll(app: AppHandle, id: i32) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    payrolls::delete_payroll(&db_path, id)
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
    name: String,
    email: String,
    subject: String,
    message: String,
) -> Result<(), String> {
    email::send_support_email(name, email, subject, message)
}

// ---- Database commands (import/export) ----
#[tauri::command]
fn export_database_cmd(app: AppHandle) -> Result<String, String> {
    let db_path = get_db_path(&app)?;
    let data = std::fs::read(&db_path)
        .map_err(|e| format!("Failed to read database file: {}", e))?;
    use base64::Engine;
    Ok(base64::engine::general_purpose::STANDARD.encode(&data))
}

#[tauri::command]
fn import_database_cmd(app: AppHandle, data: String) -> Result<(), String> {
    let db_path = get_db_path(&app)?;
    use base64::Engine;
    let decoded = base64::engine::general_purpose::STANDARD
        .decode(&data)
        .map_err(|e| e.to_string())?;

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

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // Load environment variables
    load_env();

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let db_path = get_db_path(&app.handle())?;
            run_migrations(&db_path)?;

            // Ensure superuser exists from env vars (SUPERUSER_EMAIL + SUPERUSER_PASSWORD)
            if let Err(e) = auth::ensure_superuser_exists(&db_path) {
                eprintln!("[setup] superuser ensure failed (non-fatal): {e}");
            }

            // Auto-start the Python/Sanic sidecar
            #[cfg(not(any(target_os = "android", target_os = "ios")))]
            {
                if let Err(e) = start_sidecar(app.handle().clone()) {
                    eprintln!("[setup] sidecar start failed (non-fatal): {e}");
                }
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
            // Sales
            add_sale,
            get_sales,
            update_sale,
            delete_sale,
            mark_sale_uploaded,
            // Transactions
            get_transactions,
            delete_transaction,
            // Settings
            get_settings,
            save_settings,
            // Analytics
            get_analytics,
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
            // Dump
            dump_database,
            // Database
            export_database_cmd,
            import_database_cmd,
            // Auth
            check_auth_required,
            has_users,
            verify_user,
            start_support_sidecar,
            send_auth_confirmation_code,
            setup_account,
            login_user,
            change_password_cmd,
            get_superuser_email,
            // Email
            send_support_email,
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
            // Kitchen Tickets
            get_kitchen_tickets,
            add_kitchen_ticket,
            update_kitchen_ticket,
            delete_kitchen_ticket,
            // Customers
            get_customers,
            add_customer,
            update_customer,
            delete_customer,
            get_loyalty_transactions,
            add_loyalty_transaction,
            // Receipt Templates
            get_receipt_templates,
            get_default_receipt_template,
            add_receipt_template,
            update_receipt_template,
            delete_receipt_template,
            // Tax Reports
            get_tax_reports,
            add_tax_report,
            delete_tax_report,
            // Employee Schedules
            get_employee_schedules,
            add_employee_schedule,
            update_employee_schedule,
            delete_employee_schedule,
            // Payrolls
            get_payrolls,
            add_payroll,
            update_payroll,
            delete_payroll,
            // Report Metadata
            get_report_metadata,
            add_report_metadata,
            delete_report_metadata,
            // Sidecar lifecycle
            start_sidecar,
            stop_sidecar,
            sidecar_status,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
