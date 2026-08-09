use crate::db::models::*;
use crate::db::schema::coupons;
use diesel::prelude::*;
use std::path::PathBuf;

pub fn get_coupons(db_path: &PathBuf) -> Result<Vec<Coupon>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    coupons::table
        .select(Coupon::as_select())
        .order(coupons::code.asc())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn get_active_coupons(db_path: &PathBuf) -> Result<Vec<Coupon>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    coupons::table
        .filter(coupons::is_active.eq(true))
        .select(Coupon::as_select())
        .order(coupons::code.asc())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_coupon(db_path: &PathBuf, template: NewCoupon) -> Result<Coupon, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(coupons::table).values(&template).execute(conn)?;
        coupons::table.order(coupons::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn update_coupon(db_path: &PathBuf, id: i32, update: UpdateCoupon) -> Result<Coupon, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::update(coupons::table.find(id)).set(&update).execute(conn)?;
        coupons::table.find(id).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn delete_coupon(db_path: &PathBuf, id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::delete(coupons::table.find(id))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
