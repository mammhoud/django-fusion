use crate::db::models::*;
use crate::db::schema::kitchen_tickets;
use diesel::prelude::*;
use std::path::PathBuf;

pub fn get_kitchen_tickets(db_path: &PathBuf, status: Option<String>) -> Result<Vec<KitchenTicket>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    let mut query = kitchen_tickets::table.into_boxed();
    if let Some(s) = status {
        query = query.filter(kitchen_tickets::status.eq(s));
    }
    query.select(KitchenTicket::as_select()).load(&mut conn).map_err(|e| e.to_string())
}

pub fn add_kitchen_ticket(db_path: &PathBuf, ticket: NewKitchenTicket) -> Result<KitchenTicket, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(kitchen_tickets::table).values(&ticket).execute(conn)?;
        kitchen_tickets::table.order(kitchen_tickets::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn update_kitchen_ticket(db_path: &PathBuf, id: i32, update: UpdateKitchenTicket) -> Result<KitchenTicket, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::update(kitchen_tickets::table.find(id)).set(&update).execute(conn)?;
        kitchen_tickets::table.find(id).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn delete_kitchen_ticket(db_path: &PathBuf, id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::delete(kitchen_tickets::table.find(id))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}

/// Count all kitchen tickets with status = 'pending'
pub fn count_pending_tickets(db_path: &PathBuf) -> Result<i64, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    use diesel::dsl::count;
    kitchen_tickets::table
        .filter(kitchen_tickets::status.eq("pending"))
        .select(count(kitchen_tickets::id))
        .first::<i64>(&mut conn)
        .map_err(|e| e.to_string())
}
