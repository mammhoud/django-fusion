-- =============================================================================
-- Gaming Center Seed — preset data for gaming/arcade demo
-- =============================================================================
-- All INSERTs use OR IGNORE so this migration is safe to re-run.
-- Corresponding down.sql deletes the exact IDs this migration inserts.
-- =============================================================================

-- 1. Settings — rebrand as gaming center
UPDATE settings SET
    restaurant_name  = 'Level Up Gaming Center',
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

-- 2. Gaming categories
INSERT OR IGNORE INTO categories (id, name) VALUES
    (11, 'PS5 Sessions'),
    (12, 'PS4 Sessions'),
    (13, 'VR Experience'),
    (14, 'Game Modes'),
    (15, 'Accessories & Rentals'),
    (16, 'Snacks & Drinks');

-- 3. Gaming center products (all in USD, timed sessions)
INSERT OR IGNORE INTO products (id, name, price, unit, category_id) VALUES
    (51, 'PS5 Session - 1 Hour',        8.00,  'hour', 11),
    (52, 'PS5 Session - 2 Hours',       15.00, 'hour', 11),
    (53, 'PS5 Session - 3 Hours',       21.00, 'hour', 11),
    (54, 'PS5 Session - Full Day',      45.00, 'day',  11),
    (55, 'PS4 Session - 1 Hour',        5.00,  'hour', 12),
    (56, 'PS4 Session - 2 Hours',       9.00,  'hour', 12),
    (57, 'PS4 Session - 3 Hours',       12.00, 'hour', 12),
    (58, 'PS4 Session - Full Day',      28.00, 'day',  12),
    (59, 'VR Experience - 30 Minutes',  12.00, 'session', 13),
    (60, 'VR Experience - 1 Hour',      20.00, 'hour',    13),
    (61, 'Racing Mode (per hour)',       2.00,  'hour', 14),
    (62, 'Fighting Mode (per hour)',     2.00,  'hour', 14),
    (63, 'Sports Mode (per hour)',       2.00,  'hour', 14),
    (64, '2-Player Co-op (per hour)',    3.00,  'hour', 14),
    (65, 'Gaming Headset Rental',        3.00,  'item', 15),
    (66, 'Extra Controller',             4.00,  'item', 15),
    (67, 'Controller Charging',          1.00,  'item', 15),
    (68, 'HDMI Cable Rental',            1.50,  'item', 15),
    (69, 'Energy Drink',                 3.50,  'item', 16),
    (70, 'Cola (Can)',                   2.00,  'item', 16),
    (71, 'Water Bottle',                 1.50,  'item', 16),
    (72, 'Chips (Bag)',                  2.50,  'item', 16),
    (73, 'Nachos & Dip',                 4.00,  'item', 16),
    (74, 'Candy Mix',                    1.50,  'item', 16),
    (75, 'Popcorn',                      3.00,  'item', 16),
    (76, 'Snack Combo',                  7.50,  'item', 16);

-- 4. Gaming employee types
INSERT OR IGNORE INTO employee_types (id, name, description) VALUES
    (8,  'Manager',         'Gaming center manager'),
    (9,  'Game Attendant',  'Assists customers, manages stations'),
    (10, 'Cashier',         'Handles billing and payments'),
    (11, 'Technician',      'Maintains hardware and software'),
    (12, 'Security',        'Venue security personnel');

-- 5. Gaming employees
INSERT OR IGNORE INTO employees (id, name, phone, email, employee_type_id, salary, joined_at) VALUES
    (13, 'Jordan Mitchell',  '+1-555-0101', 'jordan@levelupgaming.com',  8,  4500.00, '2024-01-10'),
    (14, 'Sam Rivera',       '+1-555-0102', 'sam@levelupgaming.com',     9,  2800.00, '2024-02-15'),
    (15, 'Alex Chen',        '+1-555-0103', 'alex@levelupgaming.com',    9,  2800.00, '2024-03-01'),
    (16, 'Morgan Lee',       '+1-555-0104', 'morgan@levelupgaming.com',  10, 3000.00, '2024-03-20'),
    (17, 'Casey Thompson',   '+1-555-0105', 'casey@levelupgaming.com',   11, 3500.00, '2024-04-05'),
    (18, 'Riley Nguyen',     '+1-555-0106', 'riley@levelupgaming.com',   9,  2800.00, '2024-05-10'),
    (19, 'Taylor Brooks',    '+1-555-0107', 'taylor@levelupgaming.com',  12, 2600.00, '2024-06-01');

-- 6. Gaming delivery types (walk-in only)
INSERT OR IGNORE INTO delivery_types (id, name, description, fee_multiplier) VALUES
    (4, 'Walk-in',    'Customer visits the center',  1.0),
    (5, 'Pre-booked', 'Reserved session in advance', 1.0);

