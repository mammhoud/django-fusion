# Deployment Procedures

Step-by-step deployment instructions.

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Code reviewed
- [ ] Dependencies updated
- [ ] Environment variables configured
- [ ] Database backups created
- [ ] Deployment plan reviewed
- [ ] Team notified
- [ ] Monitoring configured

## Deployment Steps

### 1. Prepare Environment

```bash
# Create backup
docker-compose exec db pg_dump -U postgres prod_db > backup.sql

# Pull latest code
git pull origin main

# Install dependencies
npm install
pip install -r requirements.txt
```

### 2. Build Artifacts

```bash
# Build frontend
npm run build

# Build Docker images
docker-compose build

# Verify images
docker images
```

### 3. Run Migrations

```bash
# Django migrations
python manage.py migrate

# Verify migrations
python manage.py showmigrations
```

### 4. Deploy Services

```bash
# Stop current services
docker-compose down

# Start new services
docker-compose up -d

# Verify services
docker-compose ps
```

### 5. Verify Deployment

```bash
# Check service health
curl http://localhost:8000/health/

# Check logs
docker-compose logs -f

# Run smoke tests
npm run test:smoke
```

## Deployment with Zero Downtime

### Blue-Green Deployment

```bash
# 1. Deploy to green environment
docker-compose -f docker-compose.green.yml up -d

# 2. Run migrations on green
docker-compose -f docker-compose.green.yml exec db python manage.py migrate

# 3. Test green environment
curl http://localhost:8001/health/

# 4. Switch traffic to green
# Update load balancer configuration

# 5. Keep blue as rollback
# Keep blue environment running for 1 hour
```

## Deployment Rollback

If deployment fails:

```bash
# 1. Identify issue
docker-compose logs

# 2. Stop new version
docker-compose down

# 3. Restore previous version
git checkout previous-tag
docker-compose build
docker-compose up -d

# 4. Restore database if needed
psql -U postgres prod_db < backup.sql

# 5. Verify rollback
curl http://localhost:8000/health/
```

## Post-Deployment

```bash
# 1. Monitor logs
docker-compose logs -f

# 2. Check metrics
# - CPU usage
# - Memory usage
# - Error rate
# - Response time

# 3. Run tests
npm run test:e2e

# 4. Notify team
# Send deployment notification
```

## Deployment Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs service-name

# Check configuration
docker-compose config

# Rebuild image
docker-compose build --no-cache service-name
```

### Database Migration Failed

```bash
# Check migration status
python manage.py showmigrations

# Rollback migration
python manage.py migrate app-name 0001

# Fix migration
# Edit migration file

# Re-run migration
python manage.py migrate
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

## Next Steps

- Review [Post-Deployment Verification](04-post-deployment-verification.md)
- Check [Rollback Procedures](05-rollback-procedures.md)
- See [Troubleshooting](06-troubleshooting.md)
