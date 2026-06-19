-- Initialize PostgreSQL databases and users
-- This script runs automatically on first container startup

-- Create databases
CREATE DATABASE ctc_research;
CREATE DATABASE lms_demo;
CREATE DATABASE vresume;

-- Create application user
CREATE USER django WITH PASSWORD 'django_password';

-- Grant privileges on ctc_research database
GRANT ALL PRIVILEGES ON DATABASE ctc_research TO django;
ALTER DATABASE ctc_research OWNER TO django;

-- Grant privileges on lms_demo database
GRANT ALL PRIVILEGES ON DATABASE lms_demo TO django;
ALTER DATABASE lms_demo OWNER TO django;

-- Grant privileges on vresume database
GRANT ALL PRIVILEGES ON DATABASE vresume TO django;
ALTER DATABASE vresume OWNER TO django;

-- Grant schema privileges
\connect ctc_research
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;

\connect lms_demo
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;

\connect vresume
GRANT ALL PRIVILEGES ON SCHEMA public TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON TABLES TO django;
ALTER DEFAULT PRIVILEGES FOR USER admin IN SCHEMA public GRANT ALL ON SEQUENCES TO django;

-- Optional: Create extensions if needed
\connect ctc_research
CREATE EXTENSION IF NOT EXISTS uuid-ossp;
CREATE EXTENSION IF NOT EXISTS hstore;

\connect lms_demo
CREATE EXTENSION IF NOT EXISTS uuid-ossp;
CREATE EXTENSION IF NOT EXISTS hstore;

\connect vresume
CREATE EXTENSION IF NOT EXISTS uuid-ossp;
CREATE EXTENSION IF NOT EXISTS hstore;
