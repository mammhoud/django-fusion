use diesel::prelude::*;
use crate::db::{models::*, open_conn};
use std::path::PathBuf;

fn validate_money(value: f64, field: &str) -> Result<(), String> {
    if !value.is_finite() || value < 0.0 {
        return Err(format!("{field} must be a finite, non-negative amount."));
    }
    Ok(())
}

fn expected_cash(opening_cash: f64, cash_sales: f64) -> f64 {
    opening_cash + cash_sales
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn includes_opening_float_in_expected_cash() {
        assert_eq!(expected_cash(100.0, 37.5), 137.5);
    }

    #[test]
    fn rejects_negative_or_non_finite_money() {
        assert!(validate_money(-0.01, "cash").is_err());
        assert!(validate_money(f64::NAN, "cash").is_err());
        assert!(validate_money(f64::INFINITY, "cash").is_err());
        assert!(validate_money(0.0, "cash").is_ok());
    }
}

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
    validate_money(new.opening_cash, "Opening cash")?;
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
    use crate::db::schema::shifts::dsl as shift_table;

    validate_money(closing_cash, "Closing cash")?;

    // Calculate expected cash from cash sales during this shift.
    let shift = shift_table::shifts
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
            .filter(s::payment_method.eq("cash"))
            .select(diesel::dsl::sum(s::total_amount))
            .first::<Option<f64>>(&mut conn)
            .map_err(|e| e.to_string())?
            .unwrap_or(0.0)
    };
    let expected = expected_cash(shift.opening_cash, expected);

    let cash_diff = closing_cash - expected;

    diesel::update(shift_table::shifts.find(shift_id))
        .set((
            shift_table::shift_status.eq("closed"),
            shift_table::closed_at.eq(chrono::Utc::now().naive_utc()),
            shift_table::closing_cash.eq(closing_cash),
            shift_table::expected_cash.eq(expected),
            shift_table::cash_difference.eq(cash_diff),
            shift_table::shift_notes.eq(notes),
        ))
        .returning(Shift::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}
