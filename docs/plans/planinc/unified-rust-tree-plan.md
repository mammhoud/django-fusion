# Unified Rust Workspace Plan for PlanInc & Formint

## Objective

Create a shared `rust/` workspace at the monorepo root that both **PlanInc** (Tauri + SurrealDB) and **Formint** (Tauri + SQLite) can use, eliminating duplication and establishing a common foundation for all desktop applications.

---

## Why Unify

Both PlanInc and Formint share the same architectural pattern:

| Aspect | PlanInc | Formint |
|---|---|---|
| Framework | Tauri v2 | Tauri v2 |
| Frontend | React + HeroUI | React + HeroUI |
| Backend | SurrealDB embedded | SQLite (rusqlite) |
| State | MobX | MobX |
| i18n | i18next | i18next |
| UI | HeroUI (@heroui/react) | HeroUI (@heroui/react) |
| Package Manager | Bun | Bun |

**Shared needs:** Tauri plugin infrastructure, shared types, UI components, state management, i18n setup, theme system.

---

## Target Structure

```
/ (workspace root)
├── rust/                              # Unified Rust workspace
│   ├── Cargo.toml                     # Workspace manifest
│   ├── rust-toolchain.toml            # Rust version pin
│   ├── crates/
│   │   │
│   │   ├── planinc-core/              # PlanInc shared SurrealDB layer
│   │   │   ├── Cargo.toml
│   │   │   └── src/
│   │   │       ├── lib.rs             # Re-exports
│   │   │       ├── db.rs              # Db struct + init
│   │   │       ├── models.rs          # Note, Tag, Account models
│   │   │       ├── error.rs           # Error enum + Result
│   │   │       ├── schema.rs          # SCHEMAFULL bootstrap
│   │   │       └── queries.rs         # Common query helpers
│   │   │
│   │   ├── formint-core/              # Formint shared SQLite layer
│   │   │   ├── Cargo.toml
│   │   │   └── src/
│   │   │       ├── lib.rs             # Re-exports
│   │   │       ├── db.rs              # Db struct + init (rusqlite)
│   │   │       ├── models.rs          # Product, Order, Item models
│   │   │       ├── error.rs           # Error enum + Result
│   │   │       ├── schema.rs          # SQLite table bootstrap
│   │   │       └── queries.rs         # Common query helpers
│   │   │
│   │   ├── shared-types/              # Platform-agnostic shared types
│   │   │   ├── Cargo.toml
│   │   │   └── src/
│   │   │       ├── lib.rs             # Re-exports
│   │   │       ├── user.rs            # User types
│   │   │       ├── settings.rs        # Settings/appearance types
│   │   │       ├── theme.rs           # Theme variant types
│   │   │       ├── i18n.rs            # i18n helpers
│   │   │       └── constants.rs       # App constants
│   │   │
│   │   ├── shared-ui/                 # Shared React + HeroUI components
│   │   │   ├── Cargo.toml             # N/A — this is a JS crate
│   │   │   └── src/
│   │   │       ├── components/        # Shared UI components
│   │   │       │   ├── Card.tsx
│   │   │       │   ├── Button.tsx
│   │   │       │   ├── Sidebar.tsx
│   │   │       │   ├── SearchBar.tsx
│   │   │       │   └── TagList.tsx
│   │   │       ├── hooks/             # Shared React hooks
│   │   │       │   ├── useDebounce.ts
│   │   │       │   └── useMediaQuery.ts
│   │   │       └── lib/
│   │   │           ├── tauriHelper.ts  # Tauri invoke wrappers
│   │   │           └── i18n.ts        # i18n setup
│   │   │
│   │   ├── tauri-plugin-shared/       # Shared Tauri plugin
│   │   │   ├── Cargo.toml
│   │   │   └── src/
│   │   │       ├── lib.rs             # Plugin entry
│   │   │       ├── commands.rs        # Common Tauri commands
│   │   │       ├── models.rs          # Shared plugin models
│   │   │       ├── desktop.rs         # Desktop module
│   │   │       └── mobile.rs          # Mobile module
│   │   │
│   │   ├── planinc-tauri/             # PlanInc Tauri app (replaces src-tauri)
│   │   │   ├── Cargo.toml
│   │   │   └── src/
│   │   │       ├── main.rs            # Entry point
│   │   │       ├── lib.rs             # Tauri builder + commands
│   │   │       ├── commands/
│   │   │       │   ├── notes.rs       # CRUD for notes
│   │   │       │   ├── tags.rs        # Tag operations
│   │   │       │   ├── search.rs      # Full-text search
│   │   │       │   ├── share.rs       # Share/invite
│   │   │       │   └── settings.rs    # Workspace settings
│   │   │       ├── desktop/           # Platform-specific
│   │   │       │   ├── mod.rs
│   │   │       │   ├── hotkey.rs
│   │   │       │   ├── tray.rs
│   │   │       │   └── window.rs
│   │   │       └── error.rs
│   │   │
│   │   └── formint-tauri/             # Formint Tauri app
│   │       ├── Cargo.toml
│   │       └── src/
│   │           ├── main.rs
│   │           ├── lib.rs
│   │           ├── commands/
│   │           │   ├── products.rs    # Product CRUD
│   │           │   ├── orders.rs      # Order management
│   │           │   └── inventory.rs   # Inventory operations
│   │           └── desktop/
│   │
│   ├── examples/
│   │   ├── cli-client/                # CLI using planinc-core
│   │   │   ├── Cargo.toml
│   │   │   └── src/main.rs
│   │   └── web-api/                   # REST API using planinc-core
│   │       ├── Cargo.toml
│   │       └── src/main.rs
│   │
│   └── templates/                     # Project templates
│       └── tauri-app/                 # `cargo new --template`
│           ├── Cargo.toml
│           └── src/
│
├── src/frontend/                      # Frontend (symlinked to rust crates)
│   ├── src-tauri/ → ../../rust/crates/planinc-tauri/
│   ├── tauri-plugin-planinc/          # Unchanged (plugin-specific)
│   └── package.json, vite.config.ts, etc.
│
├── application/
│   └── tools/
│       └── PlanInc/                   # Symlinks to rust/ for Docker
│           ├── Cargo.toml → ../../rust/Cargo.toml
│           └── src/frontend/
│               └── src-tauri/ → ../../../../rust/crates/planinc-tauri
│
├── projects/                          # Product code (unchanged)
│   ├── CMS/
│   ├── CRM/
│   ├── Clients/
│   └── precis/
│
├── libs/
│   └── django-fusion/               # Shared Django/Wagtail
│
├── runtime/                           # Express runtime (unchanged)
├── docker-compose.yml                 # Unchanged
└── pyproject.toml                     # Unchanged
```

