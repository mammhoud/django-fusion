-- Add prepare_time_minutes to products for default preparation time (in minutes)
ALTER TABLE products ADD COLUMN prepare_time_minutes INTEGER NOT NULL DEFAULT 0;

-- Add prepare_time to kitchen_tickets for actual/estimated preparation time
ALTER TABLE kitchen_tickets ADD COLUMN prepare_time_minutes INTEGER NOT NULL DEFAULT 0;
