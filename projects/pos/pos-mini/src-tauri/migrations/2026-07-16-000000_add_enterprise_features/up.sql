-- Enterprise feature schema extensions for POS

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

-- Seed default roles
INSERT INTO roles (name, permissions, is_active) VALUES
('Admin', '["*"]', 1),
('Manager', '["view_sales","view_inventory","view_employees","view_reports","manage_products","manage_customers"]', 1),
('Cashier', '["view_sales","create_sale","view_customers"]', 1),
('Kitchen', '["view_kitchen_tickets","update_kitchen_tickets"]', 1);

-- Seed default receipt template
INSERT INTO receipt_templates (name, template_body, is_default) VALUES
('Default', '<h1>{{restaurant_name}}</h1><p>{{address}}</p><p>Tel: {{phone}}</p><hr/><p>Receipt #: {{receipt_number}}</p><p>Date: {{date}} {{time}}</p><hr/><ul>{{#items}}<li>{{name}} x {{quantity}} {{unit}} - {{currency}}{{price}}</li>{{/items}}</ul><hr/><p>Total: {{currency}}{{total}}</p><p>{{footer}}</p>', 1);

-- =============================================================================
-- ENTERPRISE FEATURE SEED DATA
-- =============================================================================

-- Suppliers
INSERT OR IGNORE INTO suppliers (id, name, contact_name, email, phone, address, tax_id, payment_terms, is_active) VALUES
(1, 'Fresh Foods Co.', 'Ahmed Malik', 'ahmed@freshfoods.com', '+92-300-555-0101', '12 Industrial Area, Lahore', 'NTN-1234567', 'Net 30', 1),
(2, 'City Meat Suppliers', 'Usman Butt', 'usman@citymeat.com', '+92-300-555-0102', '45 Meat Market, Township', 'NTN-2345678', 'Net 15', 1),
(3, 'Al-Rashid Grocers', 'Rashid Khan', 'rashid@alrashid.com', '+92-300-555-0103', '78 Main Bazaar, Gulberg', 'NTN-3456789', 'Cash on Delivery', 1),
(4, 'Punjab Beverages', 'Sajid Ali', 'sajid@punjabbev.com', '+92-300-555-0104', '33 Beverage Road, Faisal Town', 'NTN-4567890', 'Net 30', 1),
(5, 'Green Valley Produce', 'Hassan Raza', 'hassan@greenvalley.com', '+92-300-555-0105', '90 Farm Road, Raiwind', 'NTN-5678901', 'Net 7', 1),
(6, 'Mega Mart Wholesale', 'Bilal Ahmed', 'bilal@megamart.com', '+92-300-555-0106', '55 Wholesale Market, Ichhra', 'NTN-6789012', 'Net 45', 1);

-- Customers
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

-- Inventory alerts (low stock items)
INSERT OR IGNORE INTO inventory_alerts (id, ingredient_id, alert_type, alert_message, is_resolved) VALUES
(1, 3, 'low_stock', 'Mutton is running low (below 5kg reorder level)', 0),
(2, 10, 'low_stock', 'Mozzarella Cheese is low (below 4kg reorder level)', 0),
(3, 29, 'low_stock', 'Coffee Beans nearly depleted (below 0.5kg)', 0),
(4, 37, 'low_stock', 'Gulab Jamun Mix is running low', 0),
(5, 18, 'low_stock', 'Cream stock is low', 0);

-- Employee schedules (2 weeks of shifts)
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

-- Payroll records (bi-weekly)
INSERT OR IGNORE INTO payrolls (id, employee_id, period_start, period_end, regular_hours, overtime_hours, total_pay, status) VALUES
(1, 1, '2026-07-01', '2026-07-14', 80, 4, 30000.00, 'paid'),
(2, 2, '2026-07-01', '2026-07-14', 80, 8, 23500.00, 'paid'),
(3, 3, '2026-07-01', '2026-07-14', 80, 5, 21000.00, 'paid'),
(4, 4, '2026-07-01', '2026-07-14', 80, 2, 13000.00, 'paid'),
(5, 5, '2026-07-01', '2026-07-14', 80, 3, 13000.00, 'paid'),
(6, 6, '2026-07-01', '2026-07-14', 80, 0, 12500.00, 'paid'),
(7, 7, '2026-07-01', '2026-07-14', 80, 6, 16000.00, 'paid'),
(8, 10, '2026-07-01', '2026-07-14', 40, 0, 4500.00, 'paid');

-- Purchase orders
INSERT OR IGNORE INTO purchase_orders (id, supplier_id, reference_number, status, total_amount, expected_date, notes) VALUES
(1, 1, 'PO-2026-001', 'received', 45000.00, '2026-07-10 10:00:00', 'Weekly fresh produce order'),
(2, 2, 'PO-2026-002', 'received', 32000.00, '2026-07-11 08:00:00', 'Bi-weekly meat supply'),
(3, 3, 'PO-2026-003', 'pending', 18500.00, '2026-07-18 10:00:00', 'Dry goods and spices restock'),
(4, 4, 'PO-2026-004', 'received', 12000.00, '2026-07-12 09:00:00', 'Beverages for the month'),
(5, 5, 'PO-2026-005', 'draft', 8900.00, '2026-07-20 08:00:00', 'Fresh vegetables order'),
(6, 6, 'PO-2026-006', 'pending', 25000.00, '2026-07-19 11:00:00', 'Monthly wholesale supplies');

-- Purchase order items
INSERT OR IGNORE INTO purchase_order_items (id, purchase_order_id, ingredient_id, quantity, cost_per_unit, received_quantity) VALUES
-- PO 1: Fresh Foods (produce)
(1, 1, 7, 25.0, 85.0, 25.0),
(2, 1, 8, 30.0, 65.0, 30.0),
(3, 1, 22, 30.0, 45.0, 30.0),
(4, 1, 42, 20.0, 75.0, 20.0),
(5, 1, 50, 10.0, 90.0, 10.0),
-- PO 2: City Meat (meat)
(6, 2, 1, 30.0, 420.0, 30.0),
(7, 2, 2, 20.0, 520.0, 20.0),
(8, 2, 3, 15.0, 1050.0, 15.0),
-- PO 3: Al-Rashid Grocers (dry goods)
(9, 3, 4, 25.0, 170.0, 0.0),
(10, 3, 5, 30.0, 65.0, 0.0),
(11, 3, 20, 5.0, 230.0, 0.0),
(12, 3, 53, 3.0, 330.0, 0.0),
(13, 3, 55, 5.0, 280.0, 0.0),
-- PO 4: Punjab Beverages
(14, 4, 14, 20.0, 450.0, 20.0),
(15, 4, 15, 15.0, 340.0, 15.0),
-- PO 5: Green Valley (vegetables)
(16, 5, 7, 15.0, 88.0, 0.0),
(17, 5, 8, 20.0, 68.0, 0.0),
(18, 5, 26, 5.0, 125.0, 0.0),
-- PO 6: Mega Mart Wholesale
(19, 6, 6, 30.0, 300.0, 0.0),
(20, 6, 10, 12.0, 720.0, 0.0),
(21, 6, 11, 8.0, 360.0, 0.0),
(22, 6, 16, 20.0, 100.0, 0.0);

-- Tax reports
INSERT OR IGNORE INTO tax_reports (id, period_start, period_end, total_sales, total_tax, transaction_count) VALUES
(1, '2026-07-01', '2026-07-07', 185000.00, 24050.00, 42),
(2, '2026-07-08', '2026-07-14', 203500.00, 26455.00, 48),
(3, '2026-07-01', '2026-07-14', 388500.00, 50505.00, 90);
