use crate::db::models::*;
use crate::db::schema::{customers, loyalty_transactions};
use chrono::NaiveDateTime;
use diesel::prelude::*;
use serde::Serialize;
use std::path::PathBuf;

pub fn get_customers(db_path: &PathBuf) -> Result<Vec<Customer>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    customers::table.select(Customer::as_select()).load(&mut conn).map_err(|e| e.to_string())
}

pub fn add_customer(db_path: &PathBuf, customer: NewCustomer) -> Result<Customer, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(customers::table).values(&customer).execute(conn)?;
        customers::table.order(customers::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn update_customer(db_path: &PathBuf, id: i32, update: UpdateCustomer) -> Result<Customer, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::update(customers::table.find(id)).set(&update).execute(conn)?;
        customers::table.find(id).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn delete_customer(db_path: &PathBuf, id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::delete(customers::table.find(id))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}

pub fn get_loyalty_transactions(db_path: &PathBuf, customer_id: i32) -> Result<Vec<LoyaltyTransaction>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    loyalty_transactions::table
        .filter(loyalty_transactions::customer_id.eq(customer_id))
        .select(LoyaltyTransaction::as_select())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}

#[derive(Debug, Serialize, Queryable)]
pub struct LoyaltyReportRow {
    pub id: i32,
    pub customer_id: i32,
    pub customer_name: String,
    pub sale_id: Option<i32>,
    pub points_change: f64,
    pub reason: String,
    pub created_at: NaiveDateTime,
}

/// All loyalty transactions joined with the customer name — powers the
/// loyalty report without N+1 client-side lookups.
pub fn get_all_loyalty_transactions(db_path: &PathBuf, limit: Option<i64>) -> Result<Vec<LoyaltyReportRow>, String> {
    use crate::db::schema::customers as c;
    use crate::db::schema::loyalty_transactions as lt;
    let mut conn = crate::db::open_conn(db_path)?;
    let mut query = lt::table
        .inner_join(c::table)
        .select((
            lt::id,
            lt::customer_id,
            c::name,
            lt::sale_id,
            lt::points_change,
            lt::reason,
            lt::created_at,
        ))
        .order(lt::id.desc())
        .into_boxed();
    if let Some(n) = limit {
        query = query.limit(n);
    }
    query
        .load::<LoyaltyReportRow>(&mut conn)
        .map_err(|e| e.to_string())
}

/// Adds a loyalty transaction and bumps the customer's running balance atomically.
pub fn add_loyalty_transaction(db_path: &PathBuf, transaction: NewLoyaltyTransaction) -> Result<LoyaltyTransaction, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(loyalty_transactions::table).values(&transaction).execute(conn)?;
        // Keep customers.loyalty_points in sync.
        diesel::update(customers::table)
            .filter(customers::id.eq(transaction.customer_id))
            .set(customers::loyalty_points.eq(customers::loyalty_points + transaction.points_change))
            .execute(conn)?;
        loyalty_transactions::table.order(loyalty_transactions::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}
