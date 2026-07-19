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
