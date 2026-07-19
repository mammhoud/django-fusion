# Production Deployment Guide

**Date**: June 2, 2026  
**Version**: 1.0  
**Status**: Ready for Deployment  

---

## Overview

This guide provides step-by-step instructions for deploying the three-website workspace (CTC-Research, LMS-Demo, VResume) to production with all infrastructure properly configured.

## Pre-Deployment Checklist

### Phase 1: Infrastructure Verification

```bash
# 1. Verify all necessary files are in place
echo "[1.1] Checking critical deployment files..."
ls -l docker-compose.yml
ls -l compose/docker-compose.*.yml
ls -l compose/traefik/traefik.yml
ls -l compose/media/nginx.conf

# 2. Verify asset build system
echo "[1.2] Checking build system..."
ls -l assets/webpack/*.config.js
ls -l assets/package.json

# 3. Backup current environment
echo "[1.3] Backing up current environment..."
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# 4. Check available disk space
echo "[1.4] Checking disk space..."
df -h / | tail -2
```

### Phase 2: Prepare Docker Images

```bash
# 1. Stop existing containers gracefully
echo "[2.1] Stopping existing containers..."
docker compose -f docker-compose.yml down --remove-orphans 2>/dev/null || true

# 2. Clean up old volumes (optional - be careful!)
# docker volume prune -f

# 3. Verify Docker daemon is responsive
echo "[2.2] Verifying Docker..."
docker ps -q

# 4. Create docker network if not exists
echo "[2.3] Creating traefik network..."
docker network create traefik-net 2>/dev/null || true
```

### Phase 3: Build Production Images

```bash
# 1. Build all images without starting containers
echo "[3.1] Building production images..."
docker compose -f docker-compose.yml build --no-cache 2>&1 | tee logs/docker_build_$(date +%Y%m%d_%H%M%S).log

# Check for build errors
if [ $? -ne 0 ]; then
  echo "❌ Docker build failed. Check logs."
  exit 1
fi

echo "✅ All images built successfully"

# 2. Verify images created
echo "[3.2] Verifying images..."
docker images | grep -E "(ctc-research|lms|vresume|traefik|postgres|redis|shared-media)"
```

### Phase 4: Start Infrastructure Services

```bash
# 1. Start only infrastructure (no websites yet)
echo "[4.1] Starting infrastructure services..."
docker compose -f docker-compose.yml up -d traefik postgres redis shared-media

# 2. Wait for services to initialize
echo "[4.2] Waiting for infrastructure initialization (60s)..."
sleep 60

# 3. Verify infrastructure health
echo "[4.3] Verifying infrastructure health..."
docker compose -f docker-compose.yml ps

# Check individual service health
echo "  - Traefik:"
docker exec traefik traefik ping 2>/dev/null || echo "    ⚠ Traefik not responding yet"

echo "  - PostgreSQL:"
docker exec postgres pg_isready -U structa 2>/dev/null || echo "    ⚠ PostgreSQL not ready yet"

echo "  - Redis:"
docker exec redis redis-cli ping 2>/dev/null || echo "    ⚠ Redis not responding yet"

echo "  - Shared Media:"
curl -s http://localhost/health 2>/dev/null && echo "    ✅ Media server healthy" || echo "    ⚠ Media server not responding yet"
```

### Phase 5: Start Website Services

```bash
# 1. Start all website services
echo "[5.1] Starting website services..."
docker compose -f docker-compose.yml up -d web-ctc-research web-lms web-vresume

# 2. Wait for containers to initialize
echo "[5.2] Waiting for website initialization (120s)..."
for i in {1..24}; do
  echo -n "."
  sleep 5
done
echo ""

# 3. Verify all containers are running
echo "[5.3] Verifying container status..."
docker compose -f docker-compose.yml ps

# 4. Check website health endpoints
echo "[5.4] Checking website health..."
for port in 5070 5071 5072; do
  echo "  - Port $port:"
  curl -s -I http://localhost:$port/health/ 2>/dev/null | head -1 || echo "    ⚠ Not responding yet"
done
```

### Phase 6: Database Initialization

