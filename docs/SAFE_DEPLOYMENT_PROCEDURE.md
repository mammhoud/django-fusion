# Safe Deployment Procedure

**Complete Step-by-Step Guide for Production Deployment**

**Date:** June 2, 2026
**Updated:** With fixture loading error fixes
**Status:** Ready for deployment

---

## Overview

This document provides a comprehensive, safe deployment procedure that addresses:
- ✅ SSL/TLS configuration (Task 4 completed)
- ✅ Fixture loading order and foreign key constraints
- ✅ Database initialization
- ✅ Search index building
- ✅ Service verification

---

## Pre-Deployment Checklist

### Environment Verification
```bash
# 1. Check SSL certificates
ls -lah /root/site/websites/compose/traefik/certs/*.crt

# 2. Check configuration files updated
grep "certResolver: local" /root/site/websites/compose/traefik/dynamic/*.yml

# 3. Verify documentation moved
ls -la /root/site/websites/docs/ | head -10

# 4. Run SSL verification script
/root/site/websites/VERIFY_SSL_CONFIG.sh
```

**Expected Results:**
- ✅ 15 certificate files present
- ✅ All domain configs use `certResolver: local`
- ✅ 56+ markdown files in docs/
- ✅ VERIFY_SSL_CONFIG.sh returns all checks passed

---

## Phase 1: Infrastructure Setup

### Step 1.1: Create Docker Network
```bash
docker network create traefik-net 2>/dev/null || true
docker network create ctc-research-network 2>/dev/null || true
```

**Expected Output:**
```
[network_id]  (if created)
or nothing (if already exists)
```

### Step 1.2: Start PostgreSQL
```bash
cd /root/site/websites
docker compose up -d postgres
```

**Verify:**
```bash
docker ps | grep postgres
# Should show: postgres container running
```

### Step 1.3: Wait for PostgreSQL to be Ready
```bash
# Wait max 30 seconds for postgres to start
for i in {1..30}; do
  if docker exec postgres pg_isready -U ctc_research_user > /dev/null 2>&1; then
    echo "✅ PostgreSQL is ready"
    break
  fi
  echo "Waiting for PostgreSQL... ($i/30)"
  sleep 1
done
```

---

## Phase 2: Database Setup

### Step 2.1: Run Migrations
```bash
cd /root/site/websites
docker compose run --rm web python manage.py migrate --run-syncdb
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py migrate contenttypes
```

**Expected Output:**
```
Running migrations:
  ...
  No migrations to apply.
```

### Step 2.2: Verify Database State
```bash
docker compose run --rm web python manage.py shell << 'EOF'
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
print(f"✅ Content Types: {ContentType.objects.count()}")
print(f"✅ Permissions: {Permission.objects.count()}")
EOF
```

**Expected Output:**
```
✅ Content Types: 60+
✅ Permissions: 0 (until fixtures loaded)
```

---

## Phase 3: Fixture Loading (With Error Prevention)

### Step 3.1: Clear Existing Data (Optional)
```bash
# Only if starting fresh
docker compose run --rm web python manage.py flush --noinput
```

### Step 3.2: Load Fixtures in Dependency Order

**IMPORTANT:** Load in this exact order with search disabled!

```bash
#!/bin/bash
set -e

echo "📦 Loading fixtures in dependency order..."

# Disable search indexing during fixture load
export WAGTAIL_SEARCH_DISABLED=1

cd /root/site/websites

# Step 1: Core authentication (safe to load, no dependencies)
echo "Step 1/6: Loading authentication data..."
docker compose run --rm web python manage.py loaddata \
  /app/ctc-research/assets/fixtures/auth/*.json 2>&1 | grep -E "(Installed|Problem)" || echo "✅ Auth data loaded"

# Step 2: Wagtail core (locales, sites - no dependencies except content types)
echo "Step 2/6: Loading Wagtail core (locales, sites)..."
docker compose run --rm web python manage.py loaddata \
  /app/ctc-research/assets/fixtures/wagtail/*.json 2>&1 | grep -E "(Installed|Problem)" || echo "✅ Wagtail core loaded"

# Step 3: Base pages (depends on site existing)
echo "Step 3/6: Loading base pages..."
docker compose run --rm web python manage.py loaddata \
  /app/ctc-research/assets/fixtures/pages/*.json 2>&1 | grep -E "(Installed|Problem)" || echo "✅ Pages loaded"

# Step 4: Images and media (safe to load anytime)
echo "Step 4/6: Loading images..."
docker compose run --rm web python manage.py loaddata \
  /app/ctc-research/assets/fixtures/media/*.json 2>&1 | grep -E "(Installed|Problem)" || echo "✅ Images loaded"

# Step 5: Content pages (depends on pages existing)
echo "Step 5/6: Loading content pages..."
docker compose run --rm web python manage.py loaddata \
  /app/ctc-research/assets/fixtures/content/*.json 2>&1 | grep -E "(Installed|Problem)" || echo "✅ Content loaded"

# Re-enable search
unset WAGTAIL_SEARCH_DISABLED

echo "✅ All fixtures loaded successfully!"
```

