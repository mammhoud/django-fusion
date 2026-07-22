-- Settings (singleton)
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    restaurant_name TEXT,
    address TEXT,
    phone TEXT,
    email TEXT,
    tax_rate TEXT,
    currency TEXT NOT NULL DEFAULT 'PKR',
    opening_time TEXT,
    closing_time TEXT,
    receipt_footer TEXT,
    logo TEXT,
    dine_in_tables INTEGER NOT NULL DEFAULT 0,
    delivery_fee REAL NOT NULL DEFAULT 0.0,
    delivery_fee_per_km REAL NOT NULL DEFAULT 0.0
);

-- Categories
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Products
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    unit TEXT NOT NULL DEFAULT 'item',
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    uploaded BOOLEAN NOT NULL DEFAULT 0
);

-- Delivery types
CREATE TABLE IF NOT EXISTS delivery_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    fee_multiplier REAL NOT NULL DEFAULT 1.0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Employee types
CREATE TABLE IF NOT EXISTS employee_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Employees
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    employee_type_id INTEGER NOT NULL REFERENCES employee_types(id),
    salary REAL NOT NULL DEFAULT 0.0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    joined_at TEXT DEFAULT (date('now')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    uploaded BOOLEAN NOT NULL DEFAULT 0
);

-- Sales header
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total_amount REAL NOT NULL,
    currency TEXT NOT NULL,
    date TEXT NOT NULL DEFAULT (date('now')),
    time TEXT NOT NULL DEFAULT (time('now')),
    order_type TEXT NOT NULL DEFAULT 'dine_in',
    status TEXT NOT NULL DEFAULT 'completed',
    table_number INTEGER,
    delivery_type_id INTEGER REFERENCES delivery_types(id),
    delivery_address TEXT,
    employee_id INTEGER REFERENCES employees(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    uploaded BOOLEAN NOT NULL DEFAULT 0
);

-- Sale items
CREATE TABLE IF NOT EXISTS sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    product_name TEXT NOT NULL,
    price REAL NOT NULL,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL,
    subtotal REAL GENERATED ALWAYS AS (price * quantity) STORED,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Ingredients
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    unit TEXT NOT NULL,
    current_quantity REAL NOT NULL DEFAULT 0.0,
    reorder_level REAL NOT NULL DEFAULT 0.0,
    reorder_quantity REAL NOT NULL DEFAULT 0.0,
    cost_per_unit REAL NOT NULL DEFAULT 0.0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    uploaded BOOLEAN NOT NULL DEFAULT 0
);

-- Recipe types
CREATE TABLE IF NOT EXISTS recipe_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Recipes
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    recipe_type_id INTEGER NOT NULL REFERENCES recipe_types(id),
    yield_quantity REAL NOT NULL DEFAULT 1.0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    uploaded BOOLEAN NOT NULL DEFAULT 0,
    UNIQUE(product_id, recipe_type_id)
);

-- Recipe ingredients
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id),
    quantity REAL NOT NULL,
    unit TEXT,
    preparation_note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Inventory transactions
CREATE TABLE IF NOT EXISTS inventory_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('purchase', 'usage', 'waste', 'adjustment', 'return')),
    quantity_change REAL NOT NULL,
    reference_id INTEGER,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    uploaded BOOLEAN NOT NULL DEFAULT 0
);

-- Inventory adjustments (manual corrections)
CREATE TABLE IF NOT EXISTS inventory_adjustments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    previous_quantity REAL NOT NULL,
    new_quantity REAL NOT NULL,
    reason TEXT NOT NULL,
    created_by TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    uploaded BOOLEAN NOT NULL DEFAULT 0
);

