# Deployment Troubleshooting

Common deployment issues and solutions.

## Service Won't Start

### Symptoms
- Container exits immediately
- Service not responding
- Port not listening

### Diagnosis

```bash
# Check logs
docker-compose logs service-name

# Check container status
docker-compose ps

# Inspect container
docker inspect container-name
```

### Solutions

**Port Already in Use**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

**Configuration Error**
```bash
# Validate configuration
docker-compose config

# Check environment variables
docker-compose exec service-name env
```

**Image Build Failed**
```bash
# Rebuild without cache
docker-compose build --no-cache service-name

# Check Dockerfile
cat Dockerfile
```

## Database Connection Failed

### Symptoms
- "Connection refused" error
- "Database does not exist" error
- Migration fails

### Diagnosis

```bash
# Check database service
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection
docker-compose exec db psql -U postgres -c "SELECT 1"
```

### Solutions

**Database Not Running**
```bash
# Start database
docker-compose up -d db

# Wait for startup
sleep 10

# Verify connection
docker-compose exec db psql -U postgres -c "SELECT 1"
```

**Wrong Credentials**
```bash
# Check environment variables
docker-compose config | grep DATABASE

# Update .env file
# DATABASE_URL=postgresql://user:password@db:5432/dbname
```

**Database Doesn't Exist**
```bash
# Create database
docker-compose exec db createdb -U postgres dbname

# Or run migrations
python manage.py migrate
```

## Migration Failed

### Symptoms
- "Migration not found" error
- "Column already exists" error
- Deployment stuck

### Diagnosis

```bash
# Check migration status
python manage.py showmigrations

# Check migration file
cat app/migrations/0001_initial.py

# Check database state
python manage.py dbshell
```

### Solutions

**Conflicting Migrations**
```bash
# Rollback to previous migration
python manage.py migrate app-name 0001

# Delete conflicting migration
rm app/migrations/0002_conflicting.py

# Create new migration
python manage.py makemigrations

# Apply migration
python manage.py migrate
```

**Migration Syntax Error**
```bash
# Fix migration file
# Edit app/migrations/0002_fix.py

# Validate migration
python manage.py migrate --plan

# Apply migration
python manage.py migrate
```

## Performance Issues

### Symptoms
- Slow response times
- High CPU usage
- High memory usage
- Timeouts

### Diagnosis

```bash
# Check resource usage
docker stats

# Check slow queries
docker-compose exec db psql -U postgres -c "SELECT * FROM pg_stat_statements"

# Check application logs
docker-compose logs --tail=100
```

### Solutions

**High CPU Usage**
```bash
# Identify process
docker top container-name

# Check for infinite loops
docker-compose logs | grep -i loop

# Restart service
docker-compose restart service-name
```

**High Memory Usage**
```bash
# Check memory limit
docker inspect container-name | grep Memory

# Increase memory limit
# Update docker-compose.yml
# mem_limit: 2g

# Restart service
docker-compose up -d
```

**Slow Queries**
```bash
# Enable query logging
# Add to Django settings:
# LOGGING = {
#   'handlers': {
#     'console': {
#       'class': 'logging.StreamHandler',
#     },
#   },
#   'loggers': {
#     'django.db.backends': {
#       'handlers': ['console'],
#       'level': 'DEBUG',
#     },
#   },
# }

# Analyze slow queries
docker-compose logs | grep "duration:"

# Add database indexes
python manage.py dbshell
# CREATE INDEX idx_name ON table(column);
```

## Network Issues

### Symptoms
- "Connection refused" error
- "Network unreachable" error
- Services can't communicate

### Diagnosis

```bash
# Check network
docker network ls

# Inspect network
docker network inspect compose_default

# Test connectivity
docker-compose exec service-name ping other-service
```

### Solutions

**Services on Different Networks**
```bash
# Check docker-compose.yml
# Ensure all services on same network

# Restart services
docker-compose down
docker-compose up -d
```

**Firewall Blocking**
```bash
# Check firewall rules
sudo iptables -L

# Allow port
sudo ufw allow 8000

# Restart services
docker-compose restart
```

## SSL/TLS Issues

### Symptoms
- "Certificate verification failed" error
- "SSL: CERTIFICATE_VERIFY_FAILED" error
- HTTPS not working

### Diagnosis

```bash
# Check certificate
openssl x509 -in cert.pem -text -noout

# Check certificate expiration
openssl x509 -in cert.pem -noout -dates

# Test SSL connection
openssl s_client -connect example.com:443
```

### Solutions

**Certificate Expired**
```bash
# Renew certificate
certbot renew

# Or generate new certificate
certbot certonly --standalone -d example.com

# Update docker-compose.yml
# volumes:
#   - /etc/letsencrypt:/etc/letsencrypt

# Restart services
docker-compose restart
```

**Certificate Not Found**
```bash
# Check certificate path
ls -la /etc/letsencrypt/live/example.com/

# Update docker-compose.yml with correct path
# Restart services
docker-compose restart
```

## Troubleshooting Checklist

- [ ] Check service logs
- [ ] Verify configuration
- [ ] Test connectivity
- [ ] Check resource usage
- [ ] Review recent changes
- [ ] Check error messages
- [ ] Consult documentation
- [ ] Ask for help

## Next Steps

- Review [Deployment Procedures](03-deployment-procedures.md)
- Check [Rollback Procedures](05-rollback-procedures.md)
- See [Post-Deployment Verification](04-post-deployment-verification.md)
