-- ============================================================
-- SEED DATA for POS
-- ============================================================
-- Run this AFTER migrations to populate the database with
-- realistic sample data for development and testing.
-- 
-- Usage: sqlite3 /path/to/restaurant.db < seed.sql
-- ============================================================

-- ============================================================
-- 1. UPDATE SETTINGS with realistic data
-- ============================================================
UPDATE settings SET
    restaurant_name = 'Forge',
    address = '123 Main Boulevard, Gulberg, Lahore',
    phone = '+92-300-1234567',
    email = 'forge@structa.cloud',
    tax_rate = '13',
    opening_time = '09:00',
    closing_time = '23:00',
    receipt_footer = 'Thank you for dining with us! Follow us @pos_app',
    dine_in_tables = 15,
    delivery_fee = 50.0,
    delivery_fee_per_km = 15.0
WHERE id = 1;

-- ============================================================
-- 2. CATEGORIES
-- ============================================================
INSERT OR IGNORE INTO categories (id, name) VALUES
    (1, 'Burgers & Sandwiches'),
    (2, 'Pizza'),
    (3, 'BBQ & Grills'),
    (4, 'Rice & Biryani'),
    (5, 'Karahi & Curries'),
    (6, 'Fast Food & Snacks'),
    (7, 'Beverages'),
    (8, 'Desserts'),
    (9, 'Chinese'),
    (10, 'Breakfast');

-- ============================================================
-- 3. PRODUCTS (Menu Items)
-- ============================================================
INSERT OR IGNORE INTO products (id, name, price, unit, category_id) VALUES
    -- Burgers & Sandwiches (category 1)
    (1,  'Chicken Burger',             350.00, 'item', 1),
    (2,  'Beef Burger',                400.00, 'item', 1),
    (3,  'Zinger Burger',             450.00,  'item', 1),
    (4,  'Club Sandwich',              350.00, 'item', 1),
    (5,  'Paratha Roll',               250.00, 'item', 1),
    -- Pizza (category 2)
    (6,  'Chicken Pizza (Medium)',     800.00,  'item', 2),
    (7,  'Chicken Pizza (Large)',      1200.00, 'item', 2),
    (8,  'Fajita Pizza (Medium)',      900.00,  'item', 2),
    (9,  'Fajita Pizza (Large)',       1300.00, 'item', 2),
    -- BBQ & Grills (category 3)
    (10, 'Chicken Tikka (4 pcs)',      450.00,  'plate', 3),
    (11, 'Beef Seekh Kebab (6 pcs)',   350.00,  'plate', 3),
    (12, 'Chargah (Full)',             1200.00, 'item',  3),
    (13, 'Mutton Tikka (4 pcs)',       600.00,  'plate', 3),
    -- Rice & Biryani (category 4)
    (14, 'Chicken Biryani',            250.00,  'plate', 4),
    (15, 'Mutton Biryani',             350.00,  'plate', 4),
    (16, 'Vegetable Biryani',          200.00,  'plate', 4),
    (17, 'Chicken Fried Rice',         300.00,  'plate', 4),
    -- Karahi & Curries (category 5)
    (18, 'Chicken Karahi (Half)',      900.00,  'item',  5),
    (19, 'Chicken Karahi (Full)',      1600.00, 'item',  5),
    (20, 'Mutton Karahi (Half)',       1200.00, 'item',  5),
    (21, 'Mutton Karahi (Full)',       2200.00, 'item',  5),
    (22, 'Daal Makhni',                250.00,  'plate', 5),
    -- Fast Food & Snacks (category 6)
    (23, 'French Fries',               200.00,  'plate', 6),
    (24, 'Chicken Nuggets (6 pcs)',    300.00,  'plate', 6),
    (25, 'Chicken Wings (6 pcs)',      350.00,  'plate', 6),
    (26, 'Spring Rolls (6 pcs)',       250.00,  'plate', 6),
    (27, 'Chicken Soup',               250.00,  'bowl',  6),
    -- Beverages (category 7)
    (28, 'Soft Drink (500ml)',         80.00,   'bottle', 7),
    (29, 'Mineral Water (1.5L)',       60.00,   'bottle', 7),
    (30, 'Tea',                        80.00,   'cup',    7),
    (31, 'Coffee',                     150.00,  'cup',    7),
    (32, 'Milkshake',                  250.00,  'glass',  7),
    (33, 'Fruit Juice',                200.00,  'glass',  7),
    (34, 'Lassi',                      120.00,  'glass',  7),
    -- Desserts (category 8)
    (35, 'Gulab Jamun (4 pcs)',        150.00,  'plate',  8),
    (36, 'Ice Cream',                  120.00,  'scoop',  8),
    (37, 'Kheer',                      150.00,  'bowl',   8),
    (38, 'Brownie with Ice Cream',     350.00,  'item',   8),
    -- Chinese (category 9)
    (39, 'Chicken Manchurian',         350.00,  'plate',  9),
    (40, 'Veg Noodles',                250.00,  'plate',  9),
    (41, 'Chicken Noodles',            300.00,  'plate',  9),
    (42, 'Kung Pao Chicken',           400.00,  'plate',  9),
    -- Breakfast (category 10)
    (43, 'Halwa Puri (2 puri)',        180.00,  'plate',  10),
    (44, 'Chana Cholay',               200.00,  'plate',  10),
    (45, 'Omelette',                   150.00,  'plate',  10),
    (46, 'Nihari',                     300.00,  'bowl',   10),
    (47, 'Siri Paye',                  350.00,  'bowl',   10);

