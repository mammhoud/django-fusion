-- =============================================================================
-- Gaming Center Seed Migration
-- Use-case: Digital gaming center (PlayStation / VR) with hourly billing in USD
-- =============================================================================

-- 1. Switch default currency to USD & update business info
UPDATE settings SET
    restaurant_name  = 'Forge',
    address          = '42 Arcade Avenue, Downtown District',
    phone            = '+1-555-0-GAMING',
    email            = 'hello@levelupgaming.com',
    tax_rate         = '8.5',
    currency         = 'USD',
    opening_time     = '10:00',
    closing_time     = '02:00',
    receipt_footer   = 'Thanks for gaming with us! Follow @levelupgc',
    dine_in_tables   = 0,
    delivery_fee     = 0.0,
    delivery_fee_per_km = 0.0
WHERE id = 1;

-- 2. Replace food categories with gaming ones
--    (DELETE existing seeded categories — products will get category_id = NULL via FK cascade rule)
DELETE FROM categories WHERE id BETWEEN 1 AND 10;

INSERT OR IGNORE INTO categories (id, name) VALUES
    (11, 'PS5 Sessions'),
    (12, 'PS4 Sessions'),
    (13, 'VR Experience'),
    (14, 'Game Modes'),
    (15, 'Accessories & Rentals'),
    (16, 'Snacks & Drinks');

-- 3. Remove old food products, insert gaming center products
--    Unit = 'hour' for timed sessions; 'item' for accessories/consumables
DELETE FROM products WHERE id BETWEEN 1 AND 47;

INSERT OR IGNORE INTO products (id, name, price, unit, category_id) VALUES
    -- PS5 Sessions
    (51, 'PS5 Session - 1 Hour',        8.00,  'hour', 11),
    (52, 'PS5 Session - 2 Hours',       15.00, 'hour', 11),
    (53, 'PS5 Session - 3 Hours',       21.00, 'hour', 11),
    (54, 'PS5 Session - Full Day',      45.00, 'day',  11),
    -- PS4 Sessions
    (55, 'PS4 Session - 1 Hour',        5.00,  'hour', 12),
    (56, 'PS4 Session - 2 Hours',       9.00,  'hour', 12),
    (57, 'PS4 Session - 3 Hours',       12.00, 'hour', 12),
    (58, 'PS4 Session - Full Day',      28.00, 'day',  12),
    -- VR Experience
    (59, 'VR Experience - 30 Minutes',  12.00, 'session', 13),
    (60, 'VR Experience - 1 Hour',      20.00, 'hour',    13),
    -- Game Modes (add-on to any session)
    (61, 'Racing Mode (per hour)',       2.00,  'hour', 14),
    (62, 'Fighting Mode (per hour)',     2.00,  'hour', 14),
    (63, 'Sports Mode (per hour)',       2.00,  'hour', 14),
    (64, '2-Player Co-op (per hour)',    3.00,  'hour', 14),
    -- Accessories & Rentals
    (65, 'Gaming Headset Rental',        3.00,  'item', 15),
    (66, 'Extra Controller',             4.00,  'item', 15),
    (67, 'Controller Charging',          1.00,  'item', 15),
    (68, 'HDMI Cable Rental',            1.50,  'item', 15),
    -- Snacks & Drinks
    (69, 'Energy Drink',                 3.50,  'item', 16),
    (70, 'Cola (Can)',                   2.00,  'item', 16),
    (71, 'Water Bottle',                 1.50,  'item', 16),
    (72, 'Chips (Bag)',                  2.50,  'item', 16),
    (73, 'Nachos & Dip',                 4.00,  'item', 16),
    (74, 'Candy Mix',                    1.50,  'item', 16),
    (75, 'Popcorn',                      3.00,  'item', 16),
    (76, 'Snack Combo',                  7.50,  'item', 16);

-- 4. Replace employee types with gaming center roles
DELETE FROM employee_types WHERE id BETWEEN 1 AND 7;

