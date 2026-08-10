//! Sidecar reconnect — health check, flush pending sync, HTTP proxy.
//!
//! When the Django sidecar becomes available again after being offline,
//! the pending sync_queue rows are pushed to it so real DataToken rows
//! can be created by the Django sidecar.

use tauri::Manager;

use crate::operations::sync_queue::{self, PendingSyncItem};

/// Default sidecar base URL for the POS backend.
const SIDECAR_BASE_URL: &str = "http://127.0.0.1:8767";

/// Check whether the sidecar is healthy by hitting its health endpoint.
/// Uses a short timeout (2 seconds) so the offline fallback is fast.
pub fn check_sidecar_health() -> Result<bool, String> {
    let url = format!("{SIDECAR_BASE_URL}/health/");
    match ureq::get(&url)
        .timeout(std::time::Duration::from_secs(2))
        .call()
    {
        Ok(resp) => Ok(resp.status() == 200),
        Err(_) => Ok(false),
    }
}

/// Post a single sync item to the Django sidecar's sync-proxy endpoint.
/// Called by both the dispatcher (on every write) and the flush loop.
pub fn post_sync_item_to_sidecar(
    entity_type: &str,
    entity_id: &str,
    change_type: &str,
    payload_json: &str,
) -> Result<(), String> {
    let url = format!("{SIDECAR_BASE_URL}/sync-proxy/{entity_type}/");
    let body = serde_json::json!({
        "entity_id": entity_id,
        "change_type": change_type,
        "payload": serde_json::from_str::<serde_json::Value>(payload_json)
            .unwrap_or(serde_json::json!({})),
    });

    let resp = ureq::post(&url)
        .set("Content-Type", "application/json")
        .timeout(std::time::Duration::from_secs(5))
        .send_json(body)
        .map_err(|e| format!("post_sync_item: {e}"))?;

    if resp.status() == 200 || resp.status() == 201 {
        Ok(())
    } else {
        Err(format!(
            "sidecar returned {}: {}",
            resp.status(),
            resp.into_string().unwrap_or_default()
        ))
    }
}

/// Result of a flush operation.
#[derive(Debug, Clone, serde::Serialize)]
pub struct FlushResult {
    pub pushed: usize,
    pub failed: usize,
}

/// Flush all pending sync_queue rows to the Django sidecar.
///
/// Called when the sidecar comes back online (detected via periodic
/// health check or a Tauri `online` event in the frontend).
#[tauri::command]
pub fn flush_pending_sync(app: tauri::AppHandle) -> Result<FlushResult, String> {
    let db_path = {
        let app_data = app
            .path()
            .app_data_dir()
            .map_err(|e| format!("app data dir: {e}"))?;
        app_data.join("restaurant.db")
    };

    let batch = sync_queue::get_pending_batch(&db_path, 100)?;
    if batch.is_empty() {
        return Ok(FlushResult { pushed: 0, failed: 0 });
    }

    let mut pushed = 0usize;
    let mut failed = 0usize;
    let mut flushed_ids: Vec<i32> = Vec::new();

    for item in &batch {
        let item: &PendingSyncItem = item;
        match post_sync_item_to_sidecar(
            &item.entity_type,
            &item.entity_id,
            &item.change_type,
            &item.payload_json,
        ) {
            Ok(()) => {
                flushed_ids.push(item.id);
                pushed += 1;
            }
            Err(e) => {
                sync_queue::mark_failed(&db_path, item.id, &e)
                    .unwrap_or_else(|err| {
                        eprintln!("[sync] mark_failed error: {err}");
                    });
                failed += 1;
            }
        }
    }

    sync_queue::mark_flushed(&db_path, &flushed_ids)
        .unwrap_or_else(|err| {
            eprintln!("[sync] mark_flushed error: {err}");
            0
        });

    Ok(FlushResult { pushed, failed })
}

/// Tauri command: check sidecar health and return status.
#[tauri::command]
pub fn check_sidecar_health_cmd() -> Result<String, String> {
    match check_sidecar_health() {
        Ok(true) => Ok("connected".to_string()),
        Ok(false) => Ok("disconnected".to_string()),
        Err(e) => Err(e),
    }
}

/// Tauri command: return count of pending sync queue items.
#[tauri::command]
pub fn pending_sync_count(app: tauri::AppHandle) -> Result<usize, String> {
    let db_path = {
        let app_data = app
            .path()
            .app_data_dir()
            .map_err(|e| format!("app data dir: {e}"))?;
        app_data.join("restaurant.db")
    };
    let batch = sync_queue::get_pending_batch(&db_path, 10_000)?;
    Ok(batch.len())
}