-- ============================================================
-- 4. INGREDIENTS
-- ============================================================
INSERT OR IGNORE INTO ingredients (id, name, unit, current_quantity, reorder_level, reorder_quantity, cost_per_unit) VALUES
    (1,  'Chicken Breast',         'kg',   25.0,   10.0,   20.0,  450.00),
    (2,  'Beef Mince',             'kg',   15.0,   8.0,    15.0,  550.00),
    (3,  'Mutton',                 'kg',   8.0,    5.0,    10.0,  1100.00),
    (4,  'Basmati Rice',           'kg',   20.0,   10.0,   20.0,  180.00),
    (5,  'Wheat Flour',            'kg',   30.0,   15.0,   20.0,  70.00),
    (6,  'Cooking Oil',            'liter', 25.0,  10.0,   20.0,  320.00),
    (7,  'Tomato',                 'kg',   15.0,   8.0,    12.0,  90.00),
    (8,  'Onion',                  'kg',   20.0,   10.0,   15.0,  70.00),
    (9,  'Yogurt',                 'kg',   12.0,   5.0,    10.0,  130.00),
    (10, 'Mozzarella Cheese',      'kg',   8.0,    4.0,    8.0,   750.00),
    (11, 'Pizza Sauce',            'kg',   5.0,    3.0,    5.0,   380.00),
    (12, 'Frozen French Fries',    'kg',   12.0,   5.0,    10.0,  220.00),
    (13, 'Frozen Chicken Nuggets', 'kg',   8.0,    4.0,    6.0,   550.00),
    (14, 'Soda Cans (Crate)',      'crate', 15.0,  5.0,    10.0,  480.00),
    (15, 'Water Bottles (Case)',   'case', 20.0,   8.0,    12.0,  360.00),
    (16, 'Sugar',                  'kg',   15.0,   5.0,    10.0,  110.00),
    (17, 'Milk',                   'liter', 18.0,  8.0,    12.0,  180.00),
    (18, 'Cream',                  'liter', 5.0,   3.0,    5.0,   330.00),
    (19, 'Vanilla Ice Cream',      'kg',   6.0,    3.0,    5.0,   450.00),
    (20, 'Spices Mix (Garam Masala)', 'kg', 3.0,   2.0,    3.0,   240.00),
    (21, 'Eggs',                   'dozen', 12.0,  5.0,    10.0,  220.00),
    (22, 'Potato',                 'kg',   20.0,   10.0,   15.0,  50.00),
    (23, 'Cabbage',                'kg',   5.0,    3.0,    5.0,   45.00),
    (24, 'Capsicum',               'kg',   6.0,    3.0,    5.0,   110.00),
    (25, 'Ginger Garlic Paste',    'kg',   4.0,    2.0,    3.0,   280.00),
    (26, 'Green Chilies',          'kg',   3.0,    1.5,    2.5,   130.00),
    (27, 'Salt',                   'kg',   8.0,    3.0,    5.0,   25.00),
    (28, 'Tea Leaves',             'kg',   2.0,    1.0,    2.0,   550.00),
    (29, 'Coffee Beans',           'kg',   1.5,    0.5,    1.5,   1100.00),
    (30, 'Pizza Dough Flour',      'kg',   10.0,   5.0,    10.0,  90.00),
    (31, 'Ketchup',                'kg',   5.0,    2.5,    5.0,   150.00),
    (32, 'Mayonnaise',             'kg',   4.0,    2.0,    3.0,   200.00),
    (33, 'Burger Buns',            'dozen', 8.0,   4.0,    6.0,   240.00),
    (34, 'Chicken Wings',          'kg',   10.0,   5.0,    10.0,  480.00),
    (35, 'Noodles',                'kg',   6.0,    3.0,    5.0,   150.00),
    (36, 'Soy Sauce',              'liter', 2.0,   1.0,    2.0,   180.00),
    (37, 'Gulab Jamun Mix',        'kg',   4.0,    2.0,    3.0,   280.00),
    (38, 'Rice Flour',             'kg',   3.0,    1.5,    3.0,   100.00),
    (39, 'Lentils (Daal Chana)',   'kg',   8.0,    4.0,    6.0,   140.00),
    (40, 'Mango Pulp',             'kg',   3.0,    1.0,    3.0,   350.00);

-- ============================================================
-- 5. RECIPES (Linking products to ingredients)
-- ============================================================
-- Chicken Burger (product 1) - Standard recipe
INSERT OR IGNORE INTO recipes (id, product_id, recipe_type_id, yield_quantity) VALUES
    (1,  1,  1, 1.0),   -- Chicken Burger
    (2,  2,  1, 1.0),   -- Beef Burger
    (3,  6,  1, 1.0),   -- Chicken Pizza Medium
    (4,  10, 1, 1.0),   -- Chicken Tikka
    (5,  14, 1, 1.0),   -- Chicken Biryani
    (6,  18, 1, 1.0),   -- Chicken Karahi Half
    (7,  23, 1, 1.0),   -- French Fries
    (8,  28, 1, 1.0),   -- Soft Drink
    (9,  30, 1, 1.0),   -- Tea
    (10, 35, 1, 1.0),   -- Gulab Jamun
    (11, 39, 1, 1.0),   -- Chicken Manchurian
    (12, 43, 1, 1.0),   -- Halwa Puri
    (13, 4,  1, 1.0),   -- Club Sandwich
    (14, 25, 1, 1.0);   -- Chicken Wings

-- ============================================================
-- 6. RECIPE INGREDIENTS
-- ============================================================
-- Chicken Burger (recipe 1)
INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation_note) VALUES
    (1,  1,  0.150, 'kg',  'Grilled chicken patty'),
    (1,  33, 1.0,   'unit', 'Toasted bun'),
    (1,  32, 0.020, 'kg',  'Spread on bun'),
    (1,  31, 0.015, 'kg',  'For serving'),
    (1,  23, 0.020, 'kg',  'Shredded lettuce'),
    (1,  7,  0.030, 'kg',  'Sliced tomato');

-- Beef Burger (recipe 2)
INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation_note) VALUES
    (2,  2,  0.150, 'kg',  'Beef patty'),
    (2,  33, 1.0,   'unit', 'Toasted bun'),
    (2,  32, 0.020, 'kg',  'Mayonnaise'),
    (2,  31, 0.015, 'kg',  'Ketchup'),
    (2,  23, 0.020, 'kg',  'Lettuce'),
    (2,  7,  0.030, 'kg',  'Tomato slices');

-- Chicken Pizza Medium (recipe 3)
INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation_note) VALUES
    (3,  30, 0.250, 'kg',  'Pizza dough base'),
    (3,  11, 0.080, 'kg',  'Spread evenly'),
    (3,  10, 0.150, 'kg',  'Mozzarella topping'),
    (3,  1,  0.150, 'kg',  'Diced chicken breast'),
    (3,  24, 0.030, 'kg',  'Capsicum slices'),
    (3,  8,  0.030, 'kg',  'Onion rings');

-- Chicken Tikka (recipe 4)
INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation_note) VALUES
    (4,  1,  0.400, 'kg',  'Marinated overnight'),
    (4,  9,  0.060, 'kg',  'For marinade'),
    (4,  25, 0.020, 'kg',  'Ginger garlic paste'),
    (4,  20, 0.015, 'kg',  'Tikka masala spices'),
    (4,  6,  0.040, 'liter', 'For basting'),
    (4,  26, 0.010, 'kg',  'For garnish');

