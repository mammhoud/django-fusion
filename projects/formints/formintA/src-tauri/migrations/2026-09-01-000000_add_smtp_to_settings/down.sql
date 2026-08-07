-- Remove SMTP email settings columns from the settings table
ALTER TABLE settings DROP COLUMN smtp_server;
ALTER TABLE settings DROP COLUMN smtp_port;
ALTER TABLE settings DROP COLUMN smtp_username;
ALTER TABLE settings DROP COLUMN smtp_password;
ALTER TABLE settings DROP COLUMN smtp_recipient;
ALTER TABLE settings DROP COLUMN smtp_from_name;
ALTER TABLE settings DROP COLUMN smtp_from_email;
