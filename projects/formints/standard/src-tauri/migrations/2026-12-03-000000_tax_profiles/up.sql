CREATE TABLE tax_profiles (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    rate DOUBLE NOT NULL DEFAULT 0.0,
    is_default BOOLEAN NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (is_active = 1 OR is_default = 0)
);

CREATE INDEX idx_tax_profiles_active_default_name
    ON tax_profiles (is_active DESC, is_default DESC, name ASC);

CREATE UNIQUE INDEX idx_tax_profiles_single_default
    ON tax_profiles (is_default)
    WHERE is_default = 1;

-- FK columns: products.tax_profile_id, sales.tax_profile_id
ALTER TABLE products ADD COLUMN tax_profile_id INTEGER REFERENCES tax_profiles (id);

ALTER TABLE sales ADD COLUMN tax_profile_id INTEGER REFERENCES tax_profiles (id);