-- Triggers to auto-update `updated_at`
CREATE TRIGGER IF NOT EXISTS update_products_updated_at AFTER UPDATE ON products
BEGIN UPDATE products SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_sales_updated_at AFTER UPDATE ON sales
BEGIN UPDATE sales SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_categories_updated_at AFTER UPDATE ON categories
BEGIN UPDATE categories SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_ingredients_updated_at AFTER UPDATE ON ingredients
BEGIN UPDATE ingredients SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_recipe_types_updated_at AFTER UPDATE ON recipe_types
BEGIN UPDATE recipe_types SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_recipes_updated_at AFTER UPDATE ON recipes
BEGIN UPDATE recipes SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_recipe_ingredients_updated_at AFTER UPDATE ON recipe_ingredients
BEGIN UPDATE recipe_ingredients SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_delivery_types_updated_at AFTER UPDATE ON delivery_types
BEGIN UPDATE delivery_types SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_employee_types_updated_at AFTER UPDATE ON employee_types
BEGIN UPDATE employee_types SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_employees_updated_at AFTER UPDATE ON employees
BEGIN UPDATE employees SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

-- Insert default settings
INSERT OR IGNORE INTO settings (id, restaurant_name, currency, receipt_footer)
VALUES (1, 'Forge', 'PKR', 'Thank you for your business!');

-- Insert default delivery types
INSERT OR IGNORE INTO delivery_types (id, name, description, fee_multiplier) VALUES
    (1, 'Standard', 'Standard delivery (30-45 min)', 1.0),
    (2, 'Express', 'Express delivery (15-20 min)', 1.5),
    (3, 'Scheduled', 'Scheduled delivery for later time', 1.0);

-- Insert default employee types
INSERT OR IGNORE INTO employee_types (id, name, description) VALUES
    (1, 'Manager', 'Restaurant manager'),
    (2, 'Chef', 'Head chef / cook'),
    (3, 'Waiter', 'Service staff'),
    (4, 'Cashier', 'Cash register operator'),
    (5, 'Delivery Driver', 'Delivery personnel'),
    (6, 'Cleaner', 'Cleaning staff'),
    (7, 'Other', 'Other staff');

-- Insert default recipe types
INSERT OR IGNORE INTO recipe_types (id, name, description) VALUES
    (1, 'Standard', 'Default recipe for regular production'),
    (2, 'Custom', 'Customized recipe for specific orders'),
    (3, 'Seasonal', 'Seasonal variation');

-- ============================================================
-- SEED DATA (development defaults -- INSERT OR IGNORE for safety)
-- ============================================================

-- 1. Update settings with realistic defaults
UPDATE settings SET
    restaurant_name = 'Forge',
    address = '123 Main Boulevard, Gulberg, Lahore',
    phone = '+92-300-1234567',
    email = 'structa.cloud@gmail.com',
    tax_rate = '13',
    opening_time = '09:00',
    closing_time = '23:00',
    receipt_footer = 'Thank you for dining with us! Follow us @pos_app',
    dine_in_tables = 15,
    delivery_fee = 50.0,
    delivery_fee_per_km = 15.0
WHERE id = 1;

-- 2. Categories (food menu categories)
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

