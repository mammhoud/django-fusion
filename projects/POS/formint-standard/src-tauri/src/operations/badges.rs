use crate::db::models::*;
use crate::db::schema::badges;
use diesel::prelude::*;
use std::path::PathBuf;

pub fn get_badges(db_path: &PathBuf) -> Result<Vec<Badge>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    badges::table
        .select(Badge::as_select())
        .order(badges::threshold.asc())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_badge(db_path: &PathBuf, badge: NewBadge) -> Result<Badge, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(badges::table)
            .values(&badge)
            .execute(conn)?;
        badges::table.order(badges::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn update_badge(db_path: &PathBuf, id: i32, update: UpdateBadge) -> Result<Badge, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::update(badges::table.find(id))
            .set(&update)
            .execute(conn)?;
        badges::table.find(id).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn delete_badge(db_path: &PathBuf, id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::delete(badges::table.find(id))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
