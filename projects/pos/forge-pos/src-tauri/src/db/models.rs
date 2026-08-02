use diesel::prelude::*;
use serde::{Deserialize, Serialize};
use chrono::NaiveDateTime;

// ---- User ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::users)]
pub struct User {
    pub id: i32,
    pub email: String,
    pub password_hash: String,
    pub name: String,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::users)]
pub struct NewUser {
    pub email: String,
    pub password_hash: String,
    pub name: String,
}

// ---- Settings ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::settings)]
pub struct Settings {
    pub id: i32,
    pub restaurant_name: Option<String>,
    pub address: Option<String>,
    pub phone: Option<String>,
    pub email: Option<String>,
    pub tax_rate: Option<String>,
    pub tax_id: Option<String>,
    pub currency: String,
    pub opening_time: Option<String>,
    pub closing_time: Option<String>,
    pub receipt_footer: Option<String>,
    pub logo: Option<String>,
    pub invoice_logo: Option<String>,
    pub dine_in_tables: i32,
    pub delivery_fee: f64,
    pub delivery_fee_per_km: f64,
    /// When true (default), product cards + KDS items get a deterministic
    /// unique per-product accent color. When false, cards fall back to the
    /// rotating palette (category colors still apply).
    pub unique_card_colors: bool,
    pub smtp_server: Option<String>,
    pub smtp_port: Option<i32>,
    pub smtp_username: Option<String>,
    pub smtp_password: Option<String>,
    pub smtp_recipient: Option<String>,
    pub smtp_from_name: Option<String>,
    pub smtp_from_email: Option<String>,
}

#[derive(Debug, Insertable, AsChangeset, Deserialize, Default)]
#[serde(default)]
#[diesel(table_name = crate::db::schema::settings)]
pub struct UpdateSettings {
    pub restaurant_name: Option<String>,
    pub address: Option<String>,
    pub phone: Option<String>,
    pub email: Option<String>,
    pub tax_rate: Option<String>,
    pub currency: Option<String>,
    pub opening_time: Option<String>,
    pub closing_time: Option<String>,
    pub receipt_footer: Option<String>,
    /// None = skip field (no change to DB column)
    /// Some(None) = set column to NULL (explicitly clear logo)
    /// Some(Some(data)) = set column to the given value
    pub logo: Option<Option<String>>,
    /// None = skip field, Some(None) = set to NULL, Some(Some(data)) = set value
    pub invoice_logo: Option<Option<String>>,
    pub dine_in_tables: Option<i32>,
    pub tax_id: Option<Option<String>>,
    pub delivery_fee: Option<f64>,
    pub delivery_fee_per_km: Option<f64>,
    pub unique_card_colors: Option<bool>,
    pub smtp_server: Option<String>,
    pub smtp_port: Option<i32>,
    pub smtp_username: Option<String>,
    pub smtp_password: Option<String>,
    pub smtp_recipient: Option<String>,
    pub smtp_from_name: Option<String>,
    pub smtp_from_email: Option<String>,
}

// ---- Category ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::categories)]
pub struct Category {
    pub id: i32,
    pub name: String,
    pub color: Option<String>,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::categories)]
pub struct NewCategory {
    pub name: String,
    #[serde(default)]
    pub color: Option<String>,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::categories)]
pub struct UpdateCategory {
    pub name: Option<String>,
    pub color: Option<Option<String>>,
}

// ---- Product ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::products)]
pub struct Product {
    pub id: i32,
    pub name: String,
    pub price: f64,
    pub unit: String,
    pub category_id: Option<i32>,
    pub image: Option<String>,
    pub product_type: String,
    pub prepare_time_minutes: i32,
    pub barcode: Option<String>,
    pub description: Option<String>,
    pub available_order_types: String,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
    pub uploaded: bool,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::products)]
pub struct NewProduct {
    pub name: String,
    pub price: f64,
    pub unit: String,
    pub category_id: Option<i32>,
    pub image: Option<String>,
    /// Defaults to 'product' on the DB side. The frontend sends this
    /// explicitly; serde(default) handles missing field gracefully.
    #[serde(default)]
    pub product_type: Option<String>,
    #[serde(default)]
    pub prepare_time_minutes: Option<i32>,
    #[serde(default)]
    pub barcode: Option<String>,
    #[serde(default)]
    pub description: Option<String>,
    /// Comma-separated list of order types this product is available for.
    /// Empty string = available for all order types.
    #[serde(default)]
    pub available_order_types: Option<String>,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::products)]
