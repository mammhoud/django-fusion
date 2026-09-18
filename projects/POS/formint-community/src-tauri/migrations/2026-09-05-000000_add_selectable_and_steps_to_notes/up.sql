-- Add selectable + steps columns to receipt_templates (the notes table).
--   selectable: notes flagged as quick-pick on other screens (KDS, Sale)
--   steps:      structured preparation steps (JSON array of {title, details})
ALTER TABLE receipt_templates ADD COLUMN selectable BOOLEAN NOT NULL DEFAULT 0;
ALTER TABLE receipt_templates ADD COLUMN steps TEXT;
