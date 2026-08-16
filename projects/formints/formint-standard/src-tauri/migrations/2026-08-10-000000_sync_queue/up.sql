-- DataToken Shell — local sync queue for offline-server sync.
-- The sync_queue table marks rows that need syncing when the
-- Django server is unavailable. When the server reconnects,
-- pending rows are flushed and real DataToken rows are created.

CREATE TABLE sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- What changed
    entity_type TEXT NOT NULL,          -- e.g. "currency", "sale", "product"
    entity_id TEXT NOT NULL,            -- PK of the changed row (string for flexibility)
    change_type TEXT NOT NULL,          -- "create" | "update" | "delete"
    -- Ordering
    sync_order INTEGER NOT NULL DEFAULT 0,
    -- Status
    status TEXT NOT NULL DEFAULT 'pending',  -- pending | flushing | flushed | failed
    retry_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT DEFAULT '',
    -- Payload (snapshot of the row at change time)
    payload_json TEXT NOT NULL DEFAULT '{}',
    -- Timestamps
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    flushed_at TEXT
);

CREATE INDEX idx_sync_queue_status_order
    ON sync_queue(status, sync_order, created_at);

CREATE INDEX idx_sync_queue_entity
    ON sync_queue(entity_type, entity_id);
