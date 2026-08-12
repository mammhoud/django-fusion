#!/usr/bin/env bash
set -e
cd /home/structa.cloud
UV_BIN=$(command -v uv || echo /root/.local/bin/uv)

echo '════════ landing-fusion: seed products ════════'
cd projects/landing-fusion/backend
"$UV_BIN" --project .. run --frozen python manage.py seed_pages 2>&1 | grep -iE 'product|error|failed' | tail -10

echo '════════ landing-fusion: /apis/products/ API ════════'
"$UV_BIN" --project .. run --frozen python manage.py shell -c "
from django.test import Client
c = Client()
r = c.get('/apis/products/')
print('status:', r.status_code)
import json
data = json.loads(r.content)
print('total products:', len(data.get('products', [])))
for p in data.get('products', [])[:4]:
    print(' -', p.get('slug'), '| lang:', p.get('language'), '| price:', p.get('price'), p.get('currency'), '| href:', p.get('href'))
" 2>&1 | tail -10

echo '════════ landing-fusion: seed products rerun (idempotent) ════════'
"$UV_BIN" --project .. run --frozen python manage.py seed_pages 2>&1 | grep -iE 'product|error|failed' | tail -4

echo '════════ precis: seed products ════════'
cd /home/structa.cloud/projects/precis/backend
"$UV_BIN" --project .. run --frozen python manage.py setup_wagtail_home 2>&1 | grep -iE 'product|error|failed' | tail -8

echo '════════ precis: /api/products/ API ════════'
"$UV_BIN" --project .. run --frozen python manage.py shell -c "
from django.test import Client
c = Client()
r = c.get('/api/products/')
print('status:', r.status_code)
import json
data = json.loads(r.content)
print('total products:', len(data.get('data', [])))
for p in data.get('data', [])[:4]:
    print(' -', p.get('slug'), '| lang:', p.get('language'), '| price:', p.get('price'), p.get('currency'), '| href:', p.get('href'))
" 2>&1 | tail -10

echo '════════ precis: language filter ════════'
"$UV_BIN" --project .. run --frozen python manage.py shell -c "
from django.test import Client
c = Client()
r = c.get('/api/products/?language=ar')
import json
data = json.loads(r.content)
print('ar products:', [p.get('slug') for p in data.get('data', [])])
" 2>&1 | tail -3