```bash
# 1. Create database users if needed
echo "[6.1] Initializing databases..."

# CTC Research
docker exec postgres psql -U structa -d db_ctc -c "SELECT 'db_ctc ready' as status;" 2>/dev/null || echo "Creating CTC database..."

# LMS Demo
docker exec postgres psql -U structa -d db_structa -c "SELECT 'db_structa ready' as status;" 2>/dev/null || echo "Creating LMS database..."

# VResume
docker exec postgres psql -U structa -d vresume -c "SELECT 'vresume ready' as status;" 2>/dev/null || echo "Creating VResume database..."

# 2. Run migrations for each site
echo "[6.2] Running migrations..."

docker exec web-ctc-research python manage.py migrate --noinput 2>&1 | tail -5
docker exec web-lms python manage.py migrate --noinput 2>&1 | tail -5
docker exec web-vresume python manage.py migrate --noinput 2>&1 | tail -5

# 3. Collect static files
echo "[6.3] Collecting static files..."
docker exec web-ctc-research python manage.py collectstatic --noinput 2>&1 | tail -3
docker exec web-lms python manage.py collectstatic --noinput 2>&1 | tail -3
docker exec web-vresume python manage.py collectstatic --noinput 2>&1 | tail -3
```

### Phase 7: Load Production Data

```bash
# 1. Check for fixture files
echo "[7.1] Checking for production fixtures..."
find . -name "*.json" -path "*/fixtures/*" | head -10

# 2. Load fixtures (if available)
echo "[7.2] Loading production data..."
docker exec web-ctc-research python manage.py loaddata fixtures/initial_data.json 2>/dev/null || echo "No initial_data.json found"
docker exec web-lms python manage.py loaddata fixtures/initial_data.json 2>/dev/null || echo "No initial_data.json found"

# 3. Create admin users
echo "[7.3] Creating admin users..."
echo "  - CTC Research: Run: docker exec web-ctc-research python manage.py createsuperuser"
echo "  - LMS Demo: Run: docker exec web-lms python manage.py createsuperuser"
echo "  - VResume: Run: docker exec web-vresume python manage.py createsuperuser"
```

### Phase 8: Certificate Management

```bash
# 1. Check current certificates
echo "[8.1] Checking certificates..."
docker exec traefik ls -la /acme/acme.json 2>/dev/null || echo "No ACME certificates yet"

# 2. Backup certificates
echo "[8.2] Backing up certificates..."
cd compose/traefik
./cert-backup.sh backup 2>&1 | tail -5

# 3. Verify backup
echo "[8.3] Verifying backup..."
./cert-backup.sh list 2>&1 | head -10
cd /root/site/websites
```

### Phase 9: Verification & Testing

```bash
# 1. Run comprehensive health checks
echo "[9.1] Running health checks..."
bash run_full_test_suite.sh 2>&1 | tee logs/full_deployment_check_$(date +%Y%m%d_%H%M%S).log

# 2. Check application logs for errors
echo "[9.2] Checking application logs..."
docker compose -f docker-compose.yml logs --tail 50 web-ctc-research | grep -i error || echo "No errors in CTC logs"
docker compose -f docker-compose.yml logs --tail 50 web-lms | grep -i error || echo "No errors in LMS logs"
docker compose -f docker-compose.yml logs --tail 50 web-vresume | grep -i error || echo "No errors in VResume logs"

# 3. Verify asset loading
echo "[9.3] Verifying assets..."
curl -s http://localhost:5070/ | grep -c "\.js\|\.css" && echo "✅ Assets loading in CTC Research" || echo "⚠ Asset loading issue"
curl -s http://localhost:5071/ | grep -c "\.js\|\.css" && echo "✅ Assets loading in LMS Demo" || echo "⚠ Asset loading issue"
curl -s http://localhost:5072/ | grep -c "\.js\|\.css" && echo "✅ Assets loading in VResume" || echo "⚠ Asset loading issue"
```

### Phase 10: Post-Deployment Configuration

```bash
# 1. Setup SSL/TLS if needed
echo "[10.1] SSL/TLS Status..."
docker exec traefik curl -s http://127.0.0.1:8080/ping

# 2. Configure backups
echo "[10.2] Configuring automated backups..."
# Add cron job:
# 0 2 * * * cd /root/site/websites/compose/traefik && ./cert-backup.sh backup >> /var/log/traefik-backup.log 2>&1

# 3. Enable monitoring
echo "[10.3] Monitoring Setup..."
echo "Check container logs: docker compose logs -f"
echo "Monitor resources: docker stats"

# 4. Final status report
echo "[10.4] Final Status Report"
docker compose -f docker-compose.yml ps
echo ""
echo "Website URLs:"
echo "  - CTC Research: http://localhost:5070/"
echo "  - LMS Demo: http://localhost:5071/"
echo "  - VResume: http://localhost:5072/"
echo ""
echo "Admin Panels:"
echo "  - CTC Research: http://localhost:5070/admin/"
echo "  - LMS Demo: http://localhost:5071/admin/"
echo "  - VResume: http://localhost:5072/admin/"
echo ""
echo "Media Server: http://localhost/media/"
```

