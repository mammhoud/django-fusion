# Log Analysis

How to analyze logs and find issues.

## Log Locations

### Application Logs

```bash
# Django logs
docker-compose logs ctc-research-backend

# Frontend logs
docker-compose logs ctc-research-frontend

# Nginx logs
docker-compose logs nginx
```

### System Logs

```bash
# Docker logs
docker logs container-name

# System logs
tail -f /var/log/syslog
```

## Log Levels

### ERROR
Critical issues that need immediate attention.

```
ERROR: Database connection failed
ERROR: Authentication failed
ERROR: Internal server error
```

### WARNING
Potential issues that should be investigated.

```
WARNING: Slow query detected
WARNING: High memory usage
WARNING: Deprecated API used
```

### INFO
Informational messages about normal operations.

```
INFO: Server started
INFO: Request processed
INFO: Migration completed
```

### DEBUG
Detailed information for debugging.

```
DEBUG: Variable value: 42
DEBUG: Function called with args: (1, 2, 3)
DEBUG: Query executed: SELECT * FROM users
```

## Common Error Messages

### Database Errors

```
ERROR: could not connect to server: Connection refused
ERROR: FATAL: password authentication failed
ERROR: relation "table_name" does not exist
```

**Solutions**:
- Check database is running
- Verify credentials
- Run migrations

### Authentication Errors

```
ERROR: Invalid credentials
ERROR: Token expired
ERROR: Unauthorized access
```

**Solutions**:
- Check username/password
- Refresh token
- Check permissions

### API Errors

```
ERROR: 404 Not Found
ERROR: 500 Internal Server Error
ERROR: 429 Too Many Requests
```

**Solutions**:
- Check endpoint URL
- Check server logs
- Wait and retry

## Log Analysis Tools

### grep

```bash
# Find errors
docker-compose logs | grep ERROR

# Find specific error
docker-compose logs | grep "Database connection"

# Count errors
docker-compose logs | grep ERROR | wc -l
```

### tail

```bash
# Show last 100 lines
docker-compose logs --tail=100

# Follow logs in real-time
docker-compose logs -f

# Follow specific service
docker-compose logs -f ctc-research-backend
```

### awk

```bash
# Extract timestamps
docker-compose logs | awk '{print $1, $2}'

# Extract error messages
docker-compose logs | awk '/ERROR/ {print $0}'
```

## Performance Analysis

### Slow Queries

```bash
# Find slow queries
docker-compose logs | grep "duration:"

# Extract query time
docker-compose logs | grep "duration:" | awk '{print $NF}'
```

### High Resource Usage

```bash
# Check CPU usage
docker stats

# Check memory usage
docker stats --no-stream

# Check disk usage
df -h
```

## Debugging Techniques

### Add Debug Logging

**Python**
```python
import logging

logger = logging.getLogger(__name__)
logger.debug(f"Variable value: {value}")
logger.info("Operation completed")
logger.warning("Potential issue detected")
logger.error("Error occurred")
```

**JavaScript**
```javascript
console.log('Debug message:', value)
console.info('Info message')
console.warn('Warning message')
console.error('Error message')
```

### Enable Debug Mode

**Django**
```python
# settings.py
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

**React**
```javascript
// Enable React DevTools
if (process.env.NODE_ENV === 'development') {
  window.__REACT_DEVTOOLS_GLOBAL_HOOK__ = window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || {}
}
```

## Log Aggregation

### Centralized Logging

```bash
# View all logs
docker-compose logs

# View logs from specific time
docker-compose logs --since 2024-01-01T00:00:00

# View logs until specific time
docker-compose logs --until 2024-01-02T00:00:00
```

### Log Filtering

```bash
# Filter by service
docker-compose logs ctc-research-backend

# Filter by level
docker-compose logs | grep ERROR

# Filter by keyword
docker-compose logs | grep "database"
```

## Next Steps

- Review [Common Issues](01-common-issues.md)
- Check [Debugging Guide](02-debugging-guide.md)
- See [Performance Optimization](04-performance-optimization.md)