-- 7. Gaming sales (20 transactions, all in USD)
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, employee_id) VALUES
    (13,  24.00, 'USD', '2026-07-10', '10:30:00', 'dine_in',  'completed', 14),
    (14,  35.50, 'USD', '2026-07-10', '12:00:00', 'dine_in',  'completed', 15),
    (15,  20.00, 'USD', '2026-07-10', '14:15:00', 'takeaway', 'completed', 16),
    (16,  46.00, 'USD', '2026-07-10', '17:00:00', 'dine_in',  'completed', 14),
    (17,  18.00, 'USD', '2026-07-11', '11:00:00', 'dine_in',  'completed', 15),
    (18,  57.50, 'USD', '2026-07-11', '13:30:00', 'dine_in',  'completed', 14),
    (19,  32.00, 'USD', '2026-07-11', '16:00:00', 'takeaway', 'completed', 16),
    (20,  15.50, 'USD', '2026-07-12', '10:00:00', 'dine_in',  'completed', 15),
    (21,  43.00, 'USD', '2026-07-12', '12:45:00', 'dine_in',  'completed', 14),
    (22,  26.50, 'USD', '2026-07-12', '15:30:00', 'dine_in',  'completed', 18),
    (23,  62.00, 'USD', '2026-07-12', '19:00:00', 'dine_in',  'completed', 15),
    (24,  10.50, 'USD', '2026-07-13', '11:30:00', 'dine_in',  'completed', 18),
    (25,  38.00, 'USD', '2026-07-13', '14:00:00', 'takeaway', 'completed', 16),
    (26,  29.50, 'USD', '2026-07-13', '17:45:00', 'dine_in',  'completed', 14),
    (27,  55.00, 'USD', '2026-07-14', '10:30:00', 'dine_in',  'completed', 14),
    (28,  72.00, 'USD', '2026-07-14', '12:00:00', 'dine_in',  'completed', 15),
    (29,  48.50, 'USD', '2026-07-14', '15:00:00', 'takeaway', 'completed', 16),
    (30,  85.50, 'USD', '2026-07-14', '18:30:00', 'dine_in',  'completed', 14),
    (31,  21.00, 'USD', '2026-07-15', '11:00:00', 'dine_in',  'completed', 18),
    (32,  33.50, 'USD', '2026-07-15', '14:30:00', 'dine_in',  'completed', 15);

