-- Add delivery_zone_id to sales for per-sale zone tracking
ALTER TABLE sales ADD COLUMN delivery_zone_id INTEGER REFERENCES delivery_zones(id) ON DELETE SET NULL;
