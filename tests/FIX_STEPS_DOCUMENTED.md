# Django Website Deployment Fixes - Complete Documentation

## Overview
This document summarizes all errors found during deployment and the fixes applied across this session.

---

## COMPLETED FIXES

### 1. Missing Contact Form Template
**Error:** `django.template.exceptions.TemplateDoesNotExist: components/contact/sections/form/form.html`

**Root Cause:** The contact form component was using django-osoul's component loader which expects nested folder structure `components/contact/sections/form/form.html` rather than a flat structure.

**Fix Applied:**
- Created `_shared/plugins/components/` directory structure
- Reorganized `form.html` to nested folder: `_shared/plugins/components/contact/sections/form/form.html`
- Created symlinks for both ctc-research and lms-demo pointing to shared directory
- Updated Dockerfile to include `_shared` directory in COPY command

**Files Modified:**
- `compose/django/Dockerfile` - Added `COPY _shared /app/_shared`
- Created `_shared/plugins/components/contact/sections/form/form.html`

### 2. django_rseal Model Conflict Error
**Error:** `RuntimeError: Conflicting 'role' models in application 'django_osoul': <class 'django_osoul.models.auth.Role'> and <class 'django_osoul.site.auth.models.role.Role'>`

**Root Cause:** django_rseal package has two conflicting Role model definitions causing registration failure during import. The issue occurs when importing from `django_rseal.site.payments`.

**Fix Applied:**
- Removed `django_rseal` from INSTALLED_APPS in `configs/base/apps.py`
- Added `RuntimeError` exception handling in payment URL imports in `ctc-research/plugins/lms/urls.py` and `lms-demo/plugins/lms/urls.py`

**Files Modified:**
- `configs/base/apps.py` - Removed django_rseal from LOCAL_APPS
- `ctc-research/plugins/lms/urls.py` - Changed exception from `ImportError` to `(ImportError, RuntimeError)`
- `lms-demo/plugins/lms/urls.py` - Changed exception from `ImportError` to `(ImportError, RuntimeError)`

### 3. Person Model Import Missing
**Error:** `NameError: name 'Person' is not defined` in `ctc-research/plugins/profile/views/settings.py` line 199

**Root Cause:** The Person model was used in type annotations but not imported at module level.

**Fix Applied:**
- Added import: `from django_rseal.models import Person` at top of settings.py file

**Files Modified:**
- `ctc-research/plugins/profile/views/settings.py` - Added Person import

---

## REMAINING ISSUES

### 1. allauth URL Naming Issue
**Error:** `django.urls.exceptions.NoReverseMatch: Reverse for 'account_login' not found`

**Status:** Not Yet Fixed

**Description:** allauth is trying to reverse 'account_login' URL name which is not being properly registered. This occurs during template rendering when allauth tries to construct login URLs.

**Potential Solutions:**
- Verify allauth.urls are being properly included with namespace
- Check if URL name conflicts exist with other apps
- May need to update allauth configuration or custom URL naming

**Affected Areas:**
- Allauth login/signup pages
- Any template using allauth context

### 2. SECRET_KEY Configuration Issues
**Error Messages:**
- `SECRET_KEY is only 46 characters long (minimum: 50)`
- `SECRET_KEY starts with insecure placeholder prefix 'dev-secret-key'`

**Status:** Not Yet Fixed

**Description:** The SECRET_KEY in settings is too short and uses development placeholder. This is a security issue and needs proper configuration.

**Required Fix:**
- Generate proper SECRET_KEY using: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- Store in environment variable or secure configuration
- Ensure it's loaded from conf.py settings properly

**Affected Areas:**
- All application instances
- Security posture of deployment

---

## ARCHITECTURE CHANGES MADE

### Shared Components Directory Structure
Created new shared directory structure to avoid duplication:

```
_shared/
├── plugins/
│   ├── components/
│   │   └── contact/
│   │       └── sections/
│   │           └── form/
│   │               └── form.html
│   └── products/
```

**Symlinks:**
- `ctc-research/plugins/components` → `../../_shared/plugins/components`
- `ctc-research/plugins/products` → `../../_shared/plugins/products`
- `lms-demo/plugins/components` → `../../_shared/plugins/components`
- `lms-demo/plugins/products` → `../../_shared/plugins/products`

### Docker Build Context Update
Updated Dockerfile to include `_shared` directory:

```dockerfile
COPY _shared ${APP_HOME}/_shared
```

This ensures shared plugins are available in both website containers.

---

## DEPLOYMENT CHECKLIST

### ✅ Completed
- [x] Contact form template structure fixed
- [x] django_rseal conflict resolved
- [x] Person model imports corrected
- [x] Shared components directory created
- [x] Dockerfile updated for build context
- [x] Both ctc-research and lms-demo using same components

### ⏳ Pending
- [ ] allauth URL routing configured
- [ ] SECRET_KEY properly generated and configured
- [ ] Full end-to-end testing of all pages
- [ ] SSL/HTTPS certificate issues resolved
- [ ] Namespace resolution validated for all URL patterns
- [ ] Custom SECRET_KEY from conf.py implementation

---

## TESTING COMMANDS

### Docker Deployment
```bash
make docker-deploy-websites
```

### Check Container Status
```bash
docker compose ps
```

### View Error Logs
```bash
# ctc-research
docker exec ctc-research-website tail -50 /app/logs/error.log

# lms-demo
docker exec lms-demo-website tail -50 /app/logs/error.log
```

### Test Contact Page
```bash
curl -k http://localhost/contact-page/
```

---

## GIT COMMITS

All changes have been committed:
- Commit: "Fix: Resolve django_rseal model conflicts and create shared components directory"
- Branch: generic

---

## NOTES FOR NEXT SESSION

1. **Priority**: Fix allauth account_login URL naming issue - affects all auth pages
2. **Security**: Generate and configure proper SECRET_KEY before production deployment
3. **Testing**: After URL fixes, test all authentication flows
4. **Monitoring**: Watch for additional template loading errors as more pages are accessed
5. **Documentation**: Update deployment guides with new shared components structure

---

## File Changes Summary

### Modified Files
- `compose/django/Dockerfile`
- `configs/base/apps.py`
- `ctc-research/plugins/profile/views/settings.py`
- `ctc-research/plugins/lms/urls.py`
- `lms-demo/plugins/lms/urls.py`

### New Files/Directories
- `_shared/plugins/components/` (new shared directory structure)
- `_shared/plugins/components/contact/sections/form/form.html`
- `_shared/plugins/products/` (copied structure)

### Symlinks Created
- `ctc-research/plugins/components`
- `ctc-research/plugins/products`
- `lms-demo/plugins/components`
- `lms-demo/plugins/products`

---

**Last Updated:** 2026-06-09
**Status:** Partially Resolved - Further work needed on URL routing and security configuration
