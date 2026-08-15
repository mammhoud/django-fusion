-- Employee detail & payroll fields (Formint)
-- Adds richer HR/payroll data captured by the employee wizard.
ALTER TABLE employees ADD COLUMN address TEXT;
ALTER TABLE employees ADD COLUMN date_of_birth TEXT;
ALTER TABLE employees ADD COLUMN national_id TEXT;
ALTER TABLE employees ADD COLUMN emergency_contact TEXT;
ALTER TABLE employees ADD COLUMN pay_frequency TEXT NOT NULL DEFAULT 'monthly';
ALTER TABLE employees ADD COLUMN hourly_rate DOUBLE NOT NULL DEFAULT 0;
ALTER TABLE employees ADD COLUMN bank_name TEXT;
ALTER TABLE employees ADD COLUMN bank_account TEXT;
ALTER TABLE employees ADD COLUMN tax_number TEXT;
ALTER TABLE employees ADD COLUMN notes TEXT;
