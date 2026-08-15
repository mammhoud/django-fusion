"""Seed a test restaurant.db with Rust/Diesel schema + sample rows for cross-ORM tests.

Run: python3 tests/seed_rust_db.py
Creates: projects/formints/formint-pro/restaurant.db
"""

import sqlite3
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "restaurant.db"
ts = datetime.now(timezone.utc).isoformat()

print(f"Creating: {DB_PATH}")
if DB_PATH.exists():
    DB_PATH.unlink()

conn = sqlite3.connect(str(DB_PATH))
c = conn.cursor()

# ── Core POS ──
c.executescript("""
CREATE TABLE settings (
    id INTEGER PRIMARY KEY, restaurant_name TEXT, address TEXT, phone TEXT,
    email TEXT, tax_rate TEXT, currency TEXT DEFAULT 'USD',
    opening_time TEXT, closing_time TEXT, receipt_footer TEXT, logo TEXT,
    dine_in_tables INTEGER DEFAULT 0, delivery_fee REAL DEFAULT 0,
    delivery_fee_per_km REAL DEFAULT 0
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, price REAL NOT NULL,
    unit TEXT DEFAULT 'item', category_id INTEGER REFERENCES categories(id),
    image TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
    uploaded INTEGER DEFAULT 0
);

CREATE TABLE delivery_types (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, description TEXT,
    fee_multiplier REAL DEFAULT 1.0, is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE employee_types (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, description TEXT,
    is_active INTEGER DEFAULT 1, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
""")

# ── Sales ──
c.executescript("""
CREATE TABLE customers (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, phone TEXT, email TEXT,
    loyalty_points REAL DEFAULT 0, notes TEXT,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE employees (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, phone TEXT, email TEXT,
    employee_type_id INTEGER NOT NULL REFERENCES employee_types(id),
    salary REAL DEFAULT 0.0, is_active INTEGER DEFAULT 1,
    joined_at TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
    uploaded INTEGER DEFAULT 0
);

CREATE TABLE sales (
    id INTEGER PRIMARY KEY, total_amount REAL NOT NULL,
    currency TEXT DEFAULT 'USD', date TEXT NOT NULL, time TEXT NOT NULL,
    order_type TEXT DEFAULT 'dine_in', status TEXT DEFAULT 'completed',
    table_number INTEGER, delivery_type_id INTEGER REFERENCES delivery_types(id),
    delivery_address TEXT, employee_id INTEGER REFERENCES employees(id),
    customer_id INTEGER REFERENCES customers(id),
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL, uploaded INTEGER DEFAULT 0
);

CREATE TABLE sale_items (
    id INTEGER PRIMARY KEY, sale_id INTEGER NOT NULL REFERENCES sales(id),
    product_name TEXT NOT NULL, price REAL NOT NULL, quantity REAL NOT NULL,
    unit TEXT NOT NULL, subtotal REAL NOT NULL, created_at TEXT NOT NULL
);

CREATE TABLE loyalty_transactions (
    id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id),
    sale_id INTEGER REFERENCES sales(id), points_change REAL NOT NULL,
    reason TEXT NOT NULL, created_at TEXT NOT NULL
);
""")

# ── People ──
c.executescript("""
CREATE TABLE employee_schedules (
    id INTEGER PRIMARY KEY, employee_id INTEGER NOT NULL REFERENCES employees(id),
    shift_start TEXT NOT NULL, shift_end TEXT NOT NULL,
    status TEXT DEFAULT 'scheduled', notes TEXT,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE payrolls (
    id INTEGER PRIMARY KEY, employee_id INTEGER NOT NULL REFERENCES employees(id),
    period_start TEXT NOT NULL, period_end TEXT NOT NULL,
    regular_hours REAL NOT NULL, overtime_hours REAL NOT NULL,
    total_pay REAL NOT NULL, status TEXT DEFAULT 'draft',
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL, name TEXT NOT NULL,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE roles (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE,
    permissions TEXT DEFAULT '[]', is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE user_roles (
    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
    role_id INTEGER NOT NULL REFERENCES roles(id), created_at TEXT NOT NULL,
    UNIQUE(user_id, role_id)
);
""")

