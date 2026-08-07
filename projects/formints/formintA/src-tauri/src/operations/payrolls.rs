use crate::db::models::*;
use crate::db::schema::payrolls;
use diesel::prelude::*;
use std::path::PathBuf;

pub fn get_payrolls(db_path: &PathBuf, employee_id: Option<i32>) -> Result<Vec<Payroll>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    let mut query = payrolls::table.into_boxed();
    if let Some(eid) = employee_id {
        query = query.filter(payrolls::employee_id.eq(eid));
    }
    query.select(Payroll::as_select()).load(&mut conn).map_err(|e| e.to_string())
}

pub fn add_payroll(db_path: &PathBuf, payroll: NewPayroll) -> Result<Payroll, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(payrolls::table).values(&payroll).execute(conn)?;
        payrolls::table.order(payrolls::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn update_payroll(db_path: &PathBuf, id: i32, update: UpdatePayroll) -> Result<Payroll, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::update(payrolls::table.find(id)).set(&update).execute(conn)?;
        payrolls::table.find(id).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn delete_payroll(db_path: &PathBuf, id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::delete(payrolls::table.find(id))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
