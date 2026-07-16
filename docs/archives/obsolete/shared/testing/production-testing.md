# Production Testing Guide

## 🎯 Overview

This guide covers comprehensive testing procedures for the production environment using PostgreSQL database and production-grade configurations.

## 🔧 Prerequisites

### Infrastructure Requirements
- Docker and Docker Compose installed
- PostgreSQL container running
- Redis container running
- Production environment variables configured

### Database Setup
```bash
# Start infrastructure services
docker compose up -d postgres redis

# Verify databases exist
docker exec postgres psql -U postgres -c "\l"
```

## 🚀 Production Test Execution

### 1. Automated Production Testing

Run the comprehensive production test suite:

```bash
cd ctc-research.com
python scripts/test_production.py
```

### 2. Manual Production Testing

#### Environment Setup
```bash
# Copy production environment
cp .env.production .env

# Verify environment variables
grep -E "^(SERVER_ENV|DB_NAME|DEBUG)" .env
```

#### Database Tests
```bash
# Test database connection
python manage.py dbshell --settings=configs.settings

# Run migrations
python manage.py migrate --settings=configs.settings

# Check migration status
python manage.py showmigrations --settings=configs.settings
```

#### Django System Tests
```bash
# System check
python manage.py check --settings=configs.settings

# Collect static files
python manage.py collectstatic --noinput --settings=configs.settings

# Test Django shell
python manage.py shell --settings=configs.settings
```

## 📊 Test Categories

### 1. Database Connectivity Tests

**Purpose**: Verify PostgreSQL connection and basic operations

```python
# Test script example
from django.db import connection

def test_database_connection():
    with connection.cursor() as cursor:
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"PostgreSQL Version: {version[0]}")

        cursor.execute("SELECT current_database()")
        db_name = cursor.fetchone()
        print(f"Connected to: {db_name[0]}")
```

**Expected Results**:
- ✅ Connection established successfully
- ✅ PostgreSQL version displayed
- ✅ Connected to `db_ctc` database

### 2. Migration Tests

**Purpose**: Ensure all Django migrations are applied correctly

```bash
# Check migration status
python manage.py showmigrations --settings=configs.settings

# Apply migrations
python manage.py migrate --settings=configs.settings --run-syncdb
```

**Expected Results**:
- ✅ All migrations marked as applied `[X]`
- ✅ No unapplied migrations
- ✅ Database schema matches Django models

### 3. Model Functionality Tests

**Purpose**: Verify Django ORM operations work correctly

```python
def test_model_operations():
    from django.contrib.auth.models import User

    # Test user creation
    user = User.objects.create_user(
        username='test_prod_user',
        email='test@production.com',
        password='secure_password'
    )

    # Test user retrieval
    retrieved_user = User.objects.get(username='test_prod_user')
    assert retrieved_user.email == 'test@production.com'

    # Cleanup
    user.delete()
```

**Expected Results**:
- ✅ User created successfully
- ✅ User retrieved correctly
- ✅ User deleted successfully

### 4. Admin Interface Tests

**Purpose**: Verify Django admin functionality

```python
def test_admin_functionality():
    from django.contrib import admin
    from django.contrib.auth.models import User

    # Check admin registration
    assert User in admin.site._registry

    # Test admin model count
    registered_models = len(admin.site._registry)
    print(f"Registered admin models: {registered_models}")
```

**Expected Results**:
- ✅ Core models registered in admin
- ✅ Admin interface accessible
- ✅ Model list views functional

### 5. Wagtail CMS Tests

**Purpose**: Verify Wagtail CMS functionality

```python
def test_wagtail_functionality():
    from wagtail.models import Site, Page

    # Test Wagtail models
    site_count = Site.objects.count()
    page_count = Page.objects.count()

    print(f"Wagtail sites: {site_count}")
    print(f"Wagtail pages: {page_count}")

    # Test default site
    default_site = Site.objects.filter(is_default_site=True).first()
    assert default_site is not None
```

**Expected Results**:
- ✅ Wagtail sites exist
- ✅ Default site configured
- ✅ Page tree structure intact

### 6. Static Files Tests

**Purpose**: Verify static file collection and serving

```bash
# Collect static files
python manage.py collectstatic --noinput --settings=configs.settings

# Verify static files directory
ls -la assets/staticfiles/
```

