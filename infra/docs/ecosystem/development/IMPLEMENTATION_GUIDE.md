# Implementation Guide: Package Reorganization & Enhancement

**Version:** 1.0
**Status:** Ready for Implementation
**Last Updated:** April 2026

---

## Quick Start

This guide provides step-by-step instructions for implementing the Unified Package Reorganization Specification.

### Prerequisites

- Git knowledge
- Python 3.10+
- Poetry or pip
- Understanding of Django architecture
- Access to venv/libs repository

### Tools Required

```bash
# Install development tools
pip install pytest pytest-cov black flake8 mypy isort
pip install poetry  # For package management
```

---

## Phase 1: Foundation Layer Consolidation (Weeks 1-2)

### Step 1.1: Audit Current Code

**Objective:** Identify all foundation code in django-rseal

```bash
# List all files in django-rseal
find venv/libs/django-rseal/src/django_rseal -type f -name "*.py" | sort

# Identify foundation modules
grep -r "class BaseModel" venv/libs/django-rseal/
grep -r "class.*Mixin" venv/libs/django-rseal/
grep -r "def.*route" venv/libs/django-rseal/
```

**Foundation Modules to Move:**
- `models/` - All base models and mixins
- `routes/` - URL routing utilities
- `forms/` - Form base classes
- `middleware/` - Request/response processing
- `signals/` - Django signals handlers
- `decorators/` - Function/method decorators
- `validators/` - Field validators
- `admin/` - Admin base classes

### Step 1.2: Create django-osoul Structure

```bash
# Create directory structure
mkdir -p venv/libs/django-osoul/src/django_osoul/{models,routes,forms,middleware,signals,decorators,validators,admin,utils,exceptions,tests}

# Create __init__.py files
touch venv/libs/django-osoul/src/django_osoul/__init__.py
touch venv/libs/django-osoul/src/django_osoul/models/__init__.py
touch venv/libs/django-osoul/src/django_osoul/routes/__init__.py
# ... repeat for all directories
```

### Step 1.3: Move Files with Import Updates

**Example: Moving models**

```bash
# Copy files
cp venv/libs/django-rseal/src/django_rseal/models/*.py \
   venv/libs/django-osoul/src/django_osoul/models/

# Update imports in moved files
# OLD: from django_rseal.utils import helper
# NEW: from django_osoul.utils import helper
```

**Script to Update Imports:**

```python
#!/usr/bin/env python3
import os
import re
from pathlib import Path

def update_imports(file_path, old_module, new_module):
    """Update imports in a file."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Update imports
    patterns = [
        (f'from {old_module}', f'from {new_module}'),
        (f'import {old_module}', f'import {new_module}'),
    ]

    for old, new in patterns:
        content = content.replace(old, new)

    with open(file_path, 'w') as f:
        f.write(content)

# Usage
for root, dirs, files in os.walk('venv/libs/django-osoul/src/django_osoul'):
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            update_imports(file_path, 'django_rseal', 'django_osoul')
```

### Step 1.4: Create Deprecation Shims

**File: `venv/libs/django-rseal/src/django_rseal/compat/__init__.py`**

```python
"""
Backward compatibility layer for moved modules.

This module provides deprecation shims for code that has been moved to
django-osoul. These imports will be removed in django-rseal 3.0.0.
"""

import warnings

def _deprecation_warning(old_path, new_path):
    """Generate a deprecation warning."""
    warnings.warn(
        f"Importing from {old_path} is deprecated. "
        f"Use {new_path} instead. "
        f"This will be removed in django-rseal 3.0.0.",
        DeprecationWarning,
        stacklevel=3
    )

# Models
from django_osoul.models import (
    BaseModel,
    TimestampedModel,
    UUIDModel,
    SluggedModel,
    PublishableModel,
)

__all__ = [
    'BaseModel',
    'TimestampedModel',
    'UUIDModel',
    'SluggedModel',
    'PublishableModel',
]
```

**File: `venv/libs/django-rseal/src/django_rseal/models/__init__.py`**

```python
"""
Deprecated: Use django_osoul.models instead.

This module is kept for backward compatibility only.
All imports have been moved to django-osoul.
"""

import warnings
from django_osoul.models import *

warnings.warn(
    "Importing from django_rseal.models is deprecated. "
    "Use django_osoul.models instead. "
    "This will be removed in django-rseal 3.0.0.",
    DeprecationWarning,
    stacklevel=2
)
```

