use crate::db::models::*;
use crate::db::schema::tax_reports;
use diesel::prelude::*;
use std::path::PathBuf;

pub fn get_tax_reports(db_path: &PathBuf) -> Result<Vec<TaxReport>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    tax_reports::table
        .select(TaxReport::as_select())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_tax_report(db_path: &PathBuf, report: NewTaxReport) -> Result<TaxReport, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(tax_reports::table).values(&report).execute(conn)?;
        tax_reports::table.order(tax_reports::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn delete_tax_report(db_path: &PathBuf, id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::delete(tax_reports::table.find(id))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
