#!/bin/bash
cd /home/structa.cloud

echo "=== 1. .gitignore .env patterns ==="
grep -nE '^\\.env|env' .gitignore projects/.gitignore 2>/dev/null | head -12

echo
echo "=== 2. Makefile env loading + ports (landing/precis/formint-pro/cloud/community/standard/client) ==="
for f in \
  projects/precis/landi/Makefile \
  projects/precis/main/Makefile \
  projects/formints/formint-pro/Makefile \
  projects/formints/formint-cloud/Makefile \
  projects/formints/formint-community/Makefile \
  projects/formints/formint-standard/Makefile \
  projects/formints/formint-client/Makefile \
  projects/formints/Makefile; do
  echo "--- $f"
  grep -nE 'include \.env|set -a|\. \./\.env|export |--port|PORT=|port *[:=] *[0-9]+|432[0-9]|807[0-9]|876[0-9]|142[01]' "$f" 2>/dev/null | head -8
done

echo
echo "=== 3. tauri.conf.json ports (community/standard/client) ==="
for f in projects/formints/formint-community/src-tauri/tauri.conf.json \
         projects/formints/formint-standard/src-tauri/tauri.conf.json \
         projects/formints/formint-client/src-tauri/tauri.conf.json; do
  echo "--- $f"
  grep -nE '"port"|beforeDevCommand|devUrl|frontendDist' "$f" 2>/dev/null | head -6
done

echo
echo "=== 4. existing .env content shape (non-secret keys only) ==="
for f in projects/formints/formint-community/.env projects/formints/formint-standard/.env; do
  echo "--- $f"
  grep -oE '^[A-Z_0-9]+=' "$f" 2>/dev/null | head -10
done

echo
echo "=== 5. next-legacy scripts ==="
python3 -c "
import json
d = json.load(open('projects/precis/main/frontend-next-legacy/package.json'))
print(json.dumps(d.get('scripts', {}), indent=1))
" 2>/dev/null

echo
echo "DONE"