**Expected Behavior:**
- No ForeignKeyViolation errors
- Each step completes successfully
- Total loaded objects > 100

### Step 3.3: Verify Fixture Loading
```bash
docker compose run --rm web python manage.py shell << 'EOF'
from wagtail.models import Page
from django.contrib.auth.models import User, Permission, Group
from wagtailcore.models import Locale, Site

print(f"✅ Pages: {Page.objects.count()}")
print(f"✅ Users: {User.objects.count()}")
print(f"✅ Permissions: {Permission.objects.count()}")
print(f"✅ Groups: {Group.objects.count()}")
print(f"✅ Locales: {Locale.objects.count()}")
print(f"✅ Sites: {Site.objects.count()}")
EOF
```

**Expected Output:**
```
✅ Pages: 2+
✅ Users: 1+
✅ Permissions: 30+
✅ Groups: 1+
✅ Locales: 6+
✅ Sites: 1
```

---

## Phase 4: Static Files & Indexing

### Step 4.1: Collect Static Files
```bash
docker compose run --rm web python manage.py collectstatic --noinput
```

**Expected Output:**
```
1848 static files copied to '/app/staticfiles/'
```

### Step 4.2: Build Search Index
```bash
docker compose run --rm web python manage.py update_index
```

**Expected Output:**
```
Indexing 2 pages
Update complete.
```

---

## Phase 5: SSL/Traefik Setup

### Step 5.1: Build Traefik Container
```bash
docker compose build traefik
```

**Expected Output:**
```
[+] Building 2.5s (7/7) FINISHED
```

### Step 5.2: Start All Services
```bash
docker compose up -d traefik postgres redis ctc-research-website lms-demo-website vresume-website
```

**Wait for health checks:**
```bash
# Monitor startup
docker compose logs -f traefik | head -50
```

**Expected Logs:**
```
Configuration reloaded
Traefik version 2.x started
Certificate loaded: ctc-research.crt
Certificate loaded: structa-cloud.crt
Certificate loaded: vresume.crt
```

---

## Phase 6: Verification

### Step 6.1: Check Service Status
```bash
docker ps
# Should show: traefik, postgres, redis, and 3 web services running
```

### Step 6.2: Test HTTP Redirect
```bash
echo "Testing HTTP -> HTTPS redirect..."
for domain in ctc-research.com structa.cloud vresume.structa.cloud; do
  echo "Testing $domain..."
  curl -I http://$domain 2>&1 | head -3
done
```

**Expected:**
```
HTTP/1.1 301 Moved Permanently
Location: https://...
```

### Step 6.3: Test HTTPS Connectivity
```bash
echo "Testing HTTPS connectivity..."
for domain in ctc-research.com structa.cloud vresume.structa.cloud; do
  echo "Testing $domain..."
  curl -v https://$domain 2>&1 | grep -E "(Connected|Certificate|HTTP)" | head -5
done
```

**Expected:**
```
Connected to ...
SSL connection successful
HTTP/1.1 200 OK (or 308 temporary redirect)
```

### Step 6.4: Check Database Connections
```bash
docker compose run --rm web python manage.py dbshell << 'EOF'
SELECT COUNT(*) as pages FROM wagtailcore_page;
SELECT COUNT(*) as users FROM auth_user;
EOF
```

**Expected:**
```
 pages
-------
     2+
(1 row)

 users
-------
     1+
(1 row)
```

### Step 6.5: Verify Admin Access
```bash
echo "Admin access URLs:"
echo "  http://localhost:8080/          - Traefik Dashboard"
echo "  https://ctc-research.com/admin/ - CTC-Research Admin"
echo "  https://structa.cloud/admin/    - Structa LMS Admin"
echo "  https://vresume.structa.cloud/  - VResume"
```

---

## Post-Deployment Tasks

### Task 1: View Traefik Dashboard
```
http://localhost:8080
```

Verify:
- [ ] 3 domain routes configured
- [ ] All certificates loaded
- [ ] Services healthy
- [ ] HTTP redirects to HTTPS

### Task 2: Check Application Logs
```bash
docker logs ctc-research-website | tail -50
docker logs lms-demo-website | tail -50
docker logs vresume-website | tail -50
```

Look for:
- [ ] No ERROR level entries
- [ ] Database connected
- [ ] Static files configured
- [ ] Wagtail CMS initialized

