use diesel::prelude::*;
use crate::db::{models::*, open_conn};
use std::path::PathBuf;

pub fn get_delivery_types(db_path: &PathBuf, include_inactive: bool) -> Result<Vec<DeliveryType>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::delivery_types::dsl::*;
    let mut query = delivery_types.into_boxed();
    if !include_inactive {
        query = query.filter(is_active.eq(true));
    }
    query.order(id.asc()).load::<DeliveryType>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_delivery_type(db_path: &PathBuf, new: NewDeliveryType) -> Result<DeliveryType, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::delivery_types::dsl::*;
    diesel::insert_into(delivery_types)
        .values(&new)
        .returning(DeliveryType::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn update_delivery_type(db_path: &PathBuf, type_id: i32, update: UpdateDeliveryType) -> Result<DeliveryType, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::delivery_types::dsl::*;
    diesel::update(delivery_types.filter(id.eq(type_id)))
        .set(&update)
        .returning(DeliveryType::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn soft_delete_delivery_type(db_path: &PathBuf, type_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::delivery_types::dsl::*;
    diesel::update(delivery_types.filter(id.eq(type_id)))
        .set(is_active.eq(false))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