---

## Workspace Cargo.toml

```toml
[workspace]
members = [
    # Core shared crates
    "crates/shared-types",
    "crates/shared-ui",
    "crates/tauri-plugin-shared",

    # App-specific crates
    "crates/planinc-core",
    "crates/planinc-tauri",
    "crates/formint-core",
    "crates/formint-tauri",

    # Plugins
    "crates/tauri-plugin-planinc",

    # Examples
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
tauri-plugin-fs = "2"
tauri-plugin-dialog = "2"
tauri-plugin-http = "2"
tauri-plugin-process = "2"
tauri-plugin-os = "2"
tauri-plugin-upload = "2"
tauri-plugin-single-instance = "2"
tauri-plugin-global-shortcut = "2"
tauri-plugin-updater = "2"
surrealdb = { version = "2", features = ["kv-surrealkv"] }
rusqlite = { version = "0.31", features = ["bundled"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
thiserror = "1"
tokio = { version = "1", features = ["rt", "rt-multi-thread", "sync", "macros"] }
anyhow = "1"
uuid = { version = "1", features = ["v4"] }
chrono = { version = "0.4", features = ["serde"] }
clap = "4"

# Frontend (for shared-ui crate)
react = ">=18"
```

---

## Rust Version Pin

```toml
# rust-toolchain.toml
[toolchain]
channel = "1.77.2"
components = ["rustfmt", "clippy"]
targets = ["x86_64-unknown-linux-gnu"]
```

---

## Shared Crate Details

### `shared-types` — Platform-Agnostic Types

