use crate::db::models::*;
use crate::db::schema::receipt_templates;// DB table: receipt_templates
use diesel::prelude::*;
use std::path::PathBuf;

pub fn get_notes(db_path: &PathBuf) -> Result<Vec<Note>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    receipt_templates::table
        .select(Note::as_select())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn get_default_note(db_path: &PathBuf) -> Result<Note, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    receipt_templates::table
        .filter(receipt_templates::is_default.eq(true))
        .first(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_note(db_path: &PathBuf, template: NewNote) -> Result<Note, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(receipt_templates::table).values(&template).execute(conn)?;
        receipt_templates::table.order(receipt_templates::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn update_note(db_path: &PathBuf, id: i32, update: UpdateNote) -> Result<Note, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::update(receipt_templates::table.find(id)).set(&update).execute(conn)?;
        receipt_templates::table.find(id).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn get_recipe_notes(db_path: &PathBuf, recipe_id: i32) -> Result<Vec<Note>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    receipt_templates::table
        .filter(receipt_templates::recipe_id.eq(recipe_id))
        .select(Note::as_select())
        .order(receipt_templates::created_at.desc())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_recipe_note(db_path: &PathBuf, template: NewNote) -> Result<Note, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(receipt_templates::table).values(&template).execute(conn)?;
        receipt_templates::table.order(receipt_templates::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn delete_note(db_path: &PathBuf, id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::delete(receipt_templates::table.find(id))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
