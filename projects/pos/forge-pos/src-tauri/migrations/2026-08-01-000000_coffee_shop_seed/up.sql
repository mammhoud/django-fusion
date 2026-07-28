-- =============================================================================
-- Coffee Shop Seed — preset data for coffee shop demo
-- =============================================================================
-- All INSERTs use OR IGNORE so this migration is safe to re-run.
-- Corresponding down.sql deletes the exact IDs this migration inserts.
-- =============================================================================

-- 1. Settings — rebrand as coffee shop
UPDATE settings SET
    restaurant_name  = 'Forge POS',
    address          = '15 Brew Lane, Downtown, Lahore',
    phone            = '+92-300-555-BREW',
    email            = 'hello@thedailygrind.com',
    tax_rate         = '13',
    currency         = 'PKR',
    opening_time     = '07:00',
    closing_time     = '23:00',
    receipt_footer   = 'Brewed fresh for you! ☕ Follow @dailygrind',
    dine_in_tables   = 20,
    delivery_fee     = 30.0,
    delivery_fee_per_km = 10.0
WHERE id = 1;

-- 2. Coffee shop categories (adds on top of base categories 1-10)
INSERT OR IGNORE INTO categories (id, name) VALUES
    (17, 'Espresso & Coffee'),
    (18, 'Teas & Chai'),
    (19, 'Pastries & Baked Goods'),
    (20, 'Cold Brews & Smoothies'),
    (21, 'Signature Drinks');

-- 3. Coffee shop products (IDs 77+)
INSERT OR IGNORE INTO products (id, name, price, unit, category_id) VALUES
    (77, 'Espresso (Single)',             180.00, 'cup',   17),
    (78, 'Espresso (Double)',             250.00, 'cup',   17),
    (79, 'Americano',                     220.00, 'cup',   17),
    (80, 'Cappuccino',                    350.00, 'cup',   17),
    (81, 'Latte',                         380.00, 'cup',   17),
    (82, 'Flat White',                    320.00, 'cup',   17),
    (83, 'Mocha',                         420.00, 'cup',   17),
    (84, 'Affogato',                      450.00, 'cup',   17),
    (85, 'Irish Coffee',                  500.00, 'cup',   17),
    (86, 'Karak Chai',                    120.00, 'cup',   18),
    (87, 'Green Tea',                     150.00, 'cup',   18),
    (88, 'Earl Grey',                     180.00, 'cup',   18),
    (89, 'Masala Chai',                   200.00, 'cup',   18),
    (90, 'Iced Tea (Lemon)',              180.00, 'glass', 18),
    (91, 'Matcha Latte',                  450.00, 'cup',   18),
    (92, 'Croissant',                     250.00, 'item',  19),
    (93, 'Blueberry Muffin',              220.00, 'item',  19),
    (94, 'Chocolate Chip Cookie',         150.00, 'item',  19),
    (95, 'Cheesecake Slice',              450.00, 'slice', 19),
    (96, 'Banana Bread',                  280.00, 'slice', 19),
    (97, 'Cinnamon Roll',                 320.00, 'item',  19),
    (98, 'Brownie',                       250.00, 'item',  19),
    (99, 'Cold Brew',                     350.00, 'cup',   20),
    (100, 'Nitro Cold Brew',              450.00, 'cup',   20),
    (101, 'Mango Smoothie',               350.00, 'glass', 20),
    (102, 'Berry Blast Smoothie',         380.00, 'glass', 20),
    (103, 'Banana Shake',                 320.00, 'glass', 20),
    (104, 'Caramel Macchiato',            480.00, 'cup',   21),
    (105, 'Hazelnut Latte',               450.00, 'cup',   21),
    (106, 'Spanish Latte',                420.00, 'cup',   21),
    (107, 'Turmeric Latte (Golden Milk)', 380.00, 'cup',   21),
    (108, 'Salted Caramel Frappe',        520.00, 'cup',   21);

-- 4. Coffee shop employee types
INSERT OR IGNORE INTO employee_types (id, name, description) VALUES
    (13, 'Barista',        'Coffee preparation & service'),
    (14, 'Pastry Chef',    'Baked goods preparation'),
    (15, 'Shift Manager',  'Oversees daily operations');

