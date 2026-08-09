-- User action audit log — rows for sales, coupons, offers, customer links, etc.
CREATE TABLE IF NOT EXISTS user_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id INTEGER,
    details TEXT,
    user_id INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_actions_created ON user_actions (created_at);
CREATE INDEX IF NOT EXISTS idx_user_actions_entity ON user_actions (entity_type, entity_id);
