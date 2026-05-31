#!/bin/bash
set -e

echo "Initializing databases and users..."

# Get the postgres user (superuser) from environment
POSTGRES_USER="${POSTGRES_USER:-postgres}"

# Function to create a database with user
create_database_with_user() {
    local db_name="$1"
    local db_user="${2:-}"
    local db_password="${3:-}"
    
    # Generate username if not provided
    if [ -z "$db_user" ]; then
        if [ -n "$INITDB_USER_PREFIX" ]; then
            db_user="${INITDB_USER_PREFIX}${db_name}"
        else
            db_user="${db_name}_user"
        fi
    fi
    
    # Generate password if not provided
    if [ -z "$db_password" ]; then
        db_password="${INITDB_PASSWORD_PATTERN//\{db\}/$db_name}"
    fi
    
    echo "Creating database '$db_name' with user '$db_user'..."
    
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        -- Create user if not exists
        DO \$\$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$db_user') THEN
                CREATE USER $db_user WITH ENCRYPTED PASSWORD '$db_password';
            ELSE
                -- Update password if user exists
                ALTER USER $db_user WITH ENCRYPTED PASSWORD '$db_password';
            END IF;
        END
        \$\$;
        
        -- Create database if not exists
        SELECT 'CREATE DATABASE $db_name'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$db_name')\gexec
        
        -- Grant all privileges
        GRANT ALL PRIVILEGES ON DATABASE $db_name TO $db_user;
        
        -- Connect to the database and grant schema privileges
        \c $db_name;
        GRANT ALL ON SCHEMA public TO $db_user;
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $db_user;
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $db_user;
        GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO $db_user;
        
        -- Set default privileges for future objects
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $db_user;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $db_user;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO $db_user;
EOSQL
}

# Create multiple databases from environment variable
if [ -n "$INITDB_MULTIPLE_DATABASES" ]; then
    IFS=',' read -ra DB_ARRAY <<< "$INITDB_MULTIPLE_DATABASES"
    
    for db_spec in "${DB_ARRAY[@]}"; do
        # Trim whitespace
        db_spec=$(echo "$db_spec" | xargs)
        
        # Check if spec includes explicit user:password
        if [[ "$db_spec" == *":"* ]]; then
            IFS=':' read -r db_name db_user db_password <<< "$db_spec"
            create_database_with_user "$db_name" "$db_user" "$db_password"
        else
            # Check for specific environment variables
            db_upper=$(echo "$db_name" | tr '[:lower:]' '[:upper:]' | tr '-' '_')
            specific_user_var="DB_${db_upper}_USER"
            specific_pass_var="DB_${db_upper}_PASSWORD"
            
            db_user="${!specific_user_var:-}"
            db_password="${!specific_pass_var:-}"
            
            create_database_with_user "$db_spec" "$db_user" "$db_password"
        fi
    done
fi

# Create specific databases from environment (backward compatibility)
if [ -n "${DB_STAGING_USER:-}" ] && [ -n "${DB_STAGING_PASSWORD:-}" ]; then
    create_database_with_user "db_staging" "$DB_STAGING_USER" "$DB_STAGING_PASSWORD"
fi

if [ -n "${DB_SITE_USER:-}" ] && [ -n "${DB_SITE_PASSWORD:-}" ]; then
    create_database_with_user "db_site" "$DB_SITE_USER" "$DB_SITE_PASSWORD"
fi

echo "Database initialization completed."