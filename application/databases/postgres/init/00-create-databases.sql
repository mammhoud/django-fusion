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
--    The `coder` database is intentionally NOT created here — its owner and
--    credentials come from 00.initdb-multiple-databases.sh via the
--    INITDB_MULTIPLE_DATABASES env var, so we leave it for that script to own.
-- -----------------------------------------------------------------------------
-- Databases follow the project-tree naming convention (db_<tree>):
--   db_precis_lms      → projects/precis/precis-main
--   db_precis_ctc      → projects/precis/precis-ctc
--   db_precis_landing  → projects/precis/precis-landing
--   db_loop_crm        → projects/loop-crm
--   db_vresume         → projects/portfolio (VResume legacy)
-- The coder/affine databases are created by
-- 00.initdb-multiple-databases.sh from INITDB_MULTIPLE_DATABASES.
SELECT 'CREATE DATABASE db_precis_lms'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_precis_lms')\gexec
SELECT 'CREATE DATABASE db_precis_ctc'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_precis_ctc')\gexec
SELECT 'CREATE DATABASE db_precis_landing'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_precis_landing')\gexec
SELECT 'CREATE DATABASE db_loop_crm'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_loop_crm')\gexec
SELECT 'CREATE DATABASE db_vresume'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_vresume')\gexec

-- The `affine` database/user is created by
-- 00.initdb-multiple-databases.sh from INITDB_MULTIPLE_DATABASES so the
-- Coder workspace (AFFiNE) can connect to the shared PostgreSQL service.

-- -----------------------------------------------------------------------------
-- 3. Grant privileges and set ownership for each database
--    We grant all privileges to the 'django' user and make it the owner
--    of each database (so it can create schemas, etc.).
--    Then we connect to each DB and grant schema/public permissions.
--    The `coder` database is intentionally excluded from the OWNER TO django
--    loop — its owner and schema grants are wired up by
--    00.initdb-multiple-databases.sh so the Coder role remains intact on
--    FORCE_REINIT re-runs.
-- -----------------------------------------------------------------------------
DO $$
DECLARE
   db_names text[] := ARRAY['db_precis_lms', 'db_precis_ctc', 'db_precis_landing', 'db_loop_crm', 'db_vresume'];
   db_name text;
BEGIN
   FOREACH db_name IN ARRAY db_names LOOP
      EXECUTE format('GRANT ALL PRIVILEGES ON DATABASE %I TO django', db_name);
      EXECUTE format('ALTER DATABASE %I OWNER TO django', db_name);
   END LOOP;
END $$;

-- The `coder` DB is created by 00.initdb-multiple-databases.sh (via
-- INITDB_MULTIPLE_DATABASES env var), so it won't exist when this SQL script
-- runs. Grants for the coder DB are handled by that script and by the
-- entrypoint's ensure_coder_database() function. Keep the `coder` role intact.

-- Now connect to each database and grant schema-level privileges,
-- create extensions, and set default privileges.
\c db_precis_lms
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

\c db_precis_ctc
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

\c db_precis_landing
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

\c db_loop_crm
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";

\c db_vresume
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";

-- -----------------------------------------------------------------------------
-- 4. Done
-- -----------------------------------------------------------------------------
\echo '✅ Database bootstrap completed successfully.'
