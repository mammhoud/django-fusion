#!/bin/bash
set -e
set -u

# ----------------------------------------------------------------------
# Helper: Create a database, role, and grant all privileges
# ----------------------------------------------------------------------
create_database_with_user() {
    local db_name="$1"
    local db_user="${2:-}"
    local db_password="${3:-}"

    # Generate username if not provided
    if [ -z "$db_user" ]; then
        if [ -n "${INITDB_USER_PREFIX:-}" ]; then
            db_user="${INITDB_USER_PREFIX}${db_name}"
        else
            db_user="${db_name}_user"
        fi
    fi

    # Generate password if not provided
    if [ -z "$db_password" ]; then
        if [ -n "${INITDB_PASSWORD_PATTERN:-}" ]; then
            db_password="${INITDB_PASSWORD_PATTERN//\{db\}/$db_name}"
        else
            db_password="$(openssl rand -base64 18 2>/dev/null || echo "${db_name}_pass")"
        fi
    fi

    echo "Creating database '$db_name' with user '$db_user'..."

    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        -- Create user if not exists, else update password
        DO \$\$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$db_user') THEN
                CREATE USER $db_user WITH ENCRYPTED PASSWORD '$db_password';
            ELSE
                ALTER USER $db_user WITH ENCRYPTED PASSWORD '$db_password';
            END IF;
        END
        \$\$;

        -- Create database if not exists
        SELECT 'CREATE DATABASE $db_name'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$db_name')\gexec

        -- Grant database privileges
        GRANT ALL PRIVILEGES ON DATABASE $db_name TO $db_user;

        -- Grant schema and object privileges
        \c $db_name;
        GRANT ALL ON SCHEMA public TO $db_user;
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $db_user;
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $db_user;
        GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO $db_user;

        -- Default privileges for future objects
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $db_user;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $db_user;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO $db_user;
EOSQL
}

# ----------------------------------------------------------------------
# Parse and process multiple database specifications
# ----------------------------------------------------------------------

# 1) Process the new format: INITDB_MULTIPLE_DATABASES
#    Format: db1[:user1[:pass1]],db2[:user2[:pass2]],...
#    If only db name given, user/pass are auto‑generated.
if [ -n "${INITDB_MULTIPLE_DATABASES:-}" ]; then
    echo "Processing INITDB_MULTIPLE_DATABASES: $INITDB_MULTIPLE_DATABASES"
    IFS=',' read -ra DB_SPECS <<< "$INITDB_MULTIPLE_DATABASES"
    for spec in "${DB_SPECS[@]}"; do
        spec=$(echo "$spec" | xargs)   # trim whitespace
        IFS=':' read -r db_name db_user db_password <<< "$spec"
        create_database_with_user "$db_name" "${db_user:-}" "${db_password:-}"
    done
fi

# 2) Process the old format: POSTGRES_MULTIPLE_DATABASES
#    Format: db1:owner1:pass1,db2:owner2:pass2,...
#    (owner is a role name; password is for that role)
if [ -n "${POSTGRES_MULTIPLE_DATABASES:-}" ]; then
    echo "Processing POSTGRES_MULTIPLE_DATABASES: $POSTGRES_MULTIPLE_DATABASES"
    IFS=',' read -ra DB_PAIRS <<< "$POSTGRES_MULTIPLE_DATABASES"
    for pair in "${DB_PAIRS[@]}"; do
        pair=$(echo "$pair" | xargs)
        IFS=':' read -r db_name owner password <<< "$pair"
        if [ -z "$db_name" ] || [ -z "$owner" ] || [ -z "$password" ]; then
            echo "Warning: invalid pair '$pair' – skipping"
            continue
        fi
        create_database_with_user "$db_name" "$owner" "$password"
    done
fi

# 3) Backward compatibility: individual DB_*_USER/PASSWORD variables
#    (e.g., DB_STAGING_USER, DB_STAGING_PASSWORD → db_staging)
#    You can extend this pattern as needed.
if [ -n "${DB_STAGING_USER:-}" ] && [ -n "${DB_STAGING_PASSWORD:-}" ]; then
    create_database_with_user "db_staging" "$DB_STAGING_USER" "$DB_STAGING_PASSWORD"
fi
if [ -n "${DB_SITE_USER:-}" ] && [ -n "${DB_SITE_PASSWORD:-}" ]; then
    create_database_with_user "db_site" "$DB_SITE_USER" "$DB_SITE_PASSWORD"
fi
# Add more as required (e.g., DB_CTC_USER etc.)

echo "✅ Database initialization completed."