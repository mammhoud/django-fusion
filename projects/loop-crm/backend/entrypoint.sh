#!/bin/sh
# Loop-CRM backend startup — wait for the shared PostgreSQL cluster, apply
# migrations, collect static, then hand off to gunicorn.
#
# The `postgres` container belongs to another Compose project
# (applications/databases), so we cannot `depends_on` it from here. This loop
# is the cold-boot ordering guarantee: the container retries the connection
# until the shared database accepts it (bounded by DB_READY_ATTEMPTS), then
# migrates before serving.

set -eu

DB_READY_ATTEMPTS="${DB_READY_ATTEMPTS:-30}"
DB_READY_DELAY="${DB_READY_DELAY:-2}"

echo "[STARTUP] Waiting for the database (${POSTGRES_HOST:-postgres}:${POSTGRES_PORT:-5432}/${POSTGRES_DB:-db_loop_crm})..."

ready=0
attempt=1
while [ "$attempt" -le "$DB_READY_ATTEMPTS" ]; do
    if python manage.py shell -c \
        'from django.db import connection; connection.ensure_connection()' \
        >/dev/null 2>&1; then
        ready=1
        echo "[STARTUP] Database is ready"
        break
    fi
    echo "[STARTUP] Database not ready (attempt ${attempt}/${DB_READY_ATTEMPTS}); retrying in ${DB_READY_DELAY}s..."
    sleep "$DB_READY_DELAY"
    attempt=$((attempt + 1))
done

if [ "$ready" -ne 1 ]; then
    echo "[STARTUP] Database did not become ready; refusing to start" >&2
    exit 1
fi

echo "[STARTUP] Applying migrations..."
python manage.py migrate --noinput

echo "[STARTUP] Collecting static files..."
python manage.py collectstatic --noinput

if [ "${DEMO_MODE:-0}" = "1" ]; then
    echo "[STARTUP] DEMO_MODE enabled — seeding the demo workspace (idempotent)..."
    python manage.py seed_demo --superuser
else
    echo "[STARTUP] DEMO_MODE disabled — skipping demo seed"
fi

echo "[STARTUP] Starting gunicorn..."
exec gunicorn wsgi:application \
    --bind 0.0.0.0:8074 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
