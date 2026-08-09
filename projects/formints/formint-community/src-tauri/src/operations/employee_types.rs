use diesel::prelude::*;
use crate::db::{models::*, open_conn};
use std::path::PathBuf;

pub fn get_employee_types(db_path: &PathBuf, include_inactive: bool) -> Result<Vec<EmployeeType>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::employee_types::dsl::*;
    let mut query = employee_types.into_boxed();
    if !include_inactive {
        query = query.filter(is_active.eq(true));
    }
    query.order(id.asc()).load::<EmployeeType>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_employee_type(db_path: &PathBuf, new: NewEmployeeType) -> Result<EmployeeType, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::employee_types::dsl::*;
    diesel::insert_into(employee_types)
        .values(&new)
        .returning(EmployeeType::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn update_employee_type(db_path: &PathBuf, type_id: i32, update: UpdateEmployeeType) -> Result<EmployeeType, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::employee_types::dsl::*;
    diesel::update(employee_types.filter(id.eq(type_id)))
        .set(&update)
        .returning(EmployeeType::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn soft_delete_employee_type(db_path: &PathBuf, type_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::employee_types::dsl::*;
    diesel::update(employee_types.filter(id.eq(type_id)))
        .set(is_active.eq(false))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