pub struct UpdateProduct {
    pub name: Option<String>,
    pub price: Option<f64>,
    pub unit: Option<String>,
    pub category_id: Option<Option<i32>>,
    pub image: Option<Option<String>>,
    pub product_type: Option<String>,
    pub prepare_time_minutes: Option<i32>,
    pub barcode: Option<Option<String>>,
    pub description: Option<Option<String>>,
    pub available_order_types: Option<String>,
    pub uploaded: Option<bool>,
}

// ---- Sale ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::sales)]
pub struct Sale {
    pub id: i32,
    pub total_amount: f64,
    pub currency: String,
    pub date: String,
    pub time: String,
    pub order_type: String,
    pub status: String,
    pub table_number: Option<i32>,
    pub delivery_type_id: Option<i32>,
    pub delivery_zone_id: Option<i32>,
    pub delivery_address: Option<String>,
    pub employee_id: Option<i32>,
    pub customer_id: Option<i32>,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
    pub uploaded: bool,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::sales)]
pub struct NewSale {
    pub total_amount: f64,
    pub currency: String,
    pub date: Option<String>,
    pub time: Option<String>,
    pub order_type: String,
    pub status: String,
    pub table_number: Option<i32>,
    pub delivery_type_id: Option<i32>,
    pub delivery_zone_id: Option<i32>,
    pub delivery_address: Option<String>,
    pub employee_id: Option<i32>,
    pub customer_id: Option<i32>,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::sales)]
pub struct UpdateSale {
    pub order_type: Option<String>,
    pub status: Option<String>,
    pub table_number: Option<Option<i32>>,
    pub delivery_type_id: Option<Option<i32>>,
    pub delivery_zone_id: Option<Option<i32>>,
    pub delivery_address: Option<Option<String>>,
    pub employee_id: Option<Option<i32>>,
    pub customer_id: Option<Option<i32>>,
    pub uploaded: Option<bool>,
}

// ---- SaleItem ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::sale_items)]
pub struct SaleItem {
    pub id: i32,
    pub sale_id: i32,
    pub product_name: String,
    pub price: f64,
    pub quantity: f64,
    pub unit: String,
    pub subtotal: f64,
    pub created_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::sale_items)]
pub struct NewSaleItem {
    /// sale_id is set server-side after inserting the sale.
    /// The frontend does not send it, so default to 0 (serde(default)).
    #[serde(default)]
    pub sale_id: i32,
    pub product_name: String,
    pub price: f64,
    pub quantity: f64,
    pub unit: String,
}

// ---- Ingredient ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::ingredients)]
pub struct Ingredient {
    pub id: i32,
    pub name: String,
    pub unit: String,
    pub current_quantity: f64,
    pub reorder_level: f64,
    pub reorder_quantity: f64,
    pub cost_per_unit: f64,
    pub is_active: bool,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
    pub uploaded: bool,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::ingredients)]
pub struct NewIngredient {
    pub name: String,
    pub unit: String,
    pub current_quantity: f64,
    pub reorder_level: f64,
    pub reorder_quantity: f64,
    pub cost_per_unit: f64,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::ingredients)]
pub struct UpdateIngredient {
    pub name: Option<String>,
    pub unit: Option<String>,
    pub current_quantity: Option<f64>,
    pub reorder_level: Option<f64>,
    pub reorder_quantity: Option<f64>,
    pub cost_per_unit: Option<f64>,
    pub is_active: Option<bool>,
    pub uploaded: Option<bool>,
}

// ---- RecipeType ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::recipe_types)]
pub struct RecipeType {
    pub id: i32,
    pub name: String,
    pub description: Option<String>,
    pub is_active: bool,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::recipe_types)]
pub struct NewRecipeType {
    pub name: String,
    pub description: Option<String>,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::recipe_types)]
pub struct UpdateRecipeType {
    pub name: Option<String>,
    pub description: Option<Option<String>>,
    pub is_active: Option<bool>,
}

