-- Add SMTP email settings columns to settings table for the support/email
-- integration. All columns are nullable — existing rows keep working without
-- configuring email.
ALTER TABLE settings ADD COLUMN smtp_server TEXT;
ALTER TABLE settings ADD COLUMN smtp_port INTEGER;
ALTER TABLE settings ADD COLUMN smtp_username TEXT;
ALTER TABLE settings ADD COLUMN smtp_password TEXT;
ALTER TABLE settings ADD COLUMN smtp_recipient TEXT;
ALTER TABLE settings ADD COLUMN smtp_from_name TEXT;
ALTER TABLE settings ADD COLUMN smtp_from_email TEXT;
