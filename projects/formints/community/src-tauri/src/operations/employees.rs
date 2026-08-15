use diesel::prelude::*;
use crate::db::{models::*, open_conn};
use std::path::PathBuf;

pub fn get_employees(db_path: &PathBuf, include_inactive: bool) -> Result<Vec<Employee>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::employees::dsl::*;
    let mut query = employees.into_boxed();
    if !include_inactive {
        query = query.filter(is_active.eq(true));
    }
    query.order(id.asc()).load::<Employee>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_employee(db_path: &PathBuf, new: NewEmployee) -> Result<Employee, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::employees::dsl::*;
    diesel::insert_into(employees)
        .values(&new)
        .returning(Employee::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn update_employee(db_path: &PathBuf, employee_id: i32, update: UpdateEmployee) -> Result<Employee, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::employees::dsl::*;
    diesel::update(employees.filter(id.eq(employee_id)))
        .set(&update)
        .returning(Employee::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn soft_delete_employee(db_path: &PathBuf, employee_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::employees::dsl::*;
    diesel::update(employees.filter(id.eq(employee_id)))
        .set(is_active.eq(false))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}

pub fn mark_employee_uploaded(db_path: &PathBuf, employee_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::employees::dsl::*;
    diesel::update(employees.filter(id.eq(employee_id)))
        .set(uploaded.eq(true))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
