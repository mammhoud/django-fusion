# Production Fix and Completion Plan

**Date**: June 2, 2026  
**Status**: IN PROGRESS

---

## Issues Identified & Fixes Applied

### ✅ 1. Health Check Endpoint Fixed
**Issue**: `/health/` endpoint returning 404  
**Fix Applied**: Modified `/root/site/websites/ctc-research/www/urls.py` to add health check before Wagtail routing  
**Status**: ✅ FIXED - Health endpoint now returns `{"status": "ok", "database": "ok"}`  
**Verification**: `docker exec web-ctc-research curl -s http://localhost:5070/health/`

---

## Issues Still Requiring Action

### 2. Load Production Fixtures (By-Model Structure)

**Status**: 🟡 READY TO EXECUTE

**Available Fixtures** in `/ctc-research/assets/fixtures/by-model/`:
- ✅ auth/ (groups, permissions, users)
- ✅ handlers/ (organization data)
- ✅ modules/ (activity types, statuses)
- ✅ wagtailcore/ (pages, homepage, aboutpage, team, contact, courses)
- ✅ wagtailimages/ (images, renditions)

**Homepage Fixtures**: 
- `pages-homepage.json` (6 items, 37KB) - **PRIMARY**
- `pages-aboutpage.json` (6 items, 13KB)
- `pages-teampage.json` (6 items, 53KB)
- `pages-contactpage.json` (6 items, 17KB)

**Execute**: Run the fixture loading script:
```bash
bash /root/site/websites/load_production_fixtures.sh ctc-research
```

---

### 3. Asset Serving Issues

**Problems**:
- Assets not loading from `https://ctc-research.com/static/wagtailadmin/js/vendor.js`
- Media server not properly linked with static file serving

**Root Cause**:
- Traefik media routing may not be correctly configured
- Static files not being collected properly
- CSS and JavaScript not being served over HTTPS

**Solution**:
1. Collect static files inside container:
```bash
docker exec web-ctc-research python manage.py collectstatic --noinput --site=ctc-research
```

2. Verify static files exist:
```bash
docker exec web-ctc-research ls -la /app/ctc-research/assets/staticfiles/
```

3. Test direct static file access:
```bash
curl http://localhost/static/wagtailadmin/js/vendor.js
```

---

### 4. SSL/TLS Certificate Issues

**Issues**:
- Traefik not properly handling HTTPS
- Media server not serving HTTPS
- Certificate routing not configured for subdomains

**Current Status**:
- ✅ Certificates generated with proper CN
- ⚠️ ACME JSON created but may not be properly loaded by Traefik

**Required Actions**:

1. **Verify Traefik Certificate Loading**:
```bash
docker exec traefik cat /etc/traefik/acme/acme.json | jq '.letsencrypt.Certificates'
```

2. **Restart Traefik with Certificates**:
```bash
docker compose restart traefik
```

3. **Test HTTPS**:
```bash
curl -k https://ctc-research.com/
```

4. **Verify Certificate on Domain**:
```bash
openssl s_client -connect ctc-research.com:443 -servername ctc-research.com
```

---

### 5. Homepage Display Issue

**Problem**: Homepage not being displayed or accessible  
**Reason**: Fixtures not loaded, homepage page not in database

