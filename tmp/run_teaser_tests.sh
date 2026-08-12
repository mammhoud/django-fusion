#!/usr/bin/env bash
set -e
cd /home/structa.cloud/projects/precis/backend
UV_BIN=$(command -v uv || echo /root/.local/bin/uv)

echo '=== running teaser tests ==='
timeout 900 "$UV_BIN" --project .. run --frozen python manage.py test \
  tests.test_fixture_data.TestFixtureData.test_home_renders_single_distinct_learning_teaser \
  tests.test_fixture_data.TestFixtureData.test_home_fragment_never_contains_learning_teaser \
  --keepdb 2>&1 | tail -60
