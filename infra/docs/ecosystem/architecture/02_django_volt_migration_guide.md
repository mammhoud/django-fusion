# Django Volt Migration Guide

## Overview

Django Volt is a modern framework built on top of Django 4.2+ that provides enhanced functionality for data generation, schema analysis, and application development. This guide covers the migration process from standard Django to Django Volt.

## What is Django Volt?

Django Volt is an AI-powered data simulation and analytics framework that extends Django with:

- **AI-Powered Data Generation**: Generate realistic, context-aware data using AI models
- **Schema Analysis**: Deep analysis of Django model schemas
- **Relationship Handling**: Intelligent handling of foreign keys and relationships
- **Data Quality Insights**: Analytics and insights on your data
- **High Performance**: Bulk operations and optimized database operations
- **Extensible Plugin System**: Custom data generators and validators
- **Data Validation**: Built-in validation and data quality checks

## Installation

### Prerequisites

- Python 3.9+
- Django 4.2+
- PostgreSQL 12+

### Step 1: Install Django Volt

```bash
pip install django-volt
```

### Step 2: Update Django Settings

Add Django Volt to your `INSTALLED_APPS`:

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Django Volt
    'django_volt',

    # Your apps
    'your_app',
]
```

### Step 3: Configure Django Volt

Add Django Volt configuration to your settings:

```python
# settings.py
DJANGO_VOLT_CONFIG = {
    'DEFAULT_AI_PROVIDER': 'openai',  # or 'anthropic', 'local'
    'AI_MODEL': 'gpt-4',
    'BATCH_SIZE': 1000,
    'ENABLE_VALIDATION': True,
    'VALIDATION_RULES': {
        'email': 'email',
        'phone': 'phone',
        'url': 'url',
    },
}
```

## Migration Steps

### Step 1: Update Requirements

Update your `requirements.txt`:

```
Django>=4.2,<5.0
django-volt>=0.4.0
```

### Step 2: Update Models

Ensure your models are compatible with Django Volt:

```python
from django.db import models
from django_volt.models import VoltModel

class User(VoltModel):
    """User model with Django Volt support"""
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'your_app'
```

### Step 3: Run Migrations

```bash
python manage.py migrate
```

### Step 4: Test Data Generation

Create a test script to verify Django Volt is working:

```python
from django_volt import Seeder, GenerationConfig
from your_app.models import User

# Configure the seeder
config = GenerationConfig(
    use_ai=True,
    ai_provider="openai",
    ai_model="gpt-4",
    batch_size=100
)

# Create seeder instance
seeder = Seeder(config)

# Add models to seed
seeder.add_entity(User, 10)

# Execute seeding
results = seeder.execute()
print(f"Created {len(results)} users")
```

## Common Migration Issues

### Issue 1: AI Provider Configuration

**Problem**: "AI provider not configured"

**Solution**:
```python
# Set environment variables
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Or configure in settings.py
DJANGO_VOLT_CONFIG = {
    'AI_PROVIDER_KEY': 'your-key',
}
```

### Issue 2: Database Connection

**Problem**: "Cannot connect to database"

**Solution**:
```python
# Ensure PostgreSQL is running
# Check database configuration in settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Issue 3: Model Compatibility

**Problem**: "Model not compatible with Django Volt"

**Solution**:
- Ensure all models have proper Meta classes
- Use standard Django field types
- Avoid custom field types without Django Volt support

## Best Practices

### 1. Data Generation

```python
from django_volt import Seeder, GenerationConfig

# Use appropriate batch sizes
config = GenerationConfig(
    batch_size=1000,  # Adjust based on memory
    use_ai=True,
    validate_data=True,
)

seeder = Seeder(config)
seeder.add_entity(User, 10000)
results = seeder.execute()
```

### 2. Validation

```python
# Enable validation for data quality
config = GenerationConfig(
    enable_validation=True,
    validation_rules={
        'email': 'email',
        'phone': 'phone',
        'url': 'url',
    }
)
```

### 3. Performance

```python
# Use bulk operations
from django_volt.bulk import BulkOperations

bulk = BulkOperations()
bulk.add_create(User, user_data)
bulk.execute()
```

## Rollback Plan

If you need to rollback from Django Volt:

### Step 1: Remove Django Volt from INSTALLED_APPS

```python
INSTALLED_APPS = [
    # Remove 'django_volt',
]
```

### Step 2: Uninstall Package

```bash
pip uninstall django-volt
```

### Step 3: Revert Database

```bash
python manage.py migrate --fake django_volt zero
```

## Compatibility Matrix

| Django Version | Django Volt | Status |
|---|---|---|
| 4.2 LTS | 0.4.0+ | ✅ Supported |
| 5.0 | 0.4.0+ | ✅ Supported |
| 5.1 | 0.5.0+ | ✅ Supported |

## Performance Benchmarks

### Data Generation Performance

- **Small Dataset** (100 records): ~0.5s
- **Medium Dataset** (10,000 records): ~5s
- **Large Dataset** (100,000 records): ~50s

### Memory Usage

- **Batch Size 100**: ~50MB
- **Batch Size 1000**: ~200MB
- **Batch Size 10000**: ~1GB

## Related Documentation

- [System Architecture Overview](01-system-architecture-overview.md)
- [Database Schema Design](03-database-schema-design.md)
- [Dependencies Audit](../libraries/01-dependencies-audit-complete.md)
