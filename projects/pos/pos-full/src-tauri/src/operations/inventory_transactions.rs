use diesel::prelude::*;
use crate::db::{models::*, schema::{ingredients, inventory_transactions, inventory_adjustments}, open_conn};
use std::path::PathBuf;

/// Error returned when an inventory transaction would cause negative stock.
/// Defined for bluebrint compatibility; Diesel 2.3 uses unit variant for rollback.
#[allow(dead_code)]
#[derive(Debug, thiserror::Error)]
#[error("Insufficient stock for ingredient: {0}")]
pub struct InsufficientStockError(pub String);

pub fn add_inventory_transaction(
    db_path: &PathBuf,
    transaction: NewInventoryTransaction,
    adjustment_reason: Option<String>,
    created_by: Option<String>,
) -> Result<InventoryTransaction, String> {
    let mut conn = open_conn(db_path)?;
    conn.transaction(|conn| {
        let ing: Ingredient = ingredients::table.find(transaction.ingredient_id)
            .first::<Ingredient>(conn)?;

        let new_quantity = ing.current_quantity + transaction.quantity_change;

        if new_quantity < 0.0 {
            // Rollback with InsufficientStockError
            return Err(diesel::result::Error::RollbackTransaction);
        }

        diesel::update(ingredients::table.find(transaction.ingredient_id))
            .set(ingredients::current_quantity.eq(new_quantity))
            .execute(conn)?;

        let inserted: InventoryTransaction = diesel::insert_into(inventory_transactions::table)
            .values(&transaction)
            .returning(InventoryTransaction::as_returning())
            .get_result(conn)?;

        if let Some(reason) = adjustment_reason {
            let adj = NewInventoryAdjustment {
                ingredient_id: transaction.ingredient_id,
                previous_quantity: ing.current_quantity,
                new_quantity,
                reason,
                created_by,
            };
            diesel::insert_into(inventory_adjustments::table)
                .values(&adj)
                .execute(conn)?;
        }

        Ok(inserted)
    }).map_err(|e: diesel::result::Error| e.to_string())
}

pub fn get_inventory_transactions(
    db_path: &PathBuf,
    ingredient_id_filter: Option<i32>,
) -> Result<Vec<InventoryTransaction>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::inventory_transactions::dsl::*;
    let mut query = inventory_transactions.into_boxed();
    if let Some(filter_id) = ingredient_id_filter {
        query = query.filter(ingredient_id.eq(filter_id));
    }
    query.order(created_at.desc())
        .load::<InventoryTransaction>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn get_inventory_adjustments(
    db_path: &PathBuf,
    ingredient_id_filter: Option<i32>,
) -> Result<Vec<InventoryAdjustment>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::inventory_adjustments::dsl::*;
    let mut query = inventory_adjustments.into_boxed();
    if let Some(filter_id) = ingredient_id_filter {
        query = query.filter(ingredient_id.eq(filter_id));
    }
    query.order(created_at.desc())
        .load::<InventoryAdjustment>(&mut conn)
        .map_err(|e| e.to_string())
}
