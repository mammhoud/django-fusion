# Complete Deployment & Testing Plan
**Date**: June 2, 2026  
**Priority**: CTC-Research, Asset Build, Full Test Suite  

## Executive Summary
This document outlines a comprehensive deployment and testing workflow for the structa.cloud multi-site workspace. The plan covers:
1. ✅ Fixing current issues (health check, DB auth)
2. ✅ Building all frontend assets
3. ✅ Running all tests with full fixtures
4. ✅ Verifying all websites and asset serving
5. ✅ Ensuring media server works with shared static files
6. ✅ Redeployment and verification

---

## Current Status

### ✅ Healthy Services
- PostgreSQL (12h, healthy)
- Redis (12h, healthy)
- Traefik (11h, healthy)
- Shared-media (11h, healthy, 1,684 static files)

### 🔴 Issues to Fix
1. **ctc-research health check failing**: Health check uses `0.0.0.0:5070` but ALLOWED_HOSTS doesn't include it
   - **Fix**: Update health check to use `127.0.0.1` or `localhost`
   - **Impact**: Container shows unhealthy but app is actually running
2. **Database auth warnings**: PostgreSQL auth failures in logs
   - **Likely cause**: Health check misconfiguration
   - **Verify**: After health check fix

---

## Phase 1: Fix Current Issues (Immediate)

### 1.1 Fix Health Check Configuration
**Problem**: Health check curl hits `0.0.0.0:5070/health/` but Django rejects invalid host
**Solution**: Update docker-compose to use `127.0.0.1` or add `0.0.0.0` to ALLOWED_HOSTS

**Files to update**:
- `/root/site/websites/ctc-research/docker-compose.yml`
- `/root/site/websites/lms/docker-compose.yml` (if applicable)
- `/root/site/websites/VResume/docker-compose.yml` (if applicable)

**Commands to run**:
```bash
# Restart containers with fixed health check
docker compose -f docker-compose.yml down
docker compose -f docker-compose.yml up -d --remove-orphans

# Verify health
docker compose -f docker-compose.yml ps
```

### 1.2 Verify Database Connectivity
```bash
# Test connections to all three databases
docker exec postgres psql -U structa -d db_ctc -c "SELECT 1;" 2>&1
docker exec postgres psql -U structa -d db_structa -c "SELECT 1;" 2>&1
docker exec postgres psql -U structa -d vresume -c "SELECT 1;" 2>&1

# Or use Django shell
docker exec web-ctc-research python manage.py shell -c "from django.db import connection; cursor = connection.cursor(); print('DB OK')"
```

---

## Phase 2: Build All Frontend Assets

### 2.1 Install Dependencies
```bash
cd /root/site/websites
npm --prefix assets install --legacy-peer-deps --no-audit
```

### 2.2 Build Assets for Each Site
```bash
# Build ctc-research (Tailwind + SCSS + JS)
make build-assets WEBSITE=ctc

# Build lms/structa (Tailwind + SCSS + JS)
make build-assets WEBSITE=structa

# Build VResume (Tailwind + SCSS + JS)
make build-assets WEBSITE=vresume

# Or build all at once
make build-assets-all
```

### 2.3 Collect Static Files
```bash
# For each site
docker exec web-ctc-research python manage.py collectstatic --noinput --site ctc-research 2>&1 | tee logs/collectstatic-ctc.log
docker exec web-lms python manage.py collectstatic --noinput --site lms 2>&1 | tee logs/collectstatic-lms.log
docker exec web-vresume python manage.py collectstatic --noinput --site vresume 2>&1 | tee logs/collectstatic-vresume.log

# Or via Makefile
make collectstatic-site WEBSITE=ctc
```

### 2.4 Verify Asset Output
```bash
# Check bundles created
ls -lh ctc-research/assets/bundles/
ls -lh lms/assets/bundles/
ls -lh VResume/assets/bundles/

# Check static files collected
ls -lh ctc-research/assets/staticfiles/ | head -20
ls -lh lms/assets/staticfiles/ | head -20
ls -lh VResume/assets/staticfiles/ | head -20

# Verify shared media server has files
docker exec shared-media ls -lh /var/www/static | head -20
docker exec shared-media ls -lh /var/www/sites/ctc-research/static | head -20
```