-- 8. Gaming sale items
INSERT OR IGNORE INTO sale_items (sale_id, product_name, price, quantity, unit) VALUES
    (13, 'PS5 Session - 3 Hours',        21.00, 1, 'hour'),
    (13, 'Energy Drink',                  3.50, 1, 'item'),
    (14, 'PS5 Session - 2 Hours',        15.00, 1, 'hour'),
    (14, 'Gaming Headset Rental',         3.00, 1, 'item'),
    (14, 'VR Experience - 30 Minutes',   12.00, 1, 'session'),
    (14, 'Cola (Can)',                    2.00, 1, 'item'),
    (14, 'Chips (Bag)',                   2.50, 1, 'item'),
    (15, 'PS4 Session - 2 Hours',         9.00, 2, 'hour'),
    (15, 'Cola (Can)',                    2.00, 1, 'item'),
    (16, 'PS5 Session - Full Day',       45.00, 1, 'day'),
    (16, 'Extra Controller',              4.00, 1, 'item'),
    (16, 'Popcorn',                       3.00, 1, 'item'),
    (16, 'Water Bottle',                  1.50, 2, 'item'),
    (16, 'Energy Drink',                  3.50, 1, 'item'),
    (17, 'VR Experience - 1 Hour',       20.00, 1, 'hour'),
    (17, 'Cola (Can)',                    2.00, 1, 'item'),
    (17, 'Water Bottle',                  1.50, 1, 'item'),
    (18, 'PS5 Session - 3 Hours',        21.00, 1, 'hour'),
    (18, '2-Player Co-op (per hour)',      3.00, 3, 'hour'),
    (18, 'Fighting Mode (per hour)',       2.00, 2, 'hour'),
    (18, 'Extra Controller',              4.00, 1, 'item'),
    (18, 'Gaming Headset Rental',         3.00, 2, 'item'),
    (18, 'Nachos & Dip',                  4.00, 1, 'item'),
    (18, 'Energy Drink',                  3.50, 2, 'item'),
    (18, 'Cola (Can)',                    2.00, 2, 'item'),
    (18, 'Chips (Bag)',                   2.50, 2, 'item'),
    (19, 'PS4 Session - Full Day',        28.00, 1, 'day'),
    (19, 'Controller Charging',            1.00, 1, 'item'),
    (19, 'Snack Combo',                    7.50, 1, 'item'),
    (20, 'PS4 Session - 1 Hour',           5.00, 1, 'hour'),
    (20, 'Sports Mode (per hour)',          2.00, 1, 'hour'),
    (20, 'Water Bottle',                    1.50, 1, 'item'),
    (20, 'Candy Mix',                       1.50, 1, 'item'),
    (21, 'PS5 Session - 2 Hours',         15.00, 1, 'hour'),
    (21, '2-Player Co-op (per hour)',       3.00, 2, 'hour'),
    (21, 'Sports Mode (per hour)',          2.00, 2, 'hour'),
    (21, 'Extra Controller',               4.00, 1, 'item'),
    (21, 'Cola (Can)',                      2.00, 2, 'item'),
    (21, 'Popcorn',                         3.00, 1, 'item'),
    (22, 'VR Experience - 30 Minutes',     12.00, 1, 'session'),
    (22, 'Racing Mode (per hour)',           2.00, 1, 'hour'),
    (22, 'Chips (Bag)',                      2.50, 1, 'item'),
    (22, 'Water Bottle',                     1.50, 2, 'item'),
    (22, 'Candy Mix',                        1.50, 1, 'item'),
    (23, 'PS5 Session - Full Day',          45.00, 1, 'day'),
    (23, '2-Player Co-op (per hour)',         3.00, 4, 'hour'),
    (23, 'Fighting Mode (per hour)',          2.00, 2, 'hour'),
    (23, 'Gaming Headset Rental',            3.00, 2, 'item'),
    (23, 'Extra Controller',                 4.00, 1, 'item'),
    (23, 'HDMI Cable Rental',                1.50, 1, 'item'),
    (23, 'Snack Combo',                       7.50, 1, 'item'),
    (23, 'Energy Drink',                      3.50, 2, 'item'),
    (24, 'PS4 Session - 1 Hour',             5.00, 1, 'hour'),
    (24, 'Cola (Can)',                        2.00, 1, 'item'),
    (24, 'Chips (Bag)',                       2.50, 1, 'item'),
    (25, 'PS5 Session - 3 Hours',           21.00, 1, 'hour'),
    (25, 'Racing Mode (per hour)',            2.00, 3, 'hour'),
    (25, 'Gaming Headset Rental',            3.00, 1, 'item'),
    (25, 'Energy Drink',                      3.50, 1, 'item'),
    (25, 'Nachos & Dip',                      4.00, 1, 'item'),
    (26, 'PS5 Session - 2 Hours',           15.00, 1, 'hour'),
    (26, 'VR Experience - 30 Minutes',       12.00, 1, 'session'),
    (26, 'Water Bottle',                       1.50, 1, 'item'),
    (26, 'Popcorn',                            3.00, 1, 'item'),
    (27, 'PS5 Session - 3 Hours',            21.00, 1, 'hour'),
    (27, '2-Player Co-op (per hour)',          3.00, 3, 'hour'),
    (27, 'Fighting Mode (per hour)',           2.00, 3, 'hour'),
    (27, 'Extra Controller',                  4.00, 2, 'item'),
    (28, 'PS5 Session - Full Day',            45.00, 1, 'day'),
    (28, 'PS4 Session - Full Day',            28.00, 1, 'day'),
    (28, 'Snack Combo',                        7.50, 1, 'item'),
    (28, 'Energy Drink',                       3.50, 2, 'item'),
    (28, 'Cola (Can)',                         2.00, 2, 'item'),
    (29, 'VR Experience - 1 Hour',            20.00, 1, 'hour'),
    (29, 'Racing Mode (per hour)',             2.00, 1, 'hour'),
    (29, 'Gaming Headset Rental',             3.00, 1, 'item'),
    (29, 'Nachos & Dip',                       4.00, 1, 'item'),
    (29, 'Energy Drink',                       3.50, 2, 'item'),
    (29, 'Cola (Can)',                         2.00, 2, 'item'),
    (29, 'Candy Mix',                          1.50, 2, 'item'),
    (30, 'PS5 Session - Full Day',            45.00, 1, 'day'),
    (30, '2-Player Co-op (per hour)',          3.00, 8, 'hour'),
    (30, 'Extra Controller',                  4.00, 2, 'item'),
    (30, 'Gaming Headset Rental',             3.00, 2, 'item'),
    (30, 'Snack Combo',                        7.50, 2, 'item'),
    (30, 'Energy Drink',                       3.50, 3, 'item'),
    (30, 'Cola (Can)',                         2.00, 3, 'item'),
    (31, 'PS5 Session - 1 Hour',              8.00, 1, 'hour'),
    (31, 'Sports Mode (per hour)',             2.00, 1, 'hour'),
    (31, 'Water Bottle',                       1.50, 1, 'item'),
    (31, 'Chips (Bag)',                        2.50, 1, 'item'),
    (31, 'Candy Mix',                          1.50, 1, 'item'),
    (32, 'PS4 Session - 2 Hours',              9.00, 1, 'hour'),
    (32, 'Controller Charging',                1.00, 1, 'item'),
    (32, 'HDMI Cable Rental',                  1.50, 1, 'item'),
    (32, 'Popcorn',                             3.00, 1, 'item'),
    (32, 'Cola (Can)',                          2.00, 1, 'item'),
    (32, 'Energy Drink',                        3.50, 1, 'item'),
    (32, 'Chips (Bag)',                         2.50, 1, 'item'),
    (32, 'Candy Mix',                           1.50, 2, 'item');

