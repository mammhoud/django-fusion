-- =============================================================================
-- UNIFIED SEED DATA  —  Shared by all presets
-- =============================================================================
-- Each preset seeds only the sections it needs via `seed.rs`.  All statements
-- use INSERT OR IGNORE / UPDATE so they are safe to re-run.
--
-- Sections:
--   [SECTION:shared]   — Always seeded (suppliers, customers, payroll, etc.)
--   [SECTION:base]     — Restaurant demo data (categories 1-10, products 1-47, …)
--   [SECTION:gaming]   — Gaming center data, standalone (categories 11-16, …)
--   [SECTION:coffee]   — Coffee shop data, layered on base (categories 17-21, …)
--
-- Preset → sections mapping:
--   base…… shared + base
--   gaming… shared + gaming
--   coffee… shared + base + coffee
--   all ……… shared + gaming + coffee
--
-- ⚠️  No semicolons inside string literals or /* … */ block comments.
--     seed.rs splits on `;` and runs statements one at a time.
-- =============================================================================

-- [SECTION:shared]
-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║  Data that every preset needs regardless of theme.                      ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝
-- NOTE: Only tables without FK dependencies on base/gaming-specific IDs.
-- Tables referencing employees, ingredients, etc. live in [SECTION:base].

-- Suppliers (no FK to preset-specific data)
INSERT OR IGNORE INTO suppliers (id, name, contact_name, email, phone, address, tax_id, payment_terms, is_active) VALUES
    (1, 'Fresh Foods Co.', 'Ahmed Malik', 'ahmed@freshfoods.com', '+92-300-555-0101', '12 Industrial Area, Lahore', 'NTN-1234567', 'Net 30', 1),
    (2, 'City Meat Suppliers', 'Usman Butt', 'usman@citymeat.com', '+92-300-555-0102', '45 Meat Market, Township', 'NTN-2345678', 'Net 15', 1),
    (3, 'Al-Rashid Grocers', 'Rashid Khan', 'rashid@alrashid.com', '+92-300-555-0103', '78 Main Bazaar, Gulberg', 'NTN-3456789', 'Cash on Delivery', 1),
    (4, 'Punjab Beverages', 'Sajid Ali', 'sajid@punjabbev.com', '+92-300-555-0104', '33 Beverage Road, Faisal Town', 'NTN-4567890', 'Net 30', 1),
    (5, 'Green Valley Produce', 'Hassan Raza', 'hassan@greenvalley.com', '+92-300-555-0105', '90 Farm Road, Raiwind', 'NTN-5678901', 'Net 7', 1),
    (6, 'Mega Mart Wholesale', 'Bilal Ahmed', 'bilal@megamart.com', '+92-300-555-0106', '55 Wholesale Market, Ichhra', 'NTN-6789012', 'Net 45', 1);

-- Customers (no FK to preset-specific data)
INSERT OR IGNORE INTO customers (id, name, phone, email, loyalty_points, notes) VALUES
    (1, 'Ahmad Raza', '+92-300-111-1001', 'ahmad.raza@gmail.com', 250, 'Regular customer - likes chicken biryani'),
    (2, 'Fatima Zahra', '+92-300-111-1002', 'fatima.z@yahoo.com', 120, 'Orders for office meetings'),
    (3, 'Omar Farooq', '+92-300-111-1003', 'omar.farooq@hotmail.com', 450, 'VIP - catering orders'),
    (4, 'Zainab Ali', '+92-300-111-1004', 'zainab.ali@gmail.com', 80, 'Weekend family orders'),
    (5, 'Hassan Abbas', '+92-300-111-1005', 'hassan.abbas@gmail.com', 310, 'Prefers BBQ items'),
    (6, 'Noor Fatima', '+92-300-111-1006', 'noor.f@outlook.com', 180, 'Desert lover - often orders kheer'),
    (7, 'Bilal Hussain', '+92-300-111-1007', 'bilal.h@yahoo.com', 60, 'New customer - breakfast orders'),
    (8, 'Ayesha Khan', '+92-300-111-1008', 'ayesha.khan@gmail.com', 520, 'Top spender - monthly corporate'),
    (9, 'Usman Ghani', '+92-300-111-1009', 'usman.ghani@gmail.com', 200, 'Likes Chinese dishes'),
    (10, 'Sarah Ahmed', '+92-300-111-1010', 'sarah.ahmed@gmail.com', 95, 'Healthy eater - salads and grilled');

-- Tax reports (no FK to preset-specific data)
INSERT OR IGNORE INTO tax_reports (id, period_start, period_end, total_sales, total_tax, transaction_count) VALUES
    (1, '2026-07-01', '2026-07-07', 185000.00, 24050.00, 42),
    (2, '2026-07-08', '2026-07-14', 203500.00, 26455.00, 48),
    (3, '2026-07-01', '2026-07-14', 388500.00, 50505.00, 90);

-- [SECTION:base]
-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║  Restaurant demo preset — seeded for base and coffee presets.           ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

-- 1. Settings — realistic restaurant defaults
UPDATE settings SET
    restaurant_name = 'Forge POS',
    address = '123 Main Boulevard, Gulberg, Lahore',
    phone = '+92-300-1234567',
    email = 'structa.cloud@gmail.com',
    tax_rate = '13',
    opening_time = '09:00',
    closing_time = '23:00',
    receipt_footer = 'Thank you for dining with us! Follow us @pos_app',
    logo = NULL,
    dine_in_tables = 15,
    delivery_fee = 50.0,
    delivery_fee_per_km = 15.0
WHERE id = 1;

-- 2. Categories (food menu)
INSERT OR IGNORE INTO categories (id, name) VALUES
    (1, 'Burgers & Sandwiches'), (2, 'Pizza'), (3, 'BBQ & Grills'),
    (4, 'Rice & Biryani'), (5, 'Karahi & Curries'), (6, 'Fast Food & Snacks'),
    (7, 'Beverages'), (8, 'Desserts'), (9, 'Chinese'), (10, 'Breakfast');