# ── Inventory ──
c.executescript("""
CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, unit TEXT NOT NULL,
    current_quantity REAL DEFAULT 0.0, reorder_level REAL DEFAULT 0.0,
    reorder_quantity REAL DEFAULT 0.0, cost_per_unit REAL DEFAULT 0.0,
    is_active INTEGER DEFAULT 1, created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL, uploaded INTEGER DEFAULT 0
);

CREATE TABLE recipe_types (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, description TEXT,
    is_active INTEGER DEFAULT 1, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE recipes (
    id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL REFERENCES products(id),
    recipe_type_id INTEGER NOT NULL REFERENCES recipe_types(id),
    yield_quantity REAL DEFAULT 1.0, is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL, uploaded INTEGER DEFAULT 0,
    UNIQUE(product_id, recipe_type_id)
);

CREATE TABLE recipe_ingredients (
    id INTEGER PRIMARY KEY, recipe_id INTEGER NOT NULL REFERENCES recipes(id),
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id),
    quantity REAL NOT NULL, unit TEXT, preparation_note TEXT,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE inventory_transactions (
    id INTEGER PRIMARY KEY, ingredient_id INTEGER NOT NULL REFERENCES ingredients(id),
    transaction_type TEXT NOT NULL, quantity_change REAL NOT NULL,
    reference_id INTEGER, note TEXT, created_at TEXT NOT NULL, uploaded INTEGER DEFAULT 0
);

CREATE TABLE inventory_adjustments (
    id INTEGER PRIMARY KEY, ingredient_id INTEGER NOT NULL REFERENCES ingredients(id),
    previous_quantity REAL NOT NULL, new_quantity REAL NOT NULL,
    reason TEXT NOT NULL, created_by TEXT, created_at TEXT NOT NULL,
    uploaded INTEGER DEFAULT 0
);

CREATE TABLE inventory_alerts (
    id INTEGER PRIMARY KEY, ingredient_id INTEGER NOT NULL REFERENCES ingredients(id),
    alert_type TEXT DEFAULT 'low_stock', alert_message TEXT NOT NULL,
    is_resolved INTEGER DEFAULT 0, created_at TEXT NOT NULL,
    resolved_at TEXT
);

CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, contact_name TEXT,
    email TEXT, phone TEXT, address TEXT, tax_id TEXT, payment_terms TEXT,
    is_active INTEGER DEFAULT 1, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE purchase_orders (
    id INTEGER PRIMARY KEY, supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
    reference_number TEXT, status TEXT DEFAULT 'draft', total_amount REAL DEFAULT 0,
    expected_date TEXT, notes TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE purchase_order_items (
    id INTEGER PRIMARY KEY, purchase_order_id INTEGER NOT NULL REFERENCES purchase_orders(id),
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id),
    quantity REAL NOT NULL, cost_per_unit REAL NOT NULL,
    received_quantity REAL DEFAULT 0
);
""")

# ── Ops ──
c.executescript("""
CREATE TABLE kitchen_tickets (
    id INTEGER PRIMARY KEY, sale_id INTEGER NOT NULL REFERENCES sales(id),
    status TEXT DEFAULT 'pending', priority INTEGER DEFAULT 0,
    notes TEXT, created_at TEXT NOT NULL, completed_at TEXT
);

CREATE TABLE support_tickets (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL,
    subject TEXT NOT NULL, message TEXT NOT NULL,
    status TEXT DEFAULT 'open', created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE receipt_templates (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, template_body TEXT NOT NULL,
    is_default INTEGER DEFAULT 0, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE tax_reports (
    id INTEGER PRIMARY KEY, period_start TEXT NOT NULL, period_end TEXT NOT NULL,
    total_sales REAL NOT NULL, total_tax REAL NOT NULL,
    transaction_count INTEGER NOT NULL, generated_at TEXT NOT NULL
);

CREATE TABLE report_metadata (
    id INTEGER PRIMARY KEY, report_type TEXT NOT NULL, format TEXT NOT NULL,
    file_path TEXT NOT NULL, parameters TEXT, generated_by INTEGER REFERENCES users(id),
    created_at TEXT NOT NULL
);
""")

