# Rollback Procedures

How to rollback a failed deployment.

## Rollback Decision Criteria

### Immediate Rollback Required

- Service completely down
- Critical functionality broken
- Data corruption detected
- Security vulnerability discovered
- Database migration failed

### Investigate Before Rollback

- Minor UI issues
- Performance degradation
- Non-critical features broken
- Intermittent errors

## Rollback Steps

### 1. Stop Current Deployment

```bash
# Stop services
docker-compose down

# Verify stopped
docker-compose ps
```

### 2. Restore Previous Version

```bash
# Checkout previous tag
git checkout v1.2.3

# Or checkout previous commit
git checkout HEAD~1
```

### 3. Restore Database (if needed)

```bash
# Restore from backup
psql -U postgres prod_db < backup.sql

# Or rollback migrations
python manage.py migrate app-name 0001
```

### 4. Rebuild and Deploy

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Verify services
docker-compose ps
```

### 5. Verify Rollback

```bash
# Check health
curl http://localhost:8000/health/

# Check logs
docker-compose logs

# Run smoke tests
npm run test:smoke
```

## Automated Rollback

### Health Check Monitoring

```bash
#!/bin/bash

# Monitor health endpoint
while true; do
  response=$(curl -s http://localhost:8000/health/)

  if [ $? -ne 0 ]; then
    echo "Health check failed, initiating rollback"
    ./rollback.sh
    break
  fi

  sleep 30
done
```

### Rollback Script

```bash
#!/bin/bash
# rollback.sh

echo "Starting rollback..."

# Stop current services
docker-compose down

# Restore previous version
git checkout v1.2.3

# Rebuild
docker-compose build

# Start services
docker-compose up -d

# Verify
curl http://localhost:8000/health/

echo "Rollback complete"
```

## Database Rollback

### Backup Strategy

```bash
# Create backup before deployment
docker-compose exec db pg_dump -U postgres prod_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Keep backups for 7 days
find . -name "backup_*.sql" -mtime +7 -delete
```

### Restore from Backup

```bash
# List available backups
ls -la backup_*.sql

# Restore specific backup
psql -U postgres prod_db < backup_20240101_120000.sql

# Verify restore
psql -U postgres prod_db -c "SELECT COUNT(*) FROM projects;"
```

### Migration Rollback

```bash
# Show migration history
python manage.py showmigrations

# Rollback to specific migration
python manage.py migrate app-name 0005

# Verify rollback
python manage.py showmigrations
```

## Communication

### Notify Team

```
Subject: Deployment Rollback - [Service Name]

We have rolled back the deployment due to [reason].

Timeline:
- Deployment started: 2024-01-01 12:00 UTC
- Issue detected: 2024-01-01 12:15 UTC
- Rollback initiated: 2024-01-01 12:20 UTC
- Rollback complete: 2024-01-01 12:30 UTC

Current status: [Service] is back to v1.2.3

Next steps:
- Investigate root cause
- Fix issues
- Re-deploy when ready

Questions? Contact [team]
```

## Post-Rollback

### Investigation

1. Check logs for errors
2. Identify root cause
3. Document issue
4. Create fix
5. Test fix
6. Re-deploy

### Prevention

1. Add more tests
2. Improve monitoring
3. Update procedures
4. Train team
5. Review deployment process

## Rollback Checklist

- [ ] Issue identified
- [ ] Rollback decision made
- [ ] Backup verified
- [ ] Services stopped
- [ ] Previous version restored
- [ ] Database restored (if needed)
- [ ] Services started
- [ ] Health checks passing
- [ ] Smoke tests passing
- [ ] Team notified
- [ ] Root cause documented

## Next Steps

- Review [Deployment Procedures](03-deployment-procedures.md)
- Check [Post-Deployment Verification](04-post-deployment-verification.md)
- See [Troubleshooting](06-troubleshooting.md)