-- 3. Products (menu items)
INSERT OR IGNORE INTO products (id, name, price, unit, category_id) VALUES
    (1,  'Chicken Burger',             350.00, 'item', 1),
    (2,  'Beef Burger',                400.00, 'item', 1),
    (3,  'Zinger Burger',              450.00, 'item', 1),
    (4,  'Club Sandwich',              350.00, 'item', 1),
    (5,  'Paratha Roll',               250.00, 'item', 1),
    (6,  'Chicken Pizza (Medium)',     800.00, 'item', 2),
    (7,  'Chicken Pizza (Large)',      1200.00, 'item', 2),
    (8,  'Fajita Pizza (Medium)',      900.00, 'item', 2),
    (9,  'Fajita Pizza (Large)',       1300.00, 'item', 2),
    (10, 'Chicken Tikka (4 pcs)',      450.00, 'plate', 3),
    (11, 'Beef Seekh Kebab (6 pcs)',   350.00, 'plate', 3),
    (12, 'Chargah (Full)',             1200.00, 'item', 3),
    (13, 'Mutton Tikka (4 pcs)',       600.00, 'plate', 3),
    (14, 'Chicken Biryani',            250.00, 'plate', 4),
    (15, 'Mutton Biryani',             350.00, 'plate', 4),
    (16, 'Vegetable Biryani',          200.00, 'plate', 4),
    (17, 'Chicken Fried Rice',         300.00, 'plate', 4),
    (18, 'Chicken Karahi (Half)',      900.00, 'item', 5),
    (19, 'Chicken Karahi (Full)',      1600.00, 'item', 5),
    (20, 'Mutton Karahi (Half)',       1200.00, 'item', 5),
    (21, 'Mutton Karahi (Full)',       2200.00, 'item', 5),
    (22, 'Daal Makhni',                250.00, 'plate', 5),
    (23, 'French Fries',               200.00, 'plate', 6),
    (24, 'Chicken Nuggets (6 pcs)',    300.00, 'plate', 6),
    (25, 'Chicken Wings (6 pcs)',      350.00, 'plate', 6),
    (26, 'Spring Rolls (6 pcs)',       250.00, 'plate', 6),
    (27, 'Chicken Soup',               250.00, 'bowl', 6),
    (28, 'Soft Drink (500ml)',         80.00,  'bottle', 7),
    (29, 'Mineral Water (1.5L)',       60.00,  'bottle', 7),
    (30, 'Tea',                        80.00,  'cup', 7),
    (31, 'Coffee',                     150.00, 'cup', 7),
    (32, 'Milkshake',                  250.00, 'glass', 7),
    (33, 'Fruit Juice',                200.00, 'glass', 7),
    (34, 'Lassi',                      120.00, 'glass', 7),
    (35, 'Gulab Jamun (4 pcs)',        150.00, 'plate', 8),
    (36, 'Ice Cream',                  120.00, 'scoop', 8),
    (37, 'Kheer',                      150.00, 'bowl', 8),
    (38, 'Brownie with Ice Cream',     350.00, 'item', 8),
    (39, 'Chicken Manchurian',         350.00, 'plate', 9),
    (40, 'Veg Noodles',                250.00, 'plate', 9),
    (41, 'Chicken Noodles',            300.00, 'plate', 9),
    (42, 'Kung Pao Chicken',           400.00, 'plate', 9),
    (43, 'Halwa Puri (2 puri)',        180.00, 'plate', 10),
    (44, 'Chana Cholay',               200.00, 'plate', 10),
    (45, 'Omelette',                   150.00, 'plate', 10),
    (46, 'Nihari',                     300.00, 'bowl', 10),
    (47, 'Siri Paye',                  350.00, 'bowl', 10);

-- 4. Ingredients
INSERT OR IGNORE INTO ingredients (id, name, unit, current_quantity, reorder_level, reorder_quantity, cost_per_unit) VALUES
    (1,  'Chicken Breast',         'kg',    25.0,  10.0,  20.0,  450.00),
    (2,  'Beef Mince',             'kg',    15.0,  8.0,   15.0,  550.00),
    (3,  'Mutton',                 'kg',    8.0,   5.0,   10.0,  1100.00),
    (4,  'Basmati Rice',           'kg',    20.0,  10.0,  20.0,  180.00),
    (5,  'Wheat Flour',            'kg',    30.0,  15.0,  20.0,  70.00),
    (6,  'Cooking Oil',            'liter', 25.0,  10.0,  20.0,  320.00),
    (7,  'Tomato',                 'kg',    15.0,  8.0,   12.0,  90.00),
    (8,  'Onion',                  'kg',    20.0,  10.0,  15.0,  70.00),
    (9,  'Yogurt',                 'kg',    12.0,  5.0,   10.0,  130.00),
    (10, 'Mozzarella Cheese',      'kg',    8.0,   4.0,   8.0,   750.00),
    (11, 'Pizza Sauce',            'kg',    5.0,   3.0,   5.0,   380.00),
    (12, 'Frozen French Fries',    'kg',    12.0,  5.0,   10.0,  220.00),
    (13, 'Frozen Chicken Nuggets', 'kg',    8.0,   4.0,   6.0,   550.00),
    (14, 'Soda Cans (Crate)',      'crate', 15.0,  5.0,   10.0,  480.00),
    (15, 'Water Bottles (Case)',   'case',  20.0,  8.0,   12.0,  360.00),
    (16, 'Sugar',                  'kg',    15.0,  5.0,   10.0,  110.00),
    (17, 'Milk',                   'liter', 18.0,  8.0,   12.0,  180.00),
    (18, 'Cream',                  'liter', 5.0,   3.0,   5.0,   330.00),
    (19, 'Vanilla Ice Cream',      'kg',    6.0,   3.0,   5.0,   450.00),
    (20, 'Spices Mix (Garam Masala)', 'kg', 3.0,   2.0,   3.0,   240.00),
    (21, 'Eggs',                   'dozen', 12.0,  5.0,   10.0,  220.00),
    (22, 'Potato',                 'kg',    20.0,  10.0,  15.0,  50.00),
    (23, 'Cabbage',                'kg',    5.0,   3.0,   5.0,   45.00),
    (24, 'Capsicum',               'kg',    6.0,   3.0,   5.0,   110.00),
    (25, 'Ginger Garlic Paste',    'kg',    4.0,   2.0,   3.0,   280.00),
    (26, 'Green Chilies',          'kg',    3.0,   1.5,   2.5,   130.00),
    (27, 'Salt',                   'kg',    8.0,   3.0,   5.0,   25.00),
    (28, 'Tea Leaves',             'kg',    2.0,   1.0,   2.0,   550.00),
    (29, 'Coffee Beans',           'kg',    1.5,   0.5,   1.5,   1100.00),
    (30, 'Pizza Dough Flour',      'kg',    10.0,  5.0,   10.0,  90.00),
    (31, 'Ketchup',                'kg',    5.0,   2.5,   5.0,   150.00),
    (32, 'Mayonnaise',             'kg',    4.0,   2.0,   3.0,   200.00),
    (33, 'Burger Buns',            'dozen', 8.0,   4.0,   6.0,   240.00),
    (34, 'Chicken Wings',          'kg',    10.0,  5.0,   10.0,  480.00),
    (35, 'Noodles',                'kg',    6.0,   3.0,   5.0,   150.00),
    (36, 'Soy Sauce',              'liter', 2.0,   1.0,   2.0,   180.00),
    (37, 'Gulab Jamun Mix',        'kg',    4.0,   2.0,   3.0,   280.00),
    (38, 'Rice Flour',             'kg',    3.0,   1.5,   3.0,   100.00),
    (39, 'Lentils (Daal Chana)',   'kg',    8.0,   4.0,   6.0,   140.00),
    (40, 'Mango Pulp',             'kg',    3.0,   1.0,   3.0,   350.00),
    (41, 'Dried Fenugreek Leaves', 'kg',    2.0,   1.0,   2.0,   400.00),
    (42, 'Mixed Vegetables (Peas/Carrot/Beans)', 'kg', 10.0,  5.0,  8.0,   80.00),
    (43, 'Butter',                 'kg',    5.0,   2.0,   4.0,   450.00),
    (44, 'Spring Roll Pastry',     'pack',  8.0,   4.0,   6.0,   120.00),
    (45, 'Cardamom',               'kg',    1.0,   0.5,   1.0,   1800.00),
    (46, 'Almonds',                'kg',    3.0,   1.5,   3.0,   1200.00),
    (47, 'Pistachios',             'kg',    2.0,   1.0,   2.0,   1500.00),
    (48, 'Peanuts',                'kg',    5.0,   2.5,   5.0,   250.00),
    (49, 'Bread Slices',           'loaf',  10.0,  5.0,   8.0,   120.00),
    (50, 'Lemon',                  'kg',    5.0,   2.0,   5.0,   100.00),
    (51, 'Cinnamon Sticks',        'kg',    1.0,   0.5,   1.0,   900.00),
    (52, 'Black Pepper',           'kg',    1.5,   0.75,  1.5,   600.00),
    (53, 'Cumin Seeds',            'kg',    2.0,   1.0,   2.0,   350.00),
    (54, 'Turmeric Powder',        'kg',    2.0,   1.0,   2.0,   200.00),
    (55, 'Red Chili Powder',       'kg',    3.0,   1.5,   3.0,   300.00);

