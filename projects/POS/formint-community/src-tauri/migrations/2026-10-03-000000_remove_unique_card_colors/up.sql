-- Remove the "Unique Card Colors" toggle column — product cards now always
-- use the single uniform accent color (the original default look).
ALTER TABLE settings DROP COLUMN unique_card_colors;