-- Chicken Biryani (recipe 5)
INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation_note) VALUES
    (5,  4,  0.250, 'kg',  'Soaked for 30 min'),
    (5,  1,  0.200, 'kg',  'Marinated chicken'),
    (5,  9,  0.040, 'kg',  'For layering'),
    (5,  8,  0.050, 'kg',  'Fried until golden'),
    (5,  7,  0.040, 'kg',  'Chopped'),
    (5,  20, 0.010, 'kg',  'Biryani masala'),
    (5,  6,  0.030, 'liter', 'For cooking'),
    (5,  26, 0.005, 'kg',  'Garnish'),
    (5,  21, 0.083, 'dozen', 'Boiled eggs for topping');

-- Chicken Karahi Half (recipe 6)
INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation_note) VALUES
    (6,  1,  0.400, 'kg',  'Cut into pieces'),
    (6,  7,  0.150, 'kg',  'Pureed for gravy'),
    (6,  8,  0.080, 'kg',  'Sliced'),
    (6,  25, 0.020, 'kg',  'Ginger garlic paste'),
    (6,  20, 0.012, 'kg',  'Karahi masala'),
    (6,  6,  0.050, 'liter', 'For cooking'),
    (6,  26, 0.010, 'kg',  'Green chilies'),
    (6,  9,  0.050, 'kg',  'Yogurt for gravy');

-- French Fries (recipe 7)
INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation_note) VALUES
    (7,  12, 0.200, 'kg',  'Deep fry at 180°C'),
    (7,  27, 0.002, 'kg',  'Season after frying');

-- Tea (recipe 9)
INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation_note) VALUES
    (9,  28, 0.005, 'kg',  'Boil with water'),
    (9,  17, 0.150, 'liter', 'Add after boiling'),
    (9,  16, 0.010, 'kg',  'To taste');

-- Gulab Jamun (recipe 10)
INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation_note) VALUES
    (10, 37, 0.100, 'kg',  'Mix with water to form dough'),
    (10, 6,  0.050, 'liter', 'Deep fry on low heat'),
    (10, 16, 0.080, 'kg',  'Sugar syrup with cardamom');

-- Chicken Manchurian (recipe 11)
INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation_note) VALUES
    (11, 1,  0.200, 'kg',  'Diced, marinated in soy sauce'),
    (11, 36, 0.020, 'liter', 'For sauce'),
    (11, 35, 0.100, 'kg',  'For serving'),
    (11, 25, 0.010, 'kg',  'For stir fry'),
    (11, 24, 0.030, 'kg',  'Diced capsicum'),
    (11, 8,  0.030, 'kg',  'Diced onion');

-- Halwa Puri (recipe 12)
INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation_note) VALUES
    (12, 5,  0.200, 'kg',  'Knead with oil for puri'),
    (12, 16, 0.060, 'kg',  'For halwa'),
    (12, 6,  0.040, 'liter', 'For deep frying puri'),
    (12, 38, 0.020, 'kg',  'For halwa consistency');

-- Club Sandwich (recipe 13)
INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation_note) VALUES
    (13, 1,  0.100, 'kg',  'Grilled chicken slices'),
    (13, 33, 1.5,   'unit', 'Toasted bread slices'),
    (13, 32, 0.020, 'kg',  'Mayonnaise'),
    (13, 23, 0.020, 'kg',  'Lettuce'),
    (13, 7,  0.030, 'kg',  'Tomato slices'),
    (13, 21, 0.083, 'dozen', 'Boiled egg slices');

-- Chicken Wings (recipe 14)
INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation_note) VALUES
    (14, 34, 0.400, 'kg',  'Marinated in spicy sauce'),
    (14, 6,  0.030, 'liter', 'Deep fry'),
    (14, 20, 0.010, 'kg',  'Seasoning');

-- ============================================================
-- 7. EMPLOYEES
-- ============================================================
INSERT OR IGNORE INTO employees (id, name, phone, email, employee_type_id, salary, joined_at) VALUES
    (1,  'Ali Ahmed',       '+92-300-111-0001', 'ali.ahmed@structa.cloud',  1, 60000.00, '2024-01-15'),
    (2,  'Usman Khan',      '+92-300-111-0002', 'usman.khan@structa.cloud', 2, 45000.00, '2024-02-01'),
    (3,  'Hassan Ali',      '+92-300-111-0003', 'hassan.ali@structa.cloud', 2, 40000.00, '2024-03-10'),
    (4,  'Bilal Sheikh',    '+92-300-111-0004', 'bilal@structa.cloud',      3, 25000.00, '2024-01-20'),
    (5,  'Farhan Iqbal',    '+92-300-111-0005', 'farhan@structa.cloud',     3, 25000.00, '2024-04-05'),
    (6,  'Imran Hussain',   '+92-300-111-0006', 'imran@structa.cloud',      3, 25000.00, '2024-05-12'),
    (7,  'Sajid Mehmood',   '+92-300-111-0007', 'sajid@structa.cloud',      4, 30000.00, '2024-01-25'),
    (8,  'Tariq Mahmood',   '+92-300-111-0008', 'tariq@structa.cloud',      5, 22000.00, '2024-06-01'),
    (9,  'Nasir Khan',      '+92-300-111-0009', 'nasir@structa.cloud',      5, 22000.00, '2024-06-15'),
    (10, 'Rashid Ahmed',    '+92-300-111-0010', 'rashid@structa.cloud',     6, 18000.00, '2024-02-20'),
    (11, 'Zainab Bibi',     '+92-300-111-0011', 'zainab@structa.cloud',     3, 25000.00, '2024-07-01'),
    (12, 'Kamran Abbas',    '+92-300-111-0012', 'kamran@structa.cloud',     5, 22000.00, '2024-08-10');

-- ============================================================
-- 8. SAMPLE SALES (with items)
-- ============================================================
-- Sale 1: Dine-in at table 3, served by Bilal
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, table_number, employee_id) VALUES
    (1, 1360.00, 'PKR', '2026-01-10', '13:15:00', 'dine_in', 'completed', 3, 4);
INSERT OR IGNORE INTO sale_items (sale_id, product_name, price, quantity, unit) VALUES
    (1, 'Chicken Burger',    350.00, 2, 'item'),
    (1, 'French Fries',      200.00, 1, 'plate'),
    (1, 'Soft Drink (500ml)', 80.00, 2, 'bottle'),
    (1, 'Gulab Jamun (4 pcs)', 150.00, 2, 'plate');

