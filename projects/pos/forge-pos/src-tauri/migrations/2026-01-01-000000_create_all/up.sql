-- =============================================================================
-- SCHEMA — tables, triggers & essential reference data
-- Seed / demo data lives in seed.sql (run separately via seed.rs / make seed).
-- =============================================================================

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

-- Products (with image + product_type + border_color columns built-in)
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    unit TEXT NOT NULL DEFAULT 'item',
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    image TEXT,
    product_type TEXT NOT NULL DEFAULT 'product',
    border_color TEXT,
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
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('purchase', 'usage', 'waste', 'adjustment', 'return', 'goods_transfer')),
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

-- =============================================================================
-- ESSENTIAL REFERENCE DATA
-- These are the minimum rows required for the app to function (FK targets, etc.)
-- =============================================================================

-- Insert default settings (singleton row — app always expects this to exist)
INSERT OR IGNORE INTO settings (id, restaurant_name, currency, receipt_footer)
VALUES (1, 'Forge POS', 'PKR', 'Thank you for your business!');

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

-- =============================================================================
-- USERS & AUTH
-- =============================================================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS update_users_updated_at AFTER UPDATE ON users
BEGIN UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

-- =============================================================================
-- ENTERPRISE FEATURE SCHEMA (Roles, Suppliers, Kitchen, Customers, etc.)
-- =============================================================================

-- 1. USER MANAGEMENT (Roles & Permissions)
CREATE TABLE roles (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    permissions TEXT NOT NULL DEFAULT '[]',
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_roles (
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

-- 2. ADVANCED REPORTING (PDF/Excel Metadata)
CREATE TABLE report_metadata (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,
    format TEXT NOT NULL,
    file_path TEXT NOT NULL,
    parameters TEXT,
    generated_by INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (generated_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 3. INVENTORY MANAGEMENT (Stock Alerts)
CREATE TABLE inventory_alerts (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    ingredient_id INTEGER NOT NULL,
    alert_type TEXT NOT NULL DEFAULT 'low_stock',
    alert_message TEXT NOT NULL,
    is_resolved BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);

-- 4. SUPPLIER MANAGEMENT (Suppliers & Purchase Orders)
CREATE TABLE suppliers (
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

CREATE TABLE purchase_orders (
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

CREATE TABLE purchase_order_items (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    purchase_order_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    cost_per_unit REAL NOT NULL,
    received_quantity REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);

-- 5. KITCHEN DISPLAY SYSTEM (Order Tickets)
CREATE TABLE kitchen_tickets (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'pending',
    priority INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE
);

-- 6. CUSTOMER MANAGEMENT (Loyalty & CRM)
CREATE TABLE customers (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    loyalty_points REAL NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE loyalty_transactions (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    sale_id INTEGER,
    points_change REAL NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE SET NULL
);

-- Link sales to customers
ALTER TABLE sales ADD COLUMN customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL;

-- 7. RECEIPT CUSTOMIZATION (Advanced Templates)
CREATE TABLE receipt_templates (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    template_body TEXT NOT NULL,
    category TEXT,
    is_default BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 8. TAX REPORTS (Automated Summaries)
CREATE TABLE tax_reports (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    total_sales REAL NOT NULL,
    total_tax REAL NOT NULL,
    transaction_count INTEGER NOT NULL DEFAULT 0,
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 9. EMPLOYEE MANAGEMENT (Scheduling & Payroll)
CREATE TABLE employee_schedules (
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

CREATE TABLE payrolls (
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

-- =============================================================================
-- ESSENTIAL ENTERPRISE DEFAULTS
-- =============================================================================

-- Seed default roles
INSERT OR IGNORE INTO roles (name, permissions, is_active) VALUES
    ('Admin', '["*"]', 1),
    ('Manager', '["view_sales","view_inventory","view_employees","view_reports","manage_products","manage_customers"]', 1),
    ('Cashier', '["view_sales","create_sale","view_customers"]', 1),
    ('Kitchen', '["view_kitchen_tickets","update_kitchen_tickets"]', 1);

-- Seed default receipt template
INSERT OR IGNORE INTO receipt_templates (name, template_body, is_default) VALUES
    ('Default', '<h1>{{restaurant_name}}</h1><p>{{address}}</p><p>Tel: {{phone}}</p><hr/><p>Receipt #: {{receipt_number}}</p><p>Date: {{date}} {{time}}</p><hr/><ul>{{#items}}<li>{{name}} x {{quantity}} {{unit}} - {{currency}}{{price}}</li>{{/items}}</ul><hr/><p>Total: {{currency}}{{total}}</p><p>{{footer}}</p>', 1);
