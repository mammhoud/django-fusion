use diesel::prelude::*;
use crate::db::{models::*, schema::{sales, sale_items}, open_conn};
use std::path::PathBuf;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct TransactionItem {
    pub name: String,
    pub price: f64,
    pub quantity: f64,
    pub unit: String,
    pub subtotal: f64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Transaction {
    pub id: i32,
    pub items: Vec<TransactionItem>,
    pub total_amount: f64,
    pub currency: String,
    pub date: String,
    pub time: String,
    pub order_type: String,
    pub status: String,
}

pub fn get_transactions(db_path: &PathBuf) -> Result<Vec<Transaction>, String> {
    let mut conn = open_conn(db_path)?;
    let all_sales: Vec<Sale> = sales::table
        .order(sales::id.desc())
        .load::<Sale>(&mut conn)
        .map_err(|e| e.to_string())?;

    let mut transactions = Vec::new();
    for sale in all_sales {
        let items: Vec<SaleItem> = sale_items::table
            .filter(sale_items::sale_id.eq(sale.id))
            .load::<SaleItem>(&mut conn)
            .map_err(|e| e.to_string())?;

        let transaction_items = items.into_iter().map(|item| TransactionItem {
            name: item.product_name,
            price: item.price,
            quantity: item.quantity,
            unit: item.unit,
            subtotal: item.subtotal,
        }).collect();

        transactions.push(Transaction {
            id: sale.id,
            items: transaction_items,
            total_amount: sale.total_amount,
            currency: sale.currency,
            date: sale.date,
            time: sale.time,
            order_type: sale.order_type,
            status: sale.status,
        });
    }
    Ok(transactions)
}

pub fn delete_transaction(db_path: &PathBuf, id_val: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::sales::dsl::*;
    diesel::delete(sales.filter(id.eq(id_val)))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