---

## Phase 3: Load Fixtures & Populate Data

### 3.1 Load Locale Fixtures (Already Done, Verify)
```bash
# Check current locales
docker exec web-ctc-research python manage.py shell <<EOF
from wagtail_localize.models import Locale
for l in Locale.objects.all().order_by('language_code'):
    print(f"✓ {l.language_code}: {l.get_display_name()}")
EOF
```

**Expected output**:
```
✓ ar: العربية (Arabic)
✓ de: Deutsch (German)
✓ en: English
✓ es: Español (Spanish)
✓ fr: Français (French)
✓ pt-br: Português Brasileiro (Portuguese, Brazil)
```

### 3.2 Populate Page Content
**Option A (Recommended): Use populate_content command**
```bash
# For each site
docker exec web-ctc-research python manage.py populate_content --locale en
docker exec web-lms python manage.py populate_content --locale en
docker exec web-vresume python manage.py populate_content --locale en

# Or with markdown file
docker exec web-ctc-research python manage.py populate_content --content-file /app/ctc-research/docs/content.md
```

**Option B: Manual via Admin Panel**
```bash
# Create superuser first
docker exec web-ctc-research python manage.py createsuperuser --noinput \
  --username admin --email admin@ctc-research.com

# Set password
docker exec web-ctc-research python manage.py shell <<EOF
from django.contrib.auth.models import User
u = User.objects.get(username='admin')
u.set_password('admin123')
u.save()
print(f"✓ Admin user created: {u.username}")
EOF

# Access admin at https://ctc-research.com/admin/
```

### 3.3 Verify Pages Created
```bash
# Check page hierarchy
docker exec web-ctc-research python manage.py shell <<EOF
from wagtailcore.models import Page
from wagtail_localize.models import LocalizedPage

print("✓ Pages by site:")
for page in Page.objects.filter(depth__gte=2).select_related('locale'):
    indent = "  " * (page.depth - 2)
    print(f"{indent}└─ {page.title} (locale: {page.locale.language_code if page.locale else 'None'}, id: {page.id})")

print("\n✓ Total pages:", Page.objects.count())
print("✓ Total localized pages:", LocalizedPage.objects.count())
EOF
```

---

## Phase 4: Run Test Suite

### 4.1 Unit Tests
```bash
# All unit tests
make tests-unit

# Or with pytest directly
cd /root/site/websites
./.venv/bin/python -m pytest tests/unit -v

# Per-site unit tests
./.venv/bin/python -m pytest tests/unit -k ctc -v
./.venv/bin/python -m pytest tests/unit -k structa -v
./.venv/bin/python -m pytest tests/unit -k vresume -v
```

### 4.2 Integration Tests
```bash
# All integration tests
make tests-integration

# Or with pytest directly
./.venv/bin/python -m pytest tests/integration -v

# Per-site
./.venv/bin/python -m pytest tests/integration -k ctc -v
```

### 4.3 Website-Specific Tests
```bash
# All website tests
make tests-websites

# Individual sites
make tests-website WEBSITE=ctc
make tests-website WEBSITE=structa
make tests-website WEBSITE=vresume
```

### 4.4 Asset Tests
```bash
# Run any frontend/asset tests
./.venv/bin/python -m pytest tests/assets -v
```

### 4.5 Docker/Container Tests
```bash
# Test container health and environment
docker compose -f docker-compose.yml ps
docker compose -f docker-compose.yml exec web-ctc-research python manage.py check --deploy

# Verify all databases accessible
./.venv/bin/python -m pytest tests/docker -v
```

### 4.6 Production Readiness Tests
```bash
# Run production checks
./.venv/bin/python -m pytest tests/ -k "production" -v

# Or manual checks
docker exec web-ctc-research python manage.py check --deploy
docker exec web-lms python manage.py check --deploy
docker exec web-vresume python manage.py check --deploy
```

