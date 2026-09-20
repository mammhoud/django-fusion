# Plan: Unified Rust Workspace for SurrealDB Projects

## Goal

Create a shared, reusable Rust workspace for all PlanInc projects that use SurrealDB, eliminating duplication and establishing a standard project structure.

---

## Current State

| Crate | Path | Purpose | SurrealDB? |
|---|---|---|---|
| `planinc` | `src/frontend/src-tauri/` | Tauri desktop app | ✅ embedded `kv-surrealkv` |
| `tauri-plugin-planinc` | `src/frontend/tauri-plugin-planinc/` | Custom Tauri plugin | ❌ (no DB access) |

**Problems:**
- `surrealdb` dependency is only in `src-tauri/Cargo.toml`
- `db.rs`, `models.rs`, `commands/` are monolithic and not reusable
- Any future Rust project must copy this entire structure

---

## Target Structure

```
application/tools/PlanInc/
├── rust/                          # Unified Rust workspace root
│   ├── Cargo.toml                 # Workspace manifest
│   ├── rust-toolchain.toml        # Rust version pin
│   ├── crates/
│   │   ├── planinc-core/          # Shared SurrealDB crate
│   │   │   ├── Cargo.toml
│   │   │   ├── src/
│   │   │   │   ├── lib.rs         # crate root — re-exports
│   │   │   │   ├── db.rs          # Db struct, init_db()
│   │   │   │   ├── models.rs      # Note, Tag, Account, etc.
│   │   │   │   ├── error.rs       # Error enum, Result type
│   │   │   │   ├── schema.rs      # SCHEMAFULL DDL bootstrap
│   │   │   │   └── queries.rs     # Common query helpers
│   │   │   └── tests/             # Integration tests
│   │   │       └── common.rs      # Test fixtures
│   │   │
│   │   ├── planinc-tauri/         # Tauri app (replaces src-tauri/)
│   │   │   ├── Cargo.toml
│   │   │   └── src/
│   │   │       ├── main.rs
│   │   │       ├── lib.rs         # Tauri builder, commands
│   │   │       ├── commands/
│   │   │       │   ├── notes.rs
│   │   │       │   ├── tags.rs
│   │   │       │   ├── search.rs
│   │   │       │   ├── share.rs
│   │   │       │   └── settings.rs
│   │   │       ├── desktop/       # Platform-specific modules
│   │   │       │   ├── mod.rs
│   │   │       │   ├── hotkey.rs
│   │   │       │   ├── tray.rs
│   │   │       │   └── window.rs
│   │   │       └── error.rs
│   │   │
│   │   ├── tauri-plugin-planinc/  # Custom Tauri plugin (unchanged)
│   │   │   ├── Cargo.toml
│   │   │   └── src/
│   │   │       ├── lib.rs
│   │   │       ├── commands.rs
│   │   │       ├── models.rs
│   │   │       ├── error.rs
│   │   │       ├── desktop.rs
│   │   │       └── mobile.rs
│   │   │
│   │   └── planinc-shared/        # Shared types (no SurrealDB dep)
│   │       ├── Cargo.toml
│   │       └── src/
│   │           ├── lib.rs
│   │           ├── types.rs       # Shared DTOs, enums
│   │           ├── settings.rs    # Settings registry
│   │           └── constants.rs   # App constants
│   │
│   └── examples/                  # Example projects
│       ├── cli-client/            # CLI using planinc-core
│       │   ├── Cargo.toml
│       │   └── src/main.rs
│       └── web-api/               # REST API using planinc-core
│           ├── Cargo.toml
│           └── src/main.rs
│
├── src/frontend/                  # Frontend (unchanged)
│   ├── src-tauri/ → symlink → ../rust/crates/planinc-tauri/
│   ├── tauri-plugin-planinc/
│   └── package.json, vite.config.ts, etc.
│
├── runtime/                       # Express runtime (unchanged)
├── docker-compose.yml             # Unchanged
└── ...
```

---

## Workspace Cargo.toml

