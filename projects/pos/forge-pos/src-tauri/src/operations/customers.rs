use crate::db::models::*;
use crate::db::schema::{customers, loyalty_transactions};
use diesel::prelude::*;
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

pub fn add_loyalty_transaction(db_path: &PathBuf, transaction: NewLoyaltyTransaction) -> Result<LoyaltyTransaction, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(loyalty_transactions::table).values(&transaction).execute(conn)?;
        loyalty_transactions::table.order(loyalty_transactions::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}