-- Sale 2: Dine-in at table 7, served by Farhan
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, table_number, employee_id) VALUES
    (2, 2000.00, 'PKR', '2026-01-10', '14:00:00', 'dine_in', 'completed', 7, 5);
INSERT OR IGNORE INTO sale_items (sale_id, product_name, price, quantity, unit) VALUES
    (2, 'Chicken Pizza (Medium)', 800.00,  1, 'item'),
    (2, 'Chicken Karahi (Half)',  900.00,  1, 'item'),
    (2, 'Soft Drink (500ml)',     80.00,   1, 'bottle'),
    (2, 'Mineral Water (1.5L)',   60.00,   1, 'bottle'),
    (2, 'Tea',                    80.00,   2, 'cup');

-- Sale 3: Takeaway, served by Imran
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, employee_id) VALUES
    (3, 1250.00, 'PKR', '2026-01-10', '19:30:00', 'takeaway', 'completed', 6);
INSERT OR IGNORE INTO sale_items (sale_id, product_name, price, quantity, unit) VALUES
    (3, 'Zinger Burger',        450.00, 1, 'item'),
    (3, 'Club Sandwich',        350.00, 1, 'item'),
    (3, 'Chicken Biryani',      250.00, 1, 'plate'),
    (3, 'French Fries',         200.00, 1, 'plate');

-- Sale 4: Delivery - Standard, served by Tariq
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, delivery_type_id, delivery_address, employee_id) VALUES
    (4, 2060.00, 'PKR', '2026-01-11', '12:45:00', 'delivery', 'completed', 1, 'House 12, Street 5, Gulshan Colony', 8);
INSERT OR IGNORE INTO sale_items (sale_id, product_name, price, quantity, unit) VALUES
    (4, 'Chicken Pizza (Large)', 1200.00, 1, 'item'),
    (4, 'Chicken Wings (6 pcs)', 350.00,  1, 'plate'),
    (4, 'Soft Drink (500ml)',    80.00,   2, 'bottle'),
    (4, 'Brownie with Ice Cream', 350.00,  1, 'item');

-- Sale 5: Dine-in at table 1, served by Bilal
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, table_number, employee_id) VALUES
    (5, 2010.00, 'PKR', '2026-01-11', '20:00:00', 'dine_in', 'completed', 1, 4);
INSERT OR IGNORE INTO sale_items (sale_id, product_name, price, quantity, unit) VALUES
    (5, 'Chicken Tikka (4 pcs)',  450.00,  2, 'plate'),
    (5, 'Beef Seekh Kebab (6 pcs)', 350.00, 2, 'plate'),
    (5, 'Daal Makhni',            250.00,  1, 'plate'),
    (5, 'Naan (Butter)',          30.00,   4, 'item'),
    (5, 'Tea',                    80.00,   2, 'cup');

-- Sale 6: Takeaway, served by Imran
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, employee_id) VALUES
    (6, 1020.00, 'PKR', '2026-01-12', '09:30:00', 'takeaway', 'completed', 6);
INSERT OR IGNORE INTO sale_items (sale_id, product_name, price, quantity, unit) VALUES
    (6, 'Halwa Puri (2 puri)',  180.00, 2, 'plate'),
    (6, 'Chana Cholay',         200.00, 1, 'plate'),
    (6, 'Omelette',             150.00, 2, 'plate'),
    (6, 'Tea',                  80.00,  2, 'cup');

-- Sale 7: Delivery - Express, served by Nasir
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, delivery_type_id, delivery_address, employee_id) VALUES
    (7, 1450.00, 'PKR', '2026-01-12', '13:30:00', 'delivery', 'completed', 2, 'Flat 4B, Green Heights, Main Road', 9);
INSERT OR IGNORE INTO sale_items (sale_id, product_name, price, quantity, unit) VALUES
    (7, 'Fajita Pizza (Medium)', 900.00, 1, 'item'),
    (7, 'Chicken Nuggets (6 pcs)', 300.00, 1, 'plate'),
    (7, 'Milkshake',            250.00,  1, 'glass');

-- Sale 8: Dine-in at table 10, served by Farhan
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, table_number, employee_id) VALUES
    (8, 2990.00, 'PKR', '2026-01-12', '21:00:00', 'dine_in', 'completed', 10, 5);
INSERT OR IGNORE INTO sale_items (sale_id, product_name, price, quantity, unit) VALUES
    (8, 'Mutton Karahi (Full)', 2200.00, 1, 'item'),
    (8, 'Chicken Biryani',      250.00,  1, 'plate'),
    (8, 'Soft Drink (500ml)',   80.00,   3, 'bottle'),
    (8, 'Kheer',                150.00,  2, 'bowl');

-- Sale 9: Dine-in at table 5, served by Zainab
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, table_number, employee_id) VALUES
    (9, 1550.00, 'PKR', '2026-01-13', '14:30:00', 'dine_in', 'completed', 5, 11);
INSERT OR IGNORE INTO sale_items (sale_id, product_name, price, quantity, unit) VALUES
    (9, 'Chicken Karahi (Half)', 900.00,  1, 'item'),
    (9, 'Chicken Fried Rice',   300.00,  1, 'plate'),
    (9, 'Fruit Juice',          200.00,  1, 'glass'),
    (9, 'Gulab Jamun (4 pcs)',  150.00,  1, 'plate');

-- Sale 10: Delivery - Standard, served by Tariq
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, delivery_type_id, delivery_address, employee_id) VALUES
    (10, 1000.00, 'PKR', '2026-01-13', '19:00:00', 'delivery', 'completed', 1, 'Street 12, Block C, Model Town', 8);
INSERT OR IGNORE INTO sale_items (sale_id, product_name, price, quantity, unit) VALUES
    (10, 'Beef Burger',         400.00,  1, 'item'),
    (10, 'Chicken Manchurian',  350.00,  1, 'plate'),
    (10, 'Veg Noodles',         250.00,  1, 'plate');

-- Sale 11: Dine-in at table 8, served by Imran
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, table_number, employee_id) VALUES
    (11, 1060.00, 'PKR', '2026-01-14', '11:00:00', 'dine_in', 'completed', 8, 6);
INSERT OR IGNORE INTO sale_items (sale_id, product_name, price, quantity, unit) VALUES
    (11, 'Nihari',              300.00, 1, 'bowl'),
    (11, 'Siri Paye',           350.00, 1, 'bowl'),
    (11, 'Paratha Roll',        250.00, 1, 'item'),
    (11, 'Chai (Tea)',          80.00,  2, 'cup');