-- 5. Recipes
INSERT OR IGNORE INTO recipes (id, product_id, recipe_type_id, yield_quantity) VALUES
    (1,  1,  1, 1.0), (2,  2,  1, 1.0), (3,  6,  1, 1.0), (4,  10, 1, 1.0),
    (5,  14, 1, 1.0), (6,  18, 1, 1.0), (7,  23, 1, 1.0), (8,  28, 1, 1.0),
    (9,  30, 1, 1.0), (10, 35, 1, 1.0), (11, 39, 1, 1.0), (12, 43, 1, 1.0),
    (13, 4,  1, 1.0), (14, 25, 1, 1.0), (15, 3,  1, 1.0), (16, 5,  1, 1.0),
    (17, 8,  1, 1.0), (18, 11, 1, 1.0), (19, 12, 1, 1.0), (20, 13, 1, 1.0),
    (21, 15, 1, 1.0), (22, 16, 1, 1.0), (23, 17, 1, 1.0), (24, 20, 1, 1.0),
    (25, 22, 1, 1.0), (26, 24, 1, 1.0), (27, 26, 1, 1.0), (28, 27, 1, 1.0),
    (29, 31, 1, 1.0), (30, 32, 1, 1.0), (31, 34, 1, 1.0), (32, 36, 1, 1.0),
    (33, 37, 1, 1.0), (34, 38, 1, 1.0), (35, 40, 1, 1.0), (36, 41, 1, 1.0),
    (37, 42, 1, 1.0), (38, 44, 1, 1.0), (39, 45, 1, 1.0), (40, 46, 1, 1.0),
    (41, 47, 1, 1.0);

