use diesel::connection::SimpleConnection;
use diesel::sqlite::SqliteConnection;
use diesel::prelude::*;
use diesel_migrations::{embed_migrations, EmbeddedMigrations, MigrationHarness};
use std::path::PathBuf;
use std::sync::OnceLock;
use tauri::AppHandle;
use tauri::Manager;

pub mod models;
pub mod schema;

pub const MIGRATIONS: EmbeddedMigrations = embed_migrations!("migrations");

pub type DbConnection = SqliteConnection;

/// SQLite pragmas applied to every new connection.
///
/// - `journal_mode=WAL` — write-ahead logging. Lets readers proceed while a
///   single writer commits, so the short-lived per-command connections that
///   `open_conn` creates (Sale, KDS, Settings, …) no longer block each other.
/// - `synchronous=NORMAL` — safe with WAL; avoids an fsync on every commit
///   while keeping durability on checkpoint.
/// - `busy_timeout=5000` — wait up to 5 s for a locked database instead of
///   returning `SQLITE_BUSY` immediately under concurrent writes.
const SQLITE_PRAGMAS: &str = "PRAGMA journal_mode=WAL;\nPRAGMA synchronous=NORMAL;\nPRAGMA busy_timeout=5000;";

/// Establish a connection to the SQLite database (WAL mode enabled).
///
/// The pragmas are best-effort: a failure to enable WAL (e.g. a network
/// filesystem that doesn't support it, or a second app instance holding the
/// DB) logs a warning but does not refuse the connection — the database still
/// works in rollback-journal mode, so a transient environment issue must not
/// brick the whole POS.
pub fn establish_connection(db_path: &std::path::Path) -> Result<SqliteConnection, diesel::ConnectionError> {
    let database_url = db_path.to_str().expect("Invalid DB path");
    let mut conn = SqliteConnection::establish(database_url)?;
    if let Err(e) = conn.batch_execute(SQLITE_PRAGMAS) {
        eprintln!("[db] WARNING: failed to apply SQLite pragmas ({SQLITE_PRAGMAS}): {e}");
    }
    Ok(conn)
}

/// Cached resolved database path — avoids repeated logging and path resolution.
static CACHED_DB_PATH: OnceLock<PathBuf> = OnceLock::new();

/// Resolve the database path.
///
/// Priority:
/// 1. `DATABASE_URL` env var (development / test overrides)
/// 2. Platform-specific app data dir (`restaurant.db`)
///
/// The resolved path is cached after the first call so the log message
/// appears only once and subsequent calls are a cheap clone.
pub fn get_db_path(app: &AppHandle) -> Result<PathBuf, String> {
    if let Some(cached) = CACHED_DB_PATH.get() {
        return Ok(cached.clone());
    }

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
        let _ = CACHED_DB_PATH.set(path.clone());
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
    let _ = CACHED_DB_PATH.set(db_path.clone());
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

#[cfg(test)]
mod tests {
    use super::*;
    use diesel::sql_query;
    use diesel::QueryableByName;
    use diesel::sql_types::{Integer, Text};

    #[derive(QueryableByName, Debug)]
    struct JournalModeRow {
        #[diesel(sql_type = Text)]
        journal_mode: String,
    }

    #[derive(QueryableByName, Debug)]
    struct SynchronousRow {
        #[diesel(sql_type = Integer)]
        synchronous: i32,
    }

    #[derive(QueryableByName, Debug)]
    struct BusyTimeoutRow {
        // `PRAGMA busy_timeout;` reports the value under a `timeout` column.
        #[diesel(sql_type = Integer)]
        timeout: i32,
    }

    /// Unique temp DB per test — tests run in parallel and WAL switching
    /// needs exclusive access, so sharing a single path would deadlock.
    fn temp_db_path(tag: &str) -> std::path::PathBuf {
        let mut path = std::env::temp_dir();
        path.push(format!("forge-pos-wal-test-{}-{}.db", std::process::id(), tag));
        let _ = std::fs::remove_file(&path);
        path
    }

    #[test]
    fn establish_connection_enables_wal_mode() {
        let db_path = temp_db_path("wal");
        {
            let mut conn = establish_connection(&db_path).expect("connect");
            let rows: Vec<JournalModeRow> = sql_query("PRAGMA journal_mode;")
                .load(&mut conn)
                .expect("read journal_mode");
            assert_eq!(rows[0].journal_mode, "wal");
        }
        let _ = std::fs::remove_file(&db_path);
    }

    #[test]
    fn establish_connection_sets_synchronous_normal() {
        let db_path = temp_db_path("sync");
        {
            let mut conn = establish_connection(&db_path).expect("connect");
            let rows: Vec<SynchronousRow> = sql_query("PRAGMA synchronous;")
                .load(&mut conn)
                .expect("read synchronous");
            // 1 = NORMAL
            assert_eq!(rows[0].synchronous, 1);
        }
        let _ = std::fs::remove_file(&db_path);
    }

    #[test]
    fn establish_connection_sets_busy_timeout() {
        let db_path = temp_db_path("busy");
        {
            let mut conn = establish_connection(&db_path).expect("connect");
            let rows: Vec<BusyTimeoutRow> = sql_query("PRAGMA busy_timeout;")
                .load(&mut conn)
                .expect("read busy_timeout");
            assert_eq!(rows[0].timeout, 5000);
        }
        let _ = std::fs::remove_file(&db_path);
    }
}