-- Sale 12: Takeaway, served by Zainab
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, employee_id) VALUES
    (12, 620.00, 'PKR', '2026-01-14', '16:30:00', 'takeaway', 'completed', 11);
INSERT OR IGNORE INTO sale_items (sale_id, product_name, price, quantity, unit) VALUES
    (12, 'Chicken Biryani',     250.00,  2, 'plate'),
    (12, 'Mineral Water (1.5L)', 60.00,  2, 'bottle');

-- ============================================================
-- 9. INVENTORY TRANSACTIONS (Initial stock + purchases)
-- ============================================================
-- Initial stock purchases
INSERT OR IGNORE INTO inventory_transactions (id, ingredient_id, transaction_type, quantity_change, note) VALUES
    (1,  1,  'purchase', 30.0,  'Initial stock - Chicken Breast'),
    (2,  2,  'purchase', 20.0,  'Initial stock - Beef Mince'),
    (3,  3,  'purchase', 10.0,  'Initial stock - Mutton'),
    (4,  4,  'purchase', 25.0,  'Initial stock - Basmati Rice'),
    (5,  5,  'purchase', 35.0,  'Initial stock - Wheat Flour'),
    (6,  6,  'purchase', 30.0,  'Initial stock - Cooking Oil'),
    (7,  7,  'purchase', 20.0,  'Initial stock - Tomato'),
    (8,  8,  'purchase', 25.0,  'Initial stock - Onion'),
    (9,  9,  'purchase', 15.0,  'Initial stock - Yogurt'),
    (10, 10, 'purchase', 10.0,  'Initial stock - Mozzarella Cheese');

-- Re-stock purchases
INSERT OR IGNORE INTO inventory_transactions (id, ingredient_id, transaction_type, quantity_change, note) VALUES
    (11, 1,  'purchase', 20.0,  'Weekly restock - Chicken Breast'),
    (12, 6,  'purchase', 15.0,  'Weekly restock - Cooking Oil'),
    (13, 7,  'purchase', 12.0,  'Weekly restock - Tomato'),
    (14, 8,  'purchase', 15.0,  'Weekly restock - Onion'),
    (15, 14, 'purchase', 10.0,  'Weekly restock - Soda Crates'),
    (16, 15, 'purchase', 12.0,  'Weekly restock - Water Bottles'),
    (17, 17, 'purchase', 10.0,  'Weekly restock - Milk'),
    (18, 21, 'purchase', 8.0,   'Weekly restock - Eggs'),
    (19, 12, 'purchase', 10.0,  'Weekly restock - Frozen Fries'),
    (20, 33, 'purchase', 6.0,   'Weekly restock - Burger Buns');

-- Usage (consumption for sales)
INSERT OR IGNORE INTO inventory_transactions (id, ingredient_id, transaction_type, quantity_change, note) VALUES
    (21, 1,  'usage', -5.0,  'Usage: Week 1 sales - Chicken items'),
    (22, 2,  'usage', -3.0,  'Usage: Week 1 sales - Beef items'),
    (23, 4,  'usage', -4.0,  'Usage: Week 1 sales - Rice dishes'),
    (24, 6,  'usage', -8.0,  'Usage: Week 1 - Cooking'),
    (25, 7,  'usage', -5.0,  'Usage: Week 1 - Vegetable prep'),
    (26, 8,  'usage', -6.0,  'Usage: Week 1 - Vegetable prep'),
    (27, 10, 'usage', -2.0,  'Usage: Week 1 - Pizza prep'),
    (28, 12, 'usage', -3.0,  'Usage: Week 1 - Fries orders'),
    (29, 14, 'usage', -4.0,  'Usage: Week 1 - Soda sales'),
    (30, 15, 'usage', -5.0,  'Usage: Week 1 - Water sales');

-- Waste
INSERT OR IGNORE INTO inventory_transactions (id, ingredient_id, transaction_type, quantity_change, note) VALUES
    (31, 7,  'waste', -0.5,  'Spoiled tomatoes'),
    (32, 17, 'waste', -1.0,  'Expired milk'),
    (33, 22, 'waste', -0.8,  'Spoiled potatoes');

-- Adjustments
INSERT OR IGNORE INTO inventory_adjustments (id, ingredient_id, previous_quantity, new_quantity, reason, created_by) VALUES
    (1,  1,  25.0,  24.5,  'Count correction - found 0.5kg less', 'Ali Ahmed'),
    (2,  8,  20.0,  19.0,  'Count correction - weight discrepancy', 'Usman Khan');

-- ============================================================
-- 10. INVENTORY TRANSACTIONS (for inventory adjustments)
-- ============================================================
INSERT OR IGNORE INTO inventory_transactions (id, ingredient_id, transaction_type, quantity_change, note) VALUES
    (34, 1,  'adjustment', -0.5, 'Adjustment: Count variance'),
    (35, 8,  'adjustment', -1.0, 'Adjustment: Weight discrepancy');

-- ============================================================
-- 11. SUPPLIERS
-- ============================================================
INSERT OR IGNORE INTO suppliers (id, name, contact_name, email, phone, address, tax_id, payment_terms) VALUES
    (1, 'Al-Fatah Foods',        'Imran Sheikh',  'imran@alfatah.pk',     '+92-321-1112233', '12 Industry Road, Lahore',    'TAX-001', 'Net 30'),
    (2, 'Fresh Meat & Poultry',  'Kamran Butt',   'kamran@freshmeat.pk',  '+92-322-2223344', '45 Mandi Road, Lahore',       'TAX-002', 'Net 15'),
    (3, 'Metro Wholesale',       'Sajid Ali',     'sajid@metro.pk',       '+92-323-3334455', '78 Canal Road, Lahore',       'TAX-003', 'Net 30'),
    (4, 'Bakehouse Supplies',    'Nazia Hassan',  'nazia@bakehouse.pk',   '+92-324-4445566', '90 Baker Street, Lahore',     'TAX-004', 'Net 15'),
    (5, 'Beverage Distributors', 'Rashid Mehmood', 'rashid@beverage.pk',   '+92-325-5556677', '33 Circular Road, Lahore',    'TAX-005', 'Net 30'),
    (6, 'Dairy Fresh Co.',       'Farah Khan',    'farah@dairyfresh.pk',  '+92-326-6667788', '55 Milk Plant, Lahore',       'TAX-006', 'Net 7');