INSERT OR IGNORE INTO employee_types (id, name, description) VALUES
    (8,  'Manager',         'Gaming center manager'),
    (9,  'Game Attendant',  'Assists customers, manages stations'),
    (10, 'Cashier',         'Handles billing and payments'),
    (11, 'Technician',      'Maintains hardware and software'),
    (12, 'Security',        'Venue security personnel');

-- 5. Replace old restaurant employees with gaming center staff
DELETE FROM employees WHERE id BETWEEN 1 AND 12;

INSERT OR IGNORE INTO employees (id, name, phone, email, employee_type_id, salary, joined_at) VALUES
    (13, 'Jordan Mitchell',  '+1-555-0101', 'jordan@levelupgaming.com',  8,  4500.00, '2024-01-10'),
    (14, 'Sam Rivera',       '+1-555-0102', 'sam@levelupgaming.com',     9,  2800.00, '2024-02-15'),
    (15, 'Alex Chen',        '+1-555-0103', 'alex@levelupgaming.com',    9,  2800.00, '2024-03-01'),
    (16, 'Morgan Lee',       '+1-555-0104', 'morgan@levelupgaming.com',  10, 3000.00, '2024-03-20'),
    (17, 'Casey Thompson',   '+1-555-0105', 'casey@levelupgaming.com',   11, 3500.00, '2024-04-05'),
    (18, 'Riley Nguyen',     '+1-555-0106', 'riley@levelupgaming.com',   9,  2800.00, '2024-05-10'),
    (19, 'Taylor Brooks',    '+1-555-0107', 'taylor@levelupgaming.com',  12, 2600.00, '2024-06-01');

-- 6. Remove old food-based delivery types; gaming center is walk-in only
DELETE FROM delivery_types WHERE id BETWEEN 1 AND 3;

INSERT OR IGNORE INTO delivery_types (id, name, description, fee_multiplier) VALUES
    (4, 'Walk-in',    'Customer visits the center',  1.0),
    (5, 'Pre-booked', 'Reserved session in advance', 1.0);

-- 7. Remove old food sales & sale_items
DELETE FROM sale_items WHERE sale_id BETWEEN 1 AND 12;
DELETE FROM sales WHERE id BETWEEN 1 AND 12;

-- 8. Gaming center sales records (all in USD, walk-in / pre-booked)
--    order_type reused as: 'dine_in' = walk-in, 'takeaway' = pre-booked
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, employee_id) VALUES
    -- Day 1 – July 10
    (13,  24.00, 'USD', '2026-07-10', '10:30:00', 'dine_in',  'completed', 14),
    (14,  35.50, 'USD', '2026-07-10', '12:00:00', 'dine_in',  'completed', 15),
    (15,  20.00, 'USD', '2026-07-10', '14:15:00', 'takeaway', 'completed', 16),
    (16,  46.00, 'USD', '2026-07-10', '17:00:00', 'dine_in',  'completed', 14),
    -- Day 2 – July 11
    (17,  18.00, 'USD', '2026-07-11', '11:00:00', 'dine_in',  'completed', 15),
    (18,  57.50, 'USD', '2026-07-11', '13:30:00', 'dine_in',  'completed', 14),
    (19,  32.00, 'USD', '2026-07-11', '16:00:00', 'takeaway', 'completed', 16),
    -- Day 3 – July 12
    (20,  15.50, 'USD', '2026-07-12', '10:00:00', 'dine_in',  'completed', 15),
    (21,  43.00, 'USD', '2026-07-12', '12:45:00', 'dine_in',  'completed', 14),
    (22,  26.50, 'USD', '2026-07-12', '15:30:00', 'dine_in',  'completed', 18),
    (23,  62.00, 'USD', '2026-07-12', '19:00:00', 'dine_in',  'completed', 15),
    -- Day 4 – July 13
    (24,  10.50, 'USD', '2026-07-13', '11:30:00', 'dine_in',  'completed', 18),
    (25,  38.00, 'USD', '2026-07-13', '14:00:00', 'takeaway', 'completed', 16),
    (26,  29.50, 'USD', '2026-07-13', '17:45:00', 'dine_in',  'completed', 14),
    -- Day 5 – July 14 (weekend peak)
    (27,  55.00, 'USD', '2026-07-14', '10:30:00', 'dine_in',  'completed', 14),
    (28,  72.00, 'USD', '2026-07-14', '12:00:00', 'dine_in',  'completed', 15),
    (29,  48.50, 'USD', '2026-07-14', '15:00:00', 'takeaway', 'completed', 16),
    (30,  85.50, 'USD', '2026-07-14', '18:30:00', 'dine_in',  'completed', 14),
    -- Day 6 – July 15
    (31,  21.00, 'USD', '2026-07-15', '11:00:00', 'dine_in',  'completed', 18),
    (32,  33.50, 'USD', '2026-07-15', '14:30:00', 'dine_in',  'completed', 15);

