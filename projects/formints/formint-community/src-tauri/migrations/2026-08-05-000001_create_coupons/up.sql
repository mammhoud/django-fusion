-- Coupon management
CREATE TABLE IF NOT EXISTS coupons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL DEFAULT 'percent',
    value REAL NOT NULL DEFAULT 0,
    min_subtotal REAL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Seed default coupons so existing checkout codes keep working
INSERT INTO coupons (code, kind, value, min_subtotal, is_active) VALUES
  ('SAVE10', 'percent', 10, 10, 1),
  ('WELCOME5', 'fixed', 5, 15, 1);
