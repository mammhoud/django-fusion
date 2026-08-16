//! CSV/JSON data export for the Standard tier (Task B4).
//!
//! Four resources, two formats, no new external dependencies:
//!   - CSV: manual ``std::io::Write`` (no ``csv`` crate)
//!   - JSON: ``serde_json::to_string_pretty`` (already in Cargo.toml)
//!
//! Each export writes to the OS temp directory, records a row in
//! ``report_metadata``, and returns it so the frontend can show a download
//! button.

use chrono::Utc;
use diesel::prelude::*;
use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};

use crate::db::models::*;
use crate::db::open_conn;
use crate::db::schema;

/// Supported export resources.
const RESOURCES: &[&str] = &["products", "sales", "customers", "inventory"];

/// Supported export formats.
const FORMATS: &[&str] = &["csv", "json"];

// ── Helpers ──────────────────────────────────────────────────────────

fn timestamp_filename(resource: &str, format: &str) -> String {
    let ts = Utc::now().format("%Y%m%d-%H%M%S");
    format!("{resource}-{ts}.{format}")
}

fn escape_csv_field(value: &str) -> String {
    if value.contains(',') || value.contains('"') || value.contains('\n') {
        format!("\"{}\"", value.replace('"', "\"\""))
    } else {
        value.to_string()
    }
}

// ── Resource queries ─────────────────────────────────────────────────

fn export_products(db_path: &Path, format: &str) -> Result<ReportMetadata, String> {
    let mut conn = open_conn(db_path)?;

    let rows: Vec<Product> = schema::products::table
        .order(schema::products::name.asc())
        .select(Product::as_select())
        .load(&mut conn)
        .map_err(|e| format!("query products: {e}"))?;

    let filename = timestamp_filename("products", format);
    let file_path = std::env::temp_dir().join(&filename);

    match format {
        "csv" => {
            let mut f = fs::File::create(&file_path)
                .map_err(|e| format!("create file: {e}"))?;
            writeln!(f, "id,name,price,unit,category_id,product_type,prep_minutes,barcode,available_order_types,tax_profile_id")
                .map_err(|e| format!("write csv header: {e}"))?;
            for p in &rows {
                writeln!(
                    f,
                    "{},{},{},{},{},{},{},{},{},{}",
                    p.id,
                    escape_csv_field(&p.name),
                    p.price,
                    escape_csv_field(&p.unit),
                    p.category_id.map_or_else(String::new, |v| v.to_string()),
                    escape_csv_field(&p.product_type),
                    p.prepare_time_minutes,
                    p.barcode.as_deref().unwrap_or(""),
                    escape_csv_field(&p.available_order_types),
                    p.tax_profile_id.map_or_else(String::new, |v| v.to_string()),
                )
                .map_err(|e| format!("write csv row: {e}"))?;
            }
            f.flush().map_err(|e| format!("flush csv: {e}"))?;
        }
        "json" => {
            let json = serde_json::to_string_pretty(&rows)
                .map_err(|e| format!("serialize json: {e}"))?;
            fs::write(&file_path, json).map_err(|e| format!("write json: {e}"))?;
        }
        other => return Err(format!("unsupported format: {other}")),
    }

    record_export(&mut conn, "products", format, &file_path)
}

fn export_sales(db_path: &Path, format: &str) -> Result<ReportMetadata, String> {
    let mut conn = open_conn(db_path)?;

    let rows: Vec<Sale> = schema::sales::table
        .order(schema::sales::created_at.desc())
        .select(Sale::as_select())
        .load(&mut conn)
        .map_err(|e| format!("query sales: {e}"))?;

    let filename = timestamp_filename("sales", format);
    let file_path = std::env::temp_dir().join(&filename);

    match format {
        "csv" => {
            let mut f =
                fs::File::create(&file_path).map_err(|e| format!("create file: {e}"))?;
            writeln!(
                f,
                "id,total_amount,currency,date,time,order_type,status,table_number,payment_method,discount_amount,customer_id,employee_id,tax_profile_id"
            )
            .map_err(|e| format!("write csv header: {e}"))?;
            for s in &rows {
                writeln!(
                    f,
                    "{},{},{},{},{},{},{},{},{},{},{},{},{}",
                    s.id,
                    s.total_amount,
                    escape_csv_field(&s.currency),
                    escape_csv_field(&s.date),
                    escape_csv_field(&s.time),
                    escape_csv_field(&s.order_type),
                    escape_csv_field(&s.status),
                    s.table_number.map_or_else(String::new, |v| v.to_string()),
                    escape_csv_field(&s.payment_method),
                    s.discount_amount,
                    s.customer_id.map_or_else(String::new, |v| v.to_string()),
                    s.employee_id.map_or_else(String::new, |v| v.to_string()),
                    s.tax_profile_id.map_or_else(String::new, |v| v.to_string()),
                )
                .map_err(|e| format!("write csv row: {e}"))?;
            }
            f.flush().map_err(|e| format!("flush csv: {e}"))?;
        }
        "json" => {
            let json = serde_json::to_string_pretty(&rows)
                .map_err(|e| format!("serialize json: {e}"))?;
            fs::write(&file_path, json).map_err(|e| format!("write json: {e}"))?;
        }
        other => return Err(format!("unsupported format: {other}")),
    }

    record_export(&mut conn, "sales", format, &file_path)
}

