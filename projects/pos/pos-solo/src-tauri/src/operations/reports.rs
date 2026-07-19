use crate::db::models::*;
use crate::db::schema::report_metadata;
use diesel::prelude::*;
use std::path::PathBuf;

pub fn get_report_metadata(db_path: &PathBuf) -> Result<Vec<ReportMetadata>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    report_metadata::table
        .select(ReportMetadata::as_select())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_report_metadata(db_path: &PathBuf, report: NewReportMetadata) -> Result<ReportMetadata, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(report_metadata::table).values(&report).execute(conn)?;
        report_metadata::table.order(report_metadata::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn delete_report_metadata(db_path: &PathBuf, id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::delete(report_metadata::table.find(id))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
