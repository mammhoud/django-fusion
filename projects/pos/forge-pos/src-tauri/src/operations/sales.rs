use diesel::prelude::*;
use crate::db::{models::*, open_conn};
use std::path::PathBuf;

pub fn add_sale(db_path: &PathBuf, new_sale: NewSale, items: Vec<NewSaleItem>) -> Result<Sale, String> {
    let mut conn = open_conn(db_path)?;
    conn.transaction(|conn| {
        use crate::db::schema::sales::dsl::*;
        let sale: Sale = diesel::insert_into(sales)
            .values(&new_sale)
            .returning(Sale::as_returning())
            .get_result(conn)?;
        for mut item in items {
            item.sale_id = sale.id;
            diesel::insert_into(crate::db::schema::sale_items::table)
                .values(&item)
                .execute(conn)?;
        }

        // Auto-create a kitchen ticket for this sale so the KDS has work to display.
        // Dine-in and takeaway orders go to the kitchen; delivery orders are
        // treated as lower priority but still tracked.
        let priority = match sale.order_type.as_str() {
            "dine-in" => 1,
            "takeaway" => 2,
            "delivery" => 3,
            _ => 2,
        };
        let ticket = NewKitchenTicket {
            sale_id: sale.id,
            status: "pending".to_string(),
            priority,
            notes: None,
        };
        diesel::insert_into(crate::db::schema::kitchen_tickets::table)
            .values(&ticket)
            .execute(conn)?;

        Ok(sale)
    }).map_err(|e: diesel::result::Error| e.to_string())
}

pub fn get_sales(db_path: &PathBuf) -> Result<Vec<Sale>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::sales::dsl::*;
    sales.order(id.desc()).load::<Sale>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn get_sale_with_items(db_path: &PathBuf, sale_id: i32) -> Result<(Sale, Vec<SaleItem>), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::{sales, sale_items};
    let sale: Sale = sales::table.find(sale_id)
        .first(&mut conn)
        .map_err(|e| e.to_string())?;
    let items: Vec<SaleItem> = sale_items::table
        .filter(sale_items::sale_id.eq(sale_id))
        .load::<SaleItem>(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok((sale, items))
}

pub fn update_sale(db_path: &PathBuf, sale_id: i32, update: UpdateSale) -> Result<Sale, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::sales::dsl::*;
    diesel::update(sales.filter(id.eq(sale_id)))
        .set(&update)
        .returning(Sale::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn delete_sale(db_path: &PathBuf, sale_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::sales::dsl::*;
    diesel::delete(sales.filter(id.eq(sale_id)))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}

/// Fetch sale items for a given sale_id (used by Kitchen Display for detail modals)
pub fn get_sale_items_by_sale_id(db_path: &PathBuf, target_sale_id: i32) -> Result<Vec<SaleItem>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::sale_items::dsl::*;
    sale_items
        .filter(sale_id.eq(target_sale_id))
        .load::<SaleItem>(&mut conn)
        .map_err(|e| e.to_string())
}

/// Fetch a single sale by its ID (used by KDS for detail modals)
pub fn get_sale_by_id(db_path: &PathBuf, target_sale_id: i32) -> Result<Sale, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::sales::dsl::*;
    sales.find(target_sale_id)
        .first::<Sale>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn mark_sale_uploaded(db_path: &PathBuf, sale_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::sales::dsl::*;
    diesel::update(sales.filter(id.eq(sale_id)))
        .set(uploaded.eq(true))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
