//! DataToken Shell — local sync queue operations.
//!
//! These functions mark data changes that need syncing when the Django
//! sidecar is unavailable. Uses raw SQL with manual result mapping to
//! avoid Diesel type-compatibility issues with SQLite Text columns.

use diesel::prelude::*;
use std::path::PathBuf;

use crate::db::open_conn;

/// A lightweight view of a sync_queue row used for batch processing.
#[derive(Debug, Clone)]
pub struct PendingSyncItem {
    pub id: i32,
    pub entity_type: String,
    pub entity_id: String,
    pub change_type: String,
    pub payload_json: String,
    pub sync_order: i32,
    pub retry_count: i32,
}

// ── Public API ────────────────────────────────────────────────────

/// Tag a data change for later sync.
pub fn tag_for_sync(
    db_path: &PathBuf,
    entity_type: &str,
    entity_id: &str,
    change_type: &str,
    payload_json: &str,
) -> Result<i32, String> {
    let mut conn = open_conn(db_path)?;

    let max_order: Option<i32> = {
        let rows: Vec<MaxOrderRow> = diesel::sql_query(
            "SELECT MAX(sync_order) AS max_ord FROM sync_queue"
        )
        .load(&mut conn)
        .map_err(|e| format!("tag_for_sync max: {e}"))?;
        rows.first().and_then(|r| r.max_ord)
    };

    let next_order = max_order.unwrap_or(0) + 1;
    let safe_et = entity_type.replace('\'', "''");
    let safe_eid = entity_id.replace('\'', "''");
    let safe_ct = change_type.replace('\'', "''");
    let safe_payload = payload_json.replace('\'', "''");

    diesel::sql_query(format!(
        "INSERT INTO sync_queue (entity_type, entity_id, change_type, sync_order, payload_json) \
         VALUES ('{safe_et}', '{safe_eid}', '{safe_ct}', {next_order}, '{safe_payload}')"
    ))
    .execute(&mut conn)
    .map_err(|e| format!("tag_for_sync insert: {e}"))?;

    let rows: Vec<IdRow> = diesel::sql_query("SELECT last_insert_rowid() AS id")
        .load(&mut conn)
        .map_err(|e| format!("tag_for_sync last_id: {e}"))?;
    Ok(rows.first().map(|r| r.id).unwrap_or(0))
}

/// Return the next batch of pending sync queue rows.
pub fn get_pending_batch(
    db_path: &PathBuf,
    limit: i64,
) -> Result<Vec<PendingSyncItem>, String> {
    let mut conn = open_conn(db_path)?;
    let rows: Vec<SyncQueueRow> = diesel::sql_query(format!(
        "SELECT id, entity_type, entity_id, change_type, payload_json, sync_order, retry_count \
         FROM sync_queue WHERE status = 'pending' \
         ORDER BY sync_order ASC, created_at ASC LIMIT {limit}"
    ))
    .load(&mut conn)
    .map_err(|e| format!("get_pending_batch: {e}"))?;

    Ok(rows
        .into_iter()
        .map(|r| PendingSyncItem {
            id: r.id,
            entity_type: r.entity_type,
            entity_id: r.entity_id,
            change_type: r.change_type,
            payload_json: r.payload_json,
            sync_order: r.sync_order,
            retry_count: r.retry_count,
        })
        .collect())
}

/// Bulk-update sync queue rows to `flushed`.
pub fn mark_flushed(db_path: &PathBuf, ids: &[i32]) -> Result<usize, String> {
    if ids.is_empty() {
        return Ok(0);
    }
    let mut conn = open_conn(db_path)?;
    let id_list: Vec<String> = ids.iter().map(|i| i.to_string()).collect();
    diesel::sql_query(format!(
        "UPDATE sync_queue SET status = 'flushed', flushed_at = datetime('now') \
         WHERE id IN ({})",
        id_list.join(",")
    ))
    .execute(&mut conn)
    .map_err(|e| format!("mark_flushed: {e}"))
}

/// Mark a single row as failed and increment its retry count.
pub fn mark_failed(
    db_path: &PathBuf,
    row_id: i32,
    error: &str,
) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    let safe_error = error.replace('\'', "''");
    diesel::sql_query(format!(
        "UPDATE sync_queue SET status = 'failed', error_message = '{safe_error}', \
         retry_count = retry_count + 1 WHERE id = {row_id}"
    ))
    .execute(&mut conn)
    .map_err(|e| format!("mark_failed: {e}"))?;
    Ok(())
}

