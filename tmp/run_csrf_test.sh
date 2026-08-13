#!/usr/bin/env bash
cd /home/structa.cloud/projects/precis/backend
UV_BIN=$(command -v uv || echo /root/.local/bin/uv)
timeout 700 "$UV_BIN" --project .. run --frozen python manage.py test \
  tests.test_landing_api.BlogCommentsApiTests.test_authenticated_post_requires_csrf_token \
  --keepdb 2>&1 | tail -16