-- 5. Coffee shop employees
INSERT OR IGNORE INTO employees (id, name, phone, email, employee_type_id, salary, joined_at) VALUES
    (20, 'Sara Ahmed',    '+92-300-222-1001', 'sara@thedailygrind.com', 13, 35000.00, '2024-03-01'),
    (21, 'Zara Malik',    '+92-300-222-1002', 'zara@thedailygrind.com', 13, 32000.00, '2024-04-15'),
    (22, 'Omar Hassan',   '+92-300-222-1003', 'omar@thedailygrind.com', 13, 35000.00, '2024-05-01'),
    (23, 'Hina Raza',     '+92-300-222-1004', 'hina@thedailygrind.com', 14, 40000.00, '2024-02-20'),
    (24, 'Tariq Mehmood', '+92-300-222-1005', 'tariq@thedailygrind.com', 15, 50000.00, '2024-01-15');

-- 6. Coffee shop sales (8 transactions)
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, table_number, employee_id) VALUES
    (33, 1080.00, 'PKR', '2026-07-15', '08:30:00', 'dine_in',  'completed', 2,  20),
    (34, 1450.00, 'PKR', '2026-07-15', '09:15:00', 'takeaway', 'completed', NULL, 21),
    (35, 2340.00, 'PKR', '2026-07-15', '11:00:00', 'dine_in',  'completed', 5,  22),
    (36, 860.00,  'PKR', '2026-07-15', '14:30:00', 'dine_in',  'completed', 3,  20),
    (37, 1920.00, 'PKR', '2026-07-16', '08:00:00', 'takeaway', 'completed', NULL, 21),
    (38, 1560.00, 'PKR', '2026-07-16', '10:45:00', 'dine_in',  'completed', 7,  22),
    (39, 3200.00, 'PKR', '2026-07-16', '16:00:00', 'dine_in',  'completed', 1,  20),
    (40, 750.00,  'PKR', '2026-07-17', '09:30:00', 'takeaway', 'completed', NULL, 21);

-- 7. Coffee shop sale items
INSERT OR IGNORE INTO sale_items (sale_id, product_name, price, quantity, unit) VALUES
    (33, 'Karak Chai',           120.00, 2, 'cup'),
    (33, 'Croissant',            250.00, 2, 'item'),
    (33, 'Chocolate Chip Cookie',150.00, 2, 'item'),
    (34, 'Latte',                380.00, 2, 'cup'),
    (34, 'Blueberry Muffin',     220.00, 2, 'item'),
    (34, 'Brownie',              250.00, 1, 'item'),
    (35, 'Cappuccino',           350.00, 3, 'cup'),
    (35, 'Cheesecake Slice',     450.00, 2, 'slice'),
    (35, 'Cinnamon Roll',        320.00, 1, 'item'),
    (35, 'Banana Bread',         280.00, 1, 'slice'),
    (36, 'Cold Brew',            350.00, 1, 'cup'),
    (36, 'Chocolate Chip Cookie',150.00, 1, 'item'),
    (36, 'Karak Chai',           120.00, 1, 'cup'),
    (36, 'Banana Shake',         320.00, 1, 'glass'),
    (37, 'Americano',            220.00, 2, 'cup'),
    (37, 'Croissant',            250.00, 2, 'item'),
    (37, 'Blueberry Muffin',     220.00, 2, 'item'),
    (37, 'Masala Chai',          200.00, 2, 'cup'),
    (38, 'Caramel Macchiato',    480.00, 2, 'cup'),
    (38, 'Cheesecake Slice',     450.00, 1, 'slice'),
    (38, 'Brownie',              250.00, 1, 'item'),
    (39, 'Irish Coffee',         500.00, 2, 'cup'),
    (39, 'Salted Caramel Frappe',520.00, 2, 'cup'),
    (39, 'Cinnamon Roll',        320.00, 2, 'item'),
    (39, 'Chocolate Chip Cookie',150.00, 2, 'item'),
    (39, 'Cheesecake Slice',     450.00, 1, 'slice'),
    (40, 'Espresso (Double)',    250.00, 1, 'cup'),
    (40, 'Croissant',            250.00, 1, 'item'),
    (40, 'Karak Chai',           120.00, 1, 'cup'),
    (40, 'Chocolate Chip Cookie',150.00, 1, 'item');