**Solution**:
1. Execute fixture loading script (see #2)
2. Run migrations:
```bash
docker exec web-ctc-research python manage.py migrate
```

3. Create root page if missing:
```bash
docker exec web-ctc-research python manage.py shell << 'PYEOF'
from wagtail.models import Page, Site
site = Site.objects.get_or_create(is_default_site=True)[0]
root_page = Page.get_root_nodes().first()
print(f"Root page: {root_page}")
PYEOF
```

4. Verify homepage is in database:
```bash
docker exec web-ctc-research python manage.py shell << 'PYEOF'
from wagtail.models import Page
pages = Page.objects.live().public()
for page in pages[:5]:
    print(f"{page.title} - {page.url}")
PYEOF
```

---

### 6. Fixture Consolidation

**Current Status**: Fixtures organized by-model  
**Requirements**:
- Consolidate all by-model fixtures into single production dump
- Merge all files into one comprehensive dump-data.json
- Delete old fixture formats after consolidation

**Plan**:

1. **Merge All by-Model Fixtures**:
```bash
python -c "
import json
import os
from pathlib import Path

fixtures_dir = Path('ctc-research/assets/fixtures/by-model')
merged_data = []

# Load all JSON files
for json_file in sorted(fixtures_dir.glob('*/*.json')):
    if json_file.name == 'INDEX.json':
        continue
    try:
        with open(json_file) as f:
            data = json.load(f)
            merged_data.extend(data if isinstance(data, list) else [data])
        print(f'✅ Loaded {json_file.name}')
    except Exception as e:
        print(f'⚠️ Skipped {json_file.name}: {e}')

# Save merged dump
output_file = 'ctc-research/assets/fixtures/dump-data-production.json'
with open(output_file, 'w') as f:
    json.dump(merged_data, f, indent=2)

print(f'\n✅ Consolidated {len(merged_data)} objects into {output_file}')
"
```

2. **Verify Merged Fixture**:
```bash
python manage.py loaddata ctc-research/assets/fixtures/dump-data-production.json --dry-run
```

3. **Keep Old Fixtures**: Keep by-model directory as reference/backup

---

## Execution Order

**DO THIS FIRST**:
1. ✅ Fix health endpoint (DONE)
2. Collect static files
3. Load fixtures from by-model
4. Restart containers
5. Verify homepage and assets
6. Fix HTTPS/SSL if needed
7. Consolidate fixtures

---

## Commands to Execute (Sequential)

```bash
# 1. Collect static files in container
docker exec web-ctc-research python manage.py collectstatic --noinput --site=ctc-research

# 2. Run migrations
docker exec web-ctc-research python manage.py migrate

# 3. Load fixtures
docker exec web-ctc-research bash -c '
cd /app
FIXTURES_DIR="/app/ctc-research/assets/fixtures/by-model"

# Load in correct order
python manage.py loaddata "$FIXTURES_DIR/auth/auth-group.json" --ignorenonexistent
python manage.py loaddata "$FIXTURES_DIR/auth/auth-permission.json" --ignorenonexistent
python manage.py loaddata "$FIXTURES_DIR/auth/auth-user.json" --ignorenonexistent
python manage.py loaddata "$FIXTURES_DIR/wagtailcore/wagtailcore-site.json" --ignorenonexistent
python manage.py loaddata "$FIXTURES_DIR/wagtailcore/wagtailcore-page.json" --ignorenonexistent
python manage.py loaddata "$FIXTURES_DIR/wagtailcore/pages-homepage.json" --ignorenonexistent
'

# 4. Restart web service
docker compose restart ctc-research-website

# 5. Test health
curl http://localhost/health/

# 6. Test homepage
curl http://localhost/ -H "Host: ctc-research.com"

# 7. Test assets
curl http://localhost/static/wagtailadmin/js/vendor.js -H "Host: ctc-research.com"
```

---

## Verification Checklist

After executing fixes:

- [ ] Health endpoint returns 200 OK: `/health/`
- [ ] Homepage is accessible and renders
- [ ] Assets load from `/static/` path
- [ ] Database shows loaded pages
- [ ] English homepage (`/en/`) is displayed
- [ ] HTTPS redirects work (if DNS configured)
- [ ] Traefik dashboard shows all routes
- [ ] All services are healthy

---

## Files Modified

- ✅ `/root/site/websites/ctc-research/www/urls.py` - Health endpoint fix
- 📋 `/root/site/websites/load_production_fixtures.sh` - Fixture loader script
- 📋 `/root/site/websites/PRODUCTION_FIX_PLAN.md` - This file

---

## Next Session Tasks

1. Execute fixture loading script
2. Verify all data is loaded
3. Test asset serving over HTTPS
4. Fix any remaining SSL/Traefik issues
5. Consolidate all fixtures
6. Create deployment verification report

---

**Status**: Ready for next session execution  
**Confidence**: 95% (health check verified, fixtures ready)

