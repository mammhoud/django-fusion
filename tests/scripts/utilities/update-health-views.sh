#!/bin/bash
set -euo pipefail

# Hot-patch django-fusion health views inside running website containers.
# Prefer rebuilding images for normal deployments; this helper is for local debugging.

containers_to_restart=()
for container in ctc-research-website lms-demo-website vresume-website; do
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        echo "→ Updating ${container}..."
        docker cp libs/django-fusion/src/django_fusion/health/views.py "${container}:/opt/venv/lib/python3.12/site-packages/django_fusion/health/views.py"
        docker exec "$container" python -c "import django_fusion.health.views; import importlib; importlib.reload(django_fusion.health.views)"
        containers_to_restart+=("$container")
        echo "✓ ${container} updated"
    else
        echo "- ${container} is not running; skipping"
    fi
done

if [ "${#containers_to_restart[@]}" -gt 0 ]; then
    docker restart "${containers_to_restart[@]}"
fi