-- 8. Coffee shop ingredients (IDs 56-69)
INSERT OR IGNORE INTO ingredients (id, name, unit, current_quantity, reorder_level, reorder_quantity, cost_per_unit) VALUES
    (56, 'Espresso Beans',            'kg',    10.0, 5.0,  10.0, 1200.00),
    (57, 'Matcha Powder',             'kg',    3.0,  1.5,  3.0,  2500.00),
    (58, 'Chocolate Syrup',           'liter', 5.0,  2.0,  4.0,  400.00),
    (59, 'Caramel Sauce',             'liter', 4.0,  2.0,  3.0,  350.00),
    (60, 'Hazelnut Syrup',            'liter', 3.0,  1.5,  2.5,  450.00),
    (61, 'Turmeric Powder',           'kg',    2.0,  1.0,  2.0,  300.00),
    (62, 'Ice Cream Base',            'liter', 8.0,  4.0,  6.0,  280.00),
    (63, 'Mango Puree',               'kg',    5.0,  2.5,  4.0,  350.00),
    (64, 'Mixed Berries (Frozen)',    'kg',    4.0,  2.0,  3.0,  650.00),
    (65, 'Croissant Dough',           'kg',    6.0,  3.0,  5.0,  280.00),
    (66, 'Cream Cheese',              'kg',    5.0,  2.5,  4.0,  450.00),
    (67, 'Vanilla Extract',           'liter', 2.0,  0.5,  1.5,  1200.00),
    (68, 'Whipped Cream',             'liter', 8.0,  3.0,  5.0,  320.00),
    (69, 'Cinnamon Powder',           'kg',    2.0,  0.5,  1.0,  600.00);

-- 9. Coffee shop inventory transactions (IDs 32-41)
INSERT OR IGNORE INTO inventory_transactions (id, ingredient_id, transaction_type, quantity_change, note) VALUES
    (32, 56, 'purchase', 15.0,  'Initial stock - Espresso Beans'),
    (33, 57, 'purchase',  4.0,  'Initial stock - Matcha Powder'),
    (34, 58, 'purchase',  6.0,  'Initial stock - Chocolate Syrup'),
    (35, 59, 'purchase',  5.0,  'Initial stock - Caramel Sauce'),
    (36, 60, 'purchase',  4.0,  'Initial stock - Hazelnut Syrup'),
    (37, 65, 'purchase',  8.0,  'Initial stock - Croissant Dough'),
    (38, 56, 'usage',     -2.0, 'Usage: Week 1 - Coffee service'),
    (39, 65, 'usage',     -1.5, 'Usage: Week 1 - Pastry sales'),
    (40, 68, 'purchase', 10.0,  'Initial stock - Whipped Cream'),
    (41, 57, 'usage',     -0.5, 'Usage: Week 1 - Matcha latte sales');

-- 10. Coffee shop logo
UPDATE settings SET logo = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNTYiIGhlaWdodD0iMjU2IiB2aWV3Qm94PSIwIDAgMjU2IDI1NiI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNTAlIiByPSI1MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMkQxQjY5Ii8+CiAgICAgIDxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iIzFBMUE0MCIvPgogICAgPC9yYWRpYWxHcmFkaWVudD4KICAgIDxsaW5lYXJHcmFkaWVudCBpZD0iY3VwIiB4MT0iMCUiIHkxPSIwJSIgeDI9IjEwMCUiIHkyPSIxMDAlIj4KICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iI0U4QkI1QiIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiNENjk2M0UiLz4KICAgIDwvbGluZWFyR3JhZGllbnQ+CiAgPC9kZWZzPgogIDxyZWN0IHdpZHRoPSIyNTYiIGhlaWdodD0iMjU2IiByeD0iNDgiIGZpbGw9InVybCgjYmcpIi8+CiAgPHRleHQgeD0iMTI4IiB5PSIxMTUiIGZvbnQtc2l6ZT0iNjAiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7ir6M8L3RleHQ+CiAgPHRleHQgeD0iMTI4IiB5PSIxODAiIGZvbnQtc2l6ZT0iMjYiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9InVybCgjY3VwKSIKICAgICAgICB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LWZhbWlseT0ic3lzdGVtLXVpLHNhbnMtc2VyaWYiIGxldHRlci1zcGFjaW5nPSIyIj5UaGUgRGFpbHkgR3JpbmQ8L3RleHQ+Cjwvc3ZnPg==' WHERE id = 1;
