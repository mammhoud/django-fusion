-- Add recipe_id column to receipt_templates for recipe-scoped notes
-- Nullable: NULL = global note (receipt template), non-NULL = recipe-scoped note
ALTER TABLE receipt_templates ADD COLUMN recipe_id INTEGER REFERENCES recipes(id) ON DELETE CASCADE;
