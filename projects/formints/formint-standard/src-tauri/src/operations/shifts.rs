use diesel::prelude::*;
use crate::db::{models::*, open_conn};
use std::path::PathBuf;

pub fn get_shifts(db_path: &PathBuf, status: Option<String>) -> Result<Vec<Shift>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::shifts::dsl::*;
    let mut q = shifts.into_boxed();
    if let Some(s) = status {
        q = q.filter(shift_status.eq(s));
    }
    q.order(opened_at.desc())
        .load::<Shift>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn get_active_shift(db_path: &PathBuf) -> Result<Option<Shift>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::shifts::dsl::*;
    shifts
        .filter(shift_status.eq("open"))
        .order(opened_at.desc())
        .first::<Shift>(&mut conn)
        .optional()
        .map_err(|e| e.to_string())
}

pub fn open_shift(db_path: &PathBuf, new: NewShift) -> Result<Shift, String> {
    let mut conn = open_conn(db_path)?;
    // Ensure no other shift is open
    use crate::db::schema::shifts::dsl::*;
    {
        let open_count = shifts
            .filter(shift_status.eq("open"))
            .count()
            .get_result::<i64>(&mut conn)
            .map_err(|e| e.to_string())?;
        if open_count > 0 {
            return Err("A shift is already open. Close the current shift before opening a new one.".into());
        }
    }
    diesel::insert_into(shifts)
        .values(&new)
        .returning(Shift::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn close_shift(
    db_path: &PathBuf,
    shift_id: i32,
    closing_cash: f64,
    notes: Option<String>,
) -> Result<Shift, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::shifts::dsl::*;

    // Calculate expected cash from sales during this shift
    let shift = shifts
        .find(shift_id)
        .first::<Shift>(&mut conn)
        .map_err(|e| e.to_string())?;
    if shift.shift_status != "open" {
        return Err("Shift is not open.".into());
    }

    let expected: f64 = {
        use crate::db::schema::sales::dsl as s;
        let opened = shift.opened_at.format("%Y-%m-%d %H:%M:%S").to_string();
        let now = chrono::Utc::now().naive_utc().format("%Y-%m-%d %H:%M:%S").to_string();
        s::sales
            .filter(s::created_at.ge(&opened))
            .filter(s::created_at.le(&now))
            .filter(s::status.ne("cancelled"))
            .select(diesel::dsl::sum(s::total_amount))
            .first::<Option<f64>>(&mut conn)
            .map_err(|e| e.to_string())?
            .unwrap_or(0.0)
    };

    let cash_diff = closing_cash - expected;

    diesel::update(shifts.find(shift_id))
        .set((
            shift_status.eq("closed"),
            closed_at.eq(chrono::Utc::now().naive_utc()),
            closing_cash.eq(closing_cash),
            expected_cash.eq(expected),
            cash_difference.eq(cash_diff),
            shift_notes.eq(notes.unwrap_or_default()),
        ))
        .returning(Shift::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}
