use crate::db::models::*;
use crate::db::schema::roles;
use crate::db::schema::user_roles;
use diesel::prelude::*;
use std::path::PathBuf;

pub fn get_roles(db_path: &PathBuf) -> Result<Vec<Role>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    roles::table
        .filter(roles::is_active.eq(true))
        .select(Role::as_select())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_role(db_path: &PathBuf, role: NewRole) -> Result<Role, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(roles::table)
            .values(&role)
            .execute(conn)?;
        roles::table.order(roles::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn update_role(db_path: &PathBuf, id: i32, update: UpdateRole) -> Result<Role, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::update(roles::table.find(id))
            .set(&update)
            .execute(conn)?;
        roles::table.find(id).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn soft_delete_role(db_path: &PathBuf, id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::update(roles::table.find(id))
        .set(roles::is_active.eq(false))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}

pub fn get_user_roles(db_path: &PathBuf, user_id: i32) -> Result<Vec<Role>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    user_roles::table
        .inner_join(roles::table)
        .filter(user_roles::user_id.eq(user_id))
        .select(Role::as_select())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn assign_role(db_path: &PathBuf, user_id: i32, role_id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    let new_user_role = NewUserRole { user_id, role_id };
    diesel::insert_into(user_roles::table)
        .values(&new_user_role)
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}

pub fn remove_role(db_path: &PathBuf, user_id: i32, role_id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::delete(
        user_roles::table
            .filter(user_roles::user_id.eq(user_id))
            .filter(user_roles::role_id.eq(role_id)),
    )
    .execute(&mut conn)
    .map_err(|e| e.to_string())?;
    Ok(())
}