-- 6. Recipe ingredients
INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation_note) VALUES
    (1, 1,  0.150, 'kg',   'Grilled chicken patty'),
    (1, 33, 1.0,   'unit', 'Toasted bun'),
    (1, 32, 0.020, 'kg',   'Spread on bun'),
    (1, 31, 0.015, 'kg',   'For serving'),
    (1, 23, 0.020, 'kg',   'Shredded lettuce'),
    (1, 7,  0.030, 'kg',   'Sliced tomato'),
    (2, 2,  0.150, 'kg',   'Beef patty'),
    (2, 33, 1.0,   'unit', 'Toasted bun'),
    (2, 32, 0.020, 'kg',   'Mayonnaise'),
    (2, 31, 0.015, 'kg',   'Ketchup'),
    (2, 23, 0.020, 'kg',   'Lettuce'),
    (2, 7,  0.030, 'kg',   'Tomato slices'),
    (3, 30, 0.250, 'kg',   'Pizza dough base'),
    (3, 11, 0.080, 'kg',   'Spread evenly'),
    (3, 10, 0.150, 'kg',   'Mozzarella topping'),
    (3, 1,  0.150, 'kg',   'Diced chicken breast'),
    (3, 24, 0.030, 'kg',   'Capsicum slices'),
    (3, 8,  0.030, 'kg',   'Onion rings'),
    (4, 1,  0.400, 'kg',   'Marinated overnight'),
    (4, 9,  0.060, 'kg',   'For marinade'),
    (4, 25, 0.020, 'kg',   'Ginger garlic paste'),
    (4, 20, 0.015, 'kg',   'Tikka masala spices'),
    (4, 6,  0.040, 'liter', 'For basting'),
    (5, 4,  0.250, 'kg',   'Soaked for 30 min'),
    (5, 1,  0.200, 'kg',   'Marinated chicken'),
    (5, 9,  0.040, 'kg',   'For layering'),
    (5, 8,  0.050, 'kg',   'Fried until golden'),
    (5, 7,  0.040, 'kg',   'Chopped'),
    (5, 20, 0.010, 'kg',   'Biryani masala'),
    (5, 6,  0.030, 'liter', 'For cooking'),
    (5, 21, 0.083, 'dozen', 'Boiled eggs for topping'),
    (6, 1,  0.400, 'kg',   'Cut into pieces'),
    (6, 7,  0.150, 'kg',   'Pureed for gravy'),
    (6, 8,  0.080, 'kg',   'Sliced'),
    (6, 25, 0.020, 'kg',   'Ginger garlic paste'),
    (6, 20, 0.012, 'kg',   'Karahi masala'),
    (6, 6,  0.050, 'liter', 'For cooking'),
    (6, 9,  0.050, 'kg',   'Yogurt for gravy'),
    (7, 12, 0.200, 'kg',   'Deep fry at 180°C'),
    (7, 27, 0.002, 'kg',   'Season after frying'),
    (9, 28, 0.005, 'kg',   'Boil with water'),
    (9, 17, 0.150, 'liter', 'Add after boiling'),
    (9, 16, 0.010, 'kg',   'To taste'),
    (10, 37, 0.100, 'kg',  'Mix with water to form dough'),
    (10, 6,  0.050, 'liter', 'Deep fry on low heat'),
    (10, 16, 0.080, 'kg',  'Sugar syrup with cardamom'),
    (11, 1,  0.200, 'kg',  'Diced, marinated in soy sauce'),
    (11, 36, 0.020, 'liter', 'For sauce'),
    (11, 35, 0.100, 'kg',  'For serving'),
    (11, 24, 0.030, 'kg',  'Diced capsicum'),
    (11, 8,  0.030, 'kg',  'Diced onion'),
    (12, 5,  0.200, 'kg',  'Knead with oil for puri'),
    (12, 16, 0.060, 'kg',  'For halwa'),
    (12, 6,  0.040, 'liter', 'For deep frying puri'),
    (12, 38, 0.020, 'kg',  'For halwa consistency'),
    (13, 1,  0.100, 'kg',  'Grilled chicken slices'),
    (13, 33, 1.5,   'unit', 'Toasted bread slices'),
    (13, 32, 0.020, 'kg',  'Mayonnaise'),
    (13, 23, 0.020, 'kg',  'Lettuce'),
    (13, 7,  0.030, 'kg',  'Tomato slices'),
    (13, 21, 0.083, 'dozen', 'Boiled egg slices'),
    (14, 34, 0.400, 'kg',  'Marinated in spicy sauce'),
    (14, 6,  0.030, 'liter', 'Deep fry'),
    (14, 20, 0.010, 'kg',  'Seasoning'),
    (15, 1,  0.180, 'kg',  'Crispy fried chicken fillet'),
    (15, 33, 1.0,   'unit', 'Toasted bun with sesame'),
    (15, 5,  0.050, 'kg',  'Flour coating with spices'),
    (15, 32, 0.025, 'kg',  'Garlic mayo spread'),
    (15, 23, 0.020, 'kg',  'Shredded lettuce'),
    (15, 7,  0.030, 'kg',  'Sliced tomato'),
    (15, 6,  0.030, 'liter', 'Deep frying'),
    (16, 5,  0.100, 'kg',  'Paratha dough'),
    (16, 1,  0.150, 'kg',  'Spiced chicken filling'),
    (16, 8,  0.030, 'kg',  'Caramelized onions'),
    (16, 24, 0.020, 'kg',  'Thinly sliced capsicum'),
    (16, 32, 0.015, 'kg',  'Mayonnaise drizzle'),
    (16, 6,  0.020, 'liter', 'For cooking paratha'),
    (17, 30, 0.250, 'kg',  'Pizza dough base'),
    (17, 11, 0.080, 'kg',  'Fajita sauce spread'),
    (17, 10, 0.150, 'kg',  'Mozzarella topping'),
    (17, 1,  0.150, 'kg',  'Fajita spiced chicken'),
    (17, 24, 0.030, 'kg',  'Capsicum strips'),
    (17, 8,  0.030, 'kg',  'Onion rings'),
    (17, 7,  0.040, 'kg',  'Diced tomatoes'),
    (18, 2,  0.400, 'kg',  'Minced beef blend'),
    (18, 8,  0.040, 'kg',  'Finely chopped onion'),
    (18, 25, 0.015, 'kg',  'Ginger garlic paste'),
    (18, 26, 0.010, 'kg',  'Chopped green chilies'),
    (18, 20, 0.012, 'kg',  'Kebab masala spices'),
    (18, 27, 0.003, 'kg',  'Seasoning'),
    (18, 21, 0.083, 'dozen', 'Egg for binding'),
    (19, 1,  1.200, 'kg',  'Whole chicken'),
    (19, 9,  0.150, 'kg',  'Yogurt marinade'),
    (19, 25, 0.030, 'kg',  'Ginger garlic paste'),
    (19, 20, 0.020, 'kg',  'Chargah masala'),
    (19, 6,  0.060, 'liter', 'Basting oil'),
    (19, 27, 0.005, 'kg',  'Salt'),
    (20, 3,  0.400, 'kg',  'Mutton chunks'),
    (20, 9,  0.080, 'kg',  'Yogurt marinade'),
    (20, 25, 0.020, 'kg',  'Ginger garlic paste'),
    (20, 20, 0.015, 'kg',  'Tikka masala'),
    (20, 6,  0.030, 'liter', 'For basting'),
    (20, 41, 0.010, 'kg',  'Dried fenugreek leaves'),
    (21, 4,  0.250, 'kg',  'Soaked basmati rice'),
    (21, 3,  0.200, 'kg',  'Mutton pieces'),
    (21, 9,  0.050, 'kg',  'For marination'),
    (21, 8,  0.060, 'kg',  'Fried onions'),
    (21, 7,  0.050, 'kg',  'Chopped tomatoes'),
    (21, 20, 0.012, 'kg',  'Biryani masala'),
    (21, 6,  0.035, 'liter', 'For cooking'),
    (21, 17, 0.050, 'liter', 'Warm milk for layering'),
    (21, 41, 0.005, 'kg',  'Fresh mint leaves'),
    (22, 4,  0.250, 'kg',  'Basmati rice'),
    (22, 9,  0.050, 'kg',  'Yogurt'),
    (22, 8,  0.050, 'kg',  'Sliced onions'),
    (22, 7,  0.050, 'kg',  'Chopped tomatoes'),
    (22, 22, 0.080, 'kg',  'Potato cubes'),
    (22, 42, 0.050, 'kg',  'Mixed vegetables'),
    (22, 20, 0.010, 'kg',  'Biryani masala'),
    (22, 6,  0.030, 'liter', 'For cooking'),
    (23, 4,  0.200, 'kg',  'Cooked basmati rice, cooled'),
    (23, 1,  0.150, 'kg',  'Diced chicken'),
    (23, 21, 0.083, 'dozen', 'Scrambled egg'),
    (23, 8,  0.030, 'kg',  'Diced onion'),
    (23, 42, 0.040, 'kg',  'Mixed vegetables'),
    (23, 36, 0.010, 'liter', 'Soy sauce'),
    (23, 6,  0.020, 'liter', 'For stir-frying'),
    (24, 3,  0.400, 'kg',  'Mutton pieces on bone'),
    (24, 7,  0.150, 'kg',  'Pureed tomatoes'),
    (24, 8,  0.080, 'kg',  'Sliced onion'),
    (24, 25, 0.020, 'kg',  'Ginger garlic paste'),
    (24, 20, 0.012, 'kg',  'Karahi masala'),
    (24, 6,  0.050, 'liter', 'Cooking oil'),
    (24, 9,  0.050, 'kg',  'Yogurt for gravy'),
    (24, 26, 0.010, 'kg',  'Green chilies for garnish'),
    (25, 39, 0.200, 'kg',  'Black lentils, soaked overnight'),
    (25, 7,  0.060, 'kg',  'Tomato puree'),
    (25, 8,  0.030, 'kg',  'Finely chopped onion'),
    (25, 25, 0.010, 'kg',  'Ginger garlic paste'),
    (25, 18, 0.030, 'liter', 'Fresh cream'),
    (25, 43, 0.020, 'kg',  'Butter'),
    (25, 20, 0.008, 'kg',  'Masala spices'),
    (26, 1,  0.200, 'kg',  'Minced chicken'),
    (26, 5,  0.060, 'kg',  'Bread crumb coating'),
    (26, 21, 0.083, 'dozen', 'Egg wash'),
    (26, 27, 0.002, 'kg',  'Seasoning'),
    (26, 6,  0.040, 'liter', 'Deep frying'),
    (27, 44, 0.100, 'kg',  'Spring roll pastry sheets'),
    (27, 23, 0.050, 'kg',  'Shredded cabbage'),
    (27, 1,  0.080, 'kg',  'Minced chicken'),
    (27, 42, 0.030, 'kg',  'Shredded carrots and beans'),
    (27, 36, 0.005, 'liter', 'Soy sauce'),
    (27, 6,  0.030, 'liter', 'Deep frying'),
    (28, 1,  0.150, 'kg',  'Shredded chicken'),
    (28, 35, 0.050, 'kg',  'Egg noodles'),
    (28, 42, 0.030, 'kg',  'Fine chopped vegetables'),
    (28, 25, 0.005, 'kg',  'Ginger paste'),
    (28, 36, 0.010, 'liter', 'Soy sauce'),
    (28, 21, 0.042, 'dozen', 'Egg drop'),
    (29, 29, 0.010, 'kg',  'Brewed coffee grounds'),
    (29, 17, 0.150, 'liter', 'Hot milk'),
    (29, 18, 0.020, 'liter', 'Whipped cream topping'),
    (29, 16, 0.008, 'kg',  'Sugar to taste'),
    (30, 17, 0.250, 'liter', 'Full cream milk'),
    (30, 19, 0.080, 'kg',  'Vanilla ice cream'),
    (30, 16, 0.015, 'kg',  'Sugar'),
    (30, 18, 0.020, 'liter', 'Whipped cream topping'),
    (31, 9,  0.200, 'kg',  'Fresh yogurt'),
    (31, 17, 0.100, 'liter', 'Chilled milk'),
    (31, 16, 0.015, 'kg',  'Sugar'),
    (31, 45, 0.002, 'kg',  'Cardamom powder'),
    (32, 17, 0.300, 'liter', 'Full cream milk'),
    (32, 18, 0.100, 'liter', 'Heavy cream'),
    (32, 16, 0.050, 'kg',  'Sugar'),
    (32, 19, 0.050, 'kg',  'Vanilla essence'),
    (33, 4,  0.080, 'kg',  'Broken basmati rice'),
    (33, 17, 0.500, 'liter', 'Full cream milk'),
    (33, 16, 0.060, 'kg',  'Sugar'),
    (33, 45, 0.003, 'kg',  'Cardamom pods'),
    (33, 46, 0.015, 'kg',  'Chopped almonds and pistachios'),
    (34, 5,  0.080, 'kg',  'Brownie batter flour'),
    (34, 43, 0.040, 'kg',  'Butter'),
    (34, 16, 0.040, 'kg',  'Sugar'),
    (34, 21, 0.083, 'dozen', 'Eggs'),
    (34, 19, 0.080, 'kg',  'Vanilla ice cream scoop'),
    (35, 35, 0.150, 'kg',  'Egg noodles'),
    (35, 42, 0.050, 'kg',  'Mixed vegetables'),
    (35, 36, 0.010, 'liter', 'Soy sauce'),
    (35, 6,  0.015, 'liter', 'For stir-frying'),
    (35, 24, 0.020, 'kg',  'Capsicum strips'),
    (36, 35, 0.150, 'kg',  'Egg noodles'),
    (36, 1,  0.100, 'kg',  'Shredded chicken'),
    (36, 42, 0.040, 'kg',  'Mixed vegetables'),
    (36, 36, 0.012, 'liter', 'Soy sauce'),
    (36, 6,  0.015, 'liter', 'For stir-frying'),
    (36, 21, 0.083, 'dozen', 'Scrambled egg'),
    (37, 1,  0.250, 'kg',  'Diced chicken thigh'),
    (37, 48, 0.080, 'kg',  'Roasted peanuts'),
    (37, 36, 0.015, 'liter', 'Soy sauce'),
    (37, 24, 0.030, 'kg',  'Diced capsicum'),
    (37, 8,  0.030, 'kg',  'Spring onion'),
    (37, 6,  0.020, 'liter', 'Stir-fry oil'),
    (37, 26, 0.010, 'kg',  'Dried red chilies'),
    (38, 39, 0.250, 'kg',  'Chickpeas, soaked overnight'),
    (38, 8,  0.040, 'kg',  'Finely chopped onion'),
    (38, 7,  0.050, 'kg',  'Tomato puree'),
    (38, 25, 0.010, 'kg',  'Ginger garlic paste'),
    (38, 20, 0.010, 'kg',  'Chana masala'),
    (38, 6,  0.020, 'liter', 'For cooking'),
    (38, 26, 0.008, 'kg',  'Green chilies'),
    (39, 21, 0.250, 'dozen', '3 eggs'),
    (39, 8,  0.020, 'kg',  'Chopped onion'),
    (39, 7,  0.020, 'kg',  'Diced tomato'),
    (39, 26, 0.005, 'kg',  'Chopped green chili'),
    (39, 27, 0.002, 'kg',  'Salt and pepper'),
    (39, 6,  0.010, 'liter', 'For cooking'),
    (40, 2,  0.400, 'kg',  'Beef shank, bone-in'),
    (40, 5,  0.040, 'kg',  'Nihari flour paste (for thickening)'),
    (40, 25, 0.020, 'kg',  'Ginger garlic paste'),
    (40, 20, 0.012, 'kg',  'Nihari masala'),
    (40, 6,  0.030, 'liter', 'For slow cooking'),
    (40, 25, 0.010, 'kg',  'Julienned ginger for garnish'),
    (41, 3,  0.500, 'kg',  'Goat trotters/shanks'),
    (41, 5,  0.030, 'kg',  'Flour paste for thickening'),
    (41, 25, 0.020, 'kg',  'Ginger garlic paste'),
    (41, 8,  0.040, 'kg',  'Onion slices'),
    (41, 20, 0.012, 'kg',  'Paye masala'),
    (41, 6,  0.020, 'liter', 'Cooking oil'),
    (41, 25, 0.010, 'kg',  'Fresh ginger strips for garnish');

