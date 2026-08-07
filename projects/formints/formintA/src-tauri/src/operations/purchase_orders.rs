use crate::db::models::*;
use crate::db::schema::{purchase_order_items, purchase_orders};
use diesel::prelude::*;
use std::path::PathBuf;

pub fn get_purchase_orders(db_path: &PathBuf) -> Result<Vec<PurchaseOrder>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    purchase_orders::table
        .select(PurchaseOrder::as_select())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn get_purchase_order_items(db_path: &PathBuf, order_id: i32) -> Result<Vec<PurchaseOrderItem>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    purchase_order_items::table
        .filter(purchase_order_items::purchase_order_id.eq(order_id))
        .select(PurchaseOrderItem::as_select())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_purchase_order(
    db_path: &PathBuf,
    order: NewPurchaseOrder,
    items: Vec<NewPurchaseOrderItem>,
) -> Result<PurchaseOrder, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(purchase_orders::table).values(&order).execute(conn)?;
        let order: PurchaseOrder = purchase_orders::table.order(purchase_orders::id.desc()).first(conn)?;
        let items: Vec<_> = items.into_iter().map(|mut item| {
            item.purchase_order_id = order.id;
            item
        }).collect();
        diesel::insert_into(purchase_order_items::table).values(&items).execute(conn)?;
        Ok(order)
    })
    .map_err(|e| e.to_string())
}

pub fn update_purchase_order(db_path: &PathBuf, id: i32, update: UpdatePurchaseOrder) -> Result<PurchaseOrder, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::update(purchase_orders::table.find(id)).set(&update).execute(conn)?;
        purchase_orders::table.find(id).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn delete_purchase_order(db_path: &PathBuf, id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::delete(purchase_orders::table.find(id))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