---

## Automated Deployment Script

Create `/root/site/websites/deploy-production.sh`:

```bash
#!/bin/bash

set -e

DEPLOYMENT_DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="logs/production_deployment_${DEPLOYMENT_DATE}.log"

echo "🚀 Starting Production Deployment: $DEPLOYMENT_DATE" | tee -a $LOG_FILE
echo "================================" | tee -a $LOG_FILE

# Phase 1: Preparation
echo "📋 Phase 1: Preparation..." | tee -a $LOG_FILE
mkdir -p logs

# Phase 2: Docker Cleanup
echo "🧹 Phase 2: Docker Cleanup..." | tee -a $LOG_FILE
docker compose -f docker-compose.yml down --remove-orphans 2>/dev/null || true
docker network create traefik-net 2>/dev/null || true

# Phase 3: Build Images
echo "🔨 Phase 3: Building Docker Images..." | tee -a $LOG_FILE
docker compose -f docker-compose.yml build --no-cache >> $LOG_FILE 2>&1

# Phase 4: Start Infrastructure
echo "🌐 Phase 4: Starting Infrastructure..." | tee -a $LOG_FILE
docker compose -f docker-compose.yml up -d traefik postgres redis shared-media
sleep 60

# Phase 5: Start Websites
echo "🌍 Phase 5: Starting Websites..." | tee -a $LOG_FILE
docker compose -f docker-compose.yml up -d web-ctc-research web-lms web-vresume
sleep 120

# Phase 6: Run Migrations
echo "🗄️  Phase 6: Running Migrations..." | tee -a $LOG_FILE
docker exec web-ctc-research python manage.py migrate --noinput >> $LOG_FILE 2>&1
docker exec web-lms python manage.py migrate --noinput >> $LOG_FILE 2>&1
docker exec web-vresume python manage.py migrate --noinput >> $LOG_FILE 2>&1

# Phase 7: Collect Static Files
echo "📦 Phase 7: Collecting Static Files..." | tee -a $LOG_FILE
docker exec web-ctc-research python manage.py collectstatic --noinput >> $LOG_FILE 2>&1
docker exec web-lms python manage.py collectstatic --noinput >> $LOG_FILE 2>&1
docker exec web-vresume python manage.py collectstatic --noinput >> $LOG_FILE 2>&1

# Phase 8: Backup Certificates
echo "🔐 Phase 8: Backing Up Certificates..." | tee -a $LOG_FILE
cd compose/traefik && ./cert-backup.sh backup >> $LOG_FILE 2>&1 && cd ../..

# Phase 9: Health Check
echo "✅ Phase 9: Running Health Checks..." | tee -a $LOG_FILE
docker compose -f docker-compose.yml ps >> $LOG_FILE

# Phase 10: Summary
echo "================================" | tee -a $LOG_FILE
echo "✅ Deployment Complete!" | tee -a $LOG_FILE
echo "================================" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "Websites:" | tee -a $LOG_FILE
echo "  - CTC Research: http://localhost:5070/" | tee -a $LOG_FILE
echo "  - LMS Demo: http://localhost:5071/" | tee -a $LOG_FILE
echo "  - VResume: http://localhost:5072/" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "Next Steps:" | tee -a $LOG_FILE
echo "  1. Create admin users (see Phase 7 in guide)" | tee -a $LOG_FILE
echo "  2. Load production data if fixtures available" | tee -a $LOG_FILE
echo "  3. Test all websites in browser" | tee -a $LOG_FILE
echo "  4. Monitor logs: docker compose logs -f" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "Log file: $LOG_FILE" | tee -a $LOG_FILE
```

Make it executable:
```bash
chmod +x /root/site/websites/deploy-production.sh
```

---

## Quick Start Deployment

### One-Command Deployment (Recommended)

```bash
cd /root/site/websites

# Run automated deployment
./deploy-production.sh

# Watch logs as deployment progresses
docker compose logs -f
```

### Manual Step-by-Step Deployment