-- ============================================================
-- 12. PURCHASE ORDERS & ITEMS
-- ============================================================
INSERT OR IGNORE INTO purchase_orders (id, supplier_id, reference_number, status, total_amount, expected_date, notes) VALUES
    (1, 1, 'PO-2026-001', 'received', 8500.00,  '2026-01-10', 'Chicken breast + spice restock'),
    (2, 2, 'PO-2026-002', 'received', 15000.00, '2026-01-12', 'Weekly beef + mutton order'),
    (3, 3, 'PO-2026-003', 'received', 12000.00, '2026-01-15', 'Oil, rice, flour bulk restock'),
    (4, 5, 'PO-2026-004', 'ordered', 6500.00,   '2026-06-20', 'Soda cans + water bottles'),
    (5, 6, 'PO-2026-005', 'ordered', 4800.00,   '2026-06-22', 'Milk + cream + yogurt restock'),
    (6, 4, 'PO-2026-006', 'draft',   3200.00,   '2026-06-25', 'Burger buns + pizza dough flour');

INSERT OR IGNORE INTO purchase_order_items (id, purchase_order_id, ingredient_id, quantity, cost_per_unit, received_quantity) VALUES
    (1,  1, 1,  20.0, 450.00, 20.0),
    (2,  1, 20, 3.0,  240.00, 3.0),
    (3,  1, 25, 3.0,  280.00, 3.0),
    (4,  2, 2,  15.0, 550.00, 15.0),
    (5,  2, 3,  10.0, 1100.00, 10.0),
    (6,  3, 4,  20.0, 180.00, 20.0),
    (7,  3, 5,  20.0, 70.00,  20.0),
    (8,  3, 6,  20.0, 320.00, 20.0),
    (9,  4, 14, 10.0, 480.00, 0),
    (10, 4, 15, 12.0, 360.00, 0),
    (11, 5, 17, 12.0, 180.00, 0),
    (12, 5, 18, 5.0,  330.00, 0),
    (13, 5, 9,  10.0, 130.00, 0),
    (14, 6, 33, 6.0,  240.00, 0),
    (15, 6, 30, 10.0, 90.00,  0);

-- ============================================================
-- 13. CUSTOMERS (with loyalty history)
-- ============================================================
INSERT OR IGNORE INTO customers (id, name, phone, email, loyalty_points, notes) VALUES
    (1, 'Ahmed Raza',       '+92-300-1000001', 'ahmed@email.com',   450.0,  'Regular customer, prefers chicken dishes'),
    (2, 'Fatima Noor',      '+92-300-1000002', 'fatima@email.com',  320.0,  'Loves desserts and beverages'),
    (3, 'Bilal Hassan',     '+92-300-1000003', 'bilal@email.com',   780.0,  'VIP customer, orders frequently'),
    (4, 'Ayesha Malik',     '+92-300-1000004', 'ayesha@email.com',  150.0,  'New customer'),
    (5, 'Usman Dar',        '+92-300-1000005', 'usman@email.com',   600.0,  'Corporate client'),
    (6, 'Zainab Tariq',     '+92-300-1000006', 'zainab@email.com',  220.0,  'Vegetarian preference'),
    (7, 'Hassan Rizvi',     '+92-300-1000007', 'hassan@email.com',  95.0,   'Student discount'),
    (8, 'Sana Javed',       '+92-300-1000008', 'sana@email.com',    510.0,  'Family orders'),
    (9, 'Omar Sheikh',      '+92-300-1000009', 'omar@email.com',    0.0,    'Walk-in'),
    (10, 'Nadia Qureshi',   '+92-300-1000010', 'nadia@email.com',   380.0,  'Loves BBQ items');

-- ============================================================
-- 14. SALES (with customer links + delivery types + employees)
-- ============================================================
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, table_number, delivery_type_id, delivery_address, employee_id, customer_id) VALUES
    (1,  1450.00, 'PKR', '2026-01-10', '12:30', 'dine_in',    'completed', 5,  1, NULL,                          1,  1),
    (2,  800.00,  'PKR', '2026-01-10', '13:15', 'dine_in',    'completed', 10, 1, NULL,                          2,  3),
    (3,  2200.00, 'PKR', '2026-01-10', '19:00', 'delivery',   'completed', NULL, 3, '789 Canal Road, Lahore',      3,  4),
    (4,  550.00,  'PKR', '2026-01-11', '09:00', 'takeaway',   'completed', NULL, 2, NULL,                          2,  2),
    (5,  3600.00, 'PKR', '2026-01-11', '20:30', 'dine_in',    'completed', 3,  1, NULL,                          4,  5),
    (6,  1200.00, 'PKR', '2026-01-12', '14:00', 'delivery',   'completed', NULL, 3, '45 Main Boulevard, Lahore',   5,  1),
    (7,  2800.00, 'PKR', '2026-01-12', '19:45', 'dine_in',    'completed', 8,  1, NULL,                          6,  5),
    (8,  650.00,  'PKR', '2026-01-13', '10:30', 'takeaway',   'completed', NULL, 2, NULL,                          1,  6),
    (9,  1800.00, 'PKR', '2026-01-13', '18:00', 'dine_in',    'completed', 12, 1, NULL,                          3,  8),
    (10, 900.00,  'PKR', '2026-01-14', '11:00', 'dine_in',    'completed', 7,  1, NULL,                          2,  7),
    (11, 4200.00, 'PKR', '2026-01-14', '20:00', 'delivery',   'completed', NULL, 3, '123 Park Avenue, Lahore',     4,  9),
    (12, 1800.00, 'PKR', '2026-01-15', '13:00', 'dine_in',    'completed', 4,  1, NULL,                          5,  3),
    (13, 750.00,  'PKR', '2026-06-16', '12:00', 'takeaway',   'completed', NULL, 2, NULL,                          1,  1);

-- ============================================================
-- 15. SALE ITEMS
-- ============================================================
-- Sale 1: Chicken Burger + Fries + Drink
INSERT OR IGNORE INTO sale_items (id, sale_id, product_name, price, quantity, unit) VALUES
    (1,  1,  'Chicken Burger',    350.00, 2, 'item'),
    (2,  1,  'French Fries',      200.00, 1, 'plate'),
    (3,  1,  'Soft Drink (500ml)', 80.00,  1, 'bottle'),
    (4,  1,  'Gulab Jamun (4 pcs)', 150.00, 2, 'plate');
-- Sale 2: Chicken Pizza Medium + Tea
INSERT OR IGNORE INTO sale_items (id, sale_id, product_name, price, quantity, unit) VALUES
    (5,  2,  'Chicken Pizza (Medium)', 800.00, 1, 'item'),
    (6,  2,  'Tea',                    80.00,  1, 'cup');
