-- =============================================================================
-- PostgreSQL bootstrap — deterministic database + role init
-- =============================================================================
-- This script runs *once* on the first container start (before any other .sql
-- or .sh scripts in this directory). It is idempotent: every CREATE/GRANT is
-- wrapped in an IF NOT EXISTS guard so re-runs are safe.
--
-- What it does:
--   1. Creates the shared `django` application role.
--   2. Creates every project/application database the structa.cloud monorepo
--      needs (precis-main, precis-dev, precis-ctc, loop-crm, vresume, blinko).
--   3. Grants `django` ownership + schema-level privileges on project DBs.
--   4. Installs extensions (uuid-ossp, hstore, pgcrypto) on project DBs.
--   5. Creates the `blinko` role and grants ownership on the blinko DB.
--
-- The `coder` database + `coder` role are created by the companion shell
-- script (00.initdb-multiple-databases.sh) via the INITDB_MULTIPLE_DATABASES
-- env var, so they are intentionally NOT created here.
-- =============================================================================

SET timezone = 'UTC';

-- =============================================================================
-- 1. Shared application role — used by all Django/Wagtail projects
-- =============================================================================
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'django') THEN
      CREATE USER django WITH ENCRYPTED PASSWORD 'django_password';
   END IF;
END $$;


-- =============================================================================
-- 2. Database catalog
-- =============================================================================
-- Mapping of database names to project directories (keep this comment in sync
-- with the actual tree):
--
--   db_precis_lms   → projects/structa.cloud      (unified Precis product; renamed from precis-main)
--   db_precis_dev   → projects/precis/precis-dev     (development copy)
--   db_precis_ctc   → projects/precis/precis-ctc     (medical research site)
--   db_loop_crm     → projects/loop-crm              (sales + marketing CRM)
--   db_vresume      → projects/portfolio             (VResume, legacy)
--   blinko          → application/tools/blinko       (self-hosted AI notes)
--
-- coder            → application/tools/coder         (created by shell script)
--
-- Every Django project (precis-*, loop-crm, vresume) reuses the `django` role.
-- Blinko uses its own `blinko` role with a dedicated password.
-- Coder uses the `coder` role managed by 00.initdb-multiple-databases.sh.
-- =============================================================================

-- ── Project databases (Django/Wagtail) ──────────────────────────────────────
SELECT 'CREATE DATABASE db_precis_lms'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_precis_lms')\gexec

SELECT 'CREATE DATABASE db_precis_dev'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_precis_dev')\gexec

SELECT 'CREATE DATABASE db_precis_ctc'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_precis_ctc')\gexec

SELECT 'CREATE DATABASE db_loop_crm'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_loop_crm')\gexec

SELECT 'CREATE DATABASE db_vresume'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_vresume')\gexec

-- ── Tool databases (non-Django applications) ────────────────────────────────
-- Blinko: self-hosted personal AI note tool at tools.structa.cloud/notes/.
-- The `blinko` role + password + database are created by the companion shell
-- script (00.initdb-multiple-databases.sh) from INITDB_MULTIPLE_DATABASES —
-- the SQL script only pre-creates the database. The dedicated password stays
-- scoped to the Blinko application.
SELECT 'CREATE DATABASE blinko'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'blinko')\gexec


-- =============================================================================
-- 3. Grant privileges — Django project databases
-- =============================================================================
-- Every Django/Wagtail project is owned by the `django` role.  The `coder` and
-- `blinko` databases are excluded — they have their own dedicated roles (see
-- below).
-- =============================================================================
DO $$
DECLARE
   db_names text[] := ARRAY['db_precis_lms', 'db_precis_dev', 'db_precis_ctc', 'db_loop_crm', 'db_vresume'];
   db_name text;
BEGIN
   FOREACH db_name IN ARRAY db_names LOOP
      EXECUTE format('GRANT ALL PRIVILEGES ON DATABASE %I TO django', db_name);
      EXECUTE format('ALTER DATABASE %I OWNER TO django', db_name);
   END LOOP;
END $$;


-- =============================================================================
-- 4. Per-database schema grants, extensions, and default privileges
-- =============================================================================
-- Connect to each Django project database and set up the `public` schema so
-- `django` can create tables, sequences, and functions without manual grants.
-- Extensions are installed where the project's models use them.
-- =============================================================================

-- ── precis-main (db_precis_lms) — unified landing + LMS product ───────────
\c db_precis_lms
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── precis-dev (db_precis_dev) — development copy of precis-main ──────────
\c db_precis_dev
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── precis-ctc (db_precis_ctc) — medical research center ──────────────────
\c db_precis_ctc
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── loop-crm (db_loop_crm) — sales + marketing CRM ────────────────────────
\c db_loop_crm
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";

-- ── vresume (db_vresume) — legacy portfolio site ──────────────────────────
\c db_vresume
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";


-- =============================================================================
-- 5. Blinko — dedicated role + database ownership
-- =============================================================================
-- The `blinko` role and database are created by the companion shell init
-- script (00.initdb-multiple-databases.sh) via the INITDB_MULTIPLE_DATABASES
-- env var.  Add `blinko:blinko:<password>` to that list in
-- application/databases/.env and the shell script handles role creation,
-- password setting, database ownership, and schema grants automatically.
-- The SQL script above only pre-creates the database — ownership and schema
-- grants below finalize the setup on first start (idempotent).
-- =============================================================================

\c blinko
DO $$
BEGIN
   IF EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'blinko') THEN
      GRANT ALL PRIVILEGES ON DATABASE blinko TO blinko;
      ALTER DATABASE blinko OWNER TO blinko;
      GRANT ALL ON SCHEMA public TO blinko;
      ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO blinko;
      ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO blinko;
   END IF;
END $$;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- =============================================================================
-- 6. Done
-- =============================================================================
\echo '✅ Database bootstrap completed — 5 project DBs + blinko ready.'