```bash
cd /root/site/websites

# Step 1: Stop existing containers
docker compose down --remove-orphans

# Step 2: Build new images
docker compose build --no-cache

# Step 3: Start all services
docker compose up -d

# Step 4: Wait for initialization
sleep 120

# Step 5: Run migrations
docker compose exec web-ctc-research python manage.py migrate --noinput
docker compose exec web-lms python manage.py migrate --noinput
docker compose exec web-vresume python manage.py migrate --noinput

# Step 6: Collect static files
docker compose exec web-ctc-research python manage.py collectstatic --noinput
docker compose exec web-lms python manage.py collectstatic --noinput
docker compose exec web-vresume python manage.py collectstatic --noinput

# Step 7: Create admin users
docker exec -it web-ctc-research python manage.py createsuperuser
docker exec -it web-lms python manage.py createsuperuser
docker exec -it web-vresume python manage.py createsuperuser

# Step 8: Test websites
echo "Testing CTC Research..."
curl http://localhost:5070/

echo "Testing LMS Demo..."
curl http://localhost:5071/

echo "Testing VResume..."
curl http://localhost:5072/
```

---

## Production Verification Checklist

### Container Health

```bash
# Check all containers are running and healthy
docker compose ps

# Expected output:
# NAME                      STATUS
# traefik                   Up (healthy)
# postgres                  Up (healthy)
# redis                     Up (healthy)
# shared-media              Up (healthy)
# web-ctc-research          Up (healthy)
# web-lms              Up (healthy)
# web-vresume               Up (healthy)
```

### Website Accessibility

```bash
# Test each website is responding
curl -I http://localhost:5070/
curl -I http://localhost:5071/
curl -I http://localhost:5072/

# Expected: HTTP 200 OK
```

### Asset Loading

```bash
# Verify assets are being served
curl -s http://localhost:5070/ | grep -o "href=\|src=" | wc -l

# Should show multiple CSS and JS includes
```

### Database Connectivity

```bash
# Test database connections
docker exec web-ctc-research python manage.py dbshell -c "SELECT 1;"
docker exec web-lms python manage.py dbshell -c "SELECT 1;"
docker exec web-vresume python manage.py dbshell -c "SELECT 1;"

# Expected: All should return 1
```

### Admin Panels

```bash
# Test admin panels are accessible
curl -I http://localhost:5070/admin/
curl -I http://localhost:5071/admin/
curl -I http://localhost:5072/admin/

# Expected: HTTP 302 (redirect to login) or HTTP 200
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs web-ctc-research | tail -50

# Common issues:
# - Port already in use: Change ports in docker-compose.yml
# - Health check failing: Give containers more time (120s+)
# - Database not ready: Wait for postgres container to be healthy
```

### Database Connection Error

```bash
# Verify PostgreSQL is running
docker exec postgres psql -U structa -l

# Check database exists
docker exec postgres psql -U structa -c "SELECT datname FROM pg_database WHERE datname LIKE 'db_%';"

# If databases don't exist, create them:
docker exec postgres psql -U structa -c "CREATE DATABASE db_ctc;"
docker exec postgres psql -U structa -c "CREATE DATABASE db_structa;"
docker exec postgres psql -U structa -c "CREATE DATABASE vresume;"
```

### Assets Not Loading

```bash
# Rebuild and collect assets
docker compose exec web-ctc-research python manage.py collectstatic --noinput

# Verify assets directory
docker exec web-ctc-research ls -la /app/ctc-research/assets/staticfiles/ | head -20

# Check webpack output
ls -lh /root/site/websites/assets/bundles/
```

### Traefik Not Working

```bash
# Check traefik configuration
docker exec traefik cat /traefik/traefik.yml

# Verify containers are labeled correctly
docker inspect web-ctc-research | grep -A 10 "Labels"

# Check traefik logs
docker logs traefik | tail -50
```

---

## Rollback Procedure

If deployment fails and needs to be rolled back:

```bash
# 1. Stop all containers
docker compose down

# 2. Restore previous environment
cp .env.backup.YYYYMMDD_HHMMSS .env

# 3. Restore from certificate backup
cd compose/traefik
./cert-backup.sh restore /path/to/backup
cd /root/site/websites

# 4. Start previous version
docker compose up -d

# 5. Monitor
docker compose logs -f
```

---

## Success Criteria

Deployment is successful when:

✅ All 7 Docker containers are running and healthy  
✅ All three websites respond to HTTP requests  
✅ Assets (CSS, JS, images) are loading correctly  
✅ Database connections are working  
✅ Admin panels are accessible  
✅ Logs show no critical errors  
✅ Media server is serving files  
✅ Certificates are valid and backed up  

---

## Support & Documentation

- Full deployment guide: `DEPLOYMENT_TEST_PLAN.md`
- Certificate management: `compose/traefik/CERT_BACKUP_README.md`
- Test suite: `run_full_test_suite.sh`
- Build system: `assets/package.json`

---

**Status**: 🟢 READY FOR PRODUCTION DEPLOYMENT  
**Last Updated**: June 2, 2026  
**Next Steps**: Run `./deploy-production.sh`
