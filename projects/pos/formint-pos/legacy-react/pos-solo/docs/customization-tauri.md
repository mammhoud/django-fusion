# POS — Tauri/Rust Backend Customization Guide

> **Path:** `src-tauri/` | **Language:** Rust | **Framework:** Tauri 2 | **ORM:** Diesel

---

## Customization Overview

| Level | What | Effort | Risk |
|-------|------|--------|------|
| 🟢 **Settings** | Env vars, Tauri config, app metadata | Low | None |
| 🟡 **Operations** | Add/modify CRUD modules, new Tauri commands | Medium | Low |
| 🟡 **Database** | Add/modify tables, new migrations | Medium | Medium |
| 🔴 **Core** | `lib.rs`, `main.rs`, connection pool, app builder | High | High |

---

## 🟢 Configuration Customization

### App Identity

Edit `src-tauri/tauri.conf.json`:

```json
{
  "productName": "My POS",
  "version": "1.0.0",
  "identifier": "com.mycompany.pos",
  "build": {
    "beforeDevCommand": "pnpm dev",
    "devUrl": "http://localhost:1420",
    "beforeBuildCommand": "pnpm build",
    "frontendDist": "../dist"
  },
  "app": {
    "title": "My POS",
    "windows": [
      {
        "title": "My POS",
        "width": 1280,
        "height": 800,
        "resizable": true,
        "fullscreen": false
      }
    ]
  }
}
```

### Window Configuration

Key window options in `tauri.conf.json`:

| Option | Default | Purpose |
|--------|---------|---------|
| `width` | 1280 | Window width (px) |
| `height` | 800 | Window height (px) |
| `resizable` | true | Allow user resizing |
| `fullscreen` | false | Start in fullscreen |
| `minWidth`/`minHeight` | — | Minimum window size |
| `decorations` | true | Show window chrome |
| `titleBarStyle` | — | "Overlay" for custom titlebar |

### Capabilities

Edit `src-tauri/capabilities/default.json` to control what the app can do:

```json
{
  "identifier": "default",
  "description": "Default capability",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "shell:allow-open",
    "fs:default",
    "path:default"
  ]
}
```

---

## 🟡 Adding a New Operation Module

### Step 1: Create the Module

```rust
// src-tauri/src/operations/loyalty_rewards.rs
use crate::db::models::{LoyaltyReward, NewLoyaltyReward, UpdateLoyaltyReward};
use crate::db;
use diesel::prelude::*;

pub fn get_rewards(db_path: &str) -> Result<Vec<LoyaltyReward>, String> {
    let mut conn = db::establish_connection(db_path);
    use crate::db::schema::loyalty_rewards::dsl::*;
    loyalty_rewards.load::<LoyaltyReward>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_reward(db_path: &str, reward: NewLoyaltyReward) -> Result<LoyaltyReward, String> {
    let mut conn = db::establish_connection(db_path);
    diesel::insert_into(crate::db::schema::loyalty_rewards::table)
        .values(&reward)
        .returning(LoyaltyReward::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn delete_reward(db_path: &str, id: i32) -> Result<(), String> {
    let mut conn = db::establish_connection(db_path);
    use crate::db::schema::loyalty_rewards::dsl::*;
    diesel::delete(loyalty_rewards.filter(id_column.eq(id)))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
```

### Step 2: Register in `operations/mod.rs`

```rust
pub mod loyalty_rewards;  // Add this line
```

### Step 3: Register Commands in `lib.rs`

```rust
#[tauri::command]
fn get_loyalty_rewards(app: AppHandle) -> Result<Vec<db::models::LoyaltyReward>, String> {
    let db_path = get_db_path(&app)?;
    loyalty_rewards::get_rewards(&db_path)
}

#[tauri::command]
fn add_loyalty_reward(app: AppHandle, reward: db::models::NewLoyaltyReward) -> Result<db::models::LoyaltyReward, String> {
    let db_path = get_db_path(&app)?;
    loyalty_rewards::add_reward(&db_path, reward)
}
```

### Step 4: Register in Tauri Builder (`main.rs`)

```rust
fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            // ... existing commands ...
            get_loyalty_rewards,
            add_loyalty_reward,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### Step 5: Call from Frontend

```typescript
import { invoke } from '@tauri-apps/api/core';

const rewards = await invoke<LoyaltyReward[]>('get_loyalty_rewards');
await invoke('add_loyalty_reward', { reward: newReward });
```

---

## 🟡 Adding a New Database Table

### Step 1: Create Migration

```bash
cd src-tauri
diesel migration generate add_loyalty_rewards
```

Edit the generated `up.sql`:
```sql
CREATE TABLE loyalty_rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    points_required INTEGER NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Step 2: Add to `schema.rs`

```rust
diesel::table! {
    loyalty_rewards (id) {
        id -> Integer,
        name -> Text,
        points_required -> Integer,
        description -> Nullable<Text>,
        is_active -> Bool,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}
```

Update `allow_tables_to_appear_in_same_query!()`.

### Step 3: Add Models to `models.rs`

```rust
#[derive(Queryable, Selectable, Serialize, Debug)]
#[diesel(table_name = crate::db::schema::loyalty_rewards)]
pub struct LoyaltyReward {
    pub id: i32,
    pub name: String,
    pub points_required: i32,
    pub description: Option<String>,
    pub is_active: bool,
    pub created_at: ChronoNaiveDateTime,
    pub updated_at: ChronoNaiveDateTime,
}

#[derive(Insertable, Deserialize, Debug)]
#[diesel(table_name = crate::db::schema::loyalty_rewards)]
pub struct NewLoyaltyReward {
    pub name: String,
    pub points_required: i32,
    pub description: Option<String>,
}

#[derive(AsChangeset, Deserialize, Debug)]
#[diesel(table_name = crate::db::schema::loyalty_rewards)]
pub struct UpdateLoyaltyReward {
    pub name: Option<String>,
    pub points_required: Option<i32>,
    pub description: Option<String>,
    pub is_active: Option<bool>,
}
```

---

## 🔴 Core Customization (Advanced)

### Tauri Plugins

To add a new Tauri plugin:

1. Add to `Cargo.toml`:
```toml
[dependencies]
tauri-plugin-fs = "2"
```

2. Register in `main.rs`:
```rust
fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_fs::init())  // New plugin
        .plugin(tauri_plugin_shell::init())
        .run(tauri::generate_context!())
        .expect("error");
}
```

### Sidecar Lifecycle

The sidecar is managed by `operations/sidecar.rs`:

```rust
pub fn start_sidecar(app: AppHandle) -> Result<String, String> { ... }
pub fn stop_sidecar() -> Result<(), String> { ... }
pub fn sidecar_status() -> Result<String, String> { ... }
```

The sidecar is configured in `tauri.conf.json` under `bundle.externalBin`.

### Change Signals (Full Edition Only)

The `operations/signals.rs` module uses a tokio broadcast channel:

```rust
pub enum ChangeEvent {
    SettingsChanged,
    ProductCreated(i32),
    ProductUpdated(i32),
    ProductDeleted(i32),
    EntityChanged { entity_type: String, entity_id: i32, action: String },
}

pub fn get_signal_tx() -> broadcast::Sender<ChangeEvent> { ... }
pub fn subscribe_signals() -> broadcast::Receiver<ChangeEvent> { ... }
```

---

## Related Docs

- [`rust-code.md`](rust-code.md) — Rust backend architecture reference
- [`customization-react.md`](customization-react.md) — Frontend customization
- [`commands.md`](commands.md) — Full CLI reference
- [Tauri 2 Documentation](https://v2.tauri.app/)