// ---- Recipe ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::recipes)]
pub struct Recipe {
    pub id: i32,
    pub product_id: i32,
    pub recipe_type_id: i32,
    pub yield_quantity: f64,
    pub is_active: bool,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
    pub uploaded: bool,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::recipes)]
pub struct NewRecipe {
    pub product_id: i32,
    pub recipe_type_id: i32,
    pub yield_quantity: f64,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::recipes)]
pub struct UpdateRecipe {
    pub recipe_type_id: Option<i32>,
    pub yield_quantity: Option<f64>,
    pub is_active: Option<bool>,
    pub uploaded: Option<bool>,
}

// ---- RecipeIngredient ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::recipe_ingredients)]
pub struct RecipeIngredient {
    pub id: i32,
    pub recipe_id: i32,
    pub ingredient_id: i32,
    pub quantity: f64,
    pub unit: Option<String>,
    pub preparation_note: Option<String>,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::recipe_ingredients)]
pub struct NewRecipeIngredient {
    pub recipe_id: i32,
    pub ingredient_id: i32,
    pub quantity: f64,
    pub unit: Option<String>,
    pub preparation_note: Option<String>,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::recipe_ingredients)]
pub struct UpdateRecipeIngredient {
    pub quantity: Option<f64>,
    pub unit: Option<Option<String>>,
    pub preparation_note: Option<Option<String>>,
}

// ---- InventoryTransaction ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::inventory_transactions)]
pub struct InventoryTransaction {
    pub id: i32,
    pub ingredient_id: i32,
    pub transaction_type: String,
    pub quantity_change: f64,
    pub reference_id: Option<i32>,
    pub note: Option<String>,
    pub created_at: NaiveDateTime,
    pub uploaded: bool,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::inventory_transactions)]
pub struct NewInventoryTransaction {
    pub ingredient_id: i32,
    pub transaction_type: String,
    pub quantity_change: f64,
    pub reference_id: Option<i32>,
    pub note: Option<String>,
}

// ---- DeliveryType ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::delivery_types)]
pub struct DeliveryType {
    pub id: i32,
    pub name: String,
    pub description: Option<String>,
    pub fee_multiplier: f64,
    pub is_active: bool,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::delivery_types)]
pub struct NewDeliveryType {
    pub name: String,
    pub description: Option<String>,
    pub fee_multiplier: f64,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::delivery_types)]
pub struct UpdateDeliveryType {
    pub name: Option<String>,
    pub description: Option<Option<String>>,
    pub fee_multiplier: Option<f64>,
    pub is_active: Option<bool>,
}

// ---- EmployeeType ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::employee_types)]
pub struct EmployeeType {
    pub id: i32,
    pub name: String,
    pub description: Option<String>,
    pub is_active: bool,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::employee_types)]
pub struct NewEmployeeType {
    pub name: String,
    pub description: Option<String>,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::employee_types)]
pub struct UpdateEmployeeType {
    pub name: Option<String>,
    pub description: Option<Option<String>>,
    pub is_active: Option<bool>,
}

// ---- Employee ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::employees)]
pub struct Employee {
    pub id: i32,
    pub name: String,
    pub phone: Option<String>,
    pub email: Option<String>,
    pub employee_type_id: i32,
    pub salary: f64,
    pub is_active: bool,
    pub joined_at: Option<String>,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
    pub uploaded: bool,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::employees)]
pub struct NewEmployee {
    pub name: String,
    pub phone: Option<String>,
    pub email: Option<String>,
    pub employee_type_id: i32,
    pub salary: f64,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::employees)]
pub struct UpdateEmployee {
    pub name: Option<String>,
    pub phone: Option<Option<String>>,
    pub email: Option<Option<String>>,
    pub employee_type_id: Option<i32>,
    pub salary: Option<f64>,
    pub is_active: Option<bool>,
    pub uploaded: Option<bool>,
}

// ---- InventoryAdjustment ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::inventory_adjustments)]
pub struct InventoryAdjustment {
    pub id: i32,
    pub ingredient_id: i32,
    pub previous_quantity: f64,
    pub new_quantity: f64,
    pub reason: String,
    pub created_by: Option<String>,
    pub created_at: NaiveDateTime,
    pub uploaded: bool,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::inventory_adjustments)]
