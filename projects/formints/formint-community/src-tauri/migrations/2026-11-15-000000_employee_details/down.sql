-- Remove employee detail & payroll fields
ALTER TABLE employees DROP COLUMN address;
ALTER TABLE employees DROP COLUMN date_of_birth;
ALTER TABLE employees DROP COLUMN national_id;
ALTER TABLE employees DROP COLUMN emergency_contact;
ALTER TABLE employees DROP COLUMN pay_frequency;
ALTER TABLE employees DROP COLUMN hourly_rate;
ALTER TABLE employees DROP COLUMN bank_name;
ALTER TABLE employees DROP COLUMN bank_account;
ALTER TABLE employees DROP COLUMN tax_number;
ALTER TABLE employees DROP COLUMN notes;
