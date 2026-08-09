# POS Rust Integration Guide — Sidecar Linking

> **Status:** Planning Phase  
> **Last Updated:** 20 July 2026  
> **Purpose:** Document how Rust Tauri backend links with Robyn sidecar

---

## 1. Overview

The POS application has two data layers:

```
┌──────────────────────────────────────────────────────────────┐
│                    POS System Data Layers                      │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Rust Backend (Diesel, local SQLite)                   │    │
│  │  • Local CRUD (products, sales, customers, etc.)      │    │
│  │  • Works offline, full functionality                   │    │
│  │  • Tables: posapp_* (same schema as posapp Django)    │    │
│  │  • Tauri commands called from React frontend          │    │
│  └──────────────────┬───────────────────────────────────┘    │
│                     │                                         │
│                     │ Tauri IPC (invoke)                      │
│                     ▼                                         │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Robyn Sidecar (Django ORM, shared SQLite)             │    │
│  │  • Cloud sync (push/pull data to cloud)               │    │
│  │  • Node registry (register, heartbeat, events)        │    │
│  │  • Config management (device, master, cloud)          │    │
│  │  • Approval workflow (moderate incoming changes)      │    │
│  │  • WebSocket streams (real-time events)               │    │
│  │  • HTTP API consumed by frontend Pinia stores         │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Current Rust Modules

| Module | File | Purpose | Sidecar Link? |
|--------|------|---------|--------------|
| `auth.rs` | `operations/auth.rs` | Login, password, sessions | ❌ Standalone |
| `products.rs` | `operations/products.rs` | Product CRUD | ❌ Standalone |
| `sales.rs` | `operations/sales.rs` | Sale CRUD | ❌ Standalone |
| `customers.rs` | `operations/customers.rs` | Customer CRUD | ❌ Standalone |
| `categories.rs` | `operations/categories.rs` | Category CRUD | ❌ Standalone |
| `inventory.rs` | `operations/inventory.rs` | Inventory CRUD | ❌ Standalone |
| `employees.rs` | `operations/employees.rs` | Employee CRUD | ❌ Standalone |
| `sidecar.rs` | `operations/sidecar.rs` | Process lifecycle | ✅ Starts/Stops sidecar |
| `recipes.rs` | `operations/recipes.rs` | Recipe management | ❌ Standalone |
| `settings.rs` | `operations/settings.rs` | App settings | ❌ Standalone |

---

## 3. What to Add to Rust for Sidecar Linking

### 3.1 Module: `sync.rs` — Push Local Data to Sidecar

```rust
// src-tauri/src/operations/sync.rs
// 🟢 Customizable — add new entity types freely

use tauri::State;
use crate::db::DbPool;
use crate::models::{Product, Sale, Customer, InventoryTransaction};

pub struct SyncResult {
    pub pushed: u32,
    pub failed: u32,
    pub errors: Vec<String>,
}

#[tauri::command]
pub async fn push_sales_to_sidecar(
    pool: State<'_, DbPool>,
    sidecar_url: String,
    sales: Vec<i32>,  // sale IDs to sync
) -> Result<SyncResult, String> {
    let conn = pool.get().map_err(|e| e.to_string())?;
    let mut result = SyncResult { pushed: 0, failed: 0, errors: vec![] };

    for sale_id in sales {
        let sale = sales::table
            .find(sale_id)
            .first::<Sale>(&conn)
            .map_err(|e| format!("Sale {} not found: {}", sale_id, e))?;

        let client = reqwest::Client::new();
        match client
            .post(format!("{}/sync/receive/sales", sidecar_url))
            .json(&serde_json::json!({
                "node_id": std::env::var("POS_NODE_ID").unwrap_or("unknown".into()),
                "sales": [sale],
                "require_approval": true,
            }))
            .send()
            .await
        {
            Ok(_) => result.pushed += 1,
            Err(e) => {
                result.failed += 1;
                result.errors.push(format!("Sale {}: {}", sale_id, e));
            }
        }
    }
    Ok(result)
}
```

### 3.2 Module: `tokens.rs` — Get Device Token from Sidecar

```rust
// src-tauri/src/operations/tokens.rs
// 🟢 Customizable

#[tauri::command]
pub async fn get_device_token(
    sidecar_url: String,
    device_id: String,
    role: String,  // admin, manager, cashier, viewer
) -> Result<String, String> {
    let client = reqwest::Client::new();
    let resp = client
        .post(format!("{}/auth/token", sidecar_url))
        .json(&serde_json::json!({
            "device_id": device_id,
            "role": role,
            "node_type": "pos-full",
        }))
        .send()
        .await
        .map_err(|e| format!("Token request failed: {}", e))?;

    let body: serde_json::Value = resp.json().await.map_err(|e| e.to_string())?;
    Ok(body["token"].as_str().unwrap_or("").to_string())
}