---

## Phase 5: Verify Assets & Media Serving

### 5.1 Shared Media Server Test
```bash
# Verify shared-media container is healthy
docker compose -f docker-compose.yml ps shared-media

# Test access to static files
curl -I http://localhost/static/css/master.css
curl -I http://localhost/media/avatar_images/default.png

# Check via traefik
curl -I http://ctc-media.local/static/css/master.css
curl -I http://shared-media.local/static/js/app.js
```

### 5.2 Per-Site Asset Serving
```bash
# CTC Research
curl -I http://localhost:5070/static/css/master.css
curl -I http://ctc-research.local/static/css/master.css

# LMS Demo
curl -I http://localhost:5071/static/css/master.css
curl -I http://structa.local/static/css/master.css

# VResume
curl -I http://localhost:5072/static/css/master.css
curl -I http://vresume.local/static/css/master.css
```

### 5.3 Homepage Verification
```bash
# Test homepages are accessible
curl -fL http://localhost:5070/ | head -50
curl -fL http://localhost:5071/ | head -50
curl -fL http://localhost:5072/ | head -50

# With proper hostname
curl -fL http://ctc-research.local/ | head -50
curl -fL http://structa.local/ | head -50
curl -fL http://vresume.local/ | head -50

# Via traefik (via 80/443)
curl -fL http://ctc-research.local/ -H "Host: ctc-research.local" | head -50
```

### 5.4 Language Routes Test
```bash
# Test localized routes for CTC Research
curl -fL http://localhost:5070/en/ | head -30
curl -fL http://localhost:5070/ar/ | head -30
curl -fL http://localhost:5070/de/ | head -30
curl -fL http://localhost:5070/es/ | head -30
curl -fL http://localhost:5070/fr/ | head -30
curl -fL http://localhost:5070/pt-br/ | head -30
```

### 5.5 Admin Panel Access
```bash
# Admin should be accessible
curl -fL http://localhost:5070/admin/ | head -50

# With credentials
curl -fL -u admin:admin123 http://localhost:5070/admin/ | head -50
```

---

## Phase 6: Full Redeployment

### 6.1 Clean and Rebuild Everything
```bash
# Stop all services
docker compose -f docker-compose.yml down --remove-orphans

# Clean up (optional - if you want fresh start)
# docker compose -f docker-compose.yml down --volumes

# Rebuild all Docker images
make docker-rebuild WEBSITE=ctc-research
make docker-rebuild WEBSITE=lms
make docker-rebuild WEBSITE=vresume

# Or redeploy all at once
make docker-deploy-full
```

### 6.2 Verify All Services Healthy
```bash
# Wait for startup (30-60s)
sleep 30

# Check status
docker compose -f docker-compose.yml ps

# All should show "Up" and "healthy" or no health status
```

### 6.3 Run Verification Suite
```bash
# Comprehensive verification
make verify-runtime-site WEBSITE=ctc-research
make verify-runtime-site WEBSITE=lms
make verify-runtime-site WEBSITE=vresume

# Or all at once
python tests/scripts/verify_runtime.py --site all --strict-assets --strict-pages
```

---

## Phase 7: Performance & Load Testing

### 7.1 Asset Size Check
```bash
# Check bundle sizes (should be <500KB gzipped each)
du -sh ctc-research/assets/bundles/*
du -sh lms/assets/bundles/*
du -sh VResume/assets/bundles/*

# Check minification
file ctc-research/assets/bundles/main.*.js
```

### 7.2 Static File Serving Performance
```bash
# Test response times (should be <100ms for static files)
time curl -s http://localhost/static/css/master.css > /dev/null
time curl -s http://localhost/static/js/app.js > /dev/null

# Load test (optional - requires 'ab' or 'wrk')
ab -n 100 -c 10 http://localhost:5070/
ab -n 100 -c 10 http://localhost:5071/
ab -n 100 -c 10 http://localhost:5072/
```