-- 3. Products (menu items)
INSERT OR IGNORE INTO products (id, name, price, unit, category_id) VALUES
    -- Burgers & Sandwiches
    (1,  'Chicken Burger',             350.00, 'item', 1),
    (2,  'Beef Burger',                400.00, 'item', 1),
    (3,  'Zinger Burger',              450.00, 'item', 1),
    (4,  'Club Sandwich',              350.00, 'item', 1),
    (5,  'Paratha Roll',               250.00, 'item', 1),
    -- Pizza
    (6,  'Chicken Pizza (Medium)',     800.00, 'item', 2),
    (7,  'Chicken Pizza (Large)',      1200.00, 'item', 2),
    (8,  'Fajita Pizza (Medium)',      900.00, 'item', 2),
    (9,  'Fajita Pizza (Large)',       1300.00, 'item', 2),
    -- BBQ & Grills
    (10, 'Chicken Tikka (4 pcs)',      450.00, 'plate', 3),
    (11, 'Beef Seekh Kebab (6 pcs)',   350.00, 'plate', 3),
    (12, 'Chargah (Full)',             1200.00, 'item', 3),
    (13, 'Mutton Tikka (4 pcs)',       600.00, 'plate', 3),
    -- Rice & Biryani
    (14, 'Chicken Biryani',            250.00, 'plate', 4),
    (15, 'Mutton Biryani',             350.00, 'plate', 4),
    (16, 'Vegetable Biryani',          200.00, 'plate', 4),
    (17, 'Chicken Fried Rice',         300.00, 'plate', 4),
    -- Karahi & Curries
    (18, 'Chicken Karahi (Half)',      900.00, 'item', 5),
    (19, 'Chicken Karahi (Full)',      1600.00, 'item', 5),
    (20, 'Mutton Karahi (Half)',       1200.00, 'item', 5),
    (21, 'Mutton Karahi (Full)',       2200.00, 'item', 5),
    (22, 'Daal Makhni',                250.00, 'plate', 5),
    -- Fast Food & Snacks
    (23, 'French Fries',               200.00, 'plate', 6),
    (24, 'Chicken Nuggets (6 pcs)',    300.00, 'plate', 6),
    (25, 'Chicken Wings (6 pcs)',      350.00, 'plate', 6),
    (26, 'Spring Rolls (6 pcs)',       250.00, 'plate', 6),
    (27, 'Chicken Soup',               250.00, 'bowl', 6),
    -- Beverages
    (28, 'Soft Drink (500ml)',         80.00,  'bottle', 7),
    (29, 'Mineral Water (1.5L)',       60.00,  'bottle', 7),
    (30, 'Tea',                        80.00,  'cup', 7),
    (31, 'Coffee',                     150.00, 'cup', 7),
    (32, 'Milkshake',                  250.00, 'glass', 7),
    (33, 'Fruit Juice',                200.00, 'glass', 7),
    (34, 'Lassi',                      120.00, 'glass', 7),
    -- Desserts
    (35, 'Gulab Jamun (4 pcs)',        150.00, 'plate', 8),
    (36, 'Ice Cream',                  120.00, 'scoop', 8),
    (37, 'Kheer',                      150.00, 'bowl', 8),
    (38, 'Brownie with Ice Cream',     350.00, 'item', 8),
    -- Chinese
    (39, 'Chicken Manchurian',         350.00, 'plate', 9),
    (40, 'Veg Noodles',                250.00, 'plate', 9),
    (41, 'Chicken Noodles',            300.00, 'plate', 9),
    (42, 'Kung Pao Chicken',           400.00, 'plate', 9),
    -- Breakfast
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
    (30, 'Pizza Dough Flour',     'kg',    10.0,  5.0,   10.0,  90.00),
    (31, 'Ketchup',                'kg',    5.0,   2.5,   5.0,   150.00),
    (32, 'Mayonnaise',             'kg',    4.0,   2.0,   3.0,   200.00),
    (33, 'Burger Buns',            'dozen', 8.0,   4.0,   6.0,   240.00),
    (34, 'Chicken Wings',          'kg',    10.0,  5.0,   10.0,  480.00),
    (35, 'Noodles',                'kg',    6.0,   3.0,   5.0,   150.00),
    (36, 'Soy Sauce',              'liter', 2.0,   1.0,   2.0,   180.00),
    (37, 'Gulab Jamun Mix',        'kg',    4.0,   2.0,   3.0,   280.00),
    (38, 'Rice Flour',             'kg',    3.0,   1.5,   3.0,   100.00),
    (39, 'Lentils (Daal Chana)',  'kg',    8.0,   4.0,   6.0,   140.00),
    (40, 'Mango Pulp',             'kg',    3.0,   1.0,   3.0,   350.00);

-- 5. Recipes
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

