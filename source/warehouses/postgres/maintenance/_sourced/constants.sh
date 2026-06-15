#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

# Configuration from environment variables
export POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
export POSTGRES_PORT="${POSTGRES_PORT:-5432}"
export POSTGRES_USER="${POSTGRES_USER:-postgres}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-}"

# Get all databases from environment or discover them
if [ -n "${INITDB_MULTIPLE_DATABASES:-}" ]; then
    # Parse databases from environment variable
    IFS=',' read -ra ALL_DATABASES <<< "$INITDB_MULTIPLE_DATABASES"
    ALL_DATABASES=("${ALL_DATABASES[@]//[[:space:]]/}")  # Remove whitespace
    
    # Also include the default POSTGRES_DB if it exists
    if [ -n "${POSTGRES_DB:-}" ] && [ "$POSTGRES_DB" != "postgres" ]; then
        ALL_DATABASES+=("$POSTGRES_DB")
    fi
else
    # Discover databases from PostgreSQL
    if [ -n "${POSTGRES_PASSWORD}" ]; then
        export PGPASSWORD="$POSTGRES_PASSWORD"
    fi
    
    # Get list of all non-system databases
    ALL_DATABASES=($(psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" \
        -t -c "SELECT datname FROM pg_database WHERE datname NOT IN ('postgres', 'template0', 'template1')" \
        postgres 2>/dev/null || echo ""))
fi

# Unique list of databases
ALL_DATABASES=($(echo "${ALL_DATABASES[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))

# Backup configuration
export BACKUP_DIR_PATH="${BACKUP_DIR_PATH:-/backups}"
export BACKUP_FILE_PREFIX="${BACKUP_FILE_PREFIX:-backup}"
export BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"