### 7.3 Homepage Performance
```bash
# Load test homepage
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5070/

# Or with more detailed metrics
curl -I -w "Connect time: %{time_connect}
Transfer Start: %{time_starttransfer}
Total Time: %{time_total}
" http://localhost:5070/
```

---

## Phase 8: Final Verification Checklist

### Infrastructure ✅
- [ ] PostgreSQL healthy and accessible
- [ ] Redis healthy and accessible
- [ ] Traefik healthy, routing traffic
- [ ] All networks created and connected
- [ ] Volumes mounted correctly

### Applications ✅
- [ ] ctc-research container healthy
- [ ] lms container healthy  
- [ ] vresume container healthy
- [ ] All worker services running
- [ ] Health checks passing

### Assets ✅
- [ ] Shared media server healthy
- [ ] All static files collected (1,684+ files)
- [ ] CSS bundles generated and gzipped
- [ ] JavaScript bundles generated and minified
- [ ] Per-site asset directories populated

### Content ✅
- [ ] Homepage loads at root
- [ ] All 6 languages have pages
- [ ] Admin panel accessible
- [ ] Pages properly versioned in database
- [ ] Translations configured

### Tests ✅
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Website-specific tests passing
- [ ] No asset or media loading errors
- [ ] No database connection errors

### External Access ✅
- [ ] ctc-research.com accessible and healthy
- [ ] structa.cloud accessible and healthy
- [ ] vresume.structa.cloud accessible and healthy
- [ ] SSL/TLS certificates valid
- [ ] Traefik dashboard accessible
- [ ] Media server responding correctly

---

## Rollback Plan

If anything goes wrong:

```bash
# Check logs
docker compose -f docker-compose.yml logs --tail 100

# For specific service
docker compose -f docker-compose.yml logs web-ctc-research --tail 50

# Stop everything
docker compose -f docker-compose.yml down

# Restore from backup (if needed)
# docker compose -f docker-compose.yml down --volumes
# Restore postgres_data volume from backup

# Restart services
docker compose -f docker-compose.yml up -d
```

---

## Success Criteria

✅ **Deployment is successful when**:
1. All containers showing "Up" and healthy status
2. All three websites accessible via their domains
3. Asset files served correctly (verify in browser DevTools)
4. All tests passing (unit, integration, website)
5. Admin panels working and authenticated
6. Database connections stable
7. No errors in application logs
8. Response times normal (<200ms for pages, <50ms for static)

---

## Timeline

| Phase | Time | Status |
|-------|------|--------|
| Phase 1: Fix Issues | 5-10 min | Ready |
| Phase 2: Build Assets | 10-15 min | Ready |
| Phase 3: Load Fixtures | 5-10 min | Ready |
| Phase 4: Run Tests | 15-30 min | Ready |
| Phase 5: Verify Assets | 10-15 min | Ready |
| Phase 6: Full Redeploy | 10-20 min | Ready |
| Phase 7: Performance | 10 min | Optional |
| Phase 8: Final Checks | 5 min | Ready |
| **Total** | **70-125 min** | **~2 hours** |

---

## Key Commands Reference

```bash
# Build all assets
make build-assets-all

# Run all tests
make test

# Run website tests
make tests-website WEBSITE=ctc|structa|vresume|all

# Full redeployment
make docker-deploy-full

# Check status
docker compose -f docker-compose.yml ps

# View logs
docker compose -f docker-compose.yml logs -f web-ctc-research

# Access shell
docker exec -it web-ctc-research python manage.py shell

# Migrate databases
docker exec web-ctc-research python manage.py migrate

# Collect static
docker exec web-ctc-research python manage.py collectstatic --noinput

# Create admin user
docker exec web-ctc-research python manage.py createsuperuser

# Verify runtime
python tests/scripts/verify_runtime.py --site all --strict-assets --strict-pages
```

---

**Next Step**: Start with Phase 1 to fix the health check issue, then proceed through each phase sequentially.

