#!/usr/bin/env bash
set -e
cd /home/structa.cloud

echo '════════ precis-landing frontend unit tests ════════'
cd projects/precis/landi/frontend
npm test 2>&1 | tail -12

echo '════════ precis-landing backend targeted tests (products/api/seed) ════════'
cd /home/structa.cloud/projects/precis/landi/backend
UV_BIN=$(command -v uv || echo /root/.local/bin/uv)
timeout 700 "$UV_BIN" --project .. run --frozen python manage.py test \
  apps.pages.tests.test_products_api apps.pages.tests.test_seed_pages --keepdb 2>&1 | grep -E '^(OK|FAILED|Ran|ERROR|FAIL)' -A 4 | head -20 || echo '(targeted test labels may differ — listing available)'
ls apps/pages/tests/ 2>/dev/null | head -20

echo '════════ precis backend targeted tests (products api) ════════'
cd /home/structa.cloud/projects/precis/precis-lms/backend
timeout 700 "$UV_BIN" --project .. run --frozen python manage.py test \
  apps.pages.tests.test_products_api --keepdb 2>&1 | grep -E '^(OK|FAILED|Ran|ERROR|FAIL)' -A 4 | head -20 || echo '(no dedicated products test file — skipping)'
ls apps/pages/tests/ 2>/dev/null | head