```rust
// src/lib.rs
pub mod user;
pub mod settings;
pub mod theme;
pub mod i18n;
pub mod constants;

// src/settings.rs
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct AppearanceSettings {
    pub theme: ThemeVariant,
    pub accent: AccentColor,
    pub density: Density,
    pub radius_scale: RadiusScale,
    pub edge_strength: EdgeStrength,
    pub shadow_depth: ShadowDepth,
    pub density_ui: UiDensity,
    pub button_style: ButtonStyle,
    pub badge_style: BadgeStyle,
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
pub enum ThemeVariant { Dark, Light, Corporate, Luxury, Pastel }
#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
pub enum AccentColor { Violet, Blue, Green, Orange, Red }
#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
pub enum Density { Compact, Cozy, Comfortable }
```

### `shared-ui` — Shared React + HeroUI Components

This is a JavaScript/TypeScript crate (not Rust). It provides:
- Common UI components used by both PlanInc and Formint
- Shared Tauri invoke wrappers
- Shared i18n configuration
- Shared hooks

### `tauri-plugin-shared` — Common Tauri Plugin

```rust
// src/commands.rs — Common commands for all Tauri apps
#[command]
pub async fn set_desktop_theme(app: AppHandle, theme: String) -> Result<()> { ... }

#[command]
pub async fn register_hotkey(app: AppHandle, shortcut: String, command: String) -> Result<()> { ... }

#[command]
pub async fn get_selected_text(app: AppHandle) -> Result<String> { ... }

#[command]
pub async fn toggle_quicknote(app: AppHandle) -> Result<()> { ... }

#[command]
pub async fn open_app_settings(app: AppHandle) -> Result<()> { ... }
```

### `planinc-core` — SurrealDB Layer

Reuses the existing code from `src/frontend/src-tauri/src/`.

### `formint-core` — SQLite Layer

```rust
// src/db.rs
use rusqlite::{Connection, Result};

pub struct Db { pub conn: Connection }

impl Db {
    pub fn init(path: &str) -> Result<Self> {
        let conn = Connection::open(path)?;
        Self { conn }
    }

    pub fn init_for_test() -> Result<Self> {
        let conn = Connection::open_in_memory()?;
        Self { conn }
    }
}
```

---

## How PlanInc Uses It

```toml
# planinc-tauri/Cargo.toml
[dependencies]
planinc-core = { path = "../planinc-core" }
shared-types = { path = "../shared-types" }
shared-ui = { path = "../shared-ui" }
tauri-plugin-shared = { path = "../tauri-plugin-shared" }
```

```rust
// planinc-tauri/src/lib.rs
use planinc_core::{Db, models::*};

#[command]
pub async fn create_note(app: AppHandle, payload: CreateNoteRequest) -> Result<Note> {
    let db = app.state::<Db>();
    let note = db.0.create("notes").content(serde_json::to_value(&payload)?).await?;
    Ok(serde_json::from_value(note)?)
}
```

## How Formint Uses It

```toml
# formint-tauri/Cargo.toml
[dependencies]
formint-core = { path = "../formint-core" }
shared-types = { path = "../shared-types" }
shared-ui = { path = "../shared-ui" }
tauri-plugin-shared = { path = "../tauri-plugin-shared" }
```

```rust
// formint-tauri/src/lib.rs
use formint_core::{Db, models::*};

#[command]
pub async fn create_product(app: AppHandle, payload: CreateProductRequest) -> Result<Product> {
    let db = app.state::<Db>();
    let product = db.0.execute("INSERT INTO products ...").await?;
    Ok(product)
}
```

---

## Frontend Symlinks

```bash
# Frontend uses the rust crates as its src-tauri
cd src/frontend
ln -sf ../../rust/crates/planinc-tauri src-tauri

# Formint frontend (when exists)
cd projects/formints/formint-community/src-tauri
ln -sf ../../../../../rust/crates/formint-tauri src-tauri
```

---

## Migration Steps

### Step 1: Create workspace root (30 min)
```bash
mkdir -p /home/rust/{crates/{planinc-core,formint-core,shared-types,shared-ui,tauri-plugin-shared,planinc-tauri,formint-tauri},examples/{cli-client,web-api},templates/tauri-app}
```