-- 7. Employees (12 sample staff)
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

-- 8. Sample sales (12 transactions)
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, table_number, delivery_type_id, delivery_address, employee_id) VALUES
    (1,  1360.00, 'PKR', '2026-01-10', '13:15:00', 'dine_in',   'completed', 3,  NULL, NULL,                                4),
    (2,  2000.00, 'PKR', '2026-01-10', '14:00:00', 'dine_in',   'completed', 7,  NULL, NULL,                                5),
    (3,  1250.00, 'PKR', '2026-01-10', '19:30:00', 'takeaway',  'completed', NULL, NULL, NULL,                                6),
    (4,  2060.00, 'PKR', '2026-01-11', '12:45:00', 'delivery',  'completed', NULL, 1,    'House 12, Street 5, Gulshan Colony', 8),
    (5,  2010.00, 'PKR', '2026-01-11', '20:00:00', 'dine_in',   'completed', 1,   NULL, NULL,                                4),
    (6,  1020.00, 'PKR', '2026-01-12', '09:30:00', 'takeaway',  'completed', NULL, NULL, NULL,                                6),
    (7,  1450.00, 'PKR', '2026-01-12', '13:30:00', 'delivery',  'completed', NULL, 2,    'Flat 4B, Green Heights, Main Road', 9),
    (8,  2990.00, 'PKR', '2026-01-12', '21:00:00', 'dine_in',   'completed', 10,  NULL, NULL,                                5),
    (9,  1550.00, 'PKR', '2026-01-13', '14:30:00', 'dine_in',   'completed', 5,   NULL, NULL,                                11),
    (10, 1000.00, 'PKR', '2026-01-13', '19:00:00', 'delivery',  'completed', NULL, 1,    'Street 12, Block C, Model Town',     8),
    (11, 1060.00, 'PKR', '2026-01-14', '11:00:00', 'dine_in',   'completed', 8,   NULL, NULL,                                6),
    (12, 620.00,  'PKR', '2026-01-14', '16:30:00', 'takeaway',  'completed', NULL, NULL, NULL,                                11);

