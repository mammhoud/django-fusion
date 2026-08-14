#!/bin/bash
set -u
cd /home/structa.cloud/projects/precis/main/backend
UV_BIN=$(command -v uv || echo /root/.local/bin/uv)

echo "=== ruff ==="
"$UV_BIN" run --frozen ruff check tests/test_fixture_data.py 2>&1 | tail -3

echo
echo "=== new teaser tests ==="
timeout 600 "$UV_BIN" run python manage.py test \
  tests.test_fixture_data.TestFixtureData.test_home_renders_single_distinct_learning_teaser \
  tests.test_fixture_data.TestFixtureData.test_home_fragment_never_contains_learning_teaser \
  --keepdb 2>&1 | grep -E '^(OK|FAILED|Ran|ERROR|FAIL|Error|Traceback)' -A 4 | head -20

echo
echo "=== precis frontend check ==="
cd /home/structa.cloud/projects/precis/main/frontend
npm run check 2>&1 | grep -E '^Result|error|Error' | tail -4

echo "DONE"