#[tauri::command]
pub async fn refresh_device_token(
    sidecar_url: String,
    current_token: String,
) -> Result<String, String> {
    let client = reqwest::Client::new();
    let resp = client
        .post(format!("{}/auth/refresh", sidecar_url))
        .header("Authorization", format!("Bearer {}", current_token))
        .send()
        .await
        .map_err(|e| format!("Token refresh failed: {}", e))?;

    let body: serde_json::Value = resp.json().await.map_err(|e| e.to_string())?;
    Ok(body["token"].as_str().unwrap_or("").to_string())
}
```

### 3.3 Module: `config.rs` — Pull Device Config from Sidecar

```rust
// src-tauri/src/operations/config.rs
// 🟢 Customizable

use serde_json::Value;

#[tauri::command]
pub async fn get_device_config(
    sidecar_url: String,
    node_id: String,
    token: String,
) -> Result<Value, String> {
    let client = reqwest::Client::new();
    let resp = client
        .get(format!("{}/nodes/{}/config", sidecar_url, node_id))
        .header("Authorization", format!("Bearer {}", token))
        .send()
        .await
        .map_err(|e| format!("Config fetch failed: {}", e))?;

    resp.json().await.map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn set_device_config(
    sidecar_url: String,
    node_id: String,
    config_key: String,
    config_value: Value,
    token: String,
) -> Result<Value, String> {
    let client = reqwest::Client::new();
    let resp = client
        .post(format!("{}/nodes/{}/config", sidecar_url, node_id))
        .header("Authorization", format!("Bearer {}", token))
        .json(&serde_json::json!({
            "config_key": config_key,
            "config_value": config_value,
        }))
        .send()
        .await
        .map_err(|e| format!("Config push failed: {}", e))?;

    resp.json().await.map_err(|e| e.to_string())
}
```

### 3.4 Module: `approvals.rs` — Check Approval Queue

```rust
// src-tauri/src/operations/approvals.rs
// 🟢 Customizable

#[tauri::command]
pub async fn get_pending_approvals(
    sidecar_url: String,
    token: String,
) -> Result<Value, String> {
    let client = reqwest::Client::new();
    let resp = client
        .get(format!("{}/approvals/pending", sidecar_url))
        .header("Authorization", format!("Bearer {}", token))
        .send()
        .await
        .map_err(|e| format!("Approval fetch failed: {}", e))?;

    resp.json().await.map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn approve_change(
    sidecar_url: String,
    approval_id: i32,
    reviewer: String,
    token: String,
) -> Result<Value, String> {
    let client = reqwest::Client::new();
    let resp = client
        .post(format!("{}/approvals/{}/approve", sidecar_url, approval_id))
        .header("Authorization", format!("Bearer {}", token))
        .json(&serde_json::json!({ "reviewer": reviewer }))
        .send()
        .await
        .map_err(|e| format!("Approval failed: {}", e))?;

    resp.json().await.map_err(|e| e.to_string())
}
```

---

## 4. Registration in `lib.rs`

```rust
// src-tauri/src/lib.rs — add to tauri::Builder

fn main() {
    tauri::Builder::default()
        // ... existing commands ...
        .invoke_handler(tauri::generate_handler![
            // Existing
            operations::auth::login,
            operations::products::list_products,
            // ... (all existing) ...
            
            // Sidecar link — add these
            operations::sync::push_sales_to_sidecar,
            operations::tokens::get_device_token,
            operations::tokens::refresh_device_token,
            operations::config::get_device_config,
            operations::config::set_device_config,
            operations::approvals::get_pending_approvals,
            operations::approvals::approve_change,
        ])
        .run(tauri::generate_context!())
        .expect("error while running application");
}
```

---

## 5. Dependencies

Add to `src-tauri/Cargo.toml`:

```toml
[dependencies]
reqwest = { version = "0.12", features = ["json"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tokio = { version = "1", features = ["full"] }
```

---

## 6. Data Flow Diagram

```
React Frontend                Rust Backend                    Sidecar
     │                            │                              │
     │  invoke('list_products')   │                              │
     ├───────────────────────────►│                              │
     │                            │── DB query (Diesel) ────────►│
     │◄── products[] ─────────────┤                              │
     │                            │                              │
     │  invoke('push_sales')      │                              │
     ├───────────────────────────►│                              │
     │                            ├── POST /sync/receive/sales ─►│
     │                            │                              │── approval queue
     │                            │◄── { status: "pending" } ───┤
     │◄── SyncResult ─────────────┤                              │
     │                            │                              │
     │  invoke('get_device_token')│                              │
     ├───────────────────────────►│                              │
     │                            ├── POST /auth/token ─────────►│
     │                            │◄── { token: "abc..." } ─────┤
     │◄── token ──────────────────┤                              │
```

---

## 7. Sidecar URL Resolution

```rust
// How the frontend determines the sidecar URL
fn get_sidecar_url() -> String {
    std::env::var("POS_SIDECAR_URL")
        .unwrap_or_else(|_| "http://127.0.0.1:8766".to_string())
}
```

The sidecar URL is configurable via:
1. Environment variable `POS_SIDECAR_URL`
2. App settings (stored in Rust DB)
3. Default: `http://127.0.0.1:8766` (Full) or `http://127.0.0.1:8765` (Solo)