-- 9. Sale items
INSERT OR IGNORE INTO sale_items (sale_id, product_name, price, quantity, unit) VALUES
    (1,  'Chicken Burger',             350.00, 2, 'item'),
    (1,  'French Fries',               200.00, 1, 'plate'),
    (1,  'Soft Drink (500ml)',         80.00,  2, 'bottle'),
    (1,  'Gulab Jamun (4 pcs)',        150.00, 2, 'plate'),
    (2,  'Chicken Pizza (Medium)',     800.00, 1, 'item'),
    (2,  'Chicken Karahi (Half)',      900.00, 1, 'item'),
    (2,  'Soft Drink (500ml)',         80.00,  1, 'bottle'),
    (2,  'Mineral Water (1.5L)',       60.00,  1, 'bottle'),
    (2,  'Tea',                        80.00,  2, 'cup'),
    (3,  'Zinger Burger',              450.00, 1, 'item'),
    (3,  'Club Sandwich',              350.00, 1, 'item'),
    (3,  'Chicken Biryani',            250.00, 1, 'plate'),
    (3,  'French Fries',               200.00, 1, 'plate'),
    (4,  'Chicken Pizza (Large)',      1200.00, 1, 'item'),
    (4,  'Chicken Wings (6 pcs)',      350.00, 1, 'plate'),
    (4,  'Soft Drink (500ml)',         80.00,  2, 'bottle'),
    (4,  'Brownie with Ice Cream',     350.00, 1, 'item'),
    (5,  'Chicken Tikka (4 pcs)',      450.00, 2, 'plate'),
    (5,  'Beef Seekh Kebab (6 pcs)',   350.00, 2, 'plate'),
    (5,  'Daal Makhni',                250.00, 1, 'plate'),
    (5,  'Tea',                        80.00,  2, 'cup'),
    (6,  'Halwa Puri (2 puri)',        180.00, 2, 'plate'),
    (6,  'Chana Cholay',               200.00, 1, 'plate'),
    (6,  'Omelette',                   150.00, 2, 'plate'),
    (6,  'Tea',                        80.00,  2, 'cup'),
    (7,  'Fajita Pizza (Medium)',      900.00, 1, 'item'),
    (7,  'Chicken Nuggets (6 pcs)',    300.00, 1, 'plate'),
    (7,  'Milkshake',                  250.00, 1, 'glass'),
    (8,  'Mutton Karahi (Full)',       2200.00, 1, 'item'),
    (8,  'Chicken Biryani',            250.00, 1, 'plate'),
    (8,  'Soft Drink (500ml)',         80.00,  3, 'bottle'),
    (8,  'Kheer',                      150.00, 2, 'bowl'),
    (9,  'Chicken Karahi (Half)',      900.00, 1, 'item'),
    (9,  'Chicken Fried Rice',         300.00, 1, 'plate'),
    (9,  'Fruit Juice',                200.00, 1, 'glass'),
    (9,  'Gulab Jamun (4 pcs)',        150.00, 1, 'plate'),
    (10, 'Beef Burger',                400.00, 1, 'item'),
    (10, 'Chicken Manchurian',         350.00, 1, 'plate'),
    (10, 'Veg Noodles',                250.00, 1, 'plate'),
    (11, 'Nihari',                     300.00, 1, 'bowl'),
    (11, 'Siri Paye',                  350.00, 1, 'bowl'),
    (11, 'Paratha Roll',               250.00, 1, 'item'),
    (11, 'Tea',                        80.00,  2, 'cup'),
    (12, 'Chicken Biryani',            250.00, 2, 'plate'),
    (12, 'Mineral Water (1.5L)',       60.00,  2, 'bottle');

