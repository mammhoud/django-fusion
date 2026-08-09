use diesel::prelude::*;
use crate::db::{models::*, open_conn};
use std::path::PathBuf;

pub fn add_sale(db_path: &PathBuf, new_sale: NewSale, items: Vec<NewSaleItem>) -> Result<(Sale, KitchenTicket), String> {
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
            "extra-order" => 1,
            "takeaway" => 2,
            "dated-order" => 2,
            "delivery" => 3,
            _ => 2,
        };
        // Default preparation time based on order priority
        // Dine-in / extra-order: 15 min, takeaway / dated-order: 20 min, delivery: 25 min
        use crate::db::schema::kitchen_tickets::dsl as kt;
        let ticket = NewKitchenTicket {
            sale_id: sale.id,
            status: "pending".to_string(),
            priority,
            prepare_time_minutes: match priority {
                1 => 15,
                2 => 20,
                _ => 25,
            },
            notes: None,
        };
        diesel::insert_into(crate::db::schema::kitchen_tickets::table)
            .values(&ticket)
            .execute(conn)?;

        let created: KitchenTicket = kt::kitchen_tickets
            .order(kt::id.desc())
            .first(conn)?;

        Ok((sale, created))
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

/// Mark a sale as refunded. The `status` column already exists on `sales`
/// and accepts "refunded" — no schema change is required. A sale can only
/// be refunded once.
pub fn refund_sale(db_path: &PathBuf, sale_id: i32) -> Result<Sale, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::sales::dsl::*;

    let sale: Sale = sales
        .filter(id.eq(sale_id))
        .first(&mut conn)
        .map_err(|e| format!("sale {sale_id} not found: {e}"))?;
    if sale.status == "refunded" {
        return Err(format!("sale {sale_id} is already refunded"));
    }

    diesel::update(sales.filter(id.eq(sale_id)))
        .set(status.eq("refunded"))
        .returning(Sale::as_returning())
        .get_result(&mut conn)
        .map_err(|e| format!("failed to refund sale {sale_id}: {e}"))
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

#[cfg(test)]
mod tests {
    use super::*;

    fn temp_db_path(tag: &str) -> std::path::PathBuf {
        let mut path = std::env::temp_dir();
        path.push(format!("formint-pos-refund-test-{}-{}.db", std::process::id(), tag));
        let _ = std::fs::remove_file(&path);
        crate::db::run_migrations(&path).expect("migrations should succeed");
        path
    }

    fn seed_sale(db_path: &PathBuf) -> Sale {
        add_sale(
            db_path,
            NewSale {
                total_amount: 25.0,
                currency: "USD".to_string(),
                date: None,
                time: None,
                order_type: "dine_in".to_string(),
                status: "completed".to_string(),
                table_number: Some(1),
                delivery_type_id: None,
                delivery_zone_id: None,
                delivery_address: None,
                employee_id: None,
                customer_id: None,
                discount_code: None,
                discount_amount: 0.0,
                payment_method: "cash".to_string(),
            },
            vec![],
        )
        .expect("add_sale should succeed")
        .0
    }

    #[test]
    fn refund_sale_marks_sale_refunded() {
        let db_path = temp_db_path("ok");
        let sale = seed_sale(&db_path);
        let refunded = refund_sale(&db_path, sale.id).expect("refund should succeed");
        assert_eq!(refunded.status, "refunded");
        let _ = std::fs::remove_file(&db_path);
    }

    #[test]
    fn refund_sale_rejects_double_refund() {
        let db_path = temp_db_path("double");
        let sale = seed_sale(&db_path);
        refund_sale(&db_path, sale.id).expect("first refund should succeed");
        let err = refund_sale(&db_path, sale.id).expect_err("second refund must fail");
        assert!(err.contains("already refunded"), "unexpected error: {err}");
        let _ = std::fs::remove_file(&db_path);
    }

    #[test]
    fn refund_sale_rejects_missing_sale() {
        let db_path = temp_db_path("missing");
        let err = refund_sale(&db_path, 999_999).expect_err("missing sale must fail");
        assert!(err.contains("not found"), "unexpected error: {err}");
        let _ = std::fs::remove_file(&db_path);
    }
}
