-- Workspace PostgreSQL bootstrap databases for all websites.
-- The shell bootstrap also reads INITDB_MULTIPLE_DATABASES; this SQL file keeps
-- direct postgres initialization deterministic for local/dev usage.
SELECT 'CREATE DATABASE db_ctc' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_ctc')\gexec
SELECT 'CREATE DATABASE db_structa' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_structa')\gexec
SELECT 'CREATE DATABASE vresume' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'vresume')\gexec
