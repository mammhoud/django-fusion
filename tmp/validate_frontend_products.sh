#!/usr/bin/env bash
set -e
cd /home/structa.cloud

echo '════════ landing-fusion frontend: check ════════'
cd projects/precis/landi/frontend
npm run check 2>&1 | grep -E 'error|Result|Error|Found' | head -15 || true
echo '── astro build products page ──'
npx astro build 2>&1 | tail -4 || true

echo '════════ precis frontend: check ════════'
cd /home/structa.cloud/projects/precis/main/frontend
npm run check 2>&1 | grep -E 'error|Result|Error|Found' | head -15 || true

echo '════════ landing-fusion frontend unit tests (store) ════════'
cd /home/structa.cloud/projects/precis/landi/frontend
npm test 2>&1 | grep -E 'Tests:|Test Files|passed|failed' | head -8 || true