-- 6. Recipe ingredients
INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation_note) VALUES
    -- Chicken Burger
    (1, 1,  0.150, 'kg',   'Grilled chicken patty'),
    (1, 33, 1.0,   'unit', 'Toasted bun'),
    (1, 32, 0.020, 'kg',   'Spread on bun'),
    (1, 31, 0.015, 'kg',   'For serving'),
    (1, 23, 0.020, 'kg',   'Shredded lettuce'),
    (1, 7,  0.030, 'kg',   'Sliced tomato'),
    -- Beef Burger
    (2, 2,  0.150, 'kg',   'Beef patty'),
    (2, 33, 1.0,   'unit', 'Toasted bun'),
    (2, 32, 0.020, 'kg',   'Mayonnaise'),
    (2, 31, 0.015, 'kg',   'Ketchup'),
    (2, 23, 0.020, 'kg',   'Lettuce'),
    (2, 7,  0.030, 'kg',   'Tomato slices'),
    -- Chicken Pizza Medium
    (3, 30, 0.250, 'kg',   'Pizza dough base'),
    (3, 11, 0.080, 'kg',   'Spread evenly'),
    (3, 10, 0.150, 'kg',   'Mozzarella topping'),
    (3, 1,  0.150, 'kg',   'Diced chicken breast'),
    (3, 24, 0.030, 'kg',   'Capsicum slices'),
    (3, 8,  0.030, 'kg',   'Onion rings'),
    -- Chicken Tikka
    (4, 1,  0.400, 'kg',   'Marinated overnight'),
    (4, 9,  0.060, 'kg',   'For marinade'),
    (4, 25, 0.020, 'kg',   'Ginger garlic paste'),
    (4, 20, 0.015, 'kg',   'Tikka masala spices'),
    (4, 6,  0.040, 'liter', 'For basting'),
    -- Chicken Biryani
    (5, 4,  0.250, 'kg',   'Soaked for 30 min'),
    (5, 1,  0.200, 'kg',   'Marinated chicken'),
    (5, 9,  0.040, 'kg',   'For layering'),
    (5, 8,  0.050, 'kg',   'Fried until golden'),
    (5, 7,  0.040, 'kg',   'Chopped'),
    (5, 20, 0.010, 'kg',   'Biryani masala'),
    (5, 6,  0.030, 'liter', 'For cooking'),
    (5, 21, 0.083, 'dozen', 'Boiled eggs for topping'),
    -- Chicken Karahi Half
    (6, 1,  0.400, 'kg',   'Cut into pieces'),
    (6, 7,  0.150, 'kg',   'Pureed for gravy'),
    (6, 8,  0.080, 'kg',   'Sliced'),
    (6, 25, 0.020, 'kg',   'Ginger garlic paste'),
    (6, 20, 0.012, 'kg',   'Karahi masala'),
    (6, 6,  0.050, 'liter', 'For cooking'),
    (6, 9,  0.050, 'kg',   'Yogurt for gravy'),
    -- French Fries
    (7, 12, 0.200, 'kg',   'Deep fry at 180Â°C'),
    (7, 27, 0.002, 'kg',   'Season after frying'),
    -- Tea
    (9, 28, 0.005, 'kg',   'Boil with water'),
    (9, 17, 0.150, 'liter', 'Add after boiling'),
    (9, 16, 0.010, 'kg',   'To taste'),
    -- Gulab Jamun
    (10, 37, 0.100, 'kg',  'Mix with water to form dough'),
    (10, 6,  0.050, 'liter', 'Deep fry on low heat'),
    (10, 16, 0.080, 'kg',  'Sugar syrup with cardamom'),
    -- Chicken Manchurian
    (11, 1,  0.200, 'kg',  'Diced, marinated in soy sauce'),
    (11, 36, 0.020, 'liter', 'For sauce'),
    (11, 35, 0.100, 'kg',  'For serving'),
    (11, 24, 0.030, 'kg',  'Diced capsicum'),
    (11, 8,  0.030, 'kg',  'Diced onion'),
    -- Halwa Puri
    (12, 5,  0.200, 'kg',  'Knead with oil for puri'),
    (12, 16, 0.060, 'kg',  'For halwa'),
    (12, 6,  0.040, 'liter', 'For deep frying puri'),
    (12, 38, 0.020, 'kg',  'For halwa consistency'),
    -- Club Sandwich
    (13, 1,  0.100, 'kg',  'Grilled chicken slices'),
    (13, 33, 1.5,   'unit', 'Toasted bread slices'),
    (13, 32, 0.020, 'kg',  'Mayonnaise'),
    (13, 23, 0.020, 'kg',  'Lettuce'),
    (13, 7,  0.030, 'kg',  'Tomato slices'),
    (13, 21, 0.083, 'dozen', 'Boiled egg slices'),
    -- Chicken Wings
    (14, 34, 0.400, 'kg',  'Marinated in spicy sauce'),
    (14, 6,  0.030, 'liter', 'Deep fry'),
    (14, 20, 0.010, 'kg',  'Seasoning');

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

