use crate::db::models::*;
use crate::db::schema::roles;
use crate::db::schema::user_roles;
use diesel::prelude::*;
use serde::Serialize;
use std::path::PathBuf;

/// A permission definition returned from the backend.
/// The frontend uses this to render the permission checklist dynamically.
#[derive(Debug, Serialize, Clone)]
pub struct PermissionDef {
    pub key: String,
    pub label: String,
    pub icon: String,
}

/// Returns the full catalog of available permissions.
/// This is the single source of truth — adding a new permission key here
/// will automatically surface it in the frontend Roles UI without any
/// frontend code changes.
pub fn get_permission_catalog() -> Vec<PermissionDef> {
    vec![
        PermissionDef { key: "manage:products".to_string(),   label: "Manage Products".to_string(),     icon: "clipboard-list".to_string() },
        PermissionDef { key: "manage:inventory".to_string(),  label: "Manage Inventory".to_string(),    icon: "package".to_string() },
        PermissionDef { key: "manage:employees".to_string(),  label: "Manage Employees".to_string(),    icon: "users".to_string() },
        PermissionDef { key: "manage:roles".to_string(),      label: "Manage Roles".to_string(),        icon: "shield".to_string() },
        PermissionDef { key: "process:sales".to_string(),     label: "Process Sales".to_string(),       icon: "shopping-cart".to_string() },
        PermissionDef { key: "manage:customers".to_string(),  label: "Manage Customers".to_string(),    icon: "user-circle".to_string() },
        PermissionDef { key: "manage:settings".to_string(),   label: "Manage Settings".to_string(),     icon: "settings".to_string() },
        PermissionDef { key: "view:reports".to_string(),      label: "View Reports".to_string(),        icon: "file-text".to_string() },
        PermissionDef { key: "view:analytics".to_string(),    label: "View Analytics".to_string(),      icon: "chart-bar".to_string() },
        PermissionDef { key: "view:transactions".to_string(), label: "View Transactions".to_string(),   icon: "history".to_string() },
        PermissionDef { key: "manage:suppliers".to_string(),  label: "Manage Suppliers".to_string(),    icon: "truck".to_string() },
        PermissionDef { key: "manage:kitchen".to_string(),    label: "Manage Kitchen".to_string(),      icon: "tools-kitchen-2".to_string() },
    ]
}

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
