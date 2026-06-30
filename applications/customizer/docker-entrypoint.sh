#!/bin/bash
set -euo pipefail

CUSTOMIZER_PORT="${CUSTOMIZER_PORT:-5073}"
APP_HOME="/app/customizer"
WORKERS="${WORKERS:-2}"

cd "$APP_HOME"

# ── Persist SQLite database in the data volume ──────────────────────────
# The Docker compose mounts a named volume at /app/customizer/data/, but
# Django's default DB path is /app/customizer/db.sqlite3. Create a symlink
# so the DB file lives inside the persisted volume.
if [ ! -f "${APP_HOME}/data/db.sqlite3" ] && [ ! -L "${APP_HOME}/db.sqlite3" ]; then
    mkdir -p "${APP_HOME}/data"
    touch "${APP_HOME}/data/db.sqlite3"
fi
if [ ! -L "${APP_HOME}/db.sqlite3" ]; then
    ln -sf "data/db.sqlite3" "${APP_HOME}/db.sqlite3"
fi

case "${1:-server}" in
    server)
        echo "🚀 Running Django system checks..."
        python manage.py check --deploy 2>&1 || echo "  ⚠️  Deploy checks had warnings (non-fatal)"

        echo "🚀 Applying migrations..."
        python manage.py migrate --noinput 2>&1

        echo "🚀 Starting gunicorn on 0.0.0.0:${CUSTOMIZER_PORT}..."
        exec gunicorn \
            --bind "0.0.0.0:${CUSTOMIZER_PORT}" \
            --workers "${WORKERS}" \
            --worker-class uvicorn.workers.UvicornWorker \
            --access-logfile - \
            --error-logfile - \
            server:asgi_application
        ;;

    manage)
        shift
        echo "🚀 Running manage.py $*..."
        exec python manage.py "$@"
        ;;

    shell)
        exec python manage.py shell
        ;;

    bash|sh)
        exec "$@"
        ;;

    *)
        echo "Usage: /entrypoint [server|manage <args>|shell|bash]"
        exit 1
        ;;
esac
