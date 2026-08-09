-- Formint POS — rollback of the rebrand + product image seed.
-- Settings branding is reverted to the plain restaurant default; the
-- category colours set in this migration are cleared back to NULL for the
-- coffee categories, product images are cleared, and the demo sales/sale
-- items inserted by this migration are removed (INSERT OR IGNORE only
-- added rows whose IDs did not already exist, so DELETE by ID is safe).

UPDATE settings SET
    restaurant_name = 'Formint',
    address         = NULL,
    phone           = NULL,
    email           = NULL,
    receipt_footer  = 'Thank you for your business!',
    currency        = 'EGP'
WHERE id = 1;

UPDATE products SET image = NULL
WHERE id IN (77, 78, 80, 81, 83, 86, 91, 92, 93, 95, 99, 101, 102, 103);

UPDATE categories SET color = NULL WHERE id BETWEEN 17 AND 21;

DELETE FROM sale_items WHERE id BETWEEN 6001 AND 6024;
DELETE FROM sales WHERE id BETWEEN 5001 AND 5012;
