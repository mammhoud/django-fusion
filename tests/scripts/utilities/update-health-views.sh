#!/bin/bash
set -euo pipefail

# Hot-patch django-osoul health views inside running website containers.
# Prefer rebuilding images for normal deployments; this helper is for local debugging.

containers_to_restart=()
for container in ctc-research-website lms-demo-website vresume-website; do
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        echo "→ Updating ${container}..."
        docker cp libs/django-osoul/src/django_osoul/health/views.py "${container}:/opt/venv/lib/python3.12/site-packages/django_osoul/health/views.py"
        docker exec "$container" python -c "import django_osoul.health.views; import importlib; importlib.reload(django_osoul.health.views)"
        containers_to_restart+=("$container")
        echo "✓ ${container} updated"
    else
        echo "- ${container} is not running; skipping"
    fi
done

if [ "${#containers_to_restart[@]}" -gt 0 ]; then
    docker restart "${containers_to_restart[@]}"
fi
