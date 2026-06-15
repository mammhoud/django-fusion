# Production Deployment Guide

## 🚀 Overview

This guide covers the complete production deployment process for the CTC Research platform with comprehensive testing at each stage.

## 📋 Pre-Deployment Checklist

### Infrastructure Requirements
- [ ] Docker and Docker Compose installed
- [ ] PostgreSQL container running (`db_ctc` database)
- [ ] Redis container running
- [ ] SSL certificates configured (if applicable)
- [ ] Domain DNS configured
- [ ] Backup systems in place

### Environment Configuration
- [ ] Production environment variables configured (`.env.production`)
- [ ] Database connection parameters verified
- [ ] Secret keys and tokens updated
- [ ] Email configuration tested
- [ ] Static file storage configured

### Code Preparation
- [ ] All tests passing in development
- [ ] Code reviewed and approved
- [ ] Database migrations prepared
- [ ] Static files optimized
- [ ] Documentation updated

## 🔧 Deployment Process

### Step 1: Infrastructure Setup

```bash
# Start core infrastructure services
docker compose up -d postgres redis

# Verify services are running
docker compose ps

# Check database connectivity
docker exec postgres pg_isready -U postgres
```

### Step 2: Database Preparation

```bash
# Ensure production database exists
docker exec postgres psql -U postgres -c "CREATE DATABASE IF NOT EXISTS db_ctc;"

# Verify database structure
docker exec postgres psql -U postgres -d db_ctc -c "\dt"
```

### Step 3: Environment Configuration

```bash
# Copy production environment
cp .env.production .env

# Verify critical settings
grep -E "^(SERVER_ENV|DEBUG|DB_NAME)" .env
```

### Step 4: Pre-Deployment Testing

```bash
# Run production environment tests
python scripts/test_production_simple.py

# Verify database connectivity
python scripts/test_database_production.py

# Check Docker environment
python scripts/test_docker_environments.py
```

### Step 5: Application Deployment

```bash
# Build Docker images
docker compose -f ctc-research.com/docker-compose.yml build

# Run database migrations
docker compose -f ctc-research.com/docker-compose.yml run --rm website python manage.py migrate

# Collect static files
docker compose -f ctc-research.com/docker-compose.yml run --rm website python manage.py collectstatic --noinput

# Start application services
docker compose -f ctc-research.com/docker-compose.yml up -d
```

### Step 6: Post-Deployment Verification

```bash
# Check service health
curl -f http://localhost:5070/health/ || echo "Health check failed"

# Verify database operations
docker compose -f ctc-research.com/docker-compose.yml exec website python manage.py shell -c "from django.contrib.auth.models import User; print(f'Users: {User.objects.count()}')"

# Check logs for errors
docker compose -f ctc-research.com/docker-compose.yml logs --tail=50 website | grep -i error
```

## 🧪 Production Testing Suite

### Automated Testing

The production testing suite includes:

1. **Environment Configuration Tests**
   - Verify production settings
   - Check environment variables
   - Validate security configurations

2. **Database Tests**
   - PostgreSQL connectivity
   - Migration status verification
   - Data integrity checks
   - Performance benchmarks

3. **Application Tests**
   - Django system checks
   - Model operations
   - Admin interface
   - Wagtail CMS functionality

4. **Integration Tests**
   - API endpoints
   - User authentication
   - File uploads
   - Email functionality

5. **Performance Tests**
   - Database query performance
   - Memory usage
   - Response times
   - Load handling

### Running Production Tests

```bash
# Comprehensive production test suite
make test-production

# Database-specific tests
make test-database

# Docker environment tests
make test-docker

# All environment tests
make test-all-environments
```

## 📊 Monitoring and Logging

### Health Check Endpoints

The application provides several health check endpoints:

- `/health/` - Basic application health
- `/health/database/` - Database connectivity
- `/health/cache/` - Cache functionality
- `/health/storage/` - File storage access

### Log Monitoring

```bash
# Application logs
docker compose logs -f website

# Database logs
docker logs postgres

# Worker logs
docker compose logs -f website-worker

# Error log analysis
docker compose logs website | grep -i error | tail -20
```

### Performance Monitoring

```bash
# Database performance
docker exec postgres psql -U postgres -d db_ctc -c "SELECT * FROM pg_stat_activity;"

# Container resource usage
docker stats

# Disk usage
df -h
docker system df
```

## 🔄 Rollback Procedures

### Quick Rollback

```bash
# Stop current deployment
docker compose -f ctc-research.com/docker-compose.yml down

# Restore previous version
git checkout previous-stable-tag

# Rebuild and deploy
docker compose -f ctc-research.com/docker-compose.yml build
docker compose -f ctc-research.com/docker-compose.yml up -d
```

### Database Rollback

```bash
# Restore database from backup
docker exec postgres pg_restore -U postgres -d db_ctc /backups/latest_backup.sql

# Verify data integrity
python scripts/test_production_simple.py
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check PostgreSQL status
   docker exec postgres pg_isready -U postgres

   # Verify connection parameters
   docker exec postgres psql -U postgres -d db_ctc -c "SELECT current_database();"
   ```

2. **Migration Errors**
   ```bash
   # Check migration status
   docker compose exec website python manage.py showmigrations

   # Apply specific migration
   docker compose exec website python manage.py migrate app_name migration_name
   ```

3. **Static File Issues**
   ```bash
   # Recollect static files
   docker compose exec website python manage.py collectstatic --clear --noinput

   # Check static file permissions
   docker compose exec website ls -la assets/staticfiles/
   ```

4. **Service Health Failures**
   ```bash
   # Check service dependencies
   docker compose ps

   # Restart specific service
   docker compose restart website

   # Check service logs
   docker compose logs website
   ```

### Debug Commands

```bash
# Django system check
docker compose exec website python manage.py check --deploy

# Database shell access
docker compose exec website python manage.py dbshell

# Python shell with Django
docker compose exec website python manage.py shell

# Container shell access
docker compose exec website bash
```

## 📈 Performance Optimization

### Database Optimization

```sql
-- Analyze database performance
ANALYZE;

-- Check slow queries
SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;

-- Index usage analysis
SELECT schemaname, tablename, attname, n_distinct, correlation FROM pg_stats;
```

### Application Optimization

```bash
# Profile Django application
docker compose exec website python manage.py shell -c "
import cProfile
import pstats
# Add profiling code here
"

# Memory usage analysis
docker compose exec website python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

## 🔐 Security Considerations

### Production Security Checklist

- [ ] DEBUG = False in production
- [ ] Strong SECRET_KEY configured
- [ ] Database credentials secured
- [ ] HTTPS enabled (if applicable)
- [ ] CSRF protection enabled
- [ ] SQL injection protection verified
- [ ] File upload restrictions in place
- [ ] User permission system configured

### Security Testing

```bash
# Django security check
docker compose exec website python manage.py check --deploy

# Test CSRF protection
curl -X POST http://localhost:5070/admin/ -d "username=test&password=test"

# Verify HTTPS redirect (if configured)
curl -I http://localhost:5070/
```

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Docker Production Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [PostgreSQL Production Configuration](https://www.postgresql.org/docs/current/runtime-config.html)
- [Wagtail Production Guide](https://docs.wagtail.org/en/stable/advanced_topics/deploying.html)

---

**Last Updated**: $(date)
**Version**: 1.0
**Maintained By**: CTC Research Development Team