# ── CRM ──
c.executescript("""
CREATE TABLE crm_companies (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, website TEXT, phone TEXT,
    email TEXT, address TEXT, city TEXT, state TEXT, postal_code TEXT,
    country TEXT, industry TEXT, description TEXT, logo_url TEXT,
    tax_id TEXT, size TEXT, source TEXT, tags TEXT, is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
    synced_at TEXT, cloud_id TEXT
);

CREATE TABLE crm_contacts (
    id INTEGER PRIMARY KEY, salutation TEXT, first_name TEXT NOT NULL,
    last_name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT, mobile TEXT,
    job_title TEXT, department TEXT, company_id INTEGER REFERENCES crm_companies(id),
    pos_customer_id INTEGER, address TEXT, prefer_contact TEXT,
    source TEXT, tags TEXT, notes TEXT, avatar_url TEXT,
    is_active INTEGER DEFAULT 1, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
    synced_at TEXT, cloud_id TEXT
);

CREATE TABLE crm_pipelines (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, description TEXT,
    is_default INTEGER DEFAULT 0, is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
    synced_at TEXT, cloud_id TEXT
);

CREATE TABLE crm_stages (
    id INTEGER PRIMARY KEY, pipeline_id INTEGER NOT NULL REFERENCES crm_pipelines(id),
    name TEXT NOT NULL, display_order INTEGER DEFAULT 0,
    probability REAL DEFAULT 0, color TEXT, is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE crm_deals (
    id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT,
    value REAL DEFAULT 0, currency TEXT DEFAULT 'USD',
    discount_percent REAL DEFAULT 0, priority TEXT DEFAULT 'medium',
    pipeline_id INTEGER NOT NULL REFERENCES crm_pipelines(id),
    stage_id INTEGER NOT NULL REFERENCES crm_stages(id),
    contact_id INTEGER REFERENCES crm_contacts(id),
    company_id INTEGER REFERENCES crm_companies(id),
    pos_sale_id INTEGER, expected_close_date TEXT, closed_date TEXT,
    is_closed INTEGER DEFAULT 0, is_won INTEGER DEFAULT 0,
    lost_reason TEXT, is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
    synced_at TEXT, cloud_id TEXT
);

CREATE TABLE crm_activities (
    id INTEGER PRIMARY KEY, activity_type TEXT DEFAULT 'note',
    subject TEXT NOT NULL, description TEXT, outcome TEXT,
    duration_minutes INTEGER, contact_id INTEGER REFERENCES crm_contacts(id),
    deal_id INTEGER REFERENCES crm_deals(id),
    company_id INTEGER REFERENCES crm_companies(id),
    due_date TEXT, is_completed INTEGER DEFAULT 0, completed_at TEXT,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
    synced_at TEXT, cloud_id TEXT
);

CREATE TABLE crm_notes (
    id INTEGER PRIMARY KEY, content TEXT NOT NULL,
    contact_id INTEGER REFERENCES crm_contacts(id),
    deal_id INTEGER REFERENCES crm_deals(id),
    company_id INTEGER REFERENCES crm_companies(id),
    is_pinned INTEGER DEFAULT 0, created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL, synced_at TEXT, cloud_id TEXT
);

CREATE TABLE crm_sync_log (
    id INTEGER PRIMARY KEY, entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL, cloud_id TEXT, action TEXT NOT NULL,
    status TEXT NOT NULL, error_message TEXT, retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3, duration_ms INTEGER,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE crm_sync_queue (
    id INTEGER PRIMARY KEY, entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL, action TEXT NOT NULL,
    direction TEXT DEFAULT 'push', priority INTEGER DEFAULT 0,
    is_processing INTEGER DEFAULT 0, error_count INTEGER DEFAULT 0,
    last_error TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE crm_cloud_config (
    id INTEGER PRIMARY KEY, sync_enabled INTEGER DEFAULT 1,
    cloud_url TEXT, api_key TEXT, sync_interval INTEGER DEFAULT 60,
    retry_max INTEGER DEFAULT 3, retry_delay INTEGER DEFAULT 10,
    conflict_strategy TEXT DEFAULT 'server_wins',
    last_sync_at TEXT, last_sync_status TEXT, last_sync_summary TEXT,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
""")

