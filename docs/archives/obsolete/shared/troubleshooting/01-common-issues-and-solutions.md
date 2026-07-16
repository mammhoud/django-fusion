# Common Issues and Solutions

## Installation Issues

### Issue: Python Version Not Compatible

**Error**: `Python 3.9 is not supported`

**Solution**:
```bash
# Check Python version
python --version

# Install Python 3.11+
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt-get install python3.11

# Windows
# Download from python.org
```

### Issue: pip Install Fails

**Error**: `ERROR: Could not find a version that satisfies the requirement`

**Solution**:
```bash
# Upgrade pip
pip install --upgrade pip

# Clear pip cache
pip cache purge

# Try installing again
pip install -r requirements.txt
```

### Issue: Virtual Environment Not Activating

**Error**: `command not found: python`

**Solution**:
```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# Verify activation
which python  # Should show .venv path
```

## Database Issues

### Issue: Database Connection Error

**Error**: `could not connect to server: Connection refused`

**Solution**:
```bash
# Check if database is running
docker-compose ps

# Start database
docker-compose up -d db

# Check database logs
docker-compose logs db

# Verify connection string in .env
DATABASE_URL=postgresql://user:password@localhost:5432/xellent
```

### Issue: Migration Fails

**Error**: `django.db.utils.OperationalError: FATAL: database does not exist`

**Solution**:
```bash
# Create database
docker-compose exec db createdb -U postgres xellent

# Or run migrations
docker-compose exec web python manage.py migrate

# Check migration status
docker-compose exec web python manage.py showmigrations
```

### Issue: Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port
lsof -i :5432

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "5433:5432"  # Use different port
```

### Issue: Permission Denied on Database

**Error**: `permission denied for schema public`

**Solution**:
```bash
# Grant permissions
docker-compose exec db psql -U postgres -d xellent -c \
  "GRANT ALL PRIVILEGES ON SCHEMA public TO xellent_user;"

# Or reset database
make reset-db
```

## Docker Issues

### Issue: Docker Daemon Not Running

**Error**: `Cannot connect to Docker daemon`

**Solution**:
```bash
# Start Docker daemon
# macOS
open /Applications/Docker.app

# Linux
sudo systemctl start docker

# Windows
# Start Docker Desktop
```

### Issue: Container Fails to Start

**Error**: `docker-compose up` fails

**Solution**:
```bash
# Check logs
docker-compose logs

# Rebuild images
docker-compose build --no-cache

# Remove old containers
docker-compose down -v

# Start again
docker-compose up -d
```

### Issue: Out of Disk Space

**Error**: `no space left on device`

**Solution**:
```bash
# Clean up Docker
docker system prune -a

# Remove unused volumes
docker volume prune

# Check disk space
df -h
```

## Django Issues

### Issue: Module Not Found

**Error**: `ModuleNotFoundError: No module named 'django'`

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or in Docker
docker-compose build --no-cache
```

### Issue: Settings Module Not Found

**Error**: `ModuleNotFoundError: No module named 'settings'`

**Solution**:
```bash
# Set DJANGO_SETTINGS_MODULE
export DJANGO_SETTINGS_MODULE=config.settings.development

# Or in docker-compose.yml
environment:
  - DJANGO_SETTINGS_MODULE=config.settings.development
```

### Issue: Secret Key Not Set

**Error**: `ImproperlyConfigured: The SECRET_KEY setting must not be empty`

**Solution**:
```bash
# Generate secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Add to .env
SECRET_KEY=your-generated-key
```

### Issue: Static Files Not Found

**Error**: `404 Not Found` for static files

**Solution**:
```bash
# Collect static files
python manage.py collectstatic --noinput

# Or in Docker
docker-compose exec web python manage.py collectstatic --noinput

# Check STATIC_ROOT in settings
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

## API Issues

### Issue: CORS Error

**Error**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**:
```python
# settings.py
INSTALLED_APPS = [
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]
```

### Issue: Authentication Failed

**Error**: `401 Unauthorized`

**Solution**:
```bash
# Check token
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/

# Generate new token
curl -X POST http://localhost:8000/api/token/ \
  -d "username=user&password=password"

# Check token expiration
# Refresh token if needed
```

### Issue: Serializer Validation Error

**Error**: `400 Bad Request` with validation errors

**Solution**:
```python
# Check serializer validation
from apps.courses.serializers import CourseSerializer

serializer = CourseSerializer(data=data)
if not serializer.is_valid():
    print(serializer.errors)  # View validation errors
```

## Frontend Issues

### Issue: CSS Not Loading

**Error**: Styles not applied

**Solution**:
```bash
# Rebuild frontend
npm run build

# Or watch for changes
npm run watch

# Check CSS file is generated
ls -la dist/css/
```

### Issue: JavaScript Error

**Error**: `Uncaught ReferenceError: $ is not defined`

**Solution**:
```bash
# Check if JavaScript is loaded
# Open browser DevTools (F12)
# Check Console tab for errors

# Rebuild JavaScript
npm run build

# Check script tags in template
<script src="{% static 'js/main.js' %}"></script>
```

### Issue: HTMX Not Working

**Error**: HTMX attributes not triggering

**Solution**:
```html
<!-- Check HTMX is loaded -->
<script src="https://unpkg.com/htmx.org"></script>

<!-- Check HTMX attributes -->
<button hx-get="/api/data/" hx-target="#result">Load</button>

<!-- Enable HTMX logging -->
<script>
  htmx.config.logAll = true;
</script>
```

## Performance Issues

### Issue: Slow Page Load

**Error**: Page takes too long to load

**Solution**:
```bash
# Profile code
python -m cProfile -s cumulative manage.py runserver

# Check database queries
# Use Django Debug Toolbar

# Optimize queries
# Use select_related/prefetch_related
# Add database indexes
```

### Issue: High Memory Usage

**Error**: Application uses too much memory

**Solution**:
```bash
# Profile memory
python -m memory_profiler manage.py migrate

# Check for memory leaks
# Use Django Debug Toolbar

# Optimize code
# Use generators instead of lists
# Clear caches periodically
```

### Issue: Slow Database Queries

**Error**: Queries take too long

**Solution**:
```bash
# Analyze query plan
EXPLAIN ANALYZE SELECT ...;

# Add indexes
CREATE INDEX idx_name ON table(column);

# Optimize query
# Use select_related for foreign keys
# Use prefetch_related for reverse relations
```

## Deployment Issues

### Issue: Deployment Fails

**Error**: Deployment script fails

**Solution**:
```bash
# Check logs
docker-compose logs

# Verify environment variables
docker-compose exec web env

# Test locally first
make test

# Check Docker image
docker images
```

### Issue: Application Crashes After Deployment

**Error**: 500 error after deployment

**Solution**:
```bash
# Check logs
docker-compose logs web

# Verify migrations ran
docker-compose exec web python manage.py showmigrations

# Check static files
docker-compose exec web python manage.py collectstatic

# Rollback if needed
git revert <commit>
```

## Getting Help

If you can't find a solution:

1. Check the [Debugging Guide](02-debugging-guide.md)
2. Review project issues on GitHub
3. Check Django documentation
4. Contact the development team

## Related Documentation

- [Debugging Guide](02-debugging-guide.md)
- [Installation Guide](../getting-started/01-installation-guide.md)
- [Local Development Setup](../getting-started/02-local-development-setup.md)
