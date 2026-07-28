use diesel::sqlite::SqliteConnection;
use diesel::prelude::*;
use diesel_migrations::{embed_migrations, EmbeddedMigrations, MigrationHarness};
use std::path::PathBuf;
use tauri::AppHandle;
use tauri::Manager;

pub mod models;
pub mod schema;

pub const MIGRATIONS: EmbeddedMigrations = embed_migrations!("migrations");

pub type DbConnection = SqliteConnection;

/// Establish a connection to the SQLite database.
pub fn establish_connection(db_path: &std::path::Path) -> Result<SqliteConnection, diesel::ConnectionError> {
    let database_url = db_path.to_str().expect("Invalid DB path");
    SqliteConnection::establish(database_url)
}

/// Resolve the database path.
///
/// Priority:
/// 1. `DATABASE_URL` env var (development / test overrides)
/// 2. Platform-specific app data dir (`restaurant.db`)
///
/// Logs the resolved path to stderr so you can confirm which file is in use.
pub fn get_db_path(app: &AppHandle) -> Result<PathBuf, String> {
    // Check for DATABASE_URL env var first (development overrides)
    if let Ok(db_url) = std::env::var("DATABASE_URL") {
        let path = PathBuf::from(&db_url);
        if let Some(parent) = path.parent() {
            if !parent.as_os_str().is_empty() {
                std::fs::create_dir_all(parent)
                    .map_err(|e| format!("Failed to create database directory: {}", e))?;
            }
        }
        eprintln!("[db] DATABASE_URL={db_url} → resolved={}", path.display());
        return Ok(path);
    }

    // Fall back to app data directory (production)
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;
    std::fs::create_dir_all(&app_data_dir)
        .map_err(|e| format!("Failed to create app data directory: {}", e))?;
    let db_path = app_data_dir.join("restaurant.db");
    eprintln!("[db] app_data_dir={} → resolved={}", app_data_dir.display(), db_path.display());
    Ok(db_path)
}

/// Resolve the database path from the environment only (no Tauri dependency).
/// Used by the standalone seed binary.
pub fn get_db_path_from_env() -> Result<PathBuf, String> {
    if let Ok(db_url) = std::env::var("DATABASE_URL") {
        let path = PathBuf::from(&db_url);
        if let Some(parent) = path.parent() {
            if !parent.as_os_str().is_empty() {
                std::fs::create_dir_all(parent)
                    .map_err(|e| format!("Failed to create database directory: {}", e))?;
            }
        }
        Ok(path)
    } else {
        Err("DATABASE_URL is not set. Set it in .env or export it.".to_string())
    }
}

/// Run pending migrations.
pub fn run_migrations(db_path: &std::path::Path) -> Result<(), String> {
    let mut conn = establish_connection(db_path).map_err(|e| format!("Connection error: {}", e))?;
    conn.run_pending_migrations(MIGRATIONS)
        .map_err(|e| format!("Migration error: {}", e))?;
    Ok(())
}

/// Helper to open connection for operations
pub fn open_conn(db_path: &std::path::Path) -> Result<SqliteConnection, String> {
    establish_connection(db_path).map_err(|e| format!("Database connection error: {}", e))
}