# ── Seed data ──
c.execute("INSERT INTO settings (id, restaurant_name, currency) VALUES (1, 'Test Restaurant', 'USD')")
c.execute("INSERT INTO categories VALUES (1, 'Beverages', ?, ?)", (ts, ts))
c.execute("INSERT INTO categories VALUES (2, 'Food', ?, ?)", (ts, ts))
c.execute("INSERT INTO products VALUES (1, 'Espresso', 3.50, 'item', 1, NULL, ?, ?, 0)", (ts, ts))
c.execute("INSERT INTO products VALUES (2, 'Latte', 4.50, 'item', 1, NULL, ?, ?, 0)", (ts, ts))
c.execute("INSERT INTO products VALUES (3, 'Burger', 12.00, 'item', 2, NULL, ?, ?, 0)", (ts, ts))
c.execute("INSERT INTO delivery_types VALUES (1, 'Dine In', NULL, 1.0, 1, ?, ?)", (ts, ts))
c.execute("INSERT INTO employee_types VALUES (1, 'Cashier', NULL, 1, ?, ?)", (ts, ts))
c.execute("INSERT INTO employees VALUES (1, 'Alice Worker', NULL, NULL, 1, 15.0, 1, NULL, ?, ?, 0)", (ts, ts))
c.execute("INSERT INTO customers VALUES (1, 'John Doe', '+1555123', 'john@test.com', 100, NULL, ?, ?)", (ts, ts))
c.execute("INSERT INTO customers VALUES (2, 'Jane Smith', NULL, 'jane@test.com', 50, NULL, ?, ?)", (ts, ts))
c.execute("INSERT INTO sales VALUES (1, 20.00, 'USD', '2026-07-20', '14:30', 'dine_in', 'completed', 5, 1, NULL, 1, 1, ?, ?, 0)", (ts, ts))
c.execute("INSERT INTO sales VALUES (2, 12.00, 'USD', '2026-07-20', '15:00', 'dine_in', 'completed', 3, 1, NULL, 1, 2, ?, ?, 0)", (ts, ts))
c.execute("INSERT INTO sale_items VALUES (1, 1, 'Espresso', 3.50, 2, 'item', 7.00, ?)", (ts,))
c.execute("INSERT INTO sale_items VALUES (2, 1, 'Latte', 4.50, 2, 'item', 9.00, ?)", (ts,))
c.execute("INSERT INTO sale_items VALUES (3, 2, 'Burger', 12.00, 1, 'item', 12.00, ?)", (ts,))
c.execute("INSERT INTO ingredients VALUES (1, 'Coffee Beans', 'kg', 50.0, 10.0, 20.0, 15.0, 1, ?, ?, 0)", (ts, ts))
c.execute("INSERT INTO suppliers VALUES (1, 'Bean Supply Co', 'Bob Vendor', 'bob@beans.com', NULL, NULL, NULL, 'net30', 1, ?, ?)", (ts, ts))
c.execute("INSERT INTO users VALUES (1, 'admin@test.com', 'hash123', 'Admin User', ?, ?)", (ts, ts))
c.execute("INSERT INTO roles VALUES (1, 'admin', '[\"*\"]', 1, ?, ?)", (ts, ts))
c.execute("INSERT INTO support_tickets VALUES (1, 'Customer', 'cust@test.com', 'Help', 'Need help', 'open', ?, ?)", (ts, ts))

# CRM seed
c.execute("INSERT INTO crm_companies VALUES (1, 'Acme Corp', 'acme.com', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, ?, ?, NULL, NULL)", (ts, ts))
c.execute("INSERT INTO crm_contacts VALUES (1, NULL, 'Jane', 'Contact', 'jane@acme.com', NULL, NULL, 'CEO', NULL, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, ?, ?, NULL, NULL)", (ts, ts))
c.execute("INSERT INTO crm_pipelines VALUES (1, 'Default Pipeline', 'Standard sales pipeline', 1, 1, ?, ?, NULL, NULL)", (ts, ts))
c.execute("INSERT INTO crm_stages VALUES (1, 1, 'New Lead', 1, 10, '#blue', 1, ?, ?)", (ts, ts))
c.execute("INSERT INTO crm_stages VALUES (2, 1, 'Qualified', 2, 25, '#green', 1, ?, ?)", (ts, ts))
c.execute("INSERT INTO crm_deals VALUES (1, 'Big Deal', 'High value', 50000.0, 'USD', 0, 'high', 1, 1, 1, 1, NULL, NULL, NULL, 0, 0, NULL, 1, ?, ?, NULL, NULL)", (ts, ts))
c.execute("INSERT INTO crm_activities VALUES (1, 'call', 'Intro Call', 'Called CEO', 'Interested', 30, 1, 1, 1, NULL, 0, NULL, ?, ?, NULL, NULL)", (ts, ts))
c.execute("INSERT INTO crm_notes VALUES (1, 'Follow up next week', 1, 1, 1, 0, ?, ?, NULL, NULL)", (ts, ts))
c.execute("INSERT INTO crm_sync_log VALUES (1, 'deal', 1, 'cloud_123', 'push', 'success', NULL, 0, 3, 150, ?, ?)", (ts, ts))
c.execute("INSERT INTO crm_sync_queue VALUES (1, 'deal', 1, 'update', 'push', 0, 0, 0, NULL, ?, ?)", (ts, ts))
c.execute("INSERT INTO crm_cloud_config VALUES (1, 1, 'https://cloud.example.com', 'key123', 60, 3, 10, 'server_wins', NULL, NULL, NULL, ?, ?)", (ts, ts))

conn.commit()
table_count = c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
print(f"Created {DB_PATH} with {table_count} tables and seeded rows")
conn.close()
