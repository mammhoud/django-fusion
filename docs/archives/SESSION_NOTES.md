# Session Notes: CTC-Research Django Setup Issues & Solutions

## 🔴 Current Status
- **Container**: ctc-web is running but workers keep crashing
- **Root Cause**: Dependency chain failure: `crafts_ai` → `django_fusion` → `twilio`
- **Blocker**: Cannot install `twilio` due to OOM (Out of Memory) errors
- **Workaround**: Creating fake `django_fusion` module with dynamic attribute resolution

## Problem Analysis

### 1. **Dependency Chain Issue**
```
crafts_ai (installed in container)
  └─ depends on django_fusion
       └─ depends on twilio (SMS/Voice service)
            └─ Installation FAILS due to memory constraints
```

### 2. **Errors Encountered**
- `ModuleNotFoundError: No module named 'twilio'`
- `ModuleNotFoundError: No module named 'django_fusion.site.enums.env.Direction'`
- `ModuleNotFoundError: No module named 'django_fusion.managers'`
- `ModuleNotFoundError: No module named 'django_fusion.managers'; 'django_fusion' is not a package`
- `AttributeError: module 'django_fusion.site.enums.upload' has no attribute 'FileUploadStrategy'`

### 3. **Why We Can't Just Remove crafts_ai**
- Code directly imports: `from crafts_ai.models.default import DefaultBase`
- Models need to be registered in Django's app registry (INSTALLED_APPS)
- Removing from INSTALLED_APPS causes: `Model class crafts_ai.models.settings.email.EmailSettings doesn't declare an explicit app_label`

## Current Workaround

### Fake `django_fusion` Module Implementation
Located in: `/root/site/websites/ctc-research/settings.py`

**Approach**:
1. Create fake Python modules using `types.ModuleType`
2. Add dynamic `__getattr__` handlers to catch undefined attributes
3. Pre-populate known attributes (Environment, Runtime, Direction, FileUploadStorage, etc.)
4. Register all fake modules in `sys.modules` BEFORE importing configs.settings

**Modules Created**:
```
django_fusion/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── interaction/
│   │   └── call.py (has Client class for twilio)
│   └── [dynamic attributes]
├── site/
│   ├── __init__.py
│   └── enums/
│       ├── env.py (has Environment, Runtime, Module, Direction)
│       └── upload.py (has FileUploadStorage, FileUploadStrategy)
└── managers/
    └── [dynamic attributes]
```

## 🎯 Ideal Solutions (Ranked by Feasibility)

### **SOLUTION 1: Install twilio (Recommended if memory allows)**
**Status**: Not feasible currently due to OOM

**Steps**:
```bash
# Option A: Direct install in container
docker exec ctc-web pip install twilio --no-cache-dir

# Option B: Install in Dockerfile with memory swap
# Add before crafts_ai: RUN pip install --no-cache-dir twilio

# Option C: Use lightweight alternative
# Create slim twilio mock that only has Client class
```

**Pros**: Clean solution, no workarounds
**Cons**: Memory constraints, need to rebuild container

---

### **SOLUTION 2: Replace crafts_ai Entirely (Best long-term)**
**Status**: Requires architectural changes

**Steps**:
1. Remove crafts_ai dependency from:
   - `/root/site/websites/ctc-research/www/core/content/models/contact.py`
   - Any other imports from crafts_ai

2. Replace `DefaultBase` with:
   ```python
   from django.db import models
   
   class DefaultBase(models.Model):
       # Implement required fields/methods from crafts_ai.DefaultBase
       class Meta:
           abstract = True
   ```

3. Migrate all crafts_ai.GenericSetting models to Django's native approach

4. Create custom admin interfaces where needed

**Pros**: No dependencies, more control, better maintainability
**Cons**: Large refactoring, requires testing all pages

---

### **SOLUTION 3: Python Virtual Memory Swap (Quick fix)**
**Status**: May work if system has disk space

**Steps**:
```bash
# Inside container
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Then retry pip install
pip install twilio
```

**Pros**: No code changes, quick test
**Cons**: Performance impact, may crash system

---

### **SOLUTION 4: Lightweight Mock Package**
**Status**: Partially implemented

**Create** `/root/site/websites/fake_twilio_lightweight.py`:
```python
"""Minimal twilio mock for django_fusion"""

class Client:
    """Fake Twilio Client"""
    def __init__(self, *args, **kwargs):
        pass

# Create fake modules
import sys
import types

twilio = types.ModuleType('twilio')
twilio.rest = types.ModuleType('twilio.rest')
twilio.rest.Client = Client

sys.modules['twilio'] = twilio
sys.modules['twilio.rest'] = twilio.rest
```

Then install this BEFORE crafts_ai in requirements.

**Pros**: Lightweight, specific to our needs
**Cons**: Breaks if code actually tries to use Twilio features

---

## 🔧 Ongoing Maintenance Tasks

### Currently Missing Attributes to Add
- `django_fusion.managers.*` (various manager classes)
- `django_fusion.site.enums.env.Direction`
- Potentially more as crafts_ai loads additional models

### Pattern to Follow
When new `AttributeError` occurs:
```python
# In ctc-research/settings.py, add to appropriate module:

class FakeMissingAttribute:
    pass

django_fusion_env.MissingAttribute = FakeMissingAttribute
```