-- 9. Sale items — realistic gaming center line items
INSERT OR IGNORE INTO sale_items (sale_id, product_name, price, quantity, unit) VALUES
    -- Sale 13: 3hrs PS5 solo
    (13, 'PS5 Session - 3 Hours',        21.00, 1, 'hour'),
    (13, 'Energy Drink',                  3.00, 1, 'item'),

    -- Sale 14: 2hrs PS5 + headset + snacks
    (14, 'PS5 Session - 2 Hours',        15.00, 1, 'hour'),
    (14, 'Gaming Headset Rental',         3.00, 1, 'item'),
    (14, 'VR Experience - 30 Minutes',   12.00, 1, 'session'),
    (14, 'Cola (Can)',                    2.00, 1, 'item'),
    (14, 'Chips (Bag)',                   2.50, 1, 'item'),
    (14, 'Energy Drink',                  1.00, 1, 'item'),  -- discounted

    -- Sale 15: 4hrs PS4 (pre-booked = 4×5 but under full-day)
    (15, 'PS4 Session - 2 Hours',         9.00, 2, 'hour'),
    (15, 'Cola (Can)',                     2.00, 1, 'item'),

    -- Sale 16: Full-day PS5 + extras
    (16, 'PS5 Session - Full Day',        45.00, 1, 'day'),
    (16, 'Extra Controller',               4.00, 1, 'item'),
    (16, 'Popcorn',                        3.00, 1, 'item'),
    (16, 'Water Bottle',                   1.50, 2, 'item'),
    (16, 'Energy Drink',                   3.50, 1, 'item'),

    -- Sale 17: 1hr VR + racing mode
    (17, 'VR Experience - 1 Hour',        20.00, 1, 'hour'),
    (17, 'Cola (Can)',                      2.00, 1, 'item'),
    (17, 'Water Bottle',                    1.50, 1, 'item'),

    -- Sale 18: 3hrs PS5 2-player + fighting mode + snacks
    (18, 'PS5 Session - 3 Hours',         21.00, 1, 'hour'),
    (18, '2-Player Co-op (per hour)',       3.00, 3, 'hour'),
    (18, 'Fighting Mode (per hour)',        2.00, 2, 'hour'),
    (18, 'Extra Controller',               4.00, 1, 'item'),
    (18, 'Gaming Headset Rental',          3.00, 2, 'item'),
    (18, 'Nachos & Dip',                   4.00, 1, 'item'),
    (18, 'Energy Drink',                   3.50, 2, 'item'),
    (18, 'Cola (Can)',                      2.00, 2, 'item'),
    (18, 'Chips (Bag)',                     2.50, 2, 'item'),

    -- Sale 19: Pre-booked PS4 full day + controller
    (19, 'PS4 Session - Full Day',         28.00, 1, 'day'),
    (19, 'Controller Charging',             1.00, 1, 'item'),
    (19, 'Snack Combo',                     7.50, 1, 'item'),

    -- Sale 20: 1hr PS4 + water
    (20, 'PS4 Session - 1 Hour',            5.00, 1, 'hour'),
    (20, 'Sports Mode (per hour)',           2.00, 1, 'hour'),
    (20, 'Water Bottle',                     1.50, 1, 'item'),
    (20, 'Candy Mix',                        1.50, 1, 'item'),

    -- Sale 21: 2-player PS5 2hrs + sports mode
    (21, 'PS5 Session - 2 Hours',          15.00, 1, 'hour'),
    (21, '2-Player Co-op (per hour)',        3.00, 2, 'hour'),
    (21, 'Sports Mode (per hour)',           2.00, 2, 'hour'),
    (21, 'Extra Controller',                4.00, 1, 'item'),
    (21, 'Cola (Can)',                       2.00, 2, 'item'),
    (21, 'Popcorn',                          3.00, 1, 'item'),

    -- Sale 22: VR 30min + racing + chips
    (22, 'VR Experience - 30 Minutes',      12.00, 1, 'session'),
    (22, 'Racing Mode (per hour)',            2.00, 1, 'hour'),
    (22, 'Chips (Bag)',                       2.50, 1, 'item'),
    (22, 'Water Bottle',                      1.50, 2, 'item'),
    (22, 'Candy Mix',                         1.50, 1, 'item'),

    -- Sale 23: Big Friday night — PS5 full-day 2-player + full accessories + snacks
    (23, 'PS5 Session - Full Day',           45.00, 1, 'day'),
    (23, '2-Player Co-op (per hour)',          3.00, 4, 'hour'),
    (23, 'Fighting Mode (per hour)',           2.00, 2, 'hour'),
    (23, 'Gaming Headset Rental',             3.00, 2, 'item'),
    (23, 'Extra Controller',                  4.00, 1, 'item'),
    (23, 'HDMI Cable Rental',                 1.50, 1, 'item'),
    (23, 'Snack Combo',                        7.50, 1, 'item'),
    (23, 'Energy Drink',                       3.50, 2, 'item'),

    -- Sale 24: Quick 1hr PS4
    (24, 'PS4 Session - 1 Hour',              5.00, 1, 'hour'),
    (24, 'Cola (Can)',                         2.00, 1, 'item'),
    (24, 'Chips (Bag)',                        2.50, 1, 'item'),

    -- Sale 25: Pre-booked PS5 3hrs + racing
    (25, 'PS5 Session - 3 Hours',            21.00, 1, 'hour'),
    (25, 'Racing Mode (per hour)',             2.00, 3, 'hour'),
    (25, 'Gaming Headset Rental',             3.00, 1, 'item'),
    (25, 'Energy Drink',                       3.50, 1, 'item'),
    (25, 'Nachos & Dip',                       4.00, 1, 'item'),

    -- Sale 26: 2hrs PS5 + VR 30min
    (26, 'PS5 Session - 2 Hours',            15.00, 1, 'hour'),
    (26, 'VR Experience - 30 Minutes',        12.00, 1, 'session'),
    (26, 'Water Bottle',                        1.50, 1, 'item'),
    (26, 'Popcorn',                             3.00, 1, 'item'),

    -- Sale 27: Saturday morning — 3hrs PS5 + fighting
    (27, 'PS5 Session - 3 Hours',             21.00, 1, 'hour'),
    (27, '2-Player Co-op (per hour)',           3.00, 3, 'hour'),
    (27, 'Fighting Mode (per hour)',            2.00, 3, 'hour'),
    (27, 'Extra Controller',                   4.00, 2, 'item'),

    -- Sale 28: Sat afternoon group — full-day PS5 + PS4
    (28, 'PS5 Session - Full Day',             45.00, 1, 'day'),
    (28, 'PS4 Session - Full Day',             28.00, 1, 'day'),
    (28, 'Snack Combo',                         7.50, 1, 'item'),
    (28, 'Energy Drink',                        3.50, 2, 'item'),
    (28, 'Cola (Can)',                          2.00, 2, 'item'),

    -- Sale 29: Pre-booked VR session
    (29, 'VR Experience - 1 Hour',             20.00, 1, 'hour'),
    (29, 'Racing Mode (per hour)',              2.00, 1, 'hour'),
    (29, 'Gaming Headset Rental',              3.00, 1, 'item'),
    (29, 'Nachos & Dip',                        4.00, 1, 'item'),
    (29, 'Energy Drink',                        3.50, 2, 'item'),
    (29, 'Cola (Can)',                          2.00, 2, 'item'),
    (29, 'Candy Mix',                           1.50, 2, 'item'),

    -- Sale 30: Saturday peak — big group booking
    (30, 'PS5 Session - Full Day',             45.00, 1, 'day'),
    (30, '2-Player Co-op (per hour)',           3.00, 8, 'hour'),
    (30, 'Extra Controller',                   4.00, 2, 'item'),
    (30, 'Gaming Headset Rental',              3.00, 2, 'item'),
    (30, 'Snack Combo',                         7.50, 2, 'item'),
    (30, 'Energy Drink',                        3.50, 3, 'item'),
    (30, 'Cola (Can)',                          2.00, 3, 'item'),

    -- Sale 31: Quick Monday drop-in
    (31, 'PS5 Session - 1 Hour',               8.00, 1, 'hour'),
    (31, 'Sports Mode (per hour)',              2.00, 1, 'hour'),
    (31, 'Water Bottle',                        1.50, 1, 'item'),
    (31, 'Chips (Bag)',                         2.50, 1, 'item'),
    (31, 'Candy Mix',                           1.50, 1, 'item'),

    -- Sale 32: PS4 2hrs + accessories
    (32, 'PS4 Session - 2 Hours',               9.00, 1, 'hour'),
    (32, 'Controller Charging',                 1.00, 1, 'item'),
    (32, 'HDMI Cable Rental',                   1.50, 1, 'item'),
    (32, 'Popcorn',                              3.00, 1, 'item'),
    (32, 'Cola (Can)',                           2.00, 1, 'item'),
    (32, 'Energy Drink',                         3.50, 1, 'item'),
    (32, 'Chips (Bag)',                          2.50, 1, 'item'),
    (32, 'Candy Mix',                            1.50, 2, 'item');

