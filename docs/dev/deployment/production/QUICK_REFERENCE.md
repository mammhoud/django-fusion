# Quick Reference Guide - CTC-Research Deployment

**Status:** ✅ OPERATIONAL | **Date:** 2026-06-02 | **Container:** web-ctc-research

---

## ⚡ Essential Commands

### Check Website Status
```bash
# Is container running?
docker ps | grep ctc-research

# Is website responding?
curl -I http://localhost:5070/
curl -I http://localhost:5070/health/

# View live logs
docker logs web-ctc-research -f
```

### View Log Files
```bash
# Container logs
docker exec web-ctc-research tail -50 /app/logs/gunicorn-error.log
docker exec web-ctc-research tail -50 /app/logs/error.log
docker exec web-ctc-research tail -50 /app/logs/gunicorn-access.log

# Application log
docker exec web-ctc-research tail -100 /app/logs/application.log
```

### Restart Services
```bash
# Restart container
docker compose down
docker compose up -d

# Rebuild container (if changes made)
docker compose build --no-cache django
docker compose up -d
```

---

## 📊 Current Status Overview

| Item | Status | Command |
|------|--------|---------|
| Container | ✅ Running | `docker ps web-ctc-research` |
| Web Server | ✅ Healthy | `docker logs web-ctc-research \| tail -5` |
| HTTP 200 | ✅ 99%+ | `curl http://localhost:5070/` |
| Database | ✅ Connected | `docker exec web-ctc-research tail /app/logs/migrate-ctc-research.log` |
| Static Files | ✅ Ready | `3001 files collected` |
| Health Check | ✅ Passing | `curl http://localhost:5070/health/` |

---

## 🐛 Troubleshooting

### Problem: Website Not Responding
```bash
# 1. Check if container is running
docker ps

# 2. View recent errors
docker logs web-ctc-research --tail 50

# 3. Restart container
docker compose down
docker compose up -d

# 4. Wait 15 seconds and test
sleep 15
curl http://localhost:5070/
```

### Problem: 500 Errors in Logs
```bash
# Check error log
docker exec web-ctc-research tail -50 /app/logs/error.log

# Check application log
docker exec web-ctc-research tail -50 /app/logs/application.log

# Check gunicorn errors
docker exec web-ctc-research tail -50 /app/logs/gunicorn-error.log
```

### Problem: Database Connectivity Issues
```bash
# Check if postgres container is running
docker ps | grep postgres

# Check database logs
docker logs postgres | tail -20

# Verify connection string
docker exec web-ctc-research env | grep DATABASE
```

### Problem: Static Files Not Loading
```bash
# Check static file collection
docker exec web-ctc-research tail /app/logs/collectstatic-ctc-research.log

# Verify static files exist
docker exec web-ctc-research ls -la /app/assets/staticfiles/ | head

# Rebuild static files if needed
docker exec web-ctc-research python manage.py --site=ctc-research collectstatic --noinput
```

---

## 🔧 Maintenance Tasks

### Clear Background Task Errors (Optional)
```bash
# Run the background error fix script
bash /root/site/websites/fix_modelsearch_errors.sh
```

### Rebuild Python Cache (if needed)
```bash
# Clear cache and rebuild
find /root/site/websites -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
docker compose down
docker compose build --no-cache django
docker compose up -d
```

### Check Container Health
```bash
# Detailed health status
docker inspect web-ctc-research | grep -A 5 Health

# All containers
docker compose ps
```

### View Database Status
```bash
# Connect to database
docker exec -it postgres psql -U postgres -d ctc_research

# Common queries:
# \dt                    - List all tables
# SELECT COUNT(*) FROM wagtail_page;  - Count pages
# \q                     - Quit
```

---

## 📋 Important File Locations

### In Container
```
/app/logs/                 - All application logs
/app/ctc-research/        - Website code
/app/configs/             - Shared configuration
/app/assets/              - Front-end assets
/app/assets/staticfiles/  - Collected static files
```

### Local Host
```
/root/site/websites/ctc-research/logs/
/root/site/websites/configs/
/root/site/websites/docker-compose.yml
/root/site/websites/compose/django/
```