-- 9. Gaming employee schedules (one per employee)
INSERT OR IGNORE INTO employee_schedules (id, employee_id, shift_start, shift_end, status, notes) VALUES
    (13, 13, '2026-07-14 10:00:00', '2026-07-14 18:00:00', 'scheduled', 'Manager morning shift'),
    (14, 14, '2026-07-14 10:00:00', '2026-07-14 18:00:00', 'scheduled', 'Attendant AM'),
    (15, 15, '2026-07-14 14:00:00', '2026-07-14 22:00:00', 'scheduled', 'Attendant PM'),
    (16, 16, '2026-07-14 10:00:00', '2026-07-14 18:00:00', 'scheduled', 'Cashier AM'),
    (17, 17, '2026-07-14 14:00:00', '2026-07-14 22:00:00', 'scheduled', 'Technician PM'),
    (18, 18, '2026-07-14 14:00:00', '2026-07-14 22:00:00', 'scheduled', 'Attendant PM'),
    (19, 19, '2026-07-14 18:00:00', '2026-07-15 02:00:00', 'scheduled', 'Security night shift');

-- 10. Gaming payrolls (bi-weekly, USD)
INSERT OR IGNORE INTO payrolls (id, employee_id, period_start, period_end, regular_hours, overtime_hours, total_pay, status) VALUES
    (9,  13, '2026-07-01', '2026-07-14', 80, 4, 2250.00, 'paid'),
    (10, 14, '2026-07-01', '2026-07-14', 80, 2, 1400.00, 'paid'),
    (11, 15, '2026-07-01', '2026-07-14', 80, 3, 1400.00, 'paid'),
    (12, 16, '2026-07-01', '2026-07-14', 80, 0, 1500.00, 'paid'),
    (13, 17, '2026-07-01', '2026-07-14', 80, 6, 1750.00, 'paid'),
    (14, 18, '2026-07-01', '2026-07-14', 80, 1, 1400.00, 'paid'),
    (15, 19, '2026-07-01', '2026-07-14', 80, 0, 1300.00, 'paid');

-- 11. Gaming center logo
UPDATE settings SET logo = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNTYiIGhlaWdodD0iMjU2IiB2aWV3Qm94PSIwIDAgMjU2IDI1NiI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNTAlIiByPSI1MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMWUzYTVmIi8+CiAgICAgIDxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iIzBhMGYxZSIvPgogICAgPC9yYWRpYWxHcmFkaWVudD4KICAgIDxsaW5lYXJHcmFkaWVudCBpZD0iZ3JkIiB4MT0iMCUiIHkxPSIwJSIgeDI9IjEwMCUiIHkyPSIxMDAlIj4KICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzAwYjRkOCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwMDc3YjYiLz4KICAgIDwvbGluZWFyR3JhZGllbnQ+CiAgPC9kZWZzPgogIDxyZWN0IHdpZHRoPSIyNTYiIGhlaWdodD0iMjU2IiByeD0iNDgiIGZpbGw9InVybCgjYmcpIi8+CiAgPGNpcmNsZSBjeD0iMTI4IiBjeT0iMTI4IiByPSI5MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ1cmwoI2dyZCkiIHN0cm9rZS13aWR0aD0iNiIgb3BhY2l0eT0iMC42Ii8+CiAgPHRleHQgeD0iMTI4IiB5PSIxNTgiIGZvbnQtc2l6ZT0iOTAiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn46uPC90ZXh0PgogIDx0ZXh0IHg9IjEyOCIgeT0iMjIwIiBmb250LXNpemU9IjIyIiBmb250LXdlaWdodD0iNzAwIiBmaWxsPSIjMDBiNGQ4IgogICAgICAgIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiIgbGV0dGVyLXNwYWNpbmc9IjMiPkxldmVsIFVwIEdDPC90ZXh0Pgo8L3N2Zz4=' WHERE id = 1;
