//! Data mutation dispatcher with sidecar fallback chain.
//!
//! Every data mutation follows this pattern:
//!   1. Try sidecar API (if connected)
//!   2. Always write to local Diesel/SQLite (primary store)
//!   3. Tag with DataToken Shell for later sync (when sidecar offline)
//!   4. Emit `data-changed` event (if app handle available)

use std::path::PathBuf;
use tauri::AppHandle;
use tauri::Emitter;

use crate::operations::sync_queue;
use crate::operations::sidecar_reconnect;

/// Outcome of a dispatched mutation.
#[derive(Debug, Clone, serde::Serialize)]
pub struct MutationResult {
    /// True if the sidecar accepted the write.
    pub sidecar_ok: bool,
    /// The entity type that was written.
    pub entity_type: String,
    /// The entity ID (as returned by the local write).
    pub entity_id: String,
    /// Change type (create | update | delete).
    pub change_type: String,
}

/// Dispatch a data mutation through the 3-tier pipeline.
///
/// `payload_json` is the JSON snapshot of the row at change time.
/// When `app` is provided, a `data-changed` Tauri event is emitted so
/// the frontend can refresh without polling.
pub fn dispatch_mutation(
    db_path: &PathBuf,
    app: Option<&AppHandle>,
    entity_type: &str,
    entity_id: &str,
    change_type: &str,
    payload_json: &str,
) -> Result<MutationResult, String> {
    let sidecar_available = sidecar_reconnect::check_sidecar_health()
        .unwrap_or(false);

    // ── Step 1: Try sidecar (best-effort) ──
    if sidecar_available {
        if sidecar_reconnect::post_sync_item_to_sidecar(
            entity_type, entity_id, change_type, payload_json,
        ).is_ok() {
            // Sidecar accepted — still emit event for frontend.
            if let Some(app) = app {
                let _ = app.emit("data-changed", serde_json::json!({
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "change_type": change_type,
                }));
            }
            return Ok(MutationResult {
                sidecar_ok: true,
                entity_type: entity_type.to_string(),
                entity_id: entity_id.to_string(),
                change_type: change_type.to_string(),
            });
        }
        // Sidecar write failed — fall through to local tagging.
    }

    // ── Step 2: Tag with DataToken Shell ──
    sync_queue::tag_for_sync(
        db_path,
        entity_type,
        entity_id,
        change_type,
        payload_json,
    )?;

    // ── Step 3: Emit change event ──
    if let Some(app) = app {
        let _ = app.emit("data-changed", serde_json::json!({
            "entity_type": entity_type,
            "entity_id": entity_id,
            "change_type": change_type,
        }));
    }

    Ok(MutationResult {
        sidecar_ok: false,
        entity_type: entity_type.to_string(),
        entity_id: entity_id.to_string(),
        change_type: change_type.to_string(),
    })
}
