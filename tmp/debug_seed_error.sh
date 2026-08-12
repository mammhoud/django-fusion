#!/usr/bin/env bash
cd /home/structa.cloud
UV_BIN=$(command -v uv || echo /root/.local/bin/uv)

echo '════════ precis seed (setup_wagtail_home) ════════'
cd projects/precis/backend
timeout 400 "$UV_BIN" --project .. run --frozen python manage.py setup_wagtail_home 2>&1 \
  | grep -iE 'error|traceback|failed|validation|Seeded' | grep -v treebeard | head -14

echo '════════ landing seed on a fresh test DB (via test runner) ════════'
cd /home/structa.cloud/projects/landing-fusion/backend
timeout 500 "$UV_BIN" --project .. run --frozen python manage.py test apps.pages --keepdb 2>&1 \
  | grep -iE 'error|traceback|FAILED|^Ran|^OK' | grep -v treebeard | head -12