### Step 1.5: Update Internal Imports

**Update all imports in django-rseal:**

```bash
# Find all imports of moved modules
grep -r "from django_rseal.models import" venv/libs/django-rseal/
grep -r "from django_rseal.routes import" venv/libs/django-rseal/
grep -r "from django_rseal.forms import" venv/libs/django-rseal/

# Update to use django_osoul
sed -i 's/from django_rseal\.models/from django_osoul.models/g' \
    venv/libs/django-rseal/src/django_rseal/**/*.py
```

### Step 1.6: Run Tests

```bash
# Run django-osoul tests
cd venv/libs/django-osoul
pytest tests/ -v --cov=src/django_osoul

# Run django-rseal tests
cd venv/libs/django-rseal
pytest tests/ -v --cov=src/django_rseal

# Run integration tests
cd venv/libs
pytest tests/integration/ -v
```

### Step 1.7: Verify No Circular Imports

```python
#!/usr/bin/env python3
"""Check for circular imports."""

import sys
import importlib

def check_circular_imports():
    """Check for circular imports."""
    modules = [
        'django_osoul',
        'django_rseal',
        'django_grep',
        'nawaai',
    ]

    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module} imported successfully")
        except ImportError as e:
            print(f"✗ {module} import failed: {e}")
            return False

    return True

if __name__ == '__main__':
    if check_circular_imports():
        print("\n✓ No circular imports detected")
        sys.exit(0)
    else:
        print("\n✗ Circular imports detected")
        sys.exit(1)
```

---

## Phase 2: AI/MCP Extraction (Weeks 3-4)

### Step 2.1: Audit AI Code

```bash
# Find all AI-related code
find venv/libs/django-rseal -name "*ai*" -o -name "*llm*" -o -name "*mcp*"
grep -r "from openai import" venv/libs/django-rseal/
grep -r "from anthropic import" venv/libs/django-rseal/
```

### Step 2.2: Create nawaai Structure

```bash
# Create directory structure
mkdir -p venv/libs/nawaai/src/nawaai/{ai,mcp,tools,utils}

# Create __init__.py files
touch venv/libs/nawaai/src/nawaai/__init__.py
touch venv/libs/nawaai/src/nawaai/ai/__init__.py
touch venv/libs/nawaai/src/nawaai/mcp/__init__.py
touch venv/libs/nawaai/src/nawaai/tools/__init__.py
touch venv/libs/nawaai/src/nawaai/utils/__init__.py
```

### Step 2.3: Move AI Code

```bash
# Copy AI files
cp venv/libs/django-rseal/src/django_rseal/ai/*.py \
   venv/libs/nawaai/src/nawaai/ai/

# Copy MCP files
cp venv/libs/django-rseal/src/django_rseal/mcp/*.py \
   venv/libs/nawaai/src/nawaai/mcp/

# Remove Django imports from moved files
# OLD: from django.conf import settings
# NEW: import os; settings = os.environ
```

### Step 2.4: Remove Django Imports

**Script to Remove Django Imports:**

```python
#!/usr/bin/env python3
"""Remove Django imports from nawaai."""

import os
import re
from pathlib import Path

def remove_django_imports(file_path):
    """Remove Django imports from a file."""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Filter out Django imports
    filtered_lines = [
        line for line in lines
        if not line.strip().startswith(('from django', 'import django'))
    ]

    with open(file_path, 'w') as f:
        f.writelines(filtered_lines)

# Usage
for root, dirs, files in os.walk('venv/libs/nawaai/src/nawaai'):
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            remove_django_imports(file_path)
```

### Step 2.5: Create Deprecation Shims

**File: `venv/libs/django-rseal/src/django_rseal/ai/__init__.py`**

```python
"""
Deprecated: Use nawaai.ai instead.

This module is kept for backward compatibility only.
All AI code has been moved to nawaai.
"""

import warnings
from nawaai.ai import *

warnings.warn(
    "Importing from django_rseal.ai is deprecated. "
    "Use nawaai.ai instead. "
    "This will be removed in django-rseal 3.0.0.",
    DeprecationWarning,
    stacklevel=2
)
```

### Step 2.6: Update Imports

```bash
# Update imports in django-rseal
sed -i 's/from django_rseal\.ai/from nawaai.ai/g' \
    venv/libs/django-rseal/src/django_rseal/**/*.py

# Update imports in projects
sed -i 's/from django_rseal\.ai/from nawaai.ai/g' \
    ctc-research.com/**/*.py
sed -i 's/from django_rseal\.ai/from nawaai.ai/g' \
    structa.cloud/**/*.py
```

