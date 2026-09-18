use crate::db::models::*;
use crate::db::schema::employee_schedules;
use diesel::prelude::*;
use std::path::PathBuf;

const VALID_STATUSES: &[&str] = &["scheduled", "completed", "cancelled", "no_show"];

fn validate_schedule(employee_id: i32, shift_start: chrono::NaiveDateTime, shift_end: chrono::NaiveDateTime, status: &str) -> Result<(), String> {
    if employee_id <= 0 {
        return Err("Employee is required.".to_string());
    }
    if shift_end <= shift_start {
        return Err("Shift end must be after shift start.".to_string());
    }
    if !VALID_STATUSES.contains(&status) {
        return Err(format!("Invalid schedule status: {status}"));
    }
    Ok(())
}

fn ensure_no_overlap(
    conn: &mut diesel::SqliteConnection,
    employee_id_value: i32,
    start: chrono::NaiveDateTime,
    end: chrono::NaiveDateTime,
    excluded_id: Option<i32>,
) -> Result<(), String> {
    use crate::db::schema::employee_schedules::dsl::*;
    let mut query = employee_schedules
        .filter(employee_id.eq(employee_id_value))
        .filter(shift_start.lt(end))
        .filter(shift_end.gt(start))
        .filter(status.ne("completed"))
        .filter(status.ne("cancelled"))
        .filter(status.ne("no_show"))
        .into_boxed();
    if let Some(id_value) = excluded_id {
        query = query.filter(id.ne(id_value));
    }
    let overlap = query
        .select(id)
        .first::<i32>(conn)
        .optional()
        .map_err(|e| e.to_string())?;
    if overlap.is_some() {
        return Err("This employee already has an overlapping shift.".to_string());
    }
    Ok(())
}

pub fn get_employee_schedules(db_path: &PathBuf, employee_id: Option<i32>) -> Result<Vec<EmployeeSchedule>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    let mut query = employee_schedules::table.into_boxed();
    if let Some(eid) = employee_id {
        query = query.filter(employee_schedules::employee_id.eq(eid));
    }
    query.select(EmployeeSchedule::as_select()).load(&mut conn).map_err(|e| e.to_string())
}

pub fn add_employee_schedule(db_path: &PathBuf, schedule: NewEmployeeSchedule) -> Result<EmployeeSchedule, String> {
    validate_schedule(schedule.employee_id, schedule.shift_start, schedule.shift_end, &schedule.status)?;
    let mut conn = crate::db::open_conn(db_path)?;
    ensure_no_overlap(&mut conn, schedule.employee_id, schedule.shift_start, schedule.shift_end, None)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(employee_schedules::table).values(&schedule).execute(conn)?;
        employee_schedules::table.order(employee_schedules::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn update_employee_schedule(db_path: &PathBuf, id: i32, update: UpdateEmployeeSchedule) -> Result<EmployeeSchedule, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    let current = employee_schedules::table
        .find(id)
        .first::<EmployeeSchedule>(&mut conn)
        .map_err(|e| e.to_string())?;
    let employee_id_value = update.employee_id.unwrap_or(current.employee_id);
    let start = update.shift_start.unwrap_or(current.shift_start);
    let end = update.shift_end.unwrap_or(current.shift_end);
    let status = update.status.as_deref().unwrap_or(&current.status);
    validate_schedule(employee_id_value, start, end, status)?;
    ensure_no_overlap(&mut conn, employee_id_value, start, end, Some(id))?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::update(employee_schedules::table.find(id)).set(&update).execute(conn)?;
        employee_schedules::table.find(id).first(conn)
    })
    .map_err(|e| e.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn time(value: &str) -> chrono::NaiveDateTime {
        chrono::NaiveDateTime::parse_from_str(value, "%Y-%m-%d %H:%M:%S").unwrap()
    }

    #[test]
    fn rejects_reversed_schedule_window() {
        let error = validate_schedule(1, time("2026-01-15 17:00:00"), time("2026-01-15 09:00:00"), "scheduled")
            .expect_err("reversed windows must be rejected");
        assert!(error.contains("after shift start"));
    }

    #[test]
    fn accepts_a_new_shift_when_an_old_shift_is_terminal() {
        assert!(validate_schedule(1, time("2026-01-16 09:00:00"), time("2026-01-16 17:00:00"), "scheduled").is_ok());
    }

    #[test]
    fn rejects_unknown_schedule_status() {
        let error = validate_schedule(1, time("2026-01-15 09:00:00"), time("2026-01-15 17:00:00"), "draft")
            .expect_err("unknown statuses must be rejected");
        assert!(error.contains("Invalid schedule status"));
    }
}

pub fn delete_employee_schedule(db_path: &PathBuf, id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::delete(employee_schedules::table.find(id))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
