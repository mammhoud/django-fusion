-- =============================================================================
-- Coffee Shop Seed — DOWN (revert coffee-specific data)
-- =============================================================================
-- Deletes only the rows inserted by the corresponding up.sql.
-- Order respects foreign-key constraints (children first, parents last).
-- The final UPDATE reverts settings to the base defaults from create_all.
-- =============================================================================

DELETE FROM inventory_transactions WHERE id BETWEEN 32 AND 41;
DELETE FROM ingredients WHERE id BETWEEN 56 AND 69;
DELETE FROM sale_items WHERE sale_id BETWEEN 33 AND 40;
DELETE FROM sales WHERE id BETWEEN 33 AND 40;
DELETE FROM employees WHERE id BETWEEN 20 AND 24;
DELETE FROM employee_types WHERE id BETWEEN 13 AND 15;
DELETE FROM products WHERE id BETWEEN 77 AND 108;
DELETE FROM categories WHERE id BETWEEN 17 AND 21;

-- Revert coffee-specific branding in settings
UPDATE settings SET
    restaurant_name  = 'Forge POS',
    address          = NULL,
    phone            = NULL,
    email            = NULL,
    tax_rate         = NULL,
    currency         = 'PKR',
    opening_time     = NULL,
    closing_time     = NULL,
    receipt_footer   = 'Thank you for your business!',
    dine_in_tables   = 0,
    delivery_fee     = 0.0,
    delivery_fee_per_km = 0.0,
    logo             = NULL
WHERE id = 1;