### Step 2.7: Run Tests

```bash
# Run nawaai tests
cd venv/libs/nawaai
pytest tests/ -v --cov=src/nawaai

# Verify no Django imports
grep -r "from django" venv/libs/nawaai/src/nawaai/ && echo "ERROR: Django imports found" || echo "✓ No Django imports"

# Run django-rseal tests
cd venv/libs/django-rseal
pytest tests/ -v --cov=src/django_rseal
```

---

## Phase 3: Testing Framework Consolidation (Weeks 5-6)

### Step 3.1: Audit Testing Code

```bash
# Find all testing code
find venv/libs/django-rseal -name "*test*" -o -name "*factory*" -o -name "*fixture*"
find venv/libs/django-seed -name "*seed*" -o -name "*factory*"
```

### Step 3.2: Create django-grep Structure

```bash
# Create directory structure
mkdir -p venv/libs/django-grep/src/django_grep/{factories,assertions,fixtures,helpers,mocks,runners}

# Create __init__.py files
touch venv/libs/django-grep/src/django_grep/__init__.py
touch venv/libs/django-grep/src/django_grep/factories/__init__.py
# ... repeat for all directories
```

### Step 3.3: Move Testing Code

```bash
# Copy factory files
cp venv/libs/django-rseal/src/django_rseal/seeder/*.py \
   venv/libs/django-grep/src/django_grep/factories/

# Copy fixture files
cp venv/libs/django-seed/src/django_seed/seeding/*.py \
   venv/libs/django-grep/src/django_grep/fixtures/

# Copy test utilities
cp venv/libs/django-rseal/src/django_rseal/tests/*.py \
   venv/libs/django-grep/src/django_grep/helpers/
```

### Step 3.4: Create Base Test Classes

**File: `venv/libs/django-grep/src/django_grep/base.py`**

```python
"""Base test classes for Django projects."""

from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseTestCase(TestCase):
    """Base test case with common setup."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.user = self.create_user()

    def create_user(self, **kwargs):
        """Create a test user."""
        defaults = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)

    def login(self, user=None):
        """Log in a user."""
        user = user or self.user
        self.client.login(username=user.username, password='testpass123')

    def logout(self):
        """Log out the current user."""
        self.client.logout()

class BaseAPITestCase(TestCase):
    """Base test case for API tests."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.user = self.create_user()

    def create_user(self, **kwargs):
        """Create a test user."""
        defaults = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)

    def authenticate(self, user=None):
        """Authenticate a user for API requests."""
        user = user or self.user
        self.client.force_authenticate(user=user)

    def unauthenticate(self):
        """Remove authentication."""
        self.client.force_authenticate(user=None)
```

### Step 3.5: Create Factory Definitions

**File: `venv/libs/django-grep/src/django_grep/factories/__init__.py`**

```python
"""Factory definitions for testing."""

import factory
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Set password after creation."""
        if not create:
            return

        if extracted:
            obj.set_password(extracted)
        else:
            obj.set_password('testpass123')
        obj.save()
```

### Step 3.6: Create Assertion Helpers

**File: `venv/libs/django-grep/src/django_grep/assertions.py`**

```python
"""Custom assertion helpers for testing."""

from django.test import TestCase
from django.core.mail import outbox

def assert_model_created(model_class, **kwargs):
    """Assert that a model instance was created."""
    assert model_class.objects.filter(**kwargs).exists(), \
        f"{model_class.__name__} with {kwargs} was not created"

def assert_model_not_created(model_class, **kwargs):
    """Assert that a model instance was not created."""
    assert not model_class.objects.filter(**kwargs).exists(), \
        f"{model_class.__name__} with {kwargs} was created"

def assert_email_sent(subject=None, recipient=None):
    """Assert that an email was sent."""
    assert len(outbox) > 0, "No emails were sent"

    if subject:
        assert any(subject in email.subject for email in outbox), \
            f"Email with subject '{subject}' was not sent"

    if recipient:
        assert any(recipient in email.to for email in outbox), \
            f"Email to '{recipient}' was not sent"

def assert_status_code(response, expected_code):
    """Assert that response has expected status code."""
    assert response.status_code == expected_code, \
        f"Expected status {expected_code}, got {response.status_code}"
```

### Step 3.7: Run Tests