### Monitoring
Check this file regularly:
- `/app/logs/gunicorn-error.log` - shows which attributes are missing

### Command to Find New Missing Attributes
```bash
docker exec ctc-web grep "AttributeError\|ModuleNotFoundError" /app/logs/gunicorn-error.log | tail -20
```

---

## Files Modified in This Session

1. **`/root/site/websites/ctc-research/settings.py`**
   - Added fake django_fusion module hierarchy
   - Added DJANGO_SETTINGS_MODULE=ctc-research.settings (fixed import path)
   - Kept crafts_ai in INSTALLED_APPS (required for models)

2. **`/root/site/websites/ctc-research/.env`**
   - Updated DJANGO_SETTINGS_MODULE
   - Updated ALLOWED_HOSTS to include ctc-web:5070

3. **`/root/site/websites/.env`**
   - Updated ALLOWED_HOSTS

4. **`/root/site/websites/ctc-research/www/core/content/models/_compat.py`**
   - Created compatibility module for crafts_ai imports
   - Maps old import paths to correct locations

5. **`/root/site/websites/configs/base/apps.py`**
   - Fixed AppRegistry module resolution
   - Added crafts_ai to INSTALLED_APPS

---

## Testing Checklist

- [ ] Health endpoint responds: `curl http://ctc-web:5070/health/`
- [ ] Django admin loads: `http://ctc-research.com/admin/`
- [ ] Wagtail admin accessible
- [ ] Database migrations run
- [ ] Superuser created
- [ ] Home page created in Wagtail
- [ ] CSRF validation works
- [ ] Access from external domain works

---

## Next Steps (When Django Boots Successfully)

1. **Run Django migrations**:
   ```bash
   docker exec ctc-web python manage.py migrate
   ```

2. **Create superuser**:
   ```bash
   docker exec ctc-web python manage.py createsuperuser
   ```

3. **Setup Wagtail home page**:
   ```bash
   docker exec ctc-web python manage.py setup_wagtail_home
   ```

4. **Collect static files** (if needed):
   ```bash
   docker exec ctc-web python manage.py collectstatic --noinput
   ```

5. **Test CSRF** and external access

---

## Additional Websites to Check

- **LMS (lms-demo)**: Check if same crafts_ai/django_fusion issues exist
- **VResume (VResume)**: Check if same issues exist when enabled
- **structa-cloud**: Check if disabled correctly with profiles

---

## References

- **crafts_ai**: https://github.com/your-repo/crafts_ai (check actual location)
- **django_fusion**: Appears to be internal package, requires twilio
- **Issue**: Circular dependency chain with memory-intensive package



---

## ⚠️ UPDATE: Current Workaround is Hitting Diminishing Returns

### Problem with Fake Module Approach
The fake `django_fusion` module approach creates a cascading problem:
1. Add fake module → Works briefly
2. Django imports more of crafts_ai → New missing module error
3. Repeat infinitely...

**Missing modules discovered so far**:
- `django_fusion.managers` ✅ Added
- `django_fusion.site._context_mixins` ✅ Added
- `django_fusion.core` ❌ New error
- And more will follow...

### Why This Is Happening
- `crafts_ai` was designed to work with complete `django_fusion` package
- Different parts of the code import from different submodules
- We don't have complete `django_fusion` documentation to know all required submodules
- Each workaround reveals another missing piece

### Current Status
- Django partially loads (prints environment summary)
- Workers crash trying to load models
- Each fix requires restarting container and checking logs
- This is not a scalable solution

---

## ⚠️ RECOMMENDATION: Use SOLUTION 1 or SOLUTION 2

Given the complexity and time spent on workarounds, I strongly recommend:

### **IMMEDIATE**: Option A - Try to Install Twilio with Constraints
```bash
# Attempt to increase memory/swap and install
docker exec ctc-web python -c "
import subprocess
import os

# Try swap approach
subprocess.run(['fallocate', '-l', '2G', '/swapfile'], check=False)
subprocess.run(['chmod', '600', '/swapfile'], check=False)
subprocess.run(['mkswap', '/swapfile'], check=False)
subprocess.run(['swapon', '/swapfile'], check=False)

# Now try install with limited resources
subprocess.run(['pip', 'install', '--no-cache-dir', '--no-build-isolation', 'twilio'], check=False)
"
```

### **MEDIUM-TERM**: Option B - Create Lightweight Twilio Mock
Create a lightweight shim that satisfies imports but doesn't require full twilio:
```python
# File: /root/site/websites/fake_twilio.py
import sys
import types

twilio = types.ModuleType('twilio')
twilio.rest = types.ModuleType('twilio.rest')

class Client:
    def __init__(self, *args, **kwargs):
        pass

twilio.rest.Client = Client
sys.modules['twilio'] = twilio
sys.modules['twilio.rest'] = twilio.rest
```

Install this package BEFORE running `pip install crafts_ai` in the Dockerfile.

### **LONG-TERM**: Option C - Remove crafts_ai Dependency
Requires code refactoring but provides sustainable solution.

---

## Files Currently Affected by Workarounds

1. `/root/site/websites/ctc-research/settings.py` - 180+ lines of fake module creation
2. `/root/site/websites/ctc-research/www/core/content/models/_compat.py` - Compatibility shims

These files should be cleaned up once proper solution is implemented.

