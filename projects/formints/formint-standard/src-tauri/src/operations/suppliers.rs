use crate::db::models::*;
use crate::db::schema::suppliers;
use diesel::prelude::*;
use std::path::PathBuf;

pub fn get_suppliers(db_path: &PathBuf, include_inactive: bool) -> Result<Vec<Supplier>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    let mut query = suppliers::table.into_boxed();
    if !include_inactive {
        query = query.filter(suppliers::is_active.eq(true));
    }
    query.select(Supplier::as_select()).load(&mut conn).map_err(|e| e.to_string())
}

pub fn add_supplier(db_path: &PathBuf, supplier: NewSupplier) -> Result<Supplier, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(suppliers::table).values(&supplier).execute(conn)?;
        suppliers::table.order(suppliers::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn update_supplier(db_path: &PathBuf, id: i32, update: UpdateSupplier) -> Result<Supplier, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::update(suppliers::table.find(id)).set(&update).execute(conn)?;
        suppliers::table.find(id).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn soft_delete_supplier(db_path: &PathBuf, id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::update(suppliers::table.find(id))
        .set(suppliers::is_active.eq(false))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