-- 10. Clear old food-related seed data (recipes, ingredients etc. not relevant to gaming)
DELETE FROM recipe_ingredients WHERE recipe_id BETWEEN 1 AND 14;
DELETE FROM recipes WHERE id BETWEEN 1 AND 14;
DELETE FROM inventory_adjustments WHERE id BETWEEN 1 AND 2;
DELETE FROM inventory_transactions WHERE id BETWEEN 1 AND 31;
DELETE FROM ingredients WHERE id BETWEEN 1 AND 40;
-- Auto-generated product image UPDATEs for gaming center seed
-- Run AFTER the gaming center migration has been applied

UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMDA0MzljIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwZTFhMmIiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iIzAwNDM5YyIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn46uPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNmZmZmZmYiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+UFM1IDFocjwvdGV4dD4KPC9zdmc+' WHERE name = 'PS5 Session - 1 Hour';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMDA0MzljIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwZTFhMmIiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iIzAwNDM5YyIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn46uPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNmZmZmZmYiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+UFM1IDJocnM8L3RleHQ+Cjwvc3ZnPg==' WHERE name = 'PS5 Session - 2 Hours';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMDA0MzljIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwZTFhMmIiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iIzAwNDM5YyIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn46uPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNmZmZmZmYiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+UFM1IDNocnM8L3RleHQ+Cjwvc3ZnPg==' WHERE name = 'PS5 Session - 3 Hours';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMDA0MzljIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwZTFhMmIiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iIzAwNDM5YyIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn46uPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNmZmZmZmYiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+UFM1IEZ1bGwgRGF5PC90ZXh0Pgo8L3N2Zz4=' WHERE name = 'PS5 Session - Full Day';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMGYzNDYwIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMxYTFhMmUiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iIzBmMzQ2MCIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn5W577iPPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNlMGUwZTAiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+UFM0IDFocjwvdGV4dD4KPC9zdmc+' WHERE name = 'PS4 Session - 1 Hour';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMGYzNDYwIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMxYTFhMmUiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iIzBmMzQ2MCIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn5W577iPPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNlMGUwZTAiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+UFM0IDJocnM8L3RleHQ+Cjwvc3ZnPg==' WHERE name = 'PS4 Session - 2 Hours';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMGYzNDYwIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMxYTFhMmUiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iIzBmMzQ2MCIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn5W577iPPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNlMGUwZTAiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+UFM0IDNocnM8L3RleHQ+Cjwvc3ZnPg==' WHERE name = 'PS4 Session - 3 Hours';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMGYzNDYwIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMxYTFhMmUiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iIzBmMzQ2MCIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn5W577iPPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNlMGUwZTAiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+UFM0IEZ1bGwgRGF5PC90ZXh0Pgo8L3N2Zz4=' WHERE name = 'PS4 Session - Full Day';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjN2MzYWVkIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwZjE3MmEiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iIzdjM2FlZCIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn6W9PC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNmNWYzZmYiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+VlIgMzBtaW48L3RleHQ+Cjwvc3ZnPg==' WHERE name = 'VR Experience - 30 Minutes';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjN2MzYWVkIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwZjE3MmEiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iIzdjM2FlZCIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn6W9PC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNmNWYzZmYiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+VlIgMWhyPC90ZXh0Pgo8L3N2Zz4=' WHERE name = 'VR Experience - 1 Hour';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjZGMyNjI2IiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMxYzE5MTciLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iI2RjMjYyNiIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn4+O77iPPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNmZWYyZjIiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+UmFjaW5nPC90ZXh0Pgo8L3N2Zz4=' WHERE name = 'Racing Mode (per hour)';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjN2UyMmNlIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMxZTFiNGIiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iIzdlMjJjZSIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn5GKPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNlZGU5ZmUiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+RmlnaHRpbmc8L3RleHQ+Cjwvc3ZnPg==' WHERE name = 'Fighting Mode (per hour)';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMTZhMzRhIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwNTJlMTYiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iIzE2YTM0YSIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7imr08L3RleHQ+Cgo8dGV4dCB4PSIxMDAiIHk9IjE2MiIgZm9udC1zaXplPSIxNCIgZm9udC13ZWlnaHQ9IjYwMCIKICAgICAgZmlsbD0iI2RjZmNlNyIgb3BhY2l0eT0iMC44NSIgdGV4dC1hbmNob3I9Im1pZGRsZSIKICAgICAgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj5TcG9ydHM8L3RleHQ+Cjwvc3ZnPg==' WHERE name = 'Sports Mode (per hour)';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMDg5MWIyIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMxZTNhNWYiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iIzA4OTFiMiIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn5G+PC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNlMGY3ZmEiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+Mi1QbGF5ZXI8L3RleHQ+Cjwvc3ZnPg==' WHERE name = '2-Player Co-op (per hour)';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjZDk3NzA2IiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMxYzE5MTciLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iI2Q5NzcwNiIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn46nPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNmZWYzYzciIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+SGVhZHNldDwvdGV4dD4KPC9zdmc+' WHERE name = 'Gaming Headset Rental';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMzc0MTUxIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMxMTE4MjciLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iIzM3NDE1MSIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn46uPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNmOWZhZmIiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+Q29udHJvbGxlcjwvdGV4dD4KPC9zdmc+' WHERE name = 'Extra Controller';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjM2I4MmY2IiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwYzE0NDUiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iIzNiODJmNiIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn5SLPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNkYmVhZmUiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+Q2hhcmdpbmc8L3RleHQ+Cjwvc3ZnPg==' WHERE name = 'Controller Charging';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjNmI3MjgwIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMxYTFhMWEiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iIzZiNzI4MCIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn5SMPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNmM2Y0ZjYiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+SERNSSBDYWJsZTwvdGV4dD4KPC9zdmc+' WHERE name = 'HDMI Cable Rental';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjZGMyNjI2IiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMxYzE5MTciLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iI2RjMjYyNiIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7imqE8L3RleHQ+Cgo8dGV4dCB4PSIxMDAiIHk9IjE2MiIgZm9udC1zaXplPSIxNCIgZm9udC13ZWlnaHQ9IjYwMCIKICAgICAgZmlsbD0iI2ZlZjJmMiIgb3BhY2l0eT0iMC44NSIgdGV4dC1hbmNob3I9Im1pZGRsZSIKICAgICAgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj5FbmVyZ3kgRHJpbms8L3RleHQ+Cjwvc3ZnPg==' WHERE name = 'Energy Drink';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjYjkxYzFjIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwYzBjMGMiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iI2I5MWMxYyIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn6WkPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNmZWNhY2EiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+Q29sYTwvdGV4dD4KPC9zdmc+' WHERE name = 'Cola (Can)';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMDI4NGM3IiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiNlMGY3ZmEiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iIzAyODRjNyIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn5KnPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNmZmZmZmYiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+V2F0ZXI8L3RleHQ+Cjwvc3ZnPg==' WHERE name = 'Water Bottle';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjZDk3NzA2IiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiM3ODM1MGYiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iI2Q5NzcwNiIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn42fPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNmZWYzYzciIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+Q2hpcHM8L3RleHQ+Cjwvc3ZnPg==' WHERE name = 'Chips (Bag)';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjZWE1ODBjIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiM3YzJkMTIiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iI2VhNTgwYyIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn4yuPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNmZmVkZDUiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+TmFjaG9zPC90ZXh0Pgo8L3N2Zz4=' WHERE name = 'Nachos & Dip';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjYTIxY2FmIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiM0YTA0NGUiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iI2EyMWNhZiIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn42sPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNmYWU4ZmYiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+Q2FuZHkgTWl4PC90ZXh0Pgo8L3N2Zz4=' WHERE name = 'Candy Mix';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjY2E4YTA0IiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiM3MTNmMTIiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iI2NhOGEwNCIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn42/PC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNmZWZjZTgiIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+UG9wY29ybjwvdGV4dD4KPC9zdmc+' WHERE name = 'Popcorn';
UPDATE products SET image = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNDAlIiByPSI2MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMTU4MDNkIiBzdG9wLW9wYWNpdHk9IjAuNCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMxNDUzMmQiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJnbG93Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMyIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgcng9IjIwIiBmaWxsPSJ1cmwoI2JnKSIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg1IiByPSI1MiIgZmlsbD0iIzE1ODAzZCIgb3BhY2l0eT0iMC4xNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiBmb250LXNpemU9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWx0ZXI9InVybCgjZ2xvdykiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn46BPC90ZXh0PgoKPHRleHQgeD0iMTAwIiB5PSIxNjIiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiCiAgICAgIGZpbGw9IiNkY2ZjZTciIG9wYWNpdHk9IjAuODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiI+U25hY2sgQ29tYm88L3RleHQ+Cjwvc3ZnPg==' WHERE name = 'Snack Combo';