-- 10. Inventory transactions
INSERT OR IGNORE INTO inventory_transactions (id, ingredient_id, transaction_type, quantity_change, note) VALUES
    (1,  1,  'purchase',  30.0,  'Initial stock - Chicken Breast'),
    (2,  2,  'purchase',  20.0,  'Initial stock - Beef Mince'),
    (3,  3,  'purchase',  10.0,  'Initial stock - Mutton'),
    (4,  4,  'purchase',  25.0,  'Initial stock - Basmati Rice'),
    (5,  5,  'purchase',  35.0,  'Initial stock - Wheat Flour'),
    (6,  6,  'purchase',  30.0,  'Initial stock - Cooking Oil'),
    (7,  7,  'purchase',  20.0,  'Initial stock - Tomato'),
    (8,  8,  'purchase',  25.0,  'Initial stock - Onion'),
    (9,  9,  'purchase',  15.0,  'Initial stock - Yogurt'),
    (10, 10, 'purchase',  10.0,  'Initial stock - Mozzarella Cheese'),
    (11, 1,  'purchase',  20.0,  'Weekly restock - Chicken Breast'),
    (12, 6,  'purchase',  15.0,  'Weekly restock - Cooking Oil'),
    (13, 7,  'purchase',  12.0,  'Weekly restock - Tomato'),
    (14, 8,  'purchase',  15.0,  'Weekly restock - Onion'),
    (15, 14, 'purchase',  10.0,  'Weekly restock - Soda Crates'),
    (16, 15, 'purchase',  12.0,  'Weekly restock - Water Bottles'),
    (17, 1,  'usage',     -5.0,  'Usage: Week 1 sales - Chicken items'),
    (18, 2,  'usage',     -3.0,  'Usage: Week 1 sales - Beef items'),
    (19, 4,  'usage',     -4.0,  'Usage: Week 1 sales - Rice dishes'),
    (20, 6,  'usage',     -8.0,  'Usage: Week 1 - Cooking'),
    (21, 7,  'usage',     -5.0,  'Usage: Week 1 - Vegetable prep'),
    (22, 8,  'usage',     -6.0,  'Usage: Week 1 - Vegetable prep'),
    (23, 10, 'usage',     -2.0,  'Usage: Week 1 - Pizza prep'),
    (24, 12, 'usage',     -3.0,  'Usage: Week 1 - Fries orders'),
    (25, 14, 'usage',     -4.0,  'Usage: Week 1 - Soda sales'),
    (26, 15, 'usage',     -5.0,  'Usage: Week 1 - Water sales'),
    (27, 7,  'waste',     -0.5,  'Spoiled tomatoes'),
    (28, 17, 'waste',     -1.0,  'Expired milk'),
    (29, 22, 'waste',     -0.8,  'Spoiled potatoes'),
    (30, 1,  'adjustment', -0.5, 'Adjustment: Count variance on chicken breast'),
    (31, 8,  'adjustment', -1.0, 'Adjustment: Weight discrepancy on onions');

-- 11. Inventory adjustments
INSERT OR IGNORE INTO inventory_adjustments (id, ingredient_id, previous_quantity, new_quantity, reason, created_by) VALUES
    (1, 1, 25.0, 24.5, 'Count correction - found 0.5kg less chicken',       'Ali Ahmed'),
    (2, 8, 20.0, 19.0, 'Count correction - weight discrepancy in onions',   'Usman Khan');

-- 12. Employee schedules (FK references employees 1-12)
INSERT OR IGNORE INTO employee_schedules (id, employee_id, shift_start, shift_end, status, notes) VALUES
    (1, 1, '2026-07-14 09:00:00', '2026-07-14 17:00:00', 'scheduled', 'Manager morning shift'),
    (2, 2, '2026-07-14 09:00:00', '2026-07-14 17:00:00', 'scheduled', 'Chef AM'),
    (3, 3, '2026-07-14 14:00:00', '2026-07-14 22:00:00', 'scheduled', 'Chef PM'),
    (4, 4, '2026-07-14 09:00:00', '2026-07-14 17:00:00', 'scheduled', 'Waiter AM'),
    (5, 5, '2026-07-14 14:00:00', '2026-07-14 22:00:00', 'scheduled', 'Waiter PM'),
    (6, 6, '2026-07-14 14:00:00', '2026-07-14 22:00:00', 'scheduled', 'Waiter PM'),
    (7, 7, '2026-07-14 09:00:00', '2026-07-14 17:00:00', 'scheduled', 'Cashier AM'),
    (8, 1, '2026-07-15 09:00:00', '2026-07-15 17:00:00', 'scheduled', 'Manager morning shift'),
    (9, 2, '2026-07-15 14:00:00', '2026-07-15 22:00:00', 'scheduled', 'Chef PM'),
    (10, 8, '2026-07-15 09:00:00', '2026-07-15 17:00:00', 'scheduled', 'Delivery driver AM'),
    (11, 9, '2026-07-15 14:00:00', '2026-07-15 22:00:00', 'scheduled', 'Delivery driver PM'),
    (12, 10, '2026-07-15 09:00:00', '2026-07-15 13:00:00', 'scheduled', 'Cleaner AM');