```bash
# Run django-grep tests
cd venv/libs/django-grep
pytest tests/ -v --cov=src/django_grep

# Run all tests
cd venv/libs
pytest tests/ -v --cov
```

---

## Phase 4: Deprecation Shims & Backward Compatibility (Weeks 7-8)

### Step 4.1: Create Migration Guide

**File: `MIGRATION_GUIDE.md`**

```markdown
# Migration Guide: django-rseal 2.0.0

This guide helps you migrate from django-rseal 1.x to 2.0.0.

## What Changed

In django-rseal 2.0.0, we reorganized the codebase to improve maintainability and reusability:

- Foundation code moved to `django-osoul`
- AI code moved to `nawaai`
- Testing utilities moved to `django-grep`

## Migration Steps

### 1. Update Imports

**Before (1.x):**
```python
from django_rseal.models import BaseModel
from django_rseal.ai import LLMClient
from django_rseal.seeder import Seeder
```

**After (2.0.0):**
```python
from django_osoul.models import BaseModel
from nawaai.ai import LLMClient
from django_grep.factories import Seeder
```

### 2. Update Dependencies

Update your `pyproject.toml`:

```toml
[dependencies]
django-osoul = "^2.0.0"
django-rseal = "^2.0.0"
django-grep = "^2.0.0"
nawaai = "^1.0.0"
```

### 3. Run Tests

```bash
pytest tests/ -v
```

## Deprecation Timeline

- **2.0.0 (Current):** Old imports work with deprecation warnings
- **2.1.0 (Q3 2026):** Deprecation warnings become errors
- **3.0.0 (Q4 2026):** Old imports removed

## Need Help?

- Check the [API Documentation](https://docs.example.com)
- Open an [Issue](https://github.com/example/django-rseal/issues)
- Join our [Community](https://community.example.com)
```

### Step 4.2: Add Deprecation Warnings

**Update all deprecation shims to include warnings:**

```python
import warnings
import sys

def deprecated(old_path, new_path, version='3.0.0'):
    """Decorator to mark functions as deprecated."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{old_path} is deprecated. Use {new_path} instead. "
                f"This will be removed in {version}.",
                DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### Step 4.3: Update Documentation

**Update README files:**

```markdown
# django-rseal 2.0.0

## Migration from 1.x

If you're upgrading from django-rseal 1.x, please see the [Migration Guide](../deployment/MIGRATION_GUIDE.md).

## New Package Structure

- **django-osoul:** Foundation layer (models, forms, middleware, etc.)
- **django-rseal:** Automation layer (email, tasks, workflows, etc.)
- **django-grep:** Testing framework (factories, assertions, fixtures, etc.)
- **nawaai:** AI/MCP toolkit (standalone, zero Django)

## Installation

```bash
pip install django-osoul django-rseal django-grep nawaai
```

## Quick Start

```python
from django_osoul.models import BaseModel
from django_rseal.email import send_email
from django_grep.factories import UserFactory
from nawaai.ai import LLMClient
```
```

### Step 4.4: Run Full Test Suite

```bash
# Run all tests
cd venv/libs
pytest tests/ -v --cov

# Check for deprecation warnings
pytest tests/ -v -W error::DeprecationWarning

# Generate coverage report
pytest tests/ --cov --cov-report=html
```

---

## Phase 5: Documentation & Release (Weeks 9-10)

### Step 5.1: Generate API Documentation

```bash
# Install sphinx
pip install sphinx sphinx-rtd-theme

# Create documentation
cd docs
sphinx-quickstart -q -p "django-osoul" -a "Your Name" -v "2.0.0"

# Generate API docs
sphinx-apidoc -o source ../venv/libs/django-osoul/src/django_osoul

# Build HTML docs
make html
```

### Step 5.2: Create Changelog

**File: `CHANGELOG.md`**

```markdown
# Changelog

## [2.0.0] - 2026-04-14

### Added
- New `django-osoul` package for foundation layer
- New `django-grep` package for testing framework
- New `nawaai` package for AI/MCP toolkit
- Comprehensive API documentation
- Migration guide for upgrading from 1.x

### Changed
- Reorganized package structure
- Moved foundation code to `django-osoul`
- Moved AI code to `nawaai`
- Moved testing utilities to `django-grep`

### Deprecated
- Importing from `django_rseal.models` (use `django_osoul.models`)
- Importing from `django_rseal.ai` (use `nawaai.ai`)
- Importing from `django_rseal.seeder` (use `django_grep.factories`)

