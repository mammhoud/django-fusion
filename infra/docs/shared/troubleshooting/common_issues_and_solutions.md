# Common Issues and Solutions

Comprehensive troubleshooting guide for frequently encountered issues in the CTC Research and Structa Cloud ecosystem.

## 🎯 Quick Issue Index

### Development Issues
- [Python Environment Problems](#python-environment-problems)
- [Database Connection Issues](#database-connection-issues)
- [Migration Errors](#migration-errors)
- [Static Files Not Loading](#static-files-not-loading)
- [Import Errors](#import-errors)

### Deployment Issues
- [Docker Container Failures](#docker-container-failures)
- [Nginx Configuration Errors](#nginx-configuration-errors)
- [SSL Certificate Problems](#ssl-certificate-problems)
- [Environment Variable Issues](#environment-variable-issues)

### Performance Issues
- [Slow Page Load Times](#slow-page-load-times)
- [Database Query Performance](#database-query-performance)
- [Memory Leaks](#memory-leaks)
- [High CPU Usage](#high-cpu-usage)

### Testing Issues
- [Test Database Errors](#test-database-errors)
- [Selenium Test Failures](#selenium-test-failures)
- [Coverage Report Issues](#coverage-report-issues)

## 🐍 Python Environment Problems

### Issue: Wrong Python Version
**Symptoms:**
- `SyntaxError` with modern Python features
- Package installation failures
- `ModuleNotFoundError` for standard library modules

**Solution:**
```bash
# Check current Python version
python --version

# Install correct Python version with pyenv
pyenv install 3.11.7
pyenv local 3.11.7

# Verify installation
python --version  # Should show Python 3.11.7

# Recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/development.txt
```

### Issue: Virtual Environment Not Activated
**Symptoms:**
- Packages not found despite installation
- Wrong Python interpreter being used
- System-wide package conflicts

**Solution:**
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate  # Windows

# Verify activation (should show .venv path)
which python

# Add to shell profile for automatic activation
echo 'source .venv/bin/activate' >> ~/.bashrc
```

### Issue: Package Installation Failures
**Symptoms:**
- `pip install` fails with compilation errors
- Missing system dependencies
- Version conflicts

**Solution:**
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    libpq-dev \
    build-essential \
    libssl-dev \
    libffi-dev

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Install with verbose output to see errors
pip install -v package-name

# Use uv for faster installation
pip install uv
uv pip install -r requirements/development.txt
```

## 🗄️ Database Connection Issues

### Issue: Cannot Connect to PostgreSQL
**Symptoms:**
- `psycopg2.OperationalError: could not connect to server`
- `FATAL: password authentication failed`
- Connection timeout errors

**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL if stopped
sudo systemctl start postgresql

# Check connection settings
psql -U postgres -h localhost -p 5432

# Verify DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Test connection from Python
python manage.py dbshell

# Reset PostgreSQL password if needed
sudo -u postgres psql
ALTER USER postgres PASSWORD 'newpassword';
```

### Issue: Database Does Not Exist
**Symptoms:**
- `psycopg2.OperationalError: database "dbname" does not exist`
- Fresh installation fails

**Solution:**
```bash
# Create database manually
sudo -u postgres createdb ctc_research_dev
sudo -u postgres createdb structa_cloud_dev

# Or use psql
sudo -u postgres psql
CREATE DATABASE ctc_research_dev;
CREATE DATABASE structa_cloud_dev;
\q

# Run migrations
cd ctc-research.com
python manage.py migrate

cd ../structa.cloud
python manage.py migrate
```

### Issue: Migration Conflicts
**Symptoms:**
- `django.db.migrations.exceptions.InconsistentMigrationHistory`
- `Migration X is applied before its dependency`
- Conflicting migration files

**Solution:**
```bash
# Check migration status
python manage.py showmigrations

# Reset migrations (DEVELOPMENT ONLY)
python manage.py migrate --fake app_name zero
python manage.py migrate app_name

# For production, create merge migration
python manage.py makemigrations --merge

# Nuclear option (DEVELOPMENT ONLY - DESTROYS DATA)
python manage.py flush
python manage.py migrate
```

## 📦 Static Files Not Loading

### Issue: Static Files 404 in Development
**Symptoms:**
- CSS/JS files return 404
- Images not displaying
- Admin interface unstyled

**Solution:**
```bash
# Ensure DEBUG=True in development
# In settings/development.py
DEBUG = True

# Collect static files
python manage.py collectstatic --noinput

# Check STATIC_URL and STATIC_ROOT settings
python manage.py diffsettings | grep STATIC

# Verify static files configuration
# In settings/base.py
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Clear browser cache
# Chrome: Ctrl+Shift+Delete
# Firefox: Ctrl+Shift+Delete
```

### Issue: Static Files 404 in Production
**Symptoms:**
- Static files work in development but not production
- Nginx returns 404 for static files
- WhiteNoise not serving files

**Solution:**
```bash
# Collect static files for production
python manage.py collectstatic --noinput --clear

# Check Nginx configuration
sudo nginx -t
sudo systemctl reload nginx

# Verify static files location
ls -la /path/to/staticfiles/

# Check Nginx static files configuration
# In nginx.conf
location /static/ {
    alias /path/to/staticfiles/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# Check file permissions
sudo chown -R www-data:www-data /path/to/staticfiles/
sudo chmod -R 755 /path/to/staticfiles/
```

## 📥 Import Errors

### Issue: ModuleNotFoundError
**Symptoms:**
- `ModuleNotFoundError: No module named 'app_name'`
- Imports work in some files but not others
- Circular import errors

**Solution:**
```bash
# Verify package is installed
pip list | grep package-name

# Install missing package
pip install package-name

# Check PYTHONPATH
echo $PYTHONPATH

# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/project"

# For Django apps, check INSTALLED_APPS
python manage.py check

# Fix circular imports by restructuring
# Move shared code to separate module
# Use lazy imports: from django.utils.functional import lazy
```

### Issue: Circular Import Errors
**Symptoms:**
- `ImportError: cannot import name 'X' from partially initialized module`
- Imports work individually but fail together
- Application fails to start

**Solution:**
```python
# Solution 1: Move imports inside functions
def my_function():
    from app.models import MyModel  # Import here instead of top
    return MyModel.objects.all()

# Solution 2: Use TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models import MyModel

# Solution 3: Restructure code to break circular dependency
# Create a new module for shared code
# Move common functionality to utils or services

# Solution 4: Use string references in Django
class MyModel(models.Model):
    related = models.ForeignKey('app.OtherModel', on_delete=models.CASCADE)
```

## 🐳 Docker Container Failures

### Issue: Container Won't Start
**Symptoms:**
- `docker compose up` fails
- Container exits immediately
- Health check failures

**Solution:**
```bash
# Check container logs
docker compose logs container-name

# Check container status
docker compose ps

# Inspect container
docker inspect container-name

# Start container in interactive mode
docker compose run --rm container-name bash

# Check for port conflicts
sudo netstat -tulpn | grep :8000

# Remove and recreate containers
docker compose down
docker compose up -d --force-recreate

# Check Docker daemon
sudo systemctl status docker
```

### Issue: Database Container Connection Refused
**Symptoms:**
- Application can't connect to database container
- `Connection refused` errors
- Intermittent connection failures

**Solution:**
```bash
# Check database container is running
docker compose ps postgres

# Check database logs
docker compose logs postgres

# Verify network connectivity
docker compose exec app-container ping postgres

# Check database is ready
docker compose exec postgres pg_isready -U postgres

# Add health check to docker-compose.yml
services:
  postgres:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

# Wait for database in application
depends_on:
  postgres:
    condition: service_healthy
```

### Issue: Volume Permission Errors
**Symptoms:**
- `Permission denied` when accessing volumes
- Files owned by root in containers
- Cannot write to mounted volumes

**Solution:**
```bash
# Check volume ownership
docker compose exec container-name ls -la /path/to/volume

# Fix permissions on host
sudo chown -R $USER:$USER ./volumes/

# Use user directive in Dockerfile
USER app:app

# Or set permissions in entrypoint script
#!/bin/bash
chown -R app:app /app/media
exec "$@"
```

## 🌐 Nginx Configuration Errors

### Issue: Nginx Won't Start
**Symptoms:**
- `nginx: [emerg] bind() to 0.0.0.0:80 failed`
- Configuration test fails
- Nginx service fails to start

**Solution:**
```bash
# Test Nginx configuration
sudo nginx -t

# Check what's using port 80
sudo netstat -tulpn | grep :80
sudo lsof -i :80

# Kill process using port 80
sudo kill -9 $(sudo lsof -t -i:80)

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx

# Check Nginx status
sudo systemctl status nginx
```

### Issue: 502 Bad Gateway
**Symptoms:**
- Nginx returns 502 error
- Application is running but not accessible
- Upstream connection failures

**Solution:**
```bash
# Check application is running
curl http://localhost:8000

# Check Nginx upstream configuration
sudo nginx -T | grep upstream

# Verify proxy_pass directive
location / {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# Check application logs
tail -f /path/to/app/logs/gunicorn.log

# Increase timeout in Nginx
proxy_connect_timeout 60s;
proxy_send_timeout 60s;
proxy_read_timeout 60s;

# Restart both services
sudo systemctl restart nginx
sudo systemctl restart gunicorn
```

## 🔒 SSL Certificate Problems

### Issue: Certificate Expired
**Symptoms:**
- Browser shows "Your connection is not private"
- `SSL certificate problem: certificate has expired`
- HTTPS not working

**Solution:**
```bash
# Check certificate expiration
openssl x509 -in /path/to/cert.pem -noout -dates

# Renew Let's Encrypt certificate
sudo certbot renew

# Force renewal
sudo certbot renew --force-renewal

# Test renewal
sudo certbot renew --dry-run

# Reload Nginx after renewal
sudo systemctl reload nginx

# Set up auto-renewal cron job
sudo crontab -e
0 0 * * * certbot renew --quiet && systemctl reload nginx
```

### Issue: Certificate Chain Incomplete
**Symptoms:**
- Some browsers show certificate errors
- SSL Labs test shows chain issues
- Mobile devices can't connect

**Solution:**
```bash
# Check certificate chain
openssl s_client -connect domain.com:443 -showcerts

# Use fullchain certificate
ssl_certificate /etc/letsencrypt/live/domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/domain.com/privkey.pem;

# Verify chain is complete
openssl verify -CAfile /etc/ssl/certs/ca-certificates.crt \
    /etc/letsencrypt/live/domain.com/fullchain.pem
```

## 🔧 Environment Variable Issues

### Issue: Environment Variables Not Loading
**Symptoms:**
- Settings use default values
- `KeyError` for environment variables
- Configuration not applied

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Verify .env is loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('DEBUG'))"

# Load .env in settings
# In settings/__init__.py
from dotenv import load_dotenv
load_dotenv()

# Check environment variables in container
docker compose exec container-name env

# Pass environment variables in docker-compose.yml
services:
  app:
    env_file:
      - .env
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
```

## 🐌 Slow Page Load Times

### Issue: Pages Load Slowly
**Symptoms:**
- Page load times > 3 seconds
- Database queries taking too long
- High server response time

**Solution:**
```bash
# Enable Django Debug Toolbar
pip install django-debug-toolbar

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    'debug_toolbar',
]

# Check for N+1 queries
# Use select_related() for foreign keys
queryset = Model.objects.select_related('foreign_key')

# Use prefetch_related() for many-to-many
queryset = Model.objects.prefetch_related('many_to_many')

# Add database indexes
class Meta:
    indexes = [
        models.Index(fields=['field_name']),
    ]

# Enable query caching
from django.core.cache import cache
result = cache.get('key')
if result is None:
    result = expensive_operation()
    cache.set('key', result, timeout=3600)

# Use database connection pooling
DATABASES = {
    'default': {
        'CONN_MAX_AGE': 600,
    }
}
```

## 🧪 Test Database Errors

### Issue: Test Database Creation Fails
**Symptoms:**
- `Got an error creating the test database`
- Permission denied creating database
- Tests fail to run

**Solution:**
```bash
# Grant database creation permissions
sudo -u postgres psql
ALTER USER postgres CREATEDB;

# Or create test database manually
CREATE DATABASE test_ctc_research;
GRANT ALL PRIVILEGES ON DATABASE test_ctc_research TO postgres;

# Use --keepdb to reuse test database
pytest --reuse-db

# Reset test database
pytest --create-db

# Check test database settings
DATABASES = {
    'default': {
        'TEST': {
            'NAME': 'test_ctc_research',
        }
    }
}
```

## 🔍 Selenium Test Failures

### Issue: WebDriver Not Found
**Symptoms:**
- `selenium.common.exceptions.WebDriverException`
- `'chromedriver' executable needs to be in PATH`
- Browser doesn't launch

**Solution:**
```bash
# Install webdriver-manager
pip install webdriver-manager

# Use webdriver-manager in tests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Or install chromedriver manually
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# macOS
brew install chromedriver

# Add to PATH
export PATH=$PATH:/path/to/chromedriver
```

### Issue: Headless Browser Failures
**Symptoms:**
- Tests pass with visible browser but fail headless
- Element not found in headless mode
- Screenshots show blank pages

**Solution:**
```python
# Configure headless options properly
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(options=options)

# Increase wait times for headless
from selenium.webdriver.support.ui import WebDriverWait
wait = WebDriverWait(driver, 20)  # Increase from 10 to 20

# Take screenshots for debugging
driver.save_screenshot('debug.png')
```

## 📊 Memory Leaks

### Issue: Memory Usage Grows Over Time
**Symptoms:**
- Application memory usage increases continuously
- Out of memory errors after running for hours
- Container restarts due to memory limits

**Solution:**
```bash
# Monitor memory usage
docker stats

# Profile memory usage
pip install memory_profiler
python -m memory_profiler script.py

# Check for unclosed database connections
# Use connection pooling
DATABASES = {
    'default': {
        'CONN_MAX_AGE': 600,
    }
}

# Close connections explicitly
from django.db import connection
connection.close()

# Use context managers for file operations
with open('file.txt', 'r') as f:
    data = f.read()

# Clear caches periodically
from django.core.cache import cache
cache.clear()

# Set memory limits in Docker
services:
  app:
    mem_limit: 2g
    mem_reservation: 1g
```

## 🔥 High CPU Usage

### Issue: CPU Usage at 100%
**Symptoms:**
- Server becomes unresponsive
- Slow response times
- High load average

**Solution:**
```bash
# Identify CPU-intensive processes
top
htop

# Profile Python code
pip install py-spy
py-spy top --pid <process_id>

# Check for infinite loops
# Add logging to identify bottlenecks

# Optimize database queries
# Use database query profiling
python manage.py shell
from django.db import connection
from django.db import reset_queries
reset_queries()
# Run your code
print(connection.queries)

# Use caching for expensive operations
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def my_view(request):
    # Expensive operation
    pass

# Scale horizontally with multiple workers
# In docker-compose.yml
services:
  app:
    deploy:
      replicas: 4
```

## 📚 Additional Resources

### Documentation
- [Django Troubleshooting](https://docs.djangoproject.com/en/stable/faq/)
- [PostgreSQL Common Errors](https://www.postgresql.org/docs/current/errcodes-appendix.html)
- [Docker Troubleshooting](https://docs.docker.com/config/daemon/)
- [Nginx Troubleshooting](https://nginx.org/en/docs/debugging_log.html)

### Tools
- [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/)
- [Sentry Error Tracking](https://sentry.io/)
- [New Relic APM](https://newrelic.com/)
- [Datadog Monitoring](https://www.datadoghq.com/)

### Community Support
- [Stack Overflow](https://stackoverflow.com/questions/tagged/django)
- [Django Forum](https://forum.djangoproject.com/)
- [Reddit r/django](https://www.reddit.com/r/django/)
- [Django Discord](https://discord.gg/xcRH6mN4fa)

---

*This troubleshooting guide is continuously updated with new issues and solutions. If you encounter an issue not covered here, please contribute by documenting the problem and solution.*

*Last updated: 2024-12-19 | Version: 2.0.0*
