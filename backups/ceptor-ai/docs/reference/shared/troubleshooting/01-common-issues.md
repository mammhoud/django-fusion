# Common Issues

Frequently encountered problems and solutions.

## Port Already in Use

### Symptoms
- "Address already in use" error
- Service won't start
- Port binding fails

### Solution

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"
```

## Module Not Found

### Symptoms
- "ModuleNotFoundError" in Python
- "Cannot find module" in JavaScript
- Import errors

### Solution

```bash
# Python
pip install -r requirements.txt
pip install missing-module

# JavaScript
npm install
npm install missing-module
```

## Database Connection Failed

### Symptoms
- "Connection refused" error
- "Database does not exist" error
- Migration fails

### Solution

```bash
# Check database is running
docker-compose ps db

# Start database
docker-compose up -d db

# Check connection
docker-compose exec db psql -U postgres -c "SELECT 1"

# Create database if needed
docker-compose exec db createdb -U postgres dbname
```

## Authentication Failed

### Symptoms
- "Invalid credentials" error
- "Unauthorized" error
- Login fails

### Solution

```bash
# Check credentials
# Verify username and password

# Reset password
python manage.py changepassword username

# Check token expiration
# Refresh token if needed
```

## CORS Error

### Symptoms
- "CORS policy" error in browser
- "Access-Control-Allow-Origin" missing
- Cross-origin request blocked

### Solution

```python
# Add to Django settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]

# Or install django-cors-headers
pip install django-cors-headers

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    'corsheaders',
]

# Add middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
]
```

## Memory Leak

### Symptoms
- Memory usage keeps increasing
- Application slows down
- Eventually crashes

### Solution

```bash
# Monitor memory usage
docker stats

# Check for circular references
# Review event listeners
# Check for unclosed connections

# Restart service
docker-compose restart service-name
```

## Slow Performance

### Symptoms
- Slow response times
- High CPU usage
- Timeouts

### Solution

```bash
# Check resource usage
docker stats

# Analyze slow queries
# Add database indexes
# Optimize code

# Enable caching
# Use CDN for static files
```

## File Permission Denied

### Symptoms
- "Permission denied" error
- Can't read/write files
- Access denied

### Solution

```bash
# Check file permissions
ls -la file.txt

# Change permissions
chmod 644 file.txt
chmod 755 directory

# Change ownership
chown user:group file.txt
```

## SSL Certificate Error

### Symptoms
- "Certificate verification failed" error
- "SSL: CERTIFICATE_VERIFY_FAILED" error
- HTTPS not working

### Solution

```bash
# Check certificate
openssl x509 -in cert.pem -text -noout

# Check expiration
openssl x509 -in cert.pem -noout -dates

# Renew certificate
certbot renew

# Update docker-compose.yml with new certificate path
```

## Timeout Error

### Symptoms
- "Request timeout" error
- "Connection timeout" error
- Operation takes too long

### Solution

```bash
# Increase timeout
# In requests library
response = requests.get(url, timeout=30)

# In axios
axios.defaults.timeout = 30000

# In Django
CELERY_TASK_TIME_LIMIT = 600

# Optimize slow operations
# Add caching
# Use async tasks
```

## Out of Memory

### Symptoms
- "Out of memory" error
- Application crashes
- System becomes unresponsive

### Solution

```bash
# Check memory usage
free -h

# Increase memory limit
# In docker-compose.yml
mem_limit: 2g

# Optimize memory usage
# Remove unused data
# Use generators instead of lists
# Clear caches periodically
```

## Troubleshooting Checklist

- [ ] Check error message
- [ ] Review logs
- [ ] Check configuration
- [ ] Verify prerequisites
- [ ] Test with sample data
- [ ] Check resource usage
- [ ] Review recent changes
- [ ] Restart service
- [ ] Ask for help

## Next Steps

- Review [Debugging Guide](02-debugging-guide.md)
- Check [Log Analysis](03-log-analysis.md)
- See [Performance Optimization](04-performance-optimization.md)
