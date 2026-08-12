#!/usr/bin/env bash
cd /home/structa.cloud
UV_BIN=$(command -v uv || echo /root/.local/bin/uv)

echo '=== products API excludes hidden ceptor-ai? ==='
cd projects/landing-fusion/backend
"$UV_BIN" --project .. run --frozen python manage.py shell -c "
from django.test import Client
import json
c = Client()
data = json.loads(c.get('/apis/products/').content)
slugs = [p.get('slug') for p in data.get('products', [])]
print('ceptor-ai present:', any('ceptor-ai' in s for s in slugs))
print('count:', len(slugs))
print('sample:', slugs[:4])
" 2>&1 | tail -4

echo '=== landing frontend tests ==='
cd /home/structa.cloud/projects/landing-fusion/frontend
npm test 2>&1 | grep -E 'ℹ (tests|pass|fail)' | head -5
