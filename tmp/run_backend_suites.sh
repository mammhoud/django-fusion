#!/usr/bin/env bash
set -e
cd /home/structa.cloud
UV_BIN=$(command -v uv || echo /root/.local/bin/uv)

echo '════════ precis: api smoke + landing api + fixture content ════════'
cd projects/precis/main/backend
timeout 850 "$UV_BIN" --project .. run --frozen python manage.py test \
  tests.test_api_smoke tests.test_landing_api tests.test_products_api --keepdb 2>&1 \
  | grep -E '^(OK|FAILED|Ran|ERROR|FAIL)' -A 3 | head -15

echo '════════ landing-fusion: manage.py check + migration plan ════════'
cd /home/structa.cloud/projects/precis/landi/backend
"$UV_BIN" --project .. run --frozen python manage.py makemigrations --check --dry-run 2>&1 | tail -3
"$UV_BIN" --project .. run --frozen python manage.py check 2>&1 | tail -2

echo '════════ precis: migration plan clean? ════════'
cd /home/structa.cloud/projects/precis/main/backend
"$UV_BIN" --project .. run --frozen python manage.py makemigrations --check --dry-run 2>&1 | tail -3