/// Remove flushed rows older than the given number of days.
pub fn purge_flushed(db_path: &PathBuf, older_than_days: i32) -> Result<usize, String> {
    let mut conn = open_conn(db_path)?;
    diesel::sql_query(format!(
        "DELETE FROM sync_queue WHERE status = 'flushed' \
         AND flushed_at < datetime('now', '-{older_than_days} days')"
    ))
    .execute(&mut conn)
    .map_err(|e| format!("purge_flushed: {e}"))
}

// ── Raw row types for sql_query mapping ───────────────────────────

#[derive(QueryableByName, Debug)]
struct MaxOrderRow {
    #[diesel(sql_type = diesel::sql_types::Nullable<diesel::sql_types::Integer>)]
    max_ord: Option<i32>,
}

#[derive(QueryableByName, Debug)]
struct IdRow {
    #[diesel(sql_type = diesel::sql_types::Integer)]
    id: i32,
}

#[derive(QueryableByName, Debug)]
struct SyncQueueRow {
    #[diesel(sql_type = diesel::sql_types::Integer)]
    id: i32,
    #[diesel(sql_type = diesel::sql_types::Text)]
    entity_type: String,
    #[diesel(sql_type = diesel::sql_types::Text)]
    entity_id: String,
    #[diesel(sql_type = diesel::sql_types::Text)]
    change_type: String,
    #[diesel(sql_type = diesel::sql_types::Text)]
    payload_json: String,
    #[diesel(sql_type = diesel::sql_types::Integer)]
    sync_order: i32,
    #[diesel(sql_type = diesel::sql_types::Integer)]
    retry_count: i32,
}

// ── Tests ─────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use crate::db::run_migrations;
    use std::sync::atomic::{AtomicU32, Ordering};

    static COUNTER: AtomicU32 = AtomicU32::new(0);

    fn temp_db(tag: &str) -> PathBuf {
        let c = COUNTER.fetch_add(1, Ordering::SeqCst);
        let dir = std::env::temp_dir().join(format!(
            "formint-sync-queue-{}-{}-{}",
            std::process::id(), tag, c
        ));
        let _ = std::fs::create_dir_all(&dir);
        let path = dir.join("test.db");
        let _ = std::fs::remove_file(&path);
        run_migrations(&path).expect("migrations ok");
        path
    }

    #[test]
    fn tag_and_batch() {
        let db = temp_db("tag");
        let id1 = tag_for_sync(&db, "currency", "1", "create", r#"{"code":"USD"}"#)
            .expect("tag");
        let id2 = tag_for_sync(&db, "currency", "2", "create", r#"{"code":"EUR"}"#)
            .expect("tag");
        assert!(id1 > 0);
        assert!(id2 > id1);

        let batch = get_pending_batch(&db, 10).expect("batch");
        assert_eq!(batch.len(), 2);
        assert_eq!(batch[0].entity_type, "currency");
        assert!(batch[0].sync_order < batch[1].sync_order);
    }

    #[test]
    fn flush_then_purge() {
        let db = temp_db("flush");
        let id = tag_for_sync(&db, "product", "42", "update", "{}")
            .expect("tag");

        mark_flushed(&db, &[id]).expect("flush");
        let pending = get_pending_batch(&db, 10).expect("batch");
        assert!(pending.is_empty());

        let purged = purge_flushed(&db, 0).expect("purge");
        assert_eq!(purged, 1);
    }

    #[test]
    fn mark_failed_increments_retry() {
        let db = temp_db("fail");
        let id = tag_for_sync(&db, "sale", "7", "create", "{}")
            .expect("tag");
        mark_failed(&db, id, "timeout").expect("fail");

        let mut conn = open_conn(&db).expect("conn");
        #[derive(QueryableByName, Debug)]
        struct StatusRow {
            #[diesel(sql_type = diesel::sql_types::Text)]
            status: String,
            #[diesel(sql_type = diesel::sql_types::Integer)]
            retry_count: i32,
            #[diesel(sql_type = diesel::sql_types::Text)]
            error_message: String,
        }
        let rows: Vec<StatusRow> = diesel::sql_query(format!(
            "SELECT status, retry_count, error_message FROM sync_queue WHERE id = {id}"
        ))
        .load(&mut conn)
        .expect("reload");
        let row = &rows[0];
        assert_eq!(row.status, "failed");
        assert_eq!(row.retry_count, 1);
        assert_eq!(row.error_message, "timeout");
    }
}
