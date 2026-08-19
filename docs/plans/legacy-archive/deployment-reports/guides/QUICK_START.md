# 🚀 Quick Start Deployment Guide

**Time**: 5-60 minutes (5 min to read, 55 min to deploy)  
**Difficulty**: Easy  
**For**: Anyone who wants to deploy quickly  

---

## TL;DR - Deploy in 5 Minutes

```bash
# From /root/site/websites directory
./deploy-production.sh

# That's it! Deployment takes ~55 min
```

---

## What Gets Deployed

✅ **3 Django Websites**
- CTC-Research (http://localhost:5070/)
- LMS-Demo (http://localhost:5071/)
- VResume (http://localhost:5072/)

✅ **Services**
- PostgreSQL database
- Redis cache
- Traefik reverse proxy
- Nginx web servers

✅ **Features**
- SSL/TLS certificates (with backup)
- Health checks
- Auto-restart on failure
- Volume persistence
- Network isolation

---

## Prerequisites

Before deploying, ensure:
- ✅ Docker installed
- ✅ Docker Compose installed
- ✅ ~2 GB free disk space
- ✅ Ports available: 5070, 5071, 5072 (or configure alternatives)
- ✅ `.env` file configured (see below)

## Quick Environment Check

```bash
# Check Docker
docker --version

# Check Docker Compose
docker-compose --version

# Free disk space
df -h | head -3
```

---

## Step-by-Step Deployment

### Step 1: Navigate to Project Directory

```bash
cd /root/site/websites
```

### Step 2: Check/Configure Environment

```bash
# Check if .env exists
ls -la .env

# If not, copy from example
cp .env.example .env

# Edit if needed
nano .env
```

### Step 3: Build JavaScript Assets

```bash
cd assets
npm run build:all      # Build all sites
npm run collectstatic  # Collect static files
cd ..
```

**Time**: ~10 minutes (can be run in background)

### Step 4: Deploy with Docker Compose

```bash
# Start all services
docker-compose up -d

# This will:
# 1. Build Docker images
# 2. Create volumes
# 3. Start containers
# 4. Run migrations
# 5. Configure services
# Time: ~30-40 minutes
```

### Step 5: Verify Deployment

```bash
# Check container status
docker-compose ps

# Should show all containers: running ✅

# Check logs
docker-compose logs -f

# Verify websites
curl http://localhost:5070/  # CTC-Research
curl http://localhost:5071/  # LMS-Demo
curl http://localhost:5072/  # VResume
```

---

## Access Your Websites

| Site | URL | Default Path |
|------|-----|--------------|
| CTC-Research | http://localhost:5070/ | /admin/ |
| LMS-Demo | http://localhost:5071/ | /admin/ |
| VResume | http://localhost:5072/ | / |

### Create Admin Users (if needed)

```bash
# CTC-Research
docker exec -it web-precis-ctc python manage.py createsuperuser

# LMS-Demo  
docker exec -it web-lms-demo python manage.py createsuperuser

# VResume
docker exec -it web-vresume python manage.py createsuperuser
```

---

## Common Commands

### Monitor Deployment

```bash
# View logs
docker-compose logs -f                    # All services
docker-compose logs -f web-precis-ctc   # Specific container

# Check status
docker-compose ps

# Top (resource usage)
docker-compose stats
```

### Management

```bash
# Stop services
docker-compose stop

# Start services
docker-compose start

# Restart services
docker-compose restart

# Full restart (clean)
docker-compose down
docker-compose up -d

# View configuration
docker-compose config
```

### Troubleshooting

```bash
# Container shell
docker exec -it web-precis-ctc bash

# Database shell
docker exec -it db psql -U postgres

# Redis shell
docker exec -it cache redis-cli

# View container logs
docker logs web-precis-ctc
docker logs web-precis-ctc -f  # Follow logs
```

---

## Website URLs

### Local Development
```
CTC-Research: http://localhost:5070/
LMS-Demo:     http://localhost:5071/
VResume:      http://localhost:5072/
```

### Admin Panels
```
CTC-Research: http://localhost:5070/admin/
LMS-Demo:     http://localhost:5071/admin/
VResume:      http://localhost:5072/admin/
```

### Database
```
PostgreSQL: localhost:5432
Redis:      localhost:6379
```

---

## Quick Troubleshooting

### Containers Won't Start

```bash
# View error logs
docker-compose logs

# Check Docker daemon
docker ps

# Try clean restart
docker-compose down
docker system prune
docker-compose up -d
```

### Port Already in Use

```bash
# Find what's using port 5070
lsof -i :5070

# Kill it
kill -9 <PID>

# Or change port in .env
WEBSITE_PORT_CTC=5070       # Change these numbers
WEBSITE_PORT_LMS=5071
WEBSITE_PORT_VRESUME=5072
```

### Out of Disk Space

```bash
# Check usage
df -h

# Clean up Docker
docker system prune -a
docker volume prune

# Or check what's using space
du -sh * | sort -h | tail -10
```

### Database Connection Issues

```bash
# Test database connection
docker exec -it db psql -U postgres -c "SELECT 1"

# Reset database (WARNING: deletes data)
docker-compose down -v
docker-compose up -d

# Check database status
docker-compose exec db pg_isready
```

### Slow Startup

```bash
# View real-time logs
docker-compose logs -f

# Give it time (first startup can take 3-5 minutes)
sleep 300
docker-compose ps

# Check resource usage
docker stats --no-stream
```

---

## Testing After Deployment

### Health Checks

```bash
# Website responses
curl -I http://localhost:5070/       # Status code 200?
curl -I http://localhost:5071/
curl -I http://localhost:5072/

# Database health
docker-compose exec db pg_isready -U postgres

# Cache health
docker-compose exec cache redis-cli ping    # Should return PONG

# Full test suite
bash ../run_full_test_suite.sh
```

### Expected Results

- ✅ All websites return HTTP 200
- ✅ All containers show "Up" status
- ✅ All logs show no errors
- ✅ Database responds to queries
- ✅ Redis responds to ping

---

## Environment Variables

Key variables in `.env`:

```bash
# Website Ports
WEBSITE_PORT_CTC=5070
WEBSITE_PORT_LMS=5071
WEBSITE_PORT_VRESUME=5072

# Database
DATABASE_NAME=websites_db
DATABASE_USER=postgres
DATABASE_PASSWORD=yourpassword

# Django
DEBUG=False
SECRET_KEY=your-secret-key

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

## Deployment Phases

### Phase 1: Preparation (0-5 min)
- Check prerequisites
- Configure environment
- Verify permissions

### Phase 2: Build (5-15 min)
- npm run build:all
- npm run collectstatic

### Phase 3: Docker Setup (15-25 min)
- Build images
- Create volumes
- Create network

### Phase 4: Service Start (25-45 min)
- Start PostgreSQL
- Start Redis
- Start Django apps
- Run migrations

### Phase 5: Verification (45-60 min)
- Health checks
- Create admin users
- Test websites

---

## Rollback Procedure

If something goes wrong:

```bash
# Stop all services
docker-compose down

# Check what went wrong
docker-compose logs

# Fix the issue (see troubleshooting)

# Full clean restart
docker-compose down -v  # WARNING: Deletes data!
docker-compose up -d

# Restore from backup (if available)
# See: ../compose/traefik/CERT_BACKUP_README.md
```

---

## Performance Tips

### Faster Deployment

```bash
# Build assets first (while reading documentation)
cd assets
npm run build:all &
cd ..

# Then start Docker
docker-compose up -d
```

### Faster Startup

```bash
# Parallel builds
docker-compose build --parallel

# Warm cache
docker-compose exec cache redis-cli FLUSHDB
```

### Monitor During Deployment

```bash
# In one terminal
docker-compose logs -f

# In another terminal
watch -n 5 docker-compose ps

# In another terminal
docker stats --no-stream
```

---

## Post-Deployment Tasks

✅ **Done!** But consider:

1. Create admin users (see above)
2. Test admin panels
3. Verify website functionality
4. Back up certificates (if using SSL)
5. Set up monitoring
6. Configure logging
7. Document any customizations

---

## Support & Next Steps

### Stuck?
- See [MANUAL_GUIDE.md](../deployment/MANUAL_GUIDE.md) - Detailed procedures
- Check [troubleshooting](../deployment/MANUAL_GUIDE.md#troubleshooting) section

### Want to understand?
- Read [ARCHITECTURE.md](../guides/ARCHITECTURE.md) - System design
- Read [INFRASTRUCTURE.md](../guides/INFRASTRUCTURE.md) - Docker setup

### Need more options?
- See [TEST_PLAN.md](../deployment/TEST_PLAN.md) - Testing & verification
- See [MANUAL_GUIDE.md](../deployment/MANUAL_GUIDE.md) - Full procedures

---

## One-Command Deploy

If everything is already configured:

```bash
cd /root/site/websites && ./deploy-production.sh
```

---

## Common Issues & Answers

### Q: How long does deployment take?
**A**: ~60 minutes total (5 min read, 55 min deploy)

### Q: Can I stop in the middle?
**A**: Yes, but restart from Step 1 to ensure consistency

### Q: Will this overwrite my data?
**A**: No, unless you run `docker-compose down -v`

### Q: Can I deploy to production?
**A**: Yes, but customize `.env` and security settings first

### Q: What if ports 5070-5072 are taken?
**A**: Change ports in `.env` file

### Q: Can I run just one website?
**A**: Yes, edit `docker-compose.yml` to remove unwanted services

### Q: How do I backup my data?
**A**: Use Docker volume exports or PostgreSQL dump

### Q: How do I update?
**A**: Re-run `./deploy-production.sh` - it's safe

---

## Success Checklist

✅ Deployment complete when:
- [ ] All 3 containers showing "Up"
- [ ] Websites responding at http://localhost:5070/71/72
- [ ] Admin panels accessible
- [ ] Database connected
- [ ] No error logs
- [ ] Performance acceptable

---

**Ready?** Run: `./deploy-production.sh`

**Need help?** Read: [MANUAL_GUIDE.md](../deployment/MANUAL_GUIDE.md)

**Want to learn?** Read: [ARCHITECTURE.md](../guides/ARCHITECTURE.md)

---

**Last Updated**: June 2, 2026  
**Status**: ✅ Ready for Production
