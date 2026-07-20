// POS Mini — Rust/Diesel only edition. No sidecar, no Python.
// All CRUD operations via Tauri IPC → Diesel ORM → SQLite.

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::sync::Mutex;
use diesel::prelude::*;
use diesel::sqlite::SqliteConnection;
use diesel::r2d2::{ConnectionManager, Pool};
use serde::{Deserialize, Serialize};

type DbPool = Pool<ConnectionManager<SqliteConnection>>;

mod schema;
mod models;
mod operations;

/// Initialize the database connection pool.
fn init_db() -> DbPool {
    let db_path = std::env::var("POS_DB_PATH")
        .unwrap_or_else(|_| "restaurant.db".to_string());

    let manager = ConnectionManager::<SqliteConnection>::new(&db_path);
    Pool::builder()
        .max_size(4)
        .build(manager)
        .expect("Failed to create DB pool")
}

#[tauri::command]
fn version() -> String {
    "POS Mini v2.0.0 (Diesel only, no sidecar)".to_string()
}

fn main() {
    env_logger::init();
    let pool = init_db();

    tauri::Builder::default()
        .manage(pool)
        .invoke_handler(tauri::generate_handler![version])
        .run(tauri::generate_context!())
        .expect("POS Mini failed to start");
}