pub struct NewInventoryAdjustment {
    pub ingredient_id: i32,
    pub previous_quantity: f64,
    pub new_quantity: f64,
    pub reason: String,
    pub created_by: Option<String>,
}

// ---- Role ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::roles)]
pub struct Role {
    pub id: i32,
    pub name: String,
    pub permissions: String,
    pub is_active: bool,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::roles)]
pub struct NewRole {
    pub name: String,
    pub permissions: String,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::roles)]
pub struct UpdateRole {
    pub name: Option<String>,
    pub permissions: Option<String>,
    pub is_active: Option<bool>,
}

// ---- UserRole ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::user_roles)]
pub struct UserRole {
    pub user_id: i32,
    pub role_id: i32,
    pub created_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::user_roles)]
pub struct NewUserRole {
    pub user_id: i32,
    pub role_id: i32,
}

// ---- ReportMetadata ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::report_metadata)]
pub struct ReportMetadata {
    pub id: i32,
    pub report_type: String,
    pub format: String,
    pub file_path: String,
    pub parameters: Option<String>,
    pub generated_by: Option<i32>,
    pub created_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::report_metadata)]
pub struct NewReportMetadata {
    pub report_type: String,
    pub format: String,
    pub file_path: String,
    pub parameters: Option<String>,
    pub generated_by: Option<i32>,
}

// ---- InventoryAlert ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::inventory_alerts)]
pub struct InventoryAlert {
    pub id: i32,
    pub ingredient_id: i32,
    pub alert_type: String,
    pub alert_message: String,
    pub is_resolved: bool,
    pub created_at: NaiveDateTime,
    pub resolved_at: Option<NaiveDateTime>,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::inventory_alerts)]
pub struct NewInventoryAlert {
    pub ingredient_id: i32,
    pub alert_type: String,
    pub alert_message: String,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::inventory_alerts)]
pub struct UpdateInventoryAlert {
    pub is_resolved: Option<bool>,
    pub resolved_at: Option<Option<NaiveDateTime>>,
}

// ---- Supplier ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::suppliers)]
pub struct Supplier {
    pub id: i32,
    pub name: String,
    pub contact_name: Option<String>,
    pub email: Option<String>,
    pub phone: Option<String>,
    pub address: Option<String>,
    pub tax_id: Option<String>,
    pub payment_terms: Option<String>,
    pub is_active: bool,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::suppliers)]
pub struct NewSupplier {
    pub name: String,
    pub contact_name: Option<String>,
    pub email: Option<String>,
    pub phone: Option<String>,
    pub address: Option<String>,
    pub tax_id: Option<String>,
    pub payment_terms: Option<String>,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::suppliers)]
pub struct UpdateSupplier {
    pub name: Option<String>,
    pub contact_name: Option<Option<String>>,
    pub email: Option<Option<String>>,
    pub phone: Option<Option<String>>,
    pub address: Option<Option<String>>,
    pub tax_id: Option<Option<String>>,
    pub payment_terms: Option<Option<String>>,
    pub is_active: Option<bool>,
}

// ---- PurchaseOrder ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::purchase_orders)]
pub struct PurchaseOrder {
    pub id: i32,
    pub supplier_id: i32,
    pub reference_number: Option<String>,
    pub status: String,
    pub total_amount: f64,
    pub shipping_fee: f64,
    pub expected_date: Option<NaiveDateTime>,
    pub notes: Option<String>,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::purchase_orders)]
pub struct NewPurchaseOrder {
    pub supplier_id: i32,
    pub reference_number: Option<String>,
    pub status: String,
    pub total_amount: f64,
    pub shipping_fee: f64,
    pub expected_date: Option<NaiveDateTime>,
    pub notes: Option<String>,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::purchase_orders)]
pub struct UpdatePurchaseOrder {
    pub supplier_id: Option<i32>,
    pub reference_number: Option<Option<String>>,
    pub status: Option<String>,
    pub total_amount: Option<f64>,
    pub shipping_fee: Option<f64>,
    pub expected_date: Option<Option<NaiveDateTime>>,
    pub notes: Option<Option<String>>,
}

