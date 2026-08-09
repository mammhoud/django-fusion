-- Restore the "Unique Card Colors" toggle column (default ON = uniform look).
ALTER TABLE settings ADD COLUMN unique_card_colors BOOLEAN NOT NULL DEFAULT 1;