-- Sale 3: Mutton Karahi Full + 2 Naan + Drinks
INSERT OR IGNORE INTO sale_items (id, sale_id, product_name, price, quantity, unit) VALUES
    (7,  3,  'Mutton Karahi (Full)', 2200.00, 1, 'item'),
    (8,  3,  'Soft Drink (500ml)',    80.00,  2, 'bottle'),
    (9,  3,  'Water (1.5L)',          60.00,  1, 'bottle');
-- Sale 4: Breakfast items
INSERT OR IGNORE INTO sale_items (id, sale_id, product_name, price, quantity, unit) VALUES
    (10, 4,  'Halwa Puri (2 puri)', 180.00, 2, 'plate'),
    (11, 4,  'Tea',                  80.00,  2, 'cup'),
    (12, 4,  'Omelette',            150.00, 1, 'plate');
-- Sale 5: Family dinner
INSERT OR IGNORE INTO sale_items (id, sale_id, product_name, price, quantity, unit) VALUES
    (13, 5,  'Chicken Karahi (Full)', 1600.00, 1, 'item'),
    (14, 5,  'Chicken Biryani',       250.00,  3, 'plate'),
    (15, 5,  'Beef Seekh Kebab (6pcs)', 350.00, 2, 'plate'),
    (16, 5,  'Soft Drink (500ml)',    80.00,   4, 'bottle'),
    (17, 5,  'Gulab Jamun (4 pcs)',   150.00,  2, 'plate');
-- Sale 6-13: Various
INSERT OR IGNORE INTO sale_items (id, sale_id, product_name, price, quantity, unit) VALUES
    (18, 6,  'Zinger Burger',         450.00,  2, 'item'),
    (19, 6,  'French Fries',          200.00,  1, 'plate'),
    (20, 6,  'Milkshake',             250.00,  1, 'glass'),
    (21, 7,  'Chargah (Full)',        1200.00, 1, 'item'),
    (22, 7,  'Mutton Biryani',        350.00,  2, 'plate'),
    (23, 7,  'Chicken Wings (6 pcs)', 350.00,  1, 'plate'),
    (24, 7,  'Lassi',                 120.00,  4, 'glass'),
    (25, 8,  'Club Sandwich',         350.00,  1, 'item'),
    (26, 8,  'Coffee',                150.00,  1, 'cup'),
    (27, 8,  'Ice Cream',             120.00,  1, 'scoop'),
    (28, 9,  'Beef Burger',           400.00,  2, 'item'),
    (29, 9,  'French Fries',          200.00,  2, 'plate'),
    (30, 9,  'Fruit Juice',           200.00,  2, 'glass'),
    (31, 9,  'Brownie with Ice Cream', 350.00, 1, 'item'),
    (32, 10, 'Chicken Manchurian',    350.00,  1, 'plate'),
    (33, 10, 'Chicken Noodles',       300.00,  1, 'plate'),
    (34, 10, 'Spring Rolls (6 pcs)',  250.00,  1, 'plate'),
    (35, 11, 'Mutton Karahi (Full)',  2200.00, 1, 'item'),
    (36, 11, 'Chicken Fried Rice',    300.00,  2, 'plate'),
    (37, 11, 'Kung Pao Chicken',      400.00,  1, 'plate'),
    (38, 11, 'Chicken Soup',          250.00,  2, 'bowl'),
    (39, 11, 'Kheer',                 150.00,  2, 'bowl'),
    (40, 12, 'Chicken Tikka (4 pcs)', 450.00,  2, 'plate'),
    (41, 12, 'Nihari',                300.00,  2, 'bowl'),
    (42, 12, 'Soft Drink (500ml)',    80.00,   1, 'bottle'),
    (43, 12, 'Tea',                   80.00,   2, 'cup'),
    (44, 13, 'Chicken Nuggets (6pcs)', 300.00, 1, 'plate'),
    (45, 13, 'French Fries',           200.00, 1, 'plate'),
    (46, 13, 'Soft Drink (500ml)',     80.00,  1, 'bottle'),
    (47, 13, 'Ice Cream',              120.00, 1, 'scoop');

-- ============================================================
-- 16. KITCHEN TICKETS
-- ============================================================
INSERT OR IGNORE INTO kitchen_tickets (id, sale_id, status, priority, notes) VALUES
    (1,  1,  'delivered', 0, 'Table 5'),
    (2,  2,  'delivered', 0, 'Table 10'),
    (3,  3,  'delivered', 0, 'Delivery'),
    (4,  4,  'delivered', 0, 'Takeaway'),
    (5,  5,  'delivered', 1, 'Table 3 — VIP'),
    (6,  6,  'delivered', 0, 'Delivery to Main Blvd'),
    (7,  7,  'delivered', 1, 'Table 8 — Large party'),
    (8,  8,  'delivered', 0, 'Takeaway'),
    (9,  9,  'delivered', 0, 'Table 12'),
    (10, 10, 'delivered', 0, 'Table 7'),
    (11, 11, 'delivered', 0, 'Delivery to Park Ave'),
    (12, 12, 'delivered', 1, 'Table 4 — VIP');

-- ============================================================
-- 17. LOYALTY TRANSACTIONS
-- ============================================================
INSERT OR IGNORE INTO loyalty_transactions (id, customer_id, sale_id, points_change, reason) VALUES
    (1,  1,  1,  15.0,  'Points earned — Sale #1'),
    (2,  3,  2,  8.0,   'Points earned — Sale #2'),
    (3,  4,  3,  22.0,  'Points earned — Sale #3'),
    (4,  3,  12, 18.0,  'Points earned — Sale #12'),
    (5,  6,  8,  7.0,   'Points earned — Takeaway'),
    (6,  1,  6,  12.0,  'Points earned — Delivery'),
    (7,  5,  5,  36.0,  'Points earned — VIP dinner'),
    (8,  8,  9,  18.0,  'Points earned — Family order'),
    (9,  1,  13, 8.0,   'Points earned — Takeaway'),
    (10, 7,  10, 9.0,   'Points earned — Student order'),
    (11, 3,  NULL, -50.0, 'Redeemed free dessert voucher'),
    (12, 5,  NULL, -100.0,'Redeemed discount coupon');

