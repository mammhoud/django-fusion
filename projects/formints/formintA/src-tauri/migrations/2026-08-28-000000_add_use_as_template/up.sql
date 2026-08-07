-- Add use_as_template flag to receipt_templates/notes table
-- Default to false (0) for existing rows
ALTER TABLE receipt_templates ADD COLUMN use_as_template BOOLEAN NOT NULL DEFAULT 0;
