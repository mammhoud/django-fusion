-- =============================================================================
-- CONSOLIDATED SCHEMA + SEED  — 2026-07-28
-- =============================================================================
-- This single migration replaces all prior migration files and seed data.
-- It creates every table, trigger, and inserts all reference/seed data.
-- Safe to re-run (INSERT OR IGNORE / IF NOT EXISTS throughout).
-- =============================================================================

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║  SETTINGS                                                               ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    restaurant_name TEXT,
    address TEXT,
    phone TEXT,
    email TEXT,
    tax_rate TEXT,
    currency TEXT NOT NULL DEFAULT 'USD',
    opening_time TEXT,
    closing_time TEXT,
    receipt_footer TEXT,
    logo TEXT,
    invoice_logo TEXT,
    dine_in_tables INTEGER NOT NULL DEFAULT 0,
    delivery_fee REAL NOT NULL DEFAULT 0.0,
    delivery_fee_per_km REAL NOT NULL DEFAULT 0.0
);

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║  CATEGORIES & PRODUCTS                                                  ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    unit TEXT NOT NULL DEFAULT 'item',
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    image TEXT,
    product_type TEXT NOT NULL DEFAULT 'product',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    uploaded BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS delivery_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    fee_multiplier REAL NOT NULL DEFAULT 1.0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employee_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

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

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║  CUSTOMERS (needed before sales for FK reference)                       ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    loyalty_points REAL NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║  DELIVERY ZONES (needed before sales for FK reference)                  ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS delivery_zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    base_fee REAL NOT NULL DEFAULT 0.0,
    fee_per_km REAL NOT NULL DEFAULT 0.0,
    max_distance REAL NOT NULL DEFAULT 10.0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║  SALES                                                                  ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

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
    delivery_zone_id INTEGER REFERENCES delivery_zones(id) ON DELETE SET NULL,
    delivery_address TEXT,
    customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
    employee_id INTEGER REFERENCES employees(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    uploaded BOOLEAN NOT NULL DEFAULT 0
);

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

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║  INVENTORY & RECIPES                                                    ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

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

CREATE TABLE IF NOT EXISTS recipe_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

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

