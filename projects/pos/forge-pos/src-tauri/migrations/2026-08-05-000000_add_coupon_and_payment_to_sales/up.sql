-- Coupon/discount support + payment method on sales
ALTER TABLE sales ADD COLUMN discount_code TEXT;
ALTER TABLE sales ADD COLUMN discount_amount REAL NOT NULL DEFAULT 0;
ALTER TABLE sales ADD COLUMN payment_method TEXT NOT NULL DEFAULT 'cash';
