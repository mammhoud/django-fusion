use crate::db::models::*;
use crate::db::schema::{employees, payrolls};
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

/// Generates a `pending` payroll record per ACTIVE employee for the given
/// period, sourced from each employee's salary/payroll settings:
/// - `monthly` employees → `total_pay = salary` (regular_hours 0)
/// - `hourly` employees → `total_pay = hourly_rate × 160h` (regular_hours 160)
///
/// Employees that already have a record for the same period are skipped, so
/// re-running is idempotent.
pub fn generate_payrolls(db_path: &PathBuf, period_start: String, period_end: String) -> Result<Vec<Payroll>, String> {
    let mut conn = crate::db::open_conn(db_path)?;

    let active = employees::table
        .filter(employees::is_active.eq(true))
        .select(Employee::as_select())
        .load::<Employee>(&mut conn)
        .map_err(|e| e.to_string())?;

    let mut created = Vec::new();
    for emp in active {
        // Idempotent — skip employees already covered for this exact period.
        let existing: i64 = payrolls::table
            .filter(payrolls::employee_id.eq(emp.id))
            .filter(payrolls::period_start.eq(&period_start))
            .filter(payrolls::period_end.eq(&period_end))
            .count()
            .get_result(&mut conn)
            .map_err(|e| e.to_string())?;
        if existing > 0 {
            continue;
        }

        let is_hourly = emp.pay_frequency == "hourly";
        let (regular_hours, total_pay) = if is_hourly {
            (160.0, emp.hourly_rate * 160.0)
        } else {
            (0.0, emp.salary)
        };

        let row = NewPayroll {
            employee_id: emp.id,
            period_start: period_start.clone(),
            period_end: period_end.clone(),
            regular_hours,
            overtime_hours: 0.0,
            total_pay,
            status: "pending".to_string(),
        };
        let payroll = diesel::insert_into(payrolls::table)
            .values(&row)
            .returning(Payroll::as_returning())
            .get_result(&mut conn)
            .map_err(|e| e.to_string())?;
        created.push(payroll);
    }
    Ok(created)
}