-- 8. Sample sales (12 transactions with items)
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, table_number, delivery_type_id, delivery_address, employee_id) VALUES
    (1,  1360.00, 'PKR', '2026-01-10', '13:15:00', 'dine_in',   'completed', 3,  NULL, NULL,                                 4),
    (2,  2000.00, 'PKR', '2026-01-10', '14:00:00', 'dine_in',   'completed', 7,  NULL, NULL,                                 5),
    (3,  1250.00, 'PKR', '2026-01-10', '19:30:00', 'takeaway',  'completed', NULL, NULL, NULL,                                 6),
    (4,  2060.00, 'PKR', '2026-01-11', '12:45:00', 'delivery',  'completed', NULL, 1,    'House 12, Street 5, Gulshan Colony', 8),
    (5,  2010.00, 'PKR', '2026-01-11', '20:00:00', 'dine_in',   'completed', 1,   NULL, NULL,                                 4),
    (6,  1020.00, 'PKR', '2026-01-12', '09:30:00', 'takeaway',  'completed', NULL, NULL, NULL,                                 6),
    (7,  1450.00, 'PKR', '2026-01-12', '13:30:00', 'delivery',  'completed', NULL, 2,    'Flat 4B, Green Heights, Main Road',  9),
    (8,  2990.00, 'PKR', '2026-01-12', '21:00:00', 'dine_in',   'completed', 10,  NULL, NULL,                                 5),
    (9,  1550.00, 'PKR', '2026-01-13', '14:30:00', 'dine_in',   'completed', 5,   NULL, NULL,                                 11),
    (10, 1000.00, 'PKR', '2026-01-13', '19:00:00', 'delivery',  'completed', NULL, 1,    'Street 12, Block C, Model Town',      8),
    (11, 1060.00, 'PKR', '2026-01-14', '11:00:00', 'dine_in',   'completed', 8,   NULL, NULL,                                 6),
    (12, 620.00,  'PKR', '2026-01-14', '16:30:00', 'takeaway',  'completed', NULL, NULL, NULL,                                 11);

-- 9. Sale items for those 12 sales
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
    -- Purchases
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
    -- Usage
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
    -- Waste
    (27, 7,  'waste',     -0.5,  'Spoiled tomatoes'),
    (28, 17, 'waste',     -1.0,  'Expired milk'),
    (29, 22, 'waste',     -0.8,  'Spoiled potatoes'),
    -- Adjustments
    (30, 1,  'adjustment', -0.5, 'Adjustment: Count variance on chicken breast'),
    (31, 8,  'adjustment', -1.0, 'Adjustment: Weight discrepancy on onions');

-- 11. Inventory adjustments
INSERT OR IGNORE INTO inventory_adjustments (id, ingredient_id, previous_quantity, new_quantity, reason, created_by) VALUES
    (1, 1, 25.0, 24.5, 'Count correction - found 0.5kg less chicken',       'Ali Ahmed'),
    (2, 8, 20.0, 19.0, 'Count correction - weight discrepancy in onions',   'Usman Khan');
