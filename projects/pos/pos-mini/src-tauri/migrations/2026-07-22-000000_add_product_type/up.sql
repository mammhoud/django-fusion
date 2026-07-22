-- Add product_type column to products table
-- Supports: 'product' (default), 'rent', 'creation', 'service', 'digital'
ALTER TABLE products ADD COLUMN product_type TEXT NOT NULL DEFAULT 'product';
