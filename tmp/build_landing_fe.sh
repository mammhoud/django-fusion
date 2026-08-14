#!/usr/bin/env bash
set -e
cd /home/structa.cloud/projects/precis/landi/frontend
echo '=== astro build ==='
npx astro build 2>&1 | tail -4
echo '=== products page built? ==='
ls dist/products/index.html 2>/dev/null && echo OK || echo MISSING
echo '=== unit tests ==='
npm test 2>&1 | grep -E 'ℹ (tests|pass|fail)' | head -5