```toml
[workspace]
members = [
    "crates/planinc-core",
    "crates/planinc-tauri",
    "crates/planinc-shared",
    "crates/tauri-plugin-planinc",
    "examples/cli-client",
    "examples/web-api",
]
resolver = "2"

[workspace.package]
version = "1.8.8"
edition = "2021"
rust-version = "1.77.2"
license = "AGPL-3.0"
repository = "https://github.com/mammhoud/PlanInc"

[workspace.dependencies]
# Core
tauri = { version = "2", features = ["devtools", "rustls-tls", "tray-icon", "image-png"] }
tauri-plugin = { version = "2.2" }
surrealdb = { version = "2", features = ["kv-surrealkv"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
thiserror = "1"
tokio = { version = "1", features = ["rt", "rt-multi-thread", "sync", "macros"] }
anyhow = "1"
uuid = { version = "1", features = ["v4"] }
chrono = { version = "0.4", features = ["serde"] }

# Tauri plugins
tauri-plugin-fs = "2"
tauri-plugin-dialog = "2"
tauri-plugin-http = "2"
tauri-plugin-process = "2"
tauri-plugin-os = "2"
tauri-plugin-upload = "2"
tauri-plugin-single-instance = "2"
tauri-plugin-global-shortcut = "2"
tauri-plugin-updater = "2"

# Frontend
tauri-plugin-planinc = { path = "crates/tauri-plugin-planinc" }
```

---

## `planinc-core` Crate — The Shared SurrealDB Layer

### Purpose
Single source of truth for all SurrealDB interactions. Any project needing SurrealDB just depends on `planinc-core`.

### `Cargo.toml`

```toml
[package]
name = "planinc-core"
version.workspace = true
edition.workspace = true

[dependencies]
surrealdb = { version = "2", features = ["kv-surrealkv"], path = "../../../../crates/planinc-core" }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
thiserror = "1"
tokio = { version = "1", features = ["rt", "rt-multi-thread", "sync", "macros"] }
chrono = { version = "0.4", features = ["serde"] }

[lib]
name = "planinc_core"
path = "src/lib.rs"
```

### Public API

```rust
// lib.rs — all public re-exports
pub mod db;
pub mod models;
pub mod error;
pub mod schema;
pub mod queries;

pub use db::Db;
pub use error::{Error, Result};
pub use models::*;
```

### `db.rs` — Database Connection

```rust
use std::path::PathBuf;
use surrealdb::{Surreal, engine::local::SurrealKv};
use tauri::Manager;

pub struct Db(pub Surreal<SurrealKv>);

impl Db {
    pub async fn init(app: &tauri::App) -> surrealdb::Result<Self> {
        let data_dir = app.path().app_data_dir()?.join("planinc.db");
        let db = Surreal::new::<SurrealKv>(data_dir).await?;
        db.use_ns("planinc").use_db("planinc").await?;
        Ok(Self(db))
    }

    pub async fn init_for_test() -> surrealdb::Result<Self> {
        let db = Surreal::new::<SurrealKv>("mem://").await?;
        db.use_ns("planinc").use_db("planinc").await?;
        Ok(Self(db))
    }

    pub fn inner(&self) -> &Surreal<SurrealKv> {
        &self.0
    }
}
```

### `models.rs` — Data Models

```rust
use serde::{Deserialize, Serialize};
use surrealdb::RecordId;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Note {
    pub id: Option<String>,
    pub content: String,
    pub is_share: bool,
    pub created_by: Option<String>,
    pub tags: Vec<String>,
    pub created_at: Option<String>,
    pub updated_at: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Tag {
    pub id: Option<String>,
    pub name: String,
    pub note_count: Option<u64>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Account {
    pub id: Option<String>,
    pub name: String,
    pub email: Option<String>,
    pub role: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateNoteRequest {
    pub content: String,
    pub tags: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UpdateNoteRequest {
    pub id: String,
    pub content: Option<String>,
    pub is_share: Option<bool>,
    pub tags: Option<Vec<String>>,
}
```

