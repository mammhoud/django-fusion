-- Loyalty reward badges.
--
-- A badge is earned by a customer once their loyalty points reach `threshold`.
-- `icon` is a Remix icon suffix (rendered as `ri-{icon}`) and `tone` maps to
-- the shared <Badge> component variants (e.g. default, success, soft-warning).
CREATE TABLE IF NOT EXISTS badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    icon TEXT NOT NULL DEFAULT 'award-line',
    tone TEXT NOT NULL DEFAULT 'default',
    threshold REAL NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS update_badges_updated_at AFTER UPDATE ON badges
BEGIN UPDATE badges SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;
