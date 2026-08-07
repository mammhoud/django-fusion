-- Add barcode and description columns to products for inventory tracking and richer product info
ALTER TABLE products ADD COLUMN barcode TEXT;
ALTER TABLE products ADD COLUMN description TEXT;
