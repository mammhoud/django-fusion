-- =============================================================================
-- Gaming Center Seed — DOWN (revert gaming-specific data)
-- =============================================================================
-- Deletes only the rows inserted by the corresponding up.sql.
-- Order respects foreign-key constraints (children first, parents last).
-- The final UPDATE reverts settings to the base defaults from create_all.
-- =============================================================================

DELETE FROM payrolls WHERE id BETWEEN 9 AND 15;
DELETE FROM employee_schedules WHERE id BETWEEN 13 AND 19;
DELETE FROM sale_items WHERE sale_id BETWEEN 13 AND 32;
DELETE FROM sales WHERE id BETWEEN 13 AND 32;
DELETE FROM employees WHERE id BETWEEN 13 AND 19;
DELETE FROM employee_types WHERE id BETWEEN 8 AND 12;
DELETE FROM delivery_types WHERE id BETWEEN 4 AND 5;
DELETE FROM products WHERE id BETWEEN 51 AND 76;
DELETE FROM categories WHERE id BETWEEN 11 AND 16;

-- Revert gaming-specific branding in settings
UPDATE settings SET
    restaurant_name  = 'Formint',
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