fn export_customers(db_path: &Path, format: &str) -> Result<ReportMetadata, String> {
    let mut conn = open_conn(db_path)?;

    let rows: Vec<Customer> = schema::customers::table
        .order(schema::customers::name.asc())
        .select(Customer::as_select())
        .load(&mut conn)
        .map_err(|e| format!("query customers: {e}"))?;

    let filename = timestamp_filename("customers", format);
    let file_path = std::env::temp_dir().join(&filename);

    match format {
        "csv" => {
            let mut f =
                fs::File::create(&file_path).map_err(|e| format!("create file: {e}"))?;
            writeln!(f, "id,name,phone,email,loyalty_points,notes")
                .map_err(|e| format!("write csv header: {e}"))?;
            for c in &rows {
                writeln!(
                    f,
                    "{},{},{},{},{},{}",
                    c.id,
                    escape_csv_field(&c.name),
                    c.phone.as_deref().unwrap_or(""),
                    c.email.as_deref().unwrap_or(""),
                    c.loyalty_points,
                    c.notes.as_deref().unwrap_or(""),
                )
                .map_err(|e| format!("write csv row: {e}"))?;
            }
            f.flush().map_err(|e| format!("flush csv: {e}"))?;
        }
        "json" => {
            let json = serde_json::to_string_pretty(&rows)
                .map_err(|e| format!("serialize json: {e}"))?;
            fs::write(&file_path, json).map_err(|e| format!("write json: {e}"))?;
        }
        other => return Err(format!("unsupported format: {other}")),
    }

    record_export(&mut conn, "customers", format, &file_path)
}

fn export_inventory(db_path: &Path, format: &str) -> Result<ReportMetadata, String> {
    let mut conn = open_conn(db_path)?;

    let rows: Vec<Ingredient> = schema::ingredients::table
        .order(schema::ingredients::name.asc())
        .select(Ingredient::as_select())
        .load(&mut conn)
        .map_err(|e| format!("query ingredients: {e}"))?;

    let filename = timestamp_filename("inventory", format);
    let file_path = std::env::temp_dir().join(&filename);

    match format {
        "csv" => {
            let mut f =
                fs::File::create(&file_path).map_err(|e| format!("create file: {e}"))?;
            writeln!(
                f,
                "id,name,unit,current_quantity,reorder_level,reorder_quantity,cost_per_unit,is_active"
            )
            .map_err(|e| format!("write csv header: {e}"))?;
            for ing in &rows {
                writeln!(
                    f,
                    "{},{},{},{},{},{},{},{}",
                    ing.id,
                    escape_csv_field(&ing.name),
                    escape_csv_field(&ing.unit),
                    ing.current_quantity,
                    ing.reorder_level,
                    ing.reorder_quantity,
                    ing.cost_per_unit,
                    ing.is_active as u8,
                )
                .map_err(|e| format!("write csv row: {e}"))?;
            }
            f.flush().map_err(|e| format!("flush csv: {e}"))?;
        }
        "json" => {
            let json = serde_json::to_string_pretty(&rows)
                .map_err(|e| format!("serialize json: {e}"))?;
            fs::write(&file_path, json).map_err(|e| format!("write json: {e}"))?;
        }
        other => return Err(format!("unsupported format: {other}")),
    }

    record_export(&mut conn, "inventory", format, &file_path)
}

// ── Record keeping ───────────────────────────────────────────────────

fn record_export(
    conn: &mut SqliteConnection,
    resource: &str,
    format: &str,
    file_path: &Path,
) -> Result<ReportMetadata, String> {
    use schema::report_metadata;

    let row = NewReportMetadata {
        report_type: resource.to_string(),
        format: format.to_string(),
        file_path: file_path.to_string_lossy().into_owned(),
        parameters: None,
        generated_by: None,
    };

    diesel::insert_into(report_metadata::table)
        .values(&row)
        .get_result(conn)
        .map_err(|e| format!("insert report_metadata: {e}"))
}

