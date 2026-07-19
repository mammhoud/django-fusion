use crate::db::models::*;
use crate::db::schema::employee_schedules;
use diesel::prelude::*;
use std::path::PathBuf;

pub fn get_employee_schedules(db_path: &PathBuf, employee_id: Option<i32>) -> Result<Vec<EmployeeSchedule>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    let mut query = employee_schedules::table.into_boxed();
    if let Some(eid) = employee_id {
        query = query.filter(employee_schedules::employee_id.eq(eid));
    }
    query.select(EmployeeSchedule::as_select()).load(&mut conn).map_err(|e| e.to_string())
}

pub fn add_employee_schedule(db_path: &PathBuf, schedule: NewEmployeeSchedule) -> Result<EmployeeSchedule, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(employee_schedules::table).values(&schedule).execute(conn)?;
        employee_schedules::table.order(employee_schedules::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn update_employee_schedule(db_path: &PathBuf, id: i32, update: UpdateEmployeeSchedule) -> Result<EmployeeSchedule, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::update(employee_schedules::table.find(id)).set(&update).execute(conn)?;
        employee_schedules::table.find(id).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn delete_employee_schedule(db_path: &PathBuf, id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::delete(employee_schedules::table.find(id))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
