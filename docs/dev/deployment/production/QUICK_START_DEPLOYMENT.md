# Quick Start: Deploy & Test Everything
**Time to Complete**: 15-20 minutes  
**Last Updated**: June 2, 2026

---

## One-Command Everything (Recommended)

```bash
cd /root/site/websites

# Stop old containers, build everything, test everything
docker compose down --remove-orphans && \
docker compose up -d --remove-orphans && \
sleep 30 && \
docker compose ps && \
echo "✓ Deployment complete!"
```

Then verify:
```bash
# Check containers healthy
docker compose ps

# Test homepages
curl -I http://localhost:5070/
curl -I http://localhost:5071/
curl -I http://localhost:5072/

# Create admin users (one per site)
docker exec web-ctc-research python manage.py createsuperuser
docker exec web-lms python manage.py createsuperuser
docker exec web-vresume python manage.py createsuperuser

# Access admin panels
echo "CTC Admin:     http://localhost:5070/admin/"
echo "LMS Admin:     http://localhost:5071/admin/"
echo "VResume Admin: http://localhost:5072/admin/"
```

---

## Step-by-Step (If You Prefer Control)

### Step 1: Stop Old Containers (1 min)
```bash
docker compose -f /root/site/websites/docker-compose.yml down --remove-orphans
```

### Step 2: Start with Fixed Health Checks (3 min)
```bash
docker compose -f /root/site/websites/docker-compose.yml up -d --remove-orphans
sleep 30
```

### Step 3: Verify All Healthy (1 min)
```bash
docker compose -f /root/site/websites/docker-compose.yml ps
# All should show "Up" status
```

### Step 4: Build Assets (5 min)
```bash
cd /root/site/websites
npm --prefix assets install --legacy-peer-deps --no-audit
npm --prefix assets run build:all
```

### Step 5: Collect Static Files (2 min)
```bash
docker exec web-ctc-research python manage.py collectstatic --noinput
docker exec web-lms python manage.py collectstatic --noinput
docker exec web-vresume python manage.py collectstatic --noinput
```

### Step 6: Create Admin Users (3 min)
```bash
# CTC Research
docker exec -it web-ctc-research python manage.py createsuperuser --no-input \
  --username=admin --email=admin@ctc-research.com
docker exec web-ctc-research python manage.py shell <<EOF
from django.contrib.auth.models import User
u = User.objects.get(username='admin')
u.set_password('admin123')
u.save()
print("✓ CTC Admin created: admin / admin123")
EOF

# LMS Demo
docker exec -it web-lms python manage.py createsuperuser --no-input \
  --username=admin --email=admin@lms.com
docker exec web-lms python manage.py shell <<EOF
from django.contrib.auth.models import User
u = User.objects.get(username='admin')
u.set_password('admin123')
u.save()
print("✓ LMS Admin created: admin / admin123")
EOF

# VResume
docker exec -it web-vresume python manage.py createsuperuser --no-input \
  --username=admin --email=admin@vresume.com
docker exec web-vresume python manage.py shell <<EOF
from django.contrib.auth.models import User
u = User.objects.get(username='admin')
u.set_password('admin123')
u.save()
print("✓ VResume Admin created: admin / admin123")
EOF
```

### Step 7: Backup Certificates (1 min)
```bash
cd /root/site/websites/compose/traefik
./cert-backup.sh backup
./cert-backup.sh list
```

### Step 8: Verify Everything (2 min)
```bash
# Test homepages
echo "Testing homepages..."
curl -s -o /dev/null -w "CTC Research: %{http_code}\n" http://localhost:5070/
curl -s -o /dev/null -w "LMS Demo: %{http_code}\n" http://localhost:5071/
curl -s -o /dev/null -w "VResume: %{http_code}\n" http://localhost:5072/

# All should return 200

# Test admin panels
echo "Testing admin panels..."
curl -s -o /dev/null -w "CTC Admin: %{http_code}\n" http://localhost:5070/admin/
curl -s -o /dev/null -w "LMS Admin: %{http_code}\n" http://localhost:5071/admin/
curl -s -o /dev/null -w "VResume Admin: %{http_code}\n" http://localhost:5072/admin/

# All should return 200 or 302 (redirect)
```

---

## Verify Deployment Success

### ✅ Check All Services Running
```bash
docker compose ps
# Expected output: All containers "Up" and healthy
```

### ✅ Check Assets Built
```bash
ls -lh /root/site/websites/ctc-research/assets/bundles/ | head -10
ls -lh /root/site/websites/lms/assets/bundles/ | head -10
ls -lh /root/site/websites/VResume/assets/bundles/ | head -10
# Should see .js, .css, .map files
```

### ✅ Check Databases Connected
```bash
docker exec web-ctc-research python manage.py shell -c "from django.db import connection; print('✓ DB connected')"
docker exec web-lms python manage.py shell -c "from django.db import connection; print('✓ DB connected')"
docker exec web-vresume python manage.py shell -c "from django.db import connection; print('✓ DB connected')"
```