### Removed
- Nothing in this release (backward compatibility maintained)

### Fixed
- Circular import issues
- Import path inconsistencies

### Security
- No security changes in this release

## [1.9.0] - 2026-03-01

### Added
- Support for Django 5.0
- New email template system

### Fixed
- Bug fixes and improvements
```

### Step 5.3: Update Version Numbers

**File: `venv/libs/django-osoul/pyproject.toml`**

```toml
[project]
name = "django-osoul"
version = "2.0.0"
description = "Foundation layer for Django projects"
```

**File: `venv/libs/django-rseal/pyproject.toml`**

```toml
[project]
name = "django-rseal"
version = "2.0.0"
description = "Automation layer for Django projects"
dependencies = [
    "django-osoul>=2.0.0",
    "nawaai>=1.0.0",
]
```

**File: `venv/libs/django-grep/pyproject.toml`**

```toml
[project]
name = "django-grep"
version = "2.0.0"
description = "Testing framework for Django projects"
dependencies = [
    "django-osoul>=2.0.0",
    "django-rseal>=2.0.0",
]
```

**File: `venv/libs/nawaai/pyproject.toml`**

```toml
[project]
name = "nawaai"
version = "1.0.0"
description = "AI/MCP toolkit"
```

### Step 5.4: Tag Release

```bash
# Create git tags
git tag -a v2.0.0 -m "Release version 2.0.0"
git tag -a django-osoul-2.0.0 -m "django-osoul 2.0.0"
git tag -a django-rseal-2.0.0 -m "django-rseal 2.0.0"
git tag -a django-grep-2.0.0 -m "django-grep 2.0.0"
git tag -a nawaai-1.0.0 -m "nawaai 1.0.0"

# Push tags
git push origin --tags
```

### Step 5.5: Publish to PyPI

```bash
# Build packages
cd venv/libs/django-osoul
poetry build

cd ../django-rseal
poetry build

cd ../django-grep
poetry build

cd ../nawaai
poetry build

# Publish to PyPI
poetry publish
```

---

## Verification Checklist

### Code Quality
- [ ] All tests passing
- [ ] Test coverage ≥ 80%
- [ ] No linting errors
- [ ] No type errors
- [ ] No circular imports

### Architecture
- [ ] Foundation layer (django-osoul) has zero automation imports
- [ ] Automation layer (django-rseal) depends only on foundation
- [ ] AI layer (nawaai) has zero Django imports
- [ ] Testing layer (django-grep) depends on foundation + automation

### Documentation
- [ ] API documentation complete
- [ ] Migration guide provided
- [ ] Changelog updated
- [ ] README files updated
- [ ] Examples provided

### Backward Compatibility
- [ ] Deprecation shims in place
- [ ] Deprecation warnings working
- [ ] Old imports still work
- [ ] Migration path clear

### Release
- [ ] Version numbers updated
- [ ] Git tags created
- [ ] Packages published to PyPI
- [ ] Release notes published

---

## Troubleshooting

### Issue: Circular Import Error

**Solution:**
1. Identify the circular import
2. Move shared code to a separate module
3. Import from the shared module in both places

### Issue: Test Failures

**Solution:**
1. Run tests with verbose output: `pytest -vv`
2. Check for import errors
3. Verify all dependencies are installed
4. Check for database migration issues

### Issue: Deprecation Warnings

**Solution:**
1. Update imports to use new paths
2. Check migration guide for correct imports
3. Run tests with `-W error::DeprecationWarning` to find all issues

### Issue: Import Not Found

**Solution:**
1. Verify package is installed
2. Check import path is correct
3. Verify module exists in package
4. Check for typos in import statement

---

## Next Steps

After completing all phases:

1. **Monitor for Issues:** Watch for bug reports and issues
2. **Gather Feedback:** Collect user feedback on new structure
3. **Plan Enhancements:** Plan next features based on feedback
4. **Maintain Documentation:** Keep documentation up-to-date
5. **Plan v2.1.0:** Plan next release with deprecation warnings as errors

---

## Support

For questions or issues:

- Check the [API Documentation](https://docs.example.com)
- Open an [Issue](https://github.com/example/django-rseal/issues)
- Join our [Community](https://community.example.com)
- Email support@example.com

---

**Document Status:** ✅ Complete
**Last Updated:** April 14, 2026
**Next Review:** After Phase 1 completion (Week 2)
