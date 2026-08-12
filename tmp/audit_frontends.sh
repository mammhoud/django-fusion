#!/bin/bash
# Audit of JS/TS/Astro/React frontend projects: ports, env files, hardcoded values
cd /home/structa.cloud

echo "=== 1. All frontend package.json locations ==="
find projects libs -maxdepth 5 -name 'package.json' -not -path '*/node_modules/*' -not -path '*/legacy-react/*' -not -path '*/dist/*' 2>/dev/null | sort

echo
echo "=== 2. Ports in astro/vite configs ==="
find projects libs -name 'astro.config.mjs' -o -name 'astro.config.ts' -o -name 'vite.config.ts' -o -name 'vite.config.js' -o -name 'vite.config.mjs' 2>/dev/null | grep -v node_modules | grep -v dist | while read -r f; do
  ports=$(grep -oE "port[[:space:]]*:[[:space:]]*[0-9]+|--port[[:space:]]+[0-9]+|host[[:space:]]*:[[:space:]]*['\"][^'\"]+['\"]" "$f" 2>/dev/null | tr '\n' ' ')
  echo "  $f -> $ports"
done

echo
echo "=== 3. .env / .env.example files per project ==="
find projects libs -maxdepth 4 \( -name '.env' -o -name '.env.example' -o -name '.env.*' \) -not -path '*/node_modules/*' 2>/dev/null | sort

echo
echo "=== 4. package.json scripts with ports ==="
find projects libs -maxdepth 5 -name 'package.json' -not -path '*/node_modules/*' -not -path '*/dist/*' -not -path '*/legacy-react/*' 2>/dev/null | while read -r f; do
  echo "--- $f"
  python3 -c "
import json
d = json.load(open('$f'))
for k, v in d.get('scripts', {}).items():
    if any(p in v for p in ('astro', 'vite', '--port', 'PORT=', 'dev', 'preview')):
        print(f'  {k}: {v}')
" 2>/dev/null
done

echo
echo "=== 5. Hardcoded backend/API URLs in frontend src ==="
grep -rnE "http://localhost:[0-9]+|http://127\.0\.0\.1:[0-9]+" projects/*/frontend/src projects/formints/*/frontend/src projects/formints/*/src 2>/dev/null | grep -v node_modules | grep -v '.test.' | grep -v '.spec.' | head -30

echo
echo "=== 6. Existing PUBLIC_ / env var usage in frontend src ==="
grep -rnE "import\.meta\.env|process\.env|PUBLIC_" projects/*/frontend/src projects/formints/*/frontend/src 2>/dev/null | grep -v node_modules | grep -v '.test.' | head -25

echo
echo "DONE"