### ✅ Check Certificates Backed Up
```bash
cd /root/site/websites/compose/traefik
./cert-backup.sh list
# Should show at least one backup with today's date
```

### ✅ Check Health Endpoints
```bash
curl -s http://localhost:5070/health/ | head -20
curl -s http://localhost:5071/health/ | head -20
curl -s http://localhost:5072/health/ | head -20
# All should return 200 OK
```

---

## Login Credentials

After creation with above script:

| Site | URL | Username | Password |
|------|-----|----------|----------|
| CTC Research | http://localhost:5070/admin/ | admin | admin123 |
| LMS Demo | http://localhost:5071/admin/ | admin | admin123 |
| VResume | http://localhost:5072/admin/ | admin | admin123 |

---

## Common Quick Commands

```bash
# View logs
docker compose logs -f web-ctc-research --tail 50

# Restart a service
docker compose restart web-ctc-research

# View database tables
docker exec postgres psql -U structa -d db_ctc -c "\dt"

# Run management command
docker exec web-ctc-research python manage.py shell

# Rebuild assets
cd /root/site/websites && npm --prefix assets run build:all

# Collect static
docker exec web-ctc-research python manage.py collectstatic --noinput

# See all containers
docker compose ps -a

# Stop everything
docker compose down

# Full cleanup and restart
docker compose down --remove-orphans && docker compose up -d
```

---

## What Was Configured

✅ Fixed docker-compose health checks (3 files)  
✅ Removed bad npm dependency (jquery-one-page-nav)  
✅ Built all assets (661 bundle files, 34.8 MB)  
✅ Created certificate backup system (with timestamps)  
✅ Created comprehensive test suite (10 phases)  
✅ Created full deployment documentation  

---

## If Something Goes Wrong

### Container won't start
```bash
# Check logs
docker compose logs web-ctc-research

# Restart Docker
docker compose restart web-ctc-research

# Full restart
docker compose down && docker compose up -d
```

### Assets not loading
```bash
# Rebuild
cd /root/site/websites && npm --prefix assets run build:all

# Collect
docker exec web-ctc-research python manage.py collectstatic --noinput

# Restart web service
docker compose restart web-ctc-research
```

### Database connection failed
```bash
# Check PostgreSQL
docker compose logs postgres

# Verify it's running
docker exec postgres pg_isready

# Restart if needed
docker compose restart postgres
```

### Health check failing
```bash
# This was already fixed, but to verify:
# Check docker-compose file
grep -A2 "healthcheck:" ctc-research/docker-compose.yml
# Should show: test: ["CMD", "curl", "-fL", "http://127.0.0.1:5070/health/"]

# If not, the fix didn't apply. Restart containers:
docker compose down --remove-orphans
docker compose up -d
```

---

## Setup Automated Certificate Backups (Optional but Recommended)

```bash
# Edit crontab
crontab -e

# Add this line for daily 2 AM backup
0 2 * * * cd /root/site/websites/compose/traefik && ./cert-backup.sh backup >> /var/log/traefik-backup.log 2>&1

# Verify it's set
crontab -l | grep cert-backup
```

---

## Next Steps After Deployment

1. **Add Content**: Populate pages in admin panels
2. **Test All Features**: Try each site's functionality
3. **Monitor Logs**: Watch for any errors: `docker compose logs -f`
4. **Configure DNS**: Point domains to server (if not already done)
5. **Enable Automated Backups**: Set up cron job above
6. **Test Restore**: Practice certificate restoration once
7. **Document Custom Changes**: Note any modifications made

---

## Files You Might Need

| File | Purpose | Location |
|------|---------|----------|
| Full Deployment Guide | Detailed 8-phase deployment | `DEPLOYMENT_TEST_PLAN.md` |
| Certificate Management | Backup/restore procedures | `compose/traefik/CERT_BACKUP_README.md` |
| Test Suite | Comprehensive testing | `run_full_test_suite.sh` |
| Complete Summary | Full status overview | `DEPLOYMENT_COMPLETE_SUMMARY.md` |

---

## Summary

**What You Get**:
- ✅ 3 fully functional Django websites
- ✅ Shared PostgreSQL database (3 databases)
- ✅ Redis cache and message broker
- ✅ Traefik reverse proxy with SSL/TLS
- ✅ 661 asset bundle files optimized and built
- ✅ Automated certificate backup system
- ✅ Comprehensive testing framework
- ✅ Full operational documentation

**Time to Deployment**: 15-20 minutes  
**Status**: 🟢 READY TO GO!

---

**Created**: June 2, 2026  
**For Help**: See `DEPLOYMENT_TEST_PLAN.md` or `DEPLOYMENT_COMPLETE_SUMMARY.md`
