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

/// Mark a sale as refunded. The `status` column already exists on `sales`
/// and accepts "refunded" — no schema change is required. A sale can only
/// be refunded once.
pub fn refund_sale(db_path: &PathBuf, sale_id: i32) -> Result<Sale, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::sales::dsl::*;

    let sale: Sale = sales
        .filter(id.eq(sale_id))
        .first(&mut conn)
        .map_err(|e| match e {
            diesel::result::Error::NotFound => format!("sale {sale_id} not found"),
            other => format!("failed to load sale {sale_id}: {other}"),
        })?;
    match sale.status.as_str() {
        "refunded" => {
            return Err(format!("sale {sale_id} is already refunded"));
        }
        "completed" => {}
        other_status => {
            return Err(format!(
                "sale {sale_id} cannot be refunded from status {other_status}"
            ));
        }
    }

    // Keep the eligibility check in the UPDATE predicate as well as the
    // user-facing validation above. This makes the transition atomic: two
    // concurrent refund requests cannot both move the same sale from
    // `completed` to `refunded`.
    match diesel::update(sales.filter(id.eq(sale_id)).filter(status.eq("completed")))
        .set(status.eq("refunded"))
        .returning(Sale::as_returning())
        .get_result::<Sale>(&mut conn)
    {
        Ok(refunded) => Ok(refunded),
        Err(diesel::result::Error::NotFound) => {
            let current: Sale = sales
                .filter(id.eq(sale_id))
                .first(&mut conn)
                .map_err(|e| match e {
                    diesel::result::Error::NotFound => format!("sale {sale_id} not found"),
                    other => format!("failed to reload sale {sale_id}: {other}"),
                })?;
            if current.status == "refunded" {
                Err(format!("sale {sale_id} is already refunded"))
            } else {
                Err(format!(
                    "sale {sale_id} cannot be refunded from status {}",
                    current.status
                ))
            }
        }
        Err(e) => Err(format!("failed to refund sale {sale_id}: {e}")),
    }
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

    #[test]
    fn refund_sale_rejects_non_completed_sales() {
        for status in ["pending", "cancelled"] {
            let db_path = temp_db_path(status);
            let sale = add_sale(
                &db_path,
                NewSale {
                    total_amount: 25.0,
                    currency: "USD".to_string(),
                    date: None,
                    time: None,
                    order_type: "dine_in".to_string(),
                    status: status.to_string(),
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
            .expect("add_sale should succeed");

            let err = refund_sale(&db_path, sale.id)
                .expect_err("only completed sales may be refunded");
            assert!(
                err.contains(&format!("cannot be refunded from status {status}")),
                "unexpected error: {err}"
            );
            let (unchanged, _) = get_sale_with_items(&db_path, sale.id).expect("sale should remain readable");
            assert_eq!(unchanged.status, status);
            let _ = std::fs::remove_file(&db_path);
        }
    }
}