// ---- DeliveryZone ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::delivery_zones)]
pub struct DeliveryZone {
    pub id: i32,
    pub name: String,
    pub base_fee: f64,
    pub fee_per_km: f64,
    pub max_distance: f64,
    pub is_active: bool,
    pub created_at: chrono::NaiveDateTime,
    pub updated_at: chrono::NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::delivery_zones)]
pub struct NewDeliveryZone {
    pub name: String,
    pub base_fee: f64,
    pub fee_per_km: f64,
    pub max_distance: f64,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::delivery_zones)]
pub struct UpdateDeliveryZone {
    pub name: Option<String>,
    pub base_fee: Option<f64>,
    pub fee_per_km: Option<f64>,
    pub max_distance: Option<f64>,
    pub is_active: Option<bool>,
}

// ---- PurchaseOrderItem ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::purchase_order_items)]
pub struct PurchaseOrderItem {
    pub id: i32,
    pub purchase_order_id: i32,
    pub ingredient_id: i32,
    pub quantity: f64,
    pub cost_per_unit: f64,
    pub received_quantity: f64,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::purchase_order_items)]
pub struct NewPurchaseOrderItem {
    pub purchase_order_id: i32,
    pub ingredient_id: i32,
    pub quantity: f64,
    pub cost_per_unit: f64,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::purchase_order_items)]
pub struct UpdatePurchaseOrderItem {
    pub ingredient_id: Option<i32>,
    pub quantity: Option<f64>,
    pub cost_per_unit: Option<f64>,
    pub received_quantity: Option<f64>,
}

// ---- KitchenTicket ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::kitchen_tickets)]
pub struct KitchenTicket {
    pub id: i32,
    pub sale_id: i32,
    pub status: String,
    pub priority: i32,
    pub prepare_time_minutes: i32,
    pub notes: Option<String>,
    pub created_at: NaiveDateTime,
    pub completed_at: Option<NaiveDateTime>,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::kitchen_tickets)]
pub struct NewKitchenTicket {
    pub sale_id: i32,
    pub status: String,
    pub priority: i32,
    pub prepare_time_minutes: i32,
    pub notes: Option<String>,
}

/// A category that appears on a kitchen ticket (resolved via its sale items).
#[derive(Debug, Clone, Serialize)]
pub struct KitchenTicketCategory {
    pub ticket_id: i32,
    pub category_id: i32,
    pub name: String,
    pub color: Option<String>,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::kitchen_tickets)]
pub struct UpdateKitchenTicket {
    pub status: Option<String>,
    pub priority: Option<i32>,
    pub prepare_time_minutes: Option<i32>,
    pub notes: Option<Option<String>>,
    pub completed_at: Option<Option<NaiveDateTime>>,
}

// ---- Customer ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::customers)]
pub struct Customer {
    pub id: i32,
    pub name: String,
    pub phone: Option<String>,
    pub email: Option<String>,
    pub loyalty_points: f64,
    pub notes: Option<String>,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::customers)]
pub struct NewCustomer {
    pub name: String,
    pub phone: Option<String>,
    pub email: Option<String>,
    pub notes: Option<String>,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::customers)]
pub struct UpdateCustomer {
    pub name: Option<String>,
    pub phone: Option<Option<String>>,
    pub email: Option<Option<String>>,
    pub loyalty_points: Option<f64>,
    pub notes: Option<Option<String>>,
}

// ---- LoyaltyTransaction ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::loyalty_transactions)]
pub struct LoyaltyTransaction {
    pub id: i32,
    pub customer_id: i32,
    pub sale_id: Option<i32>,
    pub points_change: f64,
    pub reason: String,
    pub created_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::loyalty_transactions)]
pub struct NewLoyaltyTransaction {
    pub customer_id: i32,
    pub sale_id: Option<i32>,
    pub points_change: f64,
    pub reason: String,
}

// ---- Note (DB table: receipt_templates) ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::receipt_templates)]
pub struct Note {
    pub id: i32,
    pub name: String,
    pub template_body: String,
    pub category: Option<String>,
    pub recipe_id: Option<i32>,
    pub is_default: bool,
    pub use_as_template: bool,
    pub selectable: bool,
    pub steps: Option<String>,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::receipt_templates)]
