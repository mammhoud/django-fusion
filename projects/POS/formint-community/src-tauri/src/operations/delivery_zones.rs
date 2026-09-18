use diesel::prelude::*;
use crate::db::{models::*, open_conn};
use std::path::PathBuf;

pub fn get_delivery_zones(db_path: &PathBuf, include_inactive: bool) -> Result<Vec<DeliveryZone>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::delivery_zones::dsl::*;
    let mut query = delivery_zones.into_boxed();
    if !include_inactive {
        query = query.filter(is_active.eq(true));
    }
    query.order(name.asc())
        .load::<DeliveryZone>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_delivery_zone(db_path: &PathBuf, new: NewDeliveryZone) -> Result<DeliveryZone, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::delivery_zones::dsl::*;
    diesel::insert_into(delivery_zones)
        .values(&new)
        .returning(DeliveryZone::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn update_delivery_zone(db_path: &PathBuf, zone_id: i32, update: UpdateDeliveryZone) -> Result<DeliveryZone, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::delivery_zones::dsl::*;
    diesel::update(delivery_zones.filter(id.eq(zone_id)))
        .set(&update)
        .returning(DeliveryZone::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn soft_delete_delivery_zone(db_path: &PathBuf, zone_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::delivery_zones::dsl::*;
    diesel::update(delivery_zones.filter(id.eq(zone_id)))
        .set(is_active.eq(false))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