// ── Public API ───────────────────────────────────────────────────────

/// Export a resource to CSV or JSON.
///
/// `resource`: one of ``"products"``, ``"sales"``, ``"customers"``,
/// ``"inventory"``.
/// `format`: ``"csv"`` or ``"json"``.
///
/// Writes the file to the OS temp directory and records it in
/// `report_metadata` so the frontend can list and download past exports.
pub fn export_resource(
    db_path: &PathBuf,
    resource: &str,
    format: &str,
) -> Result<ReportMetadata, String> {
    if !RESOURCES.contains(&resource) {
        return Err(format!(
            "unknown resource '{}'. Expected one of: {}",
            resource,
            RESOURCES.join(", ")
        ));
    }
    if !FORMATS.contains(&format) {
        return Err(format!(
            "unknown format '{}'. Expected one of: {}",
            format,
            FORMATS.join(", ")
        ));
    }

    match resource {
        "products" => export_products(db_path, format),
        "sales" => export_sales(db_path, format),
        "customers" => export_customers(db_path, format),
        "inventory" => export_inventory(db_path, format),
        _ => unreachable!(),
    }
}

// ── Tests ────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use crate::db::run_migrations;

    fn temp_db(tag: &str) -> PathBuf {
        let mut path = std::env::temp_dir();
        path.push(format!(
            "formint-standard-export-{}-{}.db",
            std::process::id(),
            tag
        ));
        let _ = std::fs::remove_file(&path);
        run_migrations(&path).expect("migrations ok");
        // Seed minimal data so the tables aren't empty.
        {
            let mut conn = open_conn(&path).expect("open");
            diesel::sql_query(
                "INSERT INTO products (name, price, unit, product_type, prepare_time_minutes, available_order_types) VALUES ('Test Product', 9.99, 'each', 'product', 5, 'dine-in,takeaway')",
            )
            .execute(&mut conn)
            .expect("seed product");
        }
        path
    }

    #[test]
    fn rejects_bad_resource() {
        let db = temp_db("bad_res");
        let err = export_resource(&db, "nope", "csv").expect_err("should reject");
        assert!(err.contains("unknown resource"));
        let _ = std::fs::remove_file(&db);
    }

    #[test]
    fn rejects_bad_format() {
        let db = temp_db("bad_fmt");
        let err = export_resource(&db, "products", "xml").expect_err("should reject");
        assert!(err.contains("unknown format"));
        let _ = std::fs::remove_file(&db);
    }

    #[test]
    fn export_products_csv() {
        let db = temp_db("prod_csv");
        let meta = export_resource(&db, "products", "csv").expect("export ok");
        assert_eq!(meta.report_type, "products");
        assert_eq!(meta.format, "csv");
        assert!(meta.file_path.contains("products-"));
        assert!(std::path::Path::new(&meta.file_path).exists());
        let content = std::fs::read_to_string(&meta.file_path).expect("read");
        assert!(content.starts_with("id,name,"));
        assert!(content.contains("Test Product"));
        let _ = std::fs::remove_file(&meta.file_path);
        let _ = std::fs::remove_file(&db);
    }

    #[test]
    fn export_products_json() {
        let db = temp_db("prod_json");
        let meta = export_resource(&db, "products", "json").expect("export ok");
        assert!(meta.file_path.ends_with(".json"));
        let content = std::fs::read_to_string(&meta.file_path).expect("read");
        // Round-trip: deserialize and find our seeded product by name.
        let products: Vec<Product> = serde_json::from_str(&content).expect("parse");
        assert!(!products.is_empty());
        let found = products.iter().find(|p| p.name == "Test Product");
        assert!(found.is_some(), "seeded product not found in JSON export");
        assert!((found.unwrap().price - 9.99).abs() < 0.001);
        let _ = std::fs::remove_file(&meta.file_path);
        let _ = std::fs::remove_file(&db);
    }

    #[test]
    fn csv_escaping() {
        // Verify the helper correctly quotes fields with commas, quotes, and
        // newlines.
        assert_eq!(escape_csv_field("hello"), "hello");
        assert_eq!(escape_csv_field("a,b"), "\"a,b\"");
        assert_eq!(escape_csv_field("say \"hi\""), "\"say \"\"hi\"\"\"");
        assert_eq!(escape_csv_field("line1\nline2"), "\"line1\nline2\"");
    }
}