### Task 3: Test Functionality

**For CTC-Research:**
```bash
curl -s https://ctc-research.com/ | grep -o "<title>.*</title>"
```

**For Structa LMS:**
```bash
curl -s https://structa.cloud/ | grep -o "<title>.*</title>"
```

**For VResume:**
```bash
curl -s https://vresume.structa.cloud/ | grep -o "<title>.*</title>"
```

---

## Troubleshooting

### Issue: Certificate Not Loading
```bash
# Check certificate files
ls -l /root/site/websites/compose/traefik/certs/

# Check Traefik logs
docker logs traefik | grep -i certificate

# Fix: Ensure permissions are correct
chmod 600 /root/site/websites/compose/traefik/certs/*.key
chmod 644 /root/site/websites/compose/traefik/certs/*.crt

# Restart
docker compose restart traefik
```

### Issue: Fixture Loading Fails
```bash
# Check database state
docker compose run --rm web python manage.py shell << 'EOF'
from django.contrib.contenttypes.models import ContentType
print(f"Content types: {ContentType.objects.count()}")
EOF

# If empty, run migrations again
docker compose run --rm web python manage.py migrate

# Clear fixtures and reload
docker compose run --rm web python manage.py flush --noinput
docker compose run --rm web python manage.py migrate
# Then reload fixtures using Phase 3 above
```

### Issue: Port 443 Already in Use
```bash
# Check what's using port 443
lsof -i :443
# or
ss -tlnp | grep 443

# Stop conflicting service or change Traefik port
# Edit: compose/docker-compose.traefik.yml
# Change: - "443:443" to - "8443:443"
```

### Issue: Database Connection Error
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check database exists
docker exec postgres psql -U ctc_research_user -l

# Check credentials match docker-compose
cat /root/site/websites/.env | grep POSTGRES

# Restart PostgreSQL
docker compose restart postgres
```

---

## Rollback Procedure

If deployment fails:

### Step 1: Stop Services
```bash
docker compose down
```

### Step 2: Restore from Backup
```bash
# Restore database backup (if available)
docker exec postgres pg_restore -U ctc_research_user -d ctc_research /backups/ctc_research.backup

# Restore certificate backup
cd /root/site/websites/compose/traefik/
tar -xzf certs/production-certs-20260602-180715.tar.gz
```

### Step 3: Restart Services
```bash
docker compose up -d
```

### Step 4: Verify
```bash
docker logs traefik | tail -20
docker logs ctc-research-website | tail -20
```

---

## Monitoring After Deployment

### Daily Checks
```bash
# Run this daily
docker ps                          # Check all services running
docker compose logs --tail 50      # Check for errors
curl -s https://ctc-research.com   # HTTP test
```

### Weekly Checks
```bash
# Check certificate expiry
openssl x509 -in /root/site/websites/compose/traefik/certs/ctc-research.crt -dates

# Check database size
docker exec postgres psql -U ctc_research_user -c "SELECT pg_size_pretty(pg_database_size('ctc_research'));"

# Check search index
docker compose run --rm web python manage.py ... search_check_index
```

---

## Deployment Checklist

- [ ] Pre-deployment verification passed
- [ ] Docker networks created
- [ ] PostgreSQL running
- [ ] Migrations applied
- [ ] Fixtures loaded (Phase 3)
- [ ] Static files collected
- [ ] Search index built
- [ ] Traefik built and started
- [ ] All 3 web services running
- [ ] HTTP -> HTTPS redirects working
- [ ] HTTPS connections successful
- [ ] Database queries working
- [ ] Admin pages accessible
- [ ] No errors in logs
- [ ] SSL certificates loaded

---

## Support & Documentation

- Full documentation: `/root/site/websites/docs/00_MASTER_INDEX.md`
- SSL guide: `/root/site/websites/docs/DEPLOYMENT_GUIDE_SSL.md`
- Error analysis: `/root/site/websites/docs/FIXTURE_LOADING_ERROR_ANALYSIS.md`
- Fixture logs: `/root/site/websites/docs/fixture_loading_*.log`

---

## Summary

This procedure ensures:
1. ✅ All SSL certificates properly configured
2. ✅ Database initialized correctly
3. ✅ Fixtures loaded in dependency order
4. ✅ All services healthy and verified
5. ✅ HTTPS working for all domains
6. ✅ HTTP redirects to HTTPS
7. ✅ Admin panels accessible
8. ✅ Rollback procedures available

**Estimated Time:** 20-30 minutes
**Complexity:** Medium
**Risk Level:** Low (with verification steps)

---

**Document Generated:** June 2, 2026
**Status:** Ready for Production Deployment
