-- Delivery zones table for distance-based fee calculation.
-- Each zone represents a city or district the restaurant delivers to.
CREATE TABLE IF NOT EXISTS delivery_zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    base_fee REAL NOT NULL DEFAULT 0.0,
    fee_per_km REAL NOT NULL DEFAULT 0.0,
    max_distance REAL NOT NULL DEFAULT 10.0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS update_delivery_zones_updated_at AFTER UPDATE ON delivery_zones
BEGIN UPDATE delivery_zones SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

-- Seed some default zones
INSERT OR IGNORE INTO delivery_zones (id, name, base_fee, fee_per_km, max_distance) VALUES
    (1, 'Downtown',        5.0,  1.0,  5.0),
    (2, 'Suburbs',         8.0,  1.5,  10.0),
    (3, 'Outskirts',       12.0, 2.0,  15.0),
    (4, 'Rural',           15.0, 2.5,  25.0);