pub struct NewNote {
    pub name: String,
    pub template_body: String,
    pub category: Option<String>,
    pub recipe_id: Option<i32>,
    #[serde(default)]
    pub use_as_template: bool,
    #[serde(default)]
    pub selectable: bool,
    #[serde(default)]
    pub steps: Option<String>,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::receipt_templates)]
pub struct UpdateNote {
    pub name: Option<String>,
    pub template_body: Option<String>,
    pub category: Option<Option<String>>,
    pub recipe_id: Option<Option<i32>>,
    pub is_default: Option<bool>,
    pub use_as_template: Option<bool>,
    pub selectable: Option<bool>,
    pub steps: Option<Option<String>>,
}

// ---- SupportMessage (DB table: support_messages) ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::support_messages)]
pub struct SupportMessage {
    pub id: i32,
    pub name: String,
    pub email: String,
    pub phone: Option<String>,
    pub subject: Option<String>,
    pub category: Option<String>,
    pub priority: String,
    pub message: String,
    pub status: String,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::support_messages)]
pub struct NewSupportMessage {
    pub name: String,
    pub email: String,
    pub phone: Option<String>,
    pub subject: Option<String>,
    pub category: Option<String>,
    #[serde(default = "default_support_priority")]
    pub priority: String,
    pub message: String,
    #[serde(default = "default_support_status")]
    pub status: String,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::support_messages)]
pub struct UpdateSupportMessage {
    pub status: Option<String>,
    pub priority: Option<String>,
}

fn default_support_priority() -> String {
    "normal".to_string()
}

fn default_support_status() -> String {
    "new".to_string()
}

// ---- TaxReport ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::tax_reports)]
pub struct TaxReport {
    pub id: i32,
    pub period_start: String,
    pub period_end: String,
    pub total_sales: f64,
    pub total_tax: f64,
    pub transaction_count: i32,
    pub generated_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::tax_reports)]
pub struct NewTaxReport {
    pub period_start: String,
    pub period_end: String,
    pub total_sales: f64,
    pub total_tax: f64,
    pub transaction_count: i32,
}

// ---- EmployeeSchedule ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::employee_schedules)]
pub struct EmployeeSchedule {
    pub id: i32,
    pub employee_id: i32,
    pub shift_start: NaiveDateTime,
    pub shift_end: NaiveDateTime,
    pub status: String,
    pub notes: Option<String>,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::employee_schedules)]
pub struct NewEmployeeSchedule {
    pub employee_id: i32,
    pub shift_start: NaiveDateTime,
    pub shift_end: NaiveDateTime,
    pub status: String,
    pub notes: Option<String>,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::employee_schedules)]
pub struct UpdateEmployeeSchedule {
    pub employee_id: Option<i32>,
    pub shift_start: Option<NaiveDateTime>,
    pub shift_end: Option<NaiveDateTime>,
    pub status: Option<String>,
    pub notes: Option<Option<String>>,
}

// ---- Payroll ----
#[derive(Debug, Queryable, Selectable, Serialize, Deserialize, Clone)]
#[diesel(table_name = crate::db::schema::payrolls)]
pub struct Payroll {
    pub id: i32,
    pub employee_id: i32,
    pub period_start: String,
    pub period_end: String,
    pub regular_hours: f64,
    pub overtime_hours: f64,
    pub total_pay: f64,
    pub status: String,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Debug, Insertable, Deserialize)]
#[diesel(table_name = crate::db::schema::payrolls)]
pub struct NewPayroll {
    pub employee_id: i32,
    pub period_start: String,
    pub period_end: String,
    pub regular_hours: f64,
    pub overtime_hours: f64,
    pub total_pay: f64,
    pub status: String,
}

#[derive(Debug, AsChangeset, Deserialize)]
#[diesel(table_name = crate::db::schema::payrolls)]
pub struct UpdatePayroll {
    pub employee_id: Option<i32>,
    pub period_start: Option<String>,
    pub period_end: Option<String>,
    pub regular_hours: Option<f64>,
    pub overtime_hours: Option<f64>,
    pub total_pay: Option<f64>,
    pub status: Option<String>,
}
