#!/bin/bash
set -euo pipefail

CYPERCLOUD_PORT="${CYPERCLOUD_PORT:-5073}"
APP_HOME="/app/syntara"
WORKERS="${WORKERS:-2}"
# Auto-recycle workers to flush stale in-memory state (template caches,
# cached.Loader entries, accumulated per-worker caches) after they have
# served MAX_REQUESTS requests. Jitter spreads restarts so a thundering
# herd is avoided. Set MAX_REQUESTS=0 to disable.
MAX_REQUESTS="${MAX_REQUESTS:-1000}"
MAX_REQUESTS_JITTER="${MAX_REQUESTS_JITTER:-100}"

cd "$APP_HOME"

# ── Persist SQLite database in the data volume ──────────────────────────
# The Docker compose mounts a named volume at /app/cypercloud/data/, but
# Django's default DB path is /app/cypercloud/db.sqlite3. Create a symlink
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

        echo "🚀 Starting gunicorn on 0.0.0.0:${CYPERCLOUD_PORT}..."
        exec gunicorn \
            --bind "0.0.0.0:${CYPERCLOUD_PORT}" \
            --workers "${WORKERS}" \
            --worker-class uvicorn.workers.UvicornWorker \
            --max-requests "${MAX_REQUESTS}" \
            --max-requests-jitter "${MAX_REQUESTS_JITTER}" \
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