### `error.rs` — Error Types

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum Error {
    #[error("Database error: {0}")]
    Database(#[from] surrealdb::Error),
    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
    #[error("Not found: {0}")]
    NotFound(String),
    #[error("Permission denied")]
    PermissionDenied,
    #[error("Internal error: {0}")]
    Internal(String),
}

pub type Result<T> = std::result::Result<T, Error>;
```

### `schema.rs` — Schema Bootstrap

```rust
use crate::db::Db;

pub async fn bootstrap_schema(db: &Db) -> surrealdb::Result<()> {
    db.0.query(r#"
        DEFINE TABLE notes SCHEMAFULL;
        DEFINE FIELD is_share ON notes TYPE option<bool> DEFAULT false;
        DEFINE FIELD created_by ON notes TYPE option<record<account>>;
        DEFINE FIELD created_at ON notes TYPE option<datetime> DEFAULT time::now();
        DEFINE FIELD updated_at ON notes TYPE option<datetime> DEFAULT time::now();
        DEFINE TABLE tag SCHEMAFULL;
        DEFINE FIELD name ON tag TYPE string;
        DEFINE TABLE account SCHEMAFULL;
    "#).await?;
    Ok(())
}
```

---

## `planinc-tauri` Crate — Tauri App

### Dependency

```toml
[dependencies]
planinc-core = { path = "../planinc-core" }
planinc-shared = { path = "../planinc-shared" }
tauri = { version = "2", features = ["devtools", "rustls-tls", "tray-icon", "image-png"] }
```

### Command Structure

All Tauri commands use `planinc_core::Db` as state:

```rust
// lib.rs
use planinc_core::{Db, models::*};

#[command]
pub async fn create_note(app: AppHandle, payload: CreateNoteRequest) -> Result<Note> {
    let db = app.state::<Db>();
    let note = db.0.create("notes").content(serde_json::to_value(&payload)?).await?;
    Ok(serde_json::from_value(note)?)
}
```

---

## Migration Plan

### Step 1: Create workspace structure (1 hour)

```bash
mkdir -p rust/{crates/{planinc-core,planinc-tauri,planinc-shared,tauri-plugin-planinc},examples/{cli-client,web-api}}
```

### Step 2: Move and split existing code (2 hours)

- Extract `src-tauri/src/db.rs` → `crates/planinc-core/src/db.rs`
- Extract `src-tauri/src/models.rs` → `crates/planinc-core/src/models.rs`
- Extract `src-tauri/src/error.rs` → `crates/planinc-core/src/error.rs`
- Extract `src-tauri/src/commands/` → `crates/planinc-tauri/src/commands/`
- Create `crates/planinc-core/src/schema.rs` and `queries.rs`
- Create `crates/planinc-shared/` with shared types

### Step 3: Create workspace manifest (30 min)

- `rust/Cargo.toml` with all workspace members
- `rust/rust-toolchain.toml`

### Step 4: Update dependencies (30 min)

- Replace `surrealdb`, `serde`, etc. in `planinc-tauri/Cargo.toml` with `planinc-core`
- Update `tauri-plugin-planinc` to use `planinc-shared`

### Step 5: Symlink frontend to rust (15 min)

```bash
cd src/frontend
mv src-tauri src-tauri-old
ln -s ../../rust/crates/planinc-tauri src-tauri
```

### Step 6: Verify and test (1 hour)

```bash
cd rust
cargo check --all
cargo test --all
cargo tauri dev
```

---

## Benefits

| Before | After |
|---|---|
| SurrealDB setup copied per project | `planinc-core` dependency |
| Models duplicated across crates | Single `planinc-core/models.rs` |
| DB connection logic repeated | `Db::init()` / `Db::init_for_test()` |
| No shared types between crates | `planinc-shared` crate |
| Hard to add a new Rust project | `cargo new --template planinc-core` |
| Schema bootstrap in every app | `planinc_core::schema::bootstrap_schema()` |

---

## Future Projects Using This Workspace

### Adding a new Rust project (e.g., `planinc-cli`):

```toml
# rust/crates/planinc-cli/Cargo.toml
[dependencies]
planinc-core = { path = "../planinc-core" }
planinc-shared = { path = "../planinc-shared" }
clap = "4"
tokio = { version = "1", features = ["rt", "rt-multi-thread"] }
```

```rust
// rust/crates/planinc-cli/src/main.rs
use planinc_core::{Db, models::*};

#[tokio::main]
async fn main() {
    let db = Db::init_for_test().await.unwrap();
    planinc_core::schema::bootstrap_schema(&db).await.unwrap();
    let notes = planinc_core::queries::list_notes(&db, None, None, None).await.unwrap();
    println!("{:#?}", notes);
}
```

---

## Files to Create

| File | Description |
|---|---|
| `rust/Cargo.toml` | Workspace manifest |
| `rust/rust-toolchain.toml` | Rust version pin |
| `rust/crates/planinc-core/Cargo.toml` | Core crate |
| `rust/crates/planinc-core/src/lib.rs` | Re-exports |
| `rust/crates/planinc-core/src/db.rs` | DB connection |
| `rust/crates/planinc-core/src/models.rs` | Data models |
| `rust/crates/planinc-core/src/error.rs` | Error types |
| `rust/crates/planinc-core/src/schema.rs` | Schema bootstrap |
| `rust/crates/planinc-core/src/queries.rs` | Common query helpers |
| `rust/crates/planinc-tauri/Cargo.toml` | Tauri app crate |
| `rust/crates/planinc-tauri/src/main.rs` | Entry point |
| `rust/crates/planinc-tauri/src/lib.rs` | Tauri builder |
| `rust/crates/planinc-shared/Cargo.toml` | Shared types crate |
| `rust/crates/planinc-shared/src/lib.rs` | Shared types |
| `rust/crates/tauri-plugin-planinc/Cargo.toml` | Plugin crate (moved) |
| `rust/crates/tauri-plugin-planinc/src/lib.rs` | Plugin (moved) |

---

## License

AGPL-3.0