---

## ✅ Health Indicators

### Website is Healthy if:
- ✅ `docker ps` shows container `Up`
- ✅ `curl http://localhost:5070/` returns HTTP 200
- ✅ Health endpoint returns 200 (`curl http://localhost:5070/health/`)
- ✅ No 500 errors in gunicorn-access.log
- ✅ No CRITICAL errors in gunicorn-error.log

### Website Needs Attention if:
- ⚠️ Container is `Exited`
- ⚠️ `curl` returns connection refused
- ⚠️ Health endpoint returns 5xx error
- ⚠️ HTTP 500 errors in access log
- ⚠️ ModuleNotFoundError or ImportError in gunicorn-error.log

---

## 🚨 Emergency Recovery

### Container Won't Start
```bash
# 1. Clear cache
find /root/site/websites -type d -name "__pycache__" -exec rm -rf {} +

# 2. Rebuild everything
docker compose down
docker compose build --no-cache django
docker compose up -d

# 3. Wait and check
sleep 30
docker logs web-ctc-research | tail -50
```

### Website Returns 500 Error
```bash
# 1. Check error log
docker exec web-ctc-research tail -100 /app/logs/error.log | head -50

# 2. Check gunicorn errors
docker exec web-ctc-research tail -50 /app/logs/gunicorn-error.log

# 3. Restart container
docker compose restart web-ctc-research

# 4. Verify recovery
sleep 10
curl http://localhost:5070/
```

### Database Connection Failed
```bash
# 1. Check postgres container
docker ps | grep postgres

# 2. Check postgres logs
docker logs postgres | tail -20

# 3. Restart postgres
docker compose restart postgres

# 4. Wait for postgres to be ready
sleep 5

# 5. Restart web container
docker compose restart web-ctc-research

# 6. Verify connection
sleep 10
curl http://localhost:5070/
```

---

## 📈 Performance Monitoring

### Check Response Times
```bash
# Make 10 requests and measure time
for i in {1..10}; do
  time curl -s http://localhost:5070/ > /dev/null
done
```

### Monitor Resource Usage
```bash
# Check container resource usage
docker stats web-ctc-research

# Check system resources
free -h
df -h
```

### Check Worker Processes
```bash
# View worker status
docker exec web-ctc-research ps aux | grep gunicorn

# Expected: 1 master + 4 workers = 5 processes
```

---

## 🔍 Log Locations Quick Access

```bash
# Real-time web server log
docker exec web-ctc-research tail -f /app/logs/gunicorn-error.log

# Real-time access log
docker exec web-ctc-research tail -f /app/logs/gunicorn-access.log

# Real-time error log
docker exec web-ctc-research tail -f /app/logs/error.log

# Real-time application log
docker exec web-ctc-research tail -f /app/logs/application.log

# All logs at once
docker logs -f web-ctc-research
```

---

## 📞 Getting Help

### Useful Information to Gather
```bash
# Container status
docker ps -a

# Recent logs
docker logs web-ctc-research --tail 100

# Container health
docker inspect web-ctc-research | grep -A 10 State

# Environment
docker exec web-ctc-research env | sort

# Version info
docker exec web-ctc-research python --version
docker exec web-ctc-research python -m django --version
```

### Documentation Files
- `LOGS_AND_DEPLOYMENT_INDEX.md` - Navigation guide
- `CONTAINER_LOGS_ANALYSIS.md` - Deep analysis
- `DEPLOYMENT_STATUS_FINAL.md` - Official status
- `LOGS_RESOLUTION_REPORT.md` - What was fixed

---

## 🎯 At a Glance

**Status:** ✅ OPERATIONAL  
**HTTP:** ✅ 200 OK  
**Database:** ✅ Connected  
**Workers:** ✅ 4 active  
**Static Files:** ✅ Ready  

**Last Check:** 2026-06-02 20:45 UTC  
**Next Review:** Monitor logs for changes

---

*Quick Reference Guide - CTC-Research Website*  
*For full details, see the comprehensive documentation files*