-- ============================================================
-- 18. ROLES & USER ROLES
-- ============================================================
INSERT OR IGNORE INTO roles (id, name, permissions) VALUES
    (1, 'Admin',       '["all"]'),
    (2, 'Manager',     '["sales","inventory","employees","reports","settings"]'),
    (3, 'Chef',        '["kitchen","recipes","inventory_read"]'),
    (4, 'Waiter',      '["sales","orders"]'),
    (5, 'Cashier',     '["sales","transactions"]'),
    (6, 'Driver',      '["deliveries"]');

-- Assign superuser to Admin role (user id 1 is the superuser)
INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES
    (1, 1);

-- ============================================================
-- 19. TAX REPORTS
-- ============================================================
INSERT OR IGNORE INTO tax_reports (id, period_start, period_end, total_sales, total_tax, transaction_count) VALUES
    (1, '2026-01-01', '2026-01-15', 23150.00, 3009.50, 12),
    (2, '2026-01-16', '2026-01-31', 18700.00, 2431.00, 9),
    (3, '2026-02-01', '2026-02-15', 25400.00, 3302.00, 14);

-- ============================================================
-- 20. EMPLOYEE SCHEDULES
-- ============================================================
INSERT OR IGNORE INTO employee_schedules (id, employee_id, shift_start, shift_end, status, notes) VALUES
    (1, 1,  '2026-01-10 09:00', '2026-01-10 17:00', 'completed', 'Morning shift'),
    (2, 2,  '2026-01-10 09:00', '2026-01-10 17:00', 'completed', 'Morning shift'),
    (3, 3,  '2026-01-10 17:00', '2026-01-10 23:00', 'completed', 'Evening shift'),
    (4, 1,  '2026-01-11 09:00', '2026-01-11 17:00', 'completed', 'Morning shift'),
    (5, 4,  '2026-01-11 17:00', '2026-01-11 23:00', 'completed', 'Evening shift'),
    (6, 1,  '2026-06-16 09:00', '2026-06-16 17:00', 'scheduled',  'Upcoming shift'),
    (7, 2,  '2026-06-16 09:00', '2026-06-16 17:00', 'scheduled',  'Upcoming shift'),
    (8, 3,  '2026-06-16 17:00', '2026-06-16 23:00', 'scheduled',  'Upcoming evening'),
    (9, 6,  '2026-06-16 17:00', '2026-06-16 23:00', 'scheduled',  'Upcoming evening'),
    (10, 1, '2026-06-17 09:00', '2026-06-17 17:00', 'scheduled',  'Upcoming shift'),
    (11, 5, '2026-06-17 17:00', '2026-06-17 23:00', 'scheduled',  'Upcoming evening'),
    (12, 7, '2026-06-17 17:00', '2026-06-17 23:00', 'scheduled',  'Delivery shift');

-- ============================================================
-- 21. PAYROLLS
-- ============================================================
INSERT OR IGNORE INTO payrolls (id, employee_id, period_start, period_end, regular_hours, overtime_hours, total_pay, status) VALUES
    (1, 1, '2026-01-01', '2026-01-15', 80.0,  5.0,  22500.00, 'paid'),
    (2, 2, '2026-01-01', '2026-01-15', 80.0,  3.0,  16800.00, 'paid'),
    (3, 3, '2026-01-01', '2026-01-15', 75.0,  8.0,  19500.00, 'paid'),
    (4, 4, '2026-01-01', '2026-01-15', 80.0,  2.0,  16200.00, 'paid'),
    (5, 5, '2026-01-01', '2026-01-15', 78.0,  4.0,  17800.00, 'paid'),
    (6, 6, '2026-01-01', '2026-01-15', 80.0,  10.0, 22000.00, 'paid'),
    (7, 1, '2026-06-01', '2026-06-15', 80.0,  0.0,  20000.00, 'draft'),
    (8, 2, '2026-06-01', '2026-06-15', 75.0,  0.0,  15000.00, 'draft'),
    (9, 3, '2026-06-01', '2026-06-15', 80.0,  0.0,  17000.00, 'draft');

-- ============================================================
-- 22. RECEIPT TEMPLATES
-- ============================================================
INSERT OR IGNORE INTO receipt_templates (id, name, template_body, is_default) VALUES
    (1, 'Standard',  '<h2>{{restaurant_name}}</h2><p>{{address}}</p><table>{{items}}</table><p>Total: {{total}}</p><p>{{footer}}</p>', 1),
    (2, 'Compact',   '<p>{{restaurant_name}} — {{date}}</p><table>{{items}}</table><p>Total: {{total}}</p>', 0),
    (3, 'Detailed',  '<h2>{{restaurant_name}}</h2><p>{{address}} | {{phone}} | {{email}}</p><table>{{items}}</table><p>Subtotal: {{subtotal}} | Tax: {{tax}} | Total: {{total}}</p><p>{{footer}}</p>', 0);

-- ============================================================
-- 23. INVENTORY ALERTS
-- ============================================================
INSERT OR IGNORE INTO inventory_alerts (id, ingredient_id, alert_type, alert_message, is_resolved) VALUES
    (1, 29, 'low_stock', 'Coffee Beans below reorder level (1.5 < 0.5 reorder)', 0),
    (2, 18, 'low_stock', 'Cream below reorder level (5.0 < 3.0 reorder)', 0),
    (3, 26, 'low_stock', 'Green Chilies below reorder level (3.0 < 1.5 reorder)', 0);


-- ============================================================
-- VERIFICATION QUERIES (run these to confirm seed data)
-- ============================================================
-- SELECT 'Settings' AS table_name, COUNT(*) AS count FROM settings
-- UNION ALL SELECT 'Categories', COUNT(*) FROM categories
-- UNION ALL SELECT 'Products', COUNT(*) FROM products
-- UNION ALL SELECT 'Ingredients', COUNT(*) FROM ingredients
-- UNION ALL SELECT 'Recipes', COUNT(*) FROM recipes
-- UNION ALL SELECT 'Recipe Ingredients', COUNT(*) FROM recipe_ingredients
-- UNION ALL SELECT 'Delivery Types', COUNT(*) FROM delivery_types
-- UNION ALL SELECT 'Employee Types', COUNT(*) FROM employee_types
-- UNION ALL SELECT 'Employees', COUNT(*) FROM employees
-- UNION ALL SELECT 'Sales', COUNT(*) FROM sales
-- UNION ALL SELECT 'Sale Items', COUNT(*) FROM sale_items
-- UNION ALL SELECT 'Inventory Transactions', COUNT(*) FROM inventory_transactions
-- UNION ALL SELECT 'Inventory Adjustments', COUNT(*) FROM inventory_adjustments;