CREATE TABLE IF NOT EXISTS inventory_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('purchase', 'usage', 'waste', 'adjustment', 'return', 'goods_transfer')),
    quantity_change REAL NOT NULL,
    reference_id INTEGER,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    uploaded BOOLEAN NOT NULL DEFAULT 0
);

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

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║  USERS & AUTH                                                           ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'ar',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS roles (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    permissions TEXT NOT NULL DEFAULT '[]',
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║  ENTERPRISE TABLES (Reports, Suppliers, Kitchen, Customers, etc.)       ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS report_metadata (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,
    format TEXT NOT NULL,
    file_path TEXT NOT NULL,
    parameters TEXT,
    generated_by INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (generated_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS inventory_alerts (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    ingredient_id INTEGER NOT NULL,
    alert_type TEXT NOT NULL DEFAULT 'low_stock',
    alert_message TEXT NOT NULL,
    is_resolved BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_name TEXT,
    email TEXT,
    phone TEXT,
    address TEXT,
    tax_id TEXT,
    payment_terms TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS purchase_orders (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL,
    reference_number TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    total_amount REAL NOT NULL DEFAULT 0,
    shipping_fee REAL NOT NULL DEFAULT 0,
    expected_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS purchase_order_items (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    purchase_order_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    cost_per_unit REAL NOT NULL,
    received_quantity REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS kitchen_tickets (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'pending',
    priority INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS loyalty_transactions (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    sale_id INTEGER,
    points_change REAL NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS receipt_templates (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    template_body TEXT NOT NULL,
    category TEXT,
    is_default BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tax_reports (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    total_sales REAL NOT NULL,
    total_tax REAL NOT NULL,
    transaction_count INTEGER NOT NULL DEFAULT 0,
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employee_schedules (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    shift_start TIMESTAMP NOT NULL,
    shift_end TIMESTAMP NOT NULL,
    status TEXT NOT NULL DEFAULT 'scheduled',
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS payrolls (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    regular_hours REAL NOT NULL DEFAULT 0,
    overtime_hours REAL NOT NULL DEFAULT 0,
    total_pay REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);
-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║  TRIGGERS                                                               ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

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

CREATE TRIGGER IF NOT EXISTS update_delivery_zones_updated_at AFTER UPDATE ON delivery_zones
BEGIN UPDATE delivery_zones SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_users_updated_at AFTER UPDATE ON users
BEGIN UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║  REFERENCE DATA (essential defaults)                                    ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

INSERT OR IGNORE INTO settings (id, restaurant_name, currency, receipt_footer)
VALUES (1, 'Forge POS', 'USD', 'Thank you for your business!');

INSERT OR IGNORE INTO delivery_types (id, name, description, fee_multiplier) VALUES
    (1, 'Standard', 'Standard delivery (30-45 min)', 1.0),
    (2, 'Express', 'Express delivery (15-20 min)', 1.5),
    (3, 'Scheduled', 'Scheduled delivery for later time', 1.0);

INSERT OR IGNORE INTO employee_types (id, name, description) VALUES
    (1, 'Manager', 'Restaurant manager'),
    (2, 'Chef', 'Head chef / cook'),
    (3, 'Waiter', 'Service staff'),
    (4, 'Cashier', 'Cash register operator'),
    (5, 'Delivery Driver', 'Delivery personnel'),
    (6, 'Cleaner', 'Cleaning staff'),
    (7, 'Other', 'Other staff');

INSERT OR IGNORE INTO recipe_types (id, name, description) VALUES
    (1, 'Standard', 'Default recipe for regular production'),
    (2, 'Custom', 'Customized recipe for specific orders'),
    (3, 'Seasonal', 'Seasonal variation');

INSERT OR IGNORE INTO roles (name, permissions, is_active) VALUES
    ('Admin', '["*"]', 1),
    ('Manager', '["manage:products","manage:inventory","manage:employees","manage:roles","process:sales","manage:customers","manage:settings","view:reports","view:analytics","view:transactions","manage:suppliers","manage:kitchen"]', 1),
    ('Cashier', '["process:sales","view:transactions","manage:customers"]', 1),
    ('Kitchen', '["manage:kitchen"]', 1);

INSERT OR IGNORE INTO receipt_templates (name, template_body, is_default) VALUES
    ('Default', '<h1>{{restaurant_name}}</h1><p>{{address}}</p><p>Tel: {{phone}}</p><hr/><p>Receipt #: {{receipt_number}}</p><p>Date: {{date}} {{time}}</p><hr/><ul>{{#items}}<li>{{name}} x {{quantity}} {{unit}} - {{currency}}{{price}}</li>{{/items}}</ul><hr/><p>Total: {{currency}}{{total}}</p><p>{{footer}}</p>', 1);

INSERT OR IGNORE INTO delivery_zones (id, name, base_fee, fee_per_km, max_distance) VALUES
    (1, 'Downtown',        5.0,  1.0,  5.0),
    (2, 'Suburbs',         8.0,  1.5,  10.0),
    (3, 'Outskirts',       12.0, 2.0,  15.0),
    (4, 'Rural',           15.0, 2.5,  25.0);

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║  SEED DATA                                                              ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

-- 1. Suppliers
INSERT OR IGNORE INTO suppliers (id, name, contact_name, email, phone, address, tax_id, payment_terms, is_active) VALUES
    (1, 'Fresh Foods Co.', 'Ahmed Malik', 'ahmed@freshfoods.com', '+92-300-555-0101', '12 Industrial Area, Lahore', 'NTN-1234567', 'Net 30', 1),
    (2, 'City Meat Suppliers', 'Usman Butt', 'usman@citymeat.com', '+92-300-555-0102', '45 Meat Market, Township', 'NTN-2345678', 'Net 15', 1),
    (3, 'Al-Rashid Grocers', 'Rashid Khan', 'rashid@alrashid.com', '+92-300-555-0103', '78 Main Bazaar, Gulberg', 'NTN-3456789', 'Cash on Delivery', 1),
    (4, 'Punjab Beverages', 'Sajid Ali', 'sajid@punjabbev.com', '+92-300-555-0104', '33 Beverage Road, Faisal Town', 'NTN-4567890', 'Net 30', 1),
    (5, 'Green Valley Produce', 'Hassan Raza', 'hassan@greenvalley.com', '+92-300-555-0105', '90 Farm Road, Raiwind', 'NTN-5678901', 'Net 7', 1),
    (6, 'Mega Mart Wholesale', 'Bilal Ahmed', 'bilal@megamart.com', '+92-300-555-0106', '55 Wholesale Market, Ichhra', 'NTN-6789012', 'Net 45', 1);

-- 2. Customers
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

-- 3. Tax reports
INSERT OR IGNORE INTO tax_reports (id, period_start, period_end, total_sales, total_tax, transaction_count) VALUES
    (1, '2026-07-01', '2026-07-07', 185000.00, 24050.00, 42),
    (2, '2026-07-08', '2026-07-14', 203500.00, 26455.00, 48),
    (3, '2026-07-01', '2026-07-14', 388500.00, 50505.00, 90);

-- 4. Settings — restaurant defaults
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

-- 5. Categories (food menu)
INSERT OR IGNORE INTO categories (id, name) VALUES
    (1, 'Burgers & Sandwiches'), (2, 'Pizza'), (3, 'BBQ & Grills'),
    (4, 'Rice & Biryani'), (5, 'Karahi & Curries'), (6, 'Fast Food & Snacks'),
    (7, 'Beverages'), (8, 'Desserts'), (9, 'Chinese'), (10, 'Breakfast');

-- 6. Products
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

-- 7. Ingredients
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
    (42, 'Mixed Vegetables',       'kg',    10.0,  5.0,   8.0,   80.00),
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

-- 8. Sample sales
INSERT OR IGNORE INTO sales (id, total_amount, currency, date, time, order_type, status, table_number, delivery_type_id, delivery_address, employee_id) VALUES
    (1,  1360.00, 'USD', '2026-01-10', '13:15:00', 'dine_in',   'completed', 3,  NULL, NULL,                                4),
    (2,  2000.00, 'USD', '2026-01-10', '14:00:00', 'dine_in',   'completed', 7,  NULL, NULL,                                5),
    (3,  1250.00, 'USD', '2026-01-10', '19:30:00', 'takeaway',  'completed', NULL, NULL, NULL,                                6),
    (4,  2060.00, 'USD', '2026-01-11', '12:45:00', 'delivery',  'completed', NULL, 1,    'House 12, Street 5, Gulshan Colony', 8),
    (5,  2010.00, 'USD', '2026-01-11', '20:00:00', 'dine_in',   'completed', 1,   NULL, NULL,                                4),
    (6,  1020.00, 'USD', '2026-01-12', '09:30:00', 'takeaway',  'completed', NULL, NULL, NULL,                                6),
    (7,  1450.00, 'USD', '2026-01-12', '13:30:00', 'delivery',  'completed', NULL, 2,    'Flat 4B, Green Heights, Main Road', 9),
    (8,  2990.00, 'USD', '2026-01-12', '21:00:00', 'dine_in',   'completed', 10,  NULL, NULL,                                5),
    (9,  1550.00, 'USD', '2026-01-13', '14:30:00', 'dine_in',   'completed', 5,   NULL, NULL,                                11),
    (10, 1000.00, 'USD', '2026-01-13', '19:00:00', 'delivery',  'completed', NULL, 1,    'Street 12, Block C, Model Town',     8),
    (11, 1060.00, 'USD', '2026-01-14', '11:00:00', 'dine_in',   'completed', 8,   NULL, NULL,                                6),
    (12, 620.00,  'USD', '2026-01-14', '16:30:00', 'takeaway',  'completed', NULL, NULL, NULL,                                11);

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
