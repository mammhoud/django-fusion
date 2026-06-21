#!/bin/bash
set -e
set -u

create_db() {
    local dbname=$1
    local owner=$2
    local password=$3
    echo "Creating database '$dbname' owned by '$owner'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        DO \$\$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '$dbname') THEN
                CREATE DATABASE $dbname;
                GRANT ALL PRIVILEGES ON DATABASE $dbname TO $owner;
            END IF;
        END
        \$\$;
EOSQL
}

if [ -n "${POSTGRES_MULTIPLE_DATABASES:-}" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
    IFS=',' read -ra DB_PAIRS <<< "$POSTGRES_MULTIPLE_DATABASES"
    for pair in "${DB_PAIRS[@]}"; do
        IFS=':' read -r dbname owner password <<< "$pair"
        if [ -z "$dbname" ] || [ -z "$owner" ] || [ -z "$password" ]; then
            echo "Warning: invalid pair '$pair' – skipping"
            continue
        fi
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
            DO \$\$
            BEGIN
                IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$owner') THEN
                    CREATE ROLE $owner WITH LOGIN PASSWORD '$password';
                END IF;
            END
            \$\$;
EOSQL
        create_db "$dbname" "$owner" "$password"
    done
    echo "Multiple databases created."
else
    echo "No multiple databases specified; skipping."
fi