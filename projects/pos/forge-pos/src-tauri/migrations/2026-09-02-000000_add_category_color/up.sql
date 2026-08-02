-- Add color column to categories for the per-category accent color feature.
-- Nullable: NULL = category has no custom color (falls back to palette).
ALTER TABLE categories ADD COLUMN color TEXT;
