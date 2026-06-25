-- =============================================================================
-- PostgreSQL bootstrap – deterministic creation of databases, users, and extensions
-- This script runs once on the first container start.
-- It is idempotent: re‑runs safely without errors.
-- =============================================================================

-- Set timezone globally
SET timezone = 'UTC';

-- -----------------------------------------------------------------------------
-- 1. Create the shared application user (if not exists)
--    Change the password as needed; you can also set via environment.
-- -----------------------------------------------------------------------------
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'django') THEN
      CREATE USER django WITH ENCRYPTED PASSWORD 'django_password';
   END IF;
END $$;

-- -----------------------------------------------------------------------------
-- 2. Create all required databases (if they don't already exist)
--    Use the \gexec trick to conditionally create databases.
-- -----------------------------------------------------------------------------
SELECT 'CREATE DATABASE ctc_research'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ctc_research')\gexec
SELECT 'CREATE DATABASE lms_demo'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'lms_demo')\gexec
SELECT 'CREATE DATABASE vresume'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'vresume')\gexec
SELECT 'CREATE DATABASE db_ctc'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_ctc')\gexec
SELECT 'CREATE DATABASE db_structa'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_structa')\gexec
SELECT 'CREATE DATABASE blinko'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'blinko')\gexec

-- -----------------------------------------------------------------------------
-- 3. Grant privileges and set ownership for each database
--    We grant all privileges to the 'django' user and make it the owner
--    of each database (so it can create schemas, etc.).
--    Then we connect to each DB and grant schema/public permissions.
-- -----------------------------------------------------------------------------
DO $$
DECLARE
   db_names text[] := ARRAY['ctc_research', 'lms_demo', 'vresume', 'db_ctc', 'db_structa', 'blinko'];
   db_name text;
BEGIN
   FOREACH db_name IN ARRAY db_names LOOP
      EXECUTE format('GRANT ALL PRIVILEGES ON DATABASE %I TO django', db_name);
      EXECUTE format('ALTER DATABASE %I OWNER TO django', db_name);
   END LOOP;
END $$;

-- Now connect to each database and grant schema-level privileges,
-- create extensions, and set default privileges.
\c ctc_research
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

\c lms_demo
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

\c vresume
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

\c db_ctc
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";

\c db_structa
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";

\c blinko
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";

-- -----------------------------------------------------------------------------
-- 4. Done
-- -----------------------------------------------------------------------------
\echo '✅ Database bootstrap completed successfully.'