-- Settings logo
UPDATE settings SET logo = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNTYiIGhlaWdodD0iMjU2IiB2aWV3Qm94PSIwIDAgMjU2IDI1NiI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNTAlIiByPSI1MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMWUzYTVmIi8+CiAgICAgIDxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iIzBhMGYxZSIvPgogICAgPC9yYWRpYWxHcmFkaWVudD4KICAgIDxsaW5lYXJHcmFkaWVudCBpZD0iZ3JkIiB4MT0iMCUiIHkxPSIwJSIgeDI9IjEwMCUiIHkyPSIxMDAlIj4KICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzAwYjRkOCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwMDc3YjYiLz4KICAgIDwvbGluZWFyR3JhZGllbnQ+CiAgPC9kZWZzPgogIDxyZWN0IHdpZHRoPSIyNTYiIGhlaWdodD0iMjU2IiByeD0iNDgiIGZpbGw9InVybCgjYmcpIi8+CiAgPGNpcmNsZSBjeD0iMTI4IiBjeT0iMTI4IiByPSI5MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ1cmwoI2dyZCkiIHN0cm9rZS13aWR0aD0iNiIgb3BhY2l0eT0iMC42Ii8+CiAgPHRleHQgeD0iMTI4IiB5PSIxNTgiIGZvbnQtc2l6ZT0iOTAiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn46uPC90ZXh0PgogIDx0ZXh0IHg9IjEyOCIgeT0iMjIwIiBmb250LXNpemU9IjIyIiBmb250LXdlaWdodD0iNzAwIiBmaWxsPSIjMDBiNGQ4IgogICAgICAgIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiIgbGV0dGVyLXNwYWNpbmc9IjMiPlBPUy1LTzwvdGV4dD4KPC9zdmc+' WHERE id = 1;

-- Done
