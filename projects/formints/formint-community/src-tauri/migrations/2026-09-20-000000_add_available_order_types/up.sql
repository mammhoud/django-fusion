-- Add available order types to products so a product can be restricted to
-- specific order types (dine-in, takeaway, delivery, extra-order, dated-order).
-- Stored as a comma-separated list; empty string = available everywhere.
ALTER TABLE products ADD COLUMN available_order_types TEXT NOT NULL DEFAULT '';
