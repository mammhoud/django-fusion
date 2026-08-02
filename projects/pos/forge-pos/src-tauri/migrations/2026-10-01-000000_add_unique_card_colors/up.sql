-- Add the unique per-product card colors toggle to the settings table.
-- Default ON (1) so existing installs keep the unique-color behavior.
ALTER TABLE settings ADD COLUMN unique_card_colors BOOLEAN NOT NULL DEFAULT 1;
