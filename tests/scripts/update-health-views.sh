#!/bin/bash
# ============================================================
# Update Health Views in Running Containers
# Copies the updated health check views to running containers
# ============================================================

set -e

echo "Updating health check views in containers..."

# Update ctc-website
echo "→ Updating ctc-website..."
docker cp libs/django-grep/src/django_grep/health/views.py ctc-website:/opt/venv/lib/python3.12/site-packages/django_grep/health/views.py
docker exec ctc-website python -c "import django_grep.health.views; import importlib; importlib.reload(django_grep.health.views)"
echo "✓ ctc-website updated"

# Update structa-website
echo "→ Updating structa-website..."
docker cp libs/django-grep/src/django_grep/health/views.py structa-website:/opt/venv/lib/python3.12/site-packages/django_grep/health/views.py
docker exec structa-website python -c "import django_grep.health.views; import importlib; importlib.reload(django_grep.health.views)"
echo "✓ structa-website updated"

# Restart services to reload code
echo "→ Restarting services..."
docker restart ctc-website structa-website

echo "✓ Health check views updated successfully!"
echo ""
echo "Wait 30 seconds for services to restart, then run:"
echo "  make health-check"