### Step 2: Create workspace manifest (15 min)
- `rust/Cargo.toml` — workspace members
- `rust/rust-toolchain.toml` — version pin

### Step 3: Move planinc-core code (1 hour)
- Extract `src/frontend/src-tauri/src/db.rs` → `rust/crates/planinc-core/src/db.rs`
- Extract `src/frontend/src-tauri/src/models.rs` → `rust/crates/planinc-core/src/models.rs`
- Extract `src/frontend/src-tauri/src/error.rs` → `rust/crates/planinc-core/src/error.rs`
- Create `schema.rs`, `queries.rs`
- Create `lib.rs` re-exports

### Step 4: Create formint-core crate (2 hours)
- Design Product, Order, Item models
- Create `db.rs` using `rusqlite`
- Create `schema.rs` for SQLite table creation
- Create `queries.rs` for common operations

### Step 5: Create shared-types crate (1 hour)
- `user.rs`, `settings.rs`, `theme.rs`, `i18n.rs`, `constants.rs`

### Step 6: Create shared-ui crate (2 hours)
- Move shared React components from `src/frontend/src/components/Common/`
- Move `tauriHelper.ts`, `i18n.ts` helpers
- Create `package.json` for the JS crate

### Step 7: Create tauri-plugin-shared (1 hour)
- Common Tauri commands
- Desktop/mobile modules

### Step 8: Create planinc-tauri crate (1 hour)
- Move commands from `src/frontend/src-tauri/src/commands/`
- Move desktop modules
- Update Cargo.toml to use `planinc-core`, `shared-types`, `tauri-plugin-shared`

### Step 9: Create formint-tauri crate (2 hours)
- Create command structure for POS operations
- Use `formint-core`, `shared-types`, `tauri-plugin-shared`

### Step 10: Symlink frontend (30 min)
- `src/frontend/src-tauri` → `../../rust/crates/planinc-tauri`
- Keep `src/frontend/tauri-plugin-planinc/` as-is

### Step 11: Verify (1 hour)
```bash
cd /home/rust
cargo check --all
cargo test --all
cargo tauri dev  # in planinc-tauri
```

---

## Benefits

| Metric | Before | After |
|---|---|---|
| Duplicate Rust code | 2× db.rs, models.rs, error.rs | 1× each in shared crates |
| New Rust project setup | Copy entire structure | `cargo new --template tauri-app` |
| Shared UI components | Manual copy | Single `shared-ui` crate |
| Tauri plugin commands | Per-app duplication | Single `tauri-plugin-shared` |
| Cross-app type sharing | None | `shared-types` crate |
| Build time | Per-app full build | Cached shared crates |

---

## Files Created/Modified

### New Files
- `rust/Cargo.toml`
- `rust/rust-toolchain.toml`
- `rust/crates/planinc-core/Cargo.toml` + `src/lib.rs`, `src/db.rs`, `src/models.rs`, `src/error.rs`, `src/schema.rs`, `src/queries.rs`
- `rust/crates/formint-core/Cargo.toml` + `src/lib.rs`, `src/db.rs`, `src/models.rs`, `src/error.rs`, `src/schema.rs`, `src/queries.rs`
- `rust/crates/shared-types/Cargo.toml` + `src/lib.rs`, `src/user.rs`, `src/settings.rs`, `src/theme.rs`, `src/i18n.rs`, `src/constants.rs`
- `rust/crates/shared-ui/package.json` + `src/components/**`, `src/lib/**`
- `rust/crates/tauri-plugin-shared/Cargo.toml` + `src/lib.rs`, `src/commands.rs`, `src/desktop.rs`, `src/mobile.rs`
- `rust/crates/planinc-tauri/Cargo.toml` + `src/main.rs`, `src/lib.rs`, `src/commands/*.rs`, `src/desktop/*.rs`
- `rust/crates/formint-tauri/Cargo.toml` + `src/main.rs`, `src/lib.rs`, `src/commands/*.rs`

### Modified Files
- `src/frontend/src-tauri/` → symlink to `rust/crates/planinc-tauri`
- `src/frontend/package.json` → update tauri dependency path

---

## License

AGPL-3.0