**Expected Results**:
- ✅ Static files collected successfully
- ✅ CSS and JS files present
- ✅ Admin static files included

### 7. Cache Tests

**Purpose**: Verify caching functionality

```python
def test_cache_functionality():
    from django.core.cache import cache

    # Test cache set/get
    cache.set('test_key', 'test_value', 300)
    cached_value = cache.get('test_key')

    assert cached_value == 'test_value'

    # Cleanup
    cache.delete('test_key')
```

**Expected Results**:
- ✅ Cache set operation successful
- ✅ Cache get operation returns correct value
- ✅ Cache delete operation successful

## 🔍 Health Checks

### Database Health Check
```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('db_ctc')) as database_size;

-- Check table count
SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';

-- Check migration status
SELECT count(*) FROM django_migrations;
```

### Application Health Check
```python
def health_check():
    from django.db import connection
    from django.contrib.auth.models import User

    # Database connectivity
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")

    # Model operations
    user_count = User.objects.count()

    return {
        'database': 'healthy',
        'models': 'healthy',
        'user_count': user_count
    }
```

## 📈 Performance Tests

### Database Performance
```python
import time
from django.contrib.auth.models import User

def test_database_performance():
    start_time = time.time()

    # Test query performance
    users = list(User.objects.all()[:100])

    end_time = time.time()
    query_time = end_time - start_time

    print(f"Query time: {query_time:.3f} seconds")
    assert query_time < 1.0  # Should complete within 1 second
```

### Memory Usage Tests
```python
import psutil
import os

def test_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    print(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")

    # Memory should be reasonable for production
    assert memory_info.rss < 500 * 1024 * 1024  # Less than 500MB
```

## 🚨 Error Monitoring

### Log Analysis
```bash
# Check Django logs for errors
grep -i error logs/django.log | tail -20

# Check PostgreSQL logs
docker logs postgres | grep -i error | tail -20

# Check application logs
docker compose logs website | grep -i error | tail -20
```

### Common Error Patterns
1. **Database Connection Errors**
   - Check PostgreSQL service status
   - Verify connection parameters
   - Check network connectivity

2. **Migration Errors**
   - Check for conflicting migrations
   - Verify database permissions
   - Check for data integrity issues

3. **Static File Errors**
   - Verify static file configuration
   - Check file permissions
   - Ensure storage backend is accessible

## 📋 Test Checklist

### Pre-Production Deployment
- [ ] All tests pass in production environment
- [ ] Database migrations applied successfully
- [ ] Static files collected without errors
- [ ] Admin interface accessible
- [ ] Wagtail CMS functional
- [ ] Cache system working
- [ ] No critical errors in logs
- [ ] Performance benchmarks met

### Post-Production Deployment
- [ ] Health check endpoints responding
- [ ] Database queries performing well
- [ ] Static files serving correctly
- [ ] User authentication working
- [ ] Admin interface accessible
- [ ] Email functionality working
- [ ] Background tasks processing
- [ ] Monitoring alerts configured

## 🔧 Troubleshooting

### Database Issues
```bash
# Check database status
docker exec postgres pg_isready -U postgres

# Check database connections
docker exec postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Check database size
docker exec postgres psql -U postgres -d db_ctc -c "SELECT pg_size_pretty(pg_database_size('db_ctc'));"
```

### Application Issues
```bash
# Check Django configuration
python manage.py check --settings=configs.settings --deploy

# Test database connection
python manage.py dbshell --settings=configs.settings

# Check installed apps
python manage.py shell -c "from django.conf import settings; print(settings.INSTALLED_APPS)"
```

## 📊 Test Reports

### Automated Report Generation
```python
def generate_test_report():
    report = {
        'timestamp': datetime.now().isoformat(),
        'environment': 'production',
        'database': 'db_ctc',
        'tests_passed': 0,
        'tests_failed': 0,
        'test_results': []
    }

    # Add test results
    # Save report to file
    with open('reports/production_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
```

### Report Analysis
- Test success rate should be ≥ 95%
- Database performance within acceptable limits
- No critical errors in application logs
- All core functionality verified

---

**Next Steps**: After successful production testing, proceed to [Docker Environment Testing](docker-testing.md)