-- 13. Payroll records (FK references employees 1-10)
INSERT OR IGNORE INTO payrolls (id, employee_id, period_start, period_end, regular_hours, overtime_hours, total_pay, status) VALUES
    (1, 1, '2026-07-01', '2026-07-14', 80, 4, 30000.00, 'paid'),
    (2, 2, '2026-07-01', '2026-07-14', 80, 8, 23500.00, 'paid'),
    (3, 3, '2026-07-01', '2026-07-14', 80, 5, 21000.00, 'paid'),
    (4, 4, '2026-07-01', '2026-07-14', 80, 2, 13000.00, 'paid'),
    (5, 5, '2026-07-01', '2026-07-14', 80, 3, 13000.00, 'paid'),
    (6, 6, '2026-07-01', '2026-07-14', 80, 0, 12500.00, 'paid'),
    (7, 7, '2026-07-01', '2026-07-14', 80, 6, 16000.00, 'paid'),
    (8, 10, '2026-07-01', '2026-07-14', 40, 0, 4500.00, 'paid');

-- 14. Inventory alerts (FK references base ingredients 3,10,29,37,18)
INSERT OR IGNORE INTO inventory_alerts (id, ingredient_id, alert_type, alert_message, is_resolved) VALUES
    (1, 3, 'low_stock', 'Mutton is running low (below 5kg reorder level)', 0),
    (2, 10, 'low_stock', 'Mozzarella Cheese is low (below 4kg reorder level)', 0),
    (3, 29, 'low_stock', 'Coffee Beans nearly depleted (below 0.5kg)', 0),
    (4, 37, 'low_stock', 'Gulab Jamun Mix is running low', 0),
    (5, 18, 'low_stock', 'Cream stock is low', 0);

-- 15. Purchase orders (FK references suppliers 1-6)
INSERT OR IGNORE INTO purchase_orders (id, supplier_id, reference_number, status, total_amount, expected_date, notes) VALUES
    (1, 1, 'PO-2026-001', 'received', 45000.00, '2026-07-10 10:00:00', 'Weekly fresh produce order'),
    (2, 2, 'PO-2026-002', 'received', 32000.00, '2026-07-11 08:00:00', 'Bi-weekly meat supply'),
    (3, 3, 'PO-2026-003', 'pending', 18500.00, '2026-07-18 10:00:00', 'Dry goods and spices restock'),
    (4, 4, 'PO-2026-004', 'received', 12000.00, '2026-07-12 09:00:00', 'Beverages for the month'),
    (5, 5, 'PO-2026-005', 'draft', 8900.00, '2026-07-20 08:00:00', 'Fresh vegetables order'),
    (6, 6, 'PO-2026-006', 'pending', 25000.00, '2026-07-19 11:00:00', 'Monthly wholesale supplies');

-- 16. Purchase order items (FK references base ingredients)
INSERT OR IGNORE INTO purchase_order_items (id, purchase_order_id, ingredient_id, quantity, cost_per_unit, received_quantity) VALUES
    (1, 1, 7, 25.0, 85.0, 25.0),
    (2, 1, 8, 30.0, 65.0, 30.0),
    (3, 1, 22, 30.0, 45.0, 30.0),
    (4, 1, 42, 20.0, 75.0, 20.0),
    (5, 1, 50, 10.0, 90.0, 10.0),
    (6, 2, 1, 30.0, 420.0, 30.0),
    (7, 2, 2, 20.0, 520.0, 20.0),
    (8, 2, 3, 15.0, 1050.0, 15.0),
    (9, 3, 4, 25.0, 170.0, 0.0),
    (10, 3, 5, 30.0, 65.0, 0.0),
    (11, 3, 20, 5.0, 230.0, 0.0),
    (12, 3, 53, 3.0, 330.0, 0.0),
    (13, 3, 55, 5.0, 280.0, 0.0),
    (14, 4, 14, 20.0, 450.0, 20.0),
    (15, 4, 15, 15.0, 340.0, 15.0),
    (16, 5, 7, 15.0, 88.0, 0.0),
    (17, 5, 8, 20.0, 68.0, 0.0),
    (18, 5, 26, 5.0, 125.0, 0.0),
    (19, 6, 6, 30.0, 300.0, 0.0),
    (20, 6, 10, 12.0, 720.0, 0.0),
    (21, 6, 11, 8.0, 360.0, 0.0),
    (22, 6, 16, 20.0, 100.0, 0.0);

-- [SECTION:gaming]
-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║  Gaming center preset — standalone replacement for base.                ║
-- ║  Seeded for gaming and all presets.                                     ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

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
    (13, 'Energy Drink',                  3.00, 1, 'item'),
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

-- 9. Gaming center logo
UPDATE settings SET logo = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNTYiIGhlaWdodD0iMjU2IiB2aWV3Qm94PSIwIDAgMjU2IDI1NiI+CiAgPGRlZnM+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImJnIiBjeD0iNTAlIiBjeT0iNTAlIiByPSI1MCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMWUzYTVmIi8+CiAgICAgIDxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iIzBhMGYxZSIvPgogICAgPC9yYWRpYWxHcmFkaWVudD4KICAgIDxsaW5lYXJHcmFkaWVudCBpZD0iZ3JkIiB4MT0iMCUiIHkxPSIwJSIgeDI9IjEwMCUiIHkyPSIxMDAlIj4KICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzAwYjRkOCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwMDc3YjYiLz4KICAgIDwvbGluZWFyR3JhZGllbnQ+CiAgPC9kZWZzPgogIDxyZWN0IHdpZHRoPSIyNTYiIGhlaWdodD0iMjU2IiByeD0iNDgiIGZpbGw9InVybCgjYmcpIi8+CiAgPGNpcmNsZSBjeD0iMTI4IiBjeT0iMTI4IiByPSI5MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ1cmwoI2dyZCkiIHN0cm9rZS13aWR0aD0iNiIgb3BhY2l0eT0iMC42Ii8+CiAgPHRleHQgeD0iMTI4IiB5PSIxNTgiIGZvbnQtc2l6ZT0iOTAiIHRleHQtYW5jaG9yPSJtaWRkbGUiCiAgICAgICAgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSxzYW5zLXNlcmlmIj7wn46uPC90ZXh0PgogIDx0ZXh0IHg9IjEyOCIgeT0iMjIwIiBmb250LXNpemU9IjIyIiBmb250LXdlaWdodD0iNzAwIiBmaWxsPSIjMDBiNGQ4IgogICAgICAgIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksc2Fucy1zZXJpZiIgbGV0dGVyLXNwYWNpbmc9IjMiPkxldmVsIFVwIEdDPC90ZXh0Pgo8L3N2Zz4=' WHERE id = 1;

-- [SECTION:coffee]
-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║  Coffee shop preset — layered on top of base. Seeded for coffee and all.║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

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
