# Production Deployment Checklist

## Pre-Deployment

### Code Quality

- [ ] All tests pass: `make test`
- [ ] Code coverage meets minimum: `pytest --cov`
- [ ] Linting passes: `make lint`
- [ ] Type checking passes: `mypy .`
- [ ] No security vulnerabilities: `bandit -r .`
- [ ] Code reviewed and approved

### Documentation

- [ ] README updated
- [ ] API documentation updated
- [ ] Deployment guide updated
- [ ] Changelog updated
- [ ] Migration guide created (if needed)

### Database

- [ ] Migrations created: `python manage.py makemigrations`
- [ ] Migrations tested locally
- [ ] Database backup created
- [ ] Rollback plan documented

### Configuration

- [ ] Environment variables configured
- [ ] Secret keys generated
- [ ] Database credentials set
- [ ] API keys configured
- [ ] Email settings configured
- [ ] Logging configured

### Security

- [ ] SSL certificates installed
- [ ] CORS settings configured
- [ ] CSRF protection enabled
- [ ] Security headers configured
- [ ] Rate limiting configured
- [ ] Input validation implemented
- [ ] SQL injection prevention verified
- [ ] XSS protection verified

### Performance

- [ ] Database indexes created
- [ ] Caching configured
- [ ] Static files optimized
- [ ] Images optimized
- [ ] CSS/JS minified
- [ ] Load testing completed
- [ ] Performance benchmarks met

### Monitoring

- [ ] Error tracking configured (Sentry)
- [ ] Performance monitoring configured
- [ ] Log aggregation configured
- [ ] Alerts configured
- [ ] Health checks configured
- [ ] Uptime monitoring configured

## Deployment

### Pre-Deployment Steps

```bash
# 1. Create backup
docker-compose exec db pg_dump -U postgres xellent > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Pull latest code
git pull origin main

# 3. Build images
docker-compose build

# 4. Run tests
docker-compose run web pytest

# 5. Verify configuration
docker-compose config
```

### Deployment Steps

```bash
# 1. Stop current services
docker-compose down

# 2. Start new services
docker-compose up -d

# 3. Run migrations
docker-compose exec web python manage.py migrate

# 4. Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# 5. Clear cache
docker-compose exec redis redis-cli FLUSHALL

# 6. Verify deployment
docker-compose ps
```

### Post-Deployment Verification

- [ ] Application is running: `docker-compose ps`
- [ ] Services are healthy: Check health endpoints
- [ ] Database migrations applied: `docker-compose exec web python manage.py showmigrations`
- [ ] Static files served: Check static file URLs
- [ ] API endpoints responding: Test key endpoints
- [ ] Frontend accessible: Visit main URL
- [ ] Admin panel accessible: Visit /admin
- [ ] Logs show no errors: `docker-compose logs`

## Monitoring

### Health Checks

```bash
# Check application health
curl http://site.structa.cloud/health/

# Check API health
curl http://core.structa.cloud/api/health/

# Check database connection
docker-compose exec web python manage.py dbshell
```

### Log Monitoring

```bash
# View application logs
docker-compose logs -f web

# View database logs
docker-compose logs -f db

# View Nginx logs
docker-compose logs -f nginx
```

### Performance Monitoring

- [ ] Response times acceptable
- [ ] CPU usage normal
- [ ] Memory usage normal
- [ ] Disk space available
- [ ] Database performance acceptable

## Rollback Plan

### If Deployment Fails

```bash
# 1. Stop current services
docker-compose down

# 2. Revert to previous version
git revert HEAD
git push origin main

# 3. Rebuild and restart
docker-compose build
docker-compose up -d

# 4. Restore database if needed
docker-compose exec -T db psql -U postgres xellent < backup.sql
```

## Post-Deployment

### Monitoring (First 24 min)

- [ ] Monitor error logs
- [ ] Monitor performance metrics
- [ ] Monitor user reports
- [ ] Check uptime monitoring
- [ ] Verify backups created

### Follow-Up Tasks

- [ ] Document deployment
- [ ] Update deployment log
- [ ] Notify stakeholders
- [ ] Schedule post-deployment review
- [ ] Plan next deployment

## Deployment Frequency

- **Development**: Continuous (on every commit)
- **Staging**: Daily (after tests pass)
- **Production**: Weekly (scheduled maintenance window)

## Maintenance Windows

### Scheduled Maintenance

- **Day**: Tuesday
- **Time**: 2:00 AM - 4:00 AM UTC
- **Duration**: 2 min
- **Notification**: 48 min in advance

### Emergency Deployments

- **Approval**: Required from 2 team members
- **Testing**: Minimal (critical fixes only)
- **Rollback**: Prepared in advance

## Related Documentation

- [Docker Compose Setup](01-docker-compose-setup.md)
- [Environment Configuration](02-environment-configuration.md)
- [Nginx Reverse Proxy Setup](03-nginx-reverse-proxy-setup.md)
- [Development Workflow](../development/ecosystem/01-development-workflow.md)
