CREATE TABLE currencies (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    symbol TEXT NOT NULL DEFAULT '',
    exchange_rate DOUBLE NOT NULL DEFAULT 1.0,
    is_default BOOLEAN NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (is_active = 1 OR is_default = 0)
);

CREATE INDEX idx_currencies_active_default_code
    ON currencies (is_active DESC, is_default DESC, code ASC);

CREATE UNIQUE INDEX idx_currencies_single_default
    ON currencies (is_default)
    WHERE is_default = 1;
