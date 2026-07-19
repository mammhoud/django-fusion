-- Rollback enterprise feature schema extensions

DROP TABLE IF EXISTS payrolls;
DROP TABLE IF EXISTS employee_schedules;
DROP TABLE IF EXISTS tax_reports;
DROP TABLE IF EXISTS receipt_templates;
DROP TABLE IF EXISTS loyalty_transactions;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS kitchen_tickets;
DROP TABLE IF EXISTS purchase_order_items;
DROP TABLE IF EXISTS purchase_orders;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS inventory_alerts;
DROP TABLE IF EXISTS report_metadata;
DROP TABLE IF EXISTS user_roles;
DROP TABLE IF EXISTS roles;
