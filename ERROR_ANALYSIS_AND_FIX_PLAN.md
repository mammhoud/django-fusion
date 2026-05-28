# CTC Research Website - Test Errors Analysis & Fix Plan

## Summary
- **Total Collection Errors**: 143
- **Total Test Errors**: Multiple runtime failures
- **Root Causes**: Module import paths, missing aliases, model field mismatches, missing handler files

---

## Error Categories & Fixes

### Category 1: Missing Module Aliases (PRIMARY - ~80+ errors)
**Problem**: Tests import from `www.apps.accounts.*` but conftest.py doesn't create these aliases.

**Affected Modules**:
- `www.apps.accounts.registration` → `accounts.registration` ❌
- `www.apps.accounts.management` → `accounts.management` ❌
- `www.apps.accounts.forms` → `accounts.forms` ❌
- `www.apps.accounts.models` → `accounts.models` ✅ (exists)
- `www.apps.accounts.services` → `accounts.services` ❌
- `www.apps.accounts.views` → `accounts.views` ❌

**Test Files Affected**:
- tests/apps/accounts/registration/*.py (~15 files)
- tests/apps/handlers/registration/*.py (~15 files)
- tests/apps/accounts/*.py (various)

**Fix**: Update `tests/conftest.py` - Add missing www.apps.accounts.* aliases

**Location**: [tests/conftest.py](tests/conftest.py#L70-L90)

---

### Category 2: Missing Handler Files (SECONDARY - ~1 error)
**Problem**: Test imports from non-existent handler file.

**File**: `tests/apps/blog/test_handlers_blog.py`
**Missing**: `/root/site/websites/handlers/site/blog.py`

**Cause**: Handler file doesn't exist or path is incorrect

**Test Files Affected**:
- tests/apps/blog/test_handlers_blog.py

**Fix Options**:
1. Create the missing handler file
2. Skip/remove the test if not needed
3. Fix the import path

---

### Category 3: Missing Service Classes (TERTIARY - ~2 errors)
**Problem**: Service classes referenced in tests don't exist in the codebase.

**Missing Classes**:
- `PostFilterService` from `www.apps.blog.services`
- `TagService` from `www.apps.blog.services`

**Test Files Affected**:
- tests/apps/blog/test_properties.py
- tests/apps/blog/test_services.py

**Fix Options**:
1. Implement the missing services
2. Update tests to use correct service names
3. Remove tests if services are deprecated

---

### Category 4: Model Field Mismatches (RUNTIME - ~5+ errors)
**Problem**: Tests use field names that don't exist in current models.

**Examples**:
- `BlogPost.objects.create(body=...)` ❌ → Model expects different field name
- Model signature changed but tests weren't updated

**Test Files Affected**:
- tests/apps/blog/test_htmx_workflow.py
- tests/apps/blog/test_models.py (some assertions)

**Failures**:
```
TypeError: BlogPost() got unexpected keyword arguments: 'body'
```

**Fix**:
1. Check BlogPost model definition for correct field names
2. Update test fixtures to use correct field names
3. Verify model vs test alignment

**Location**: Check [ctc-research.com/www/apps/models/blog.py](ctc-research.com/www/apps/models/blog.py)

---

### Category 5: URL Routing Issues (RUNTIME - ~3 errors)
**Problem**: URL namespace 'blog' not registered when running tests.

**Failures**:
```
NoReverseMatch: 'blog' is not a registered namespace
```

**Test Files Affected**:
- tests/apps/blog/test_htmx_workflow.py

**Cause**: URL configuration not loaded in test environment

**Fix**:
1. Check URL configuration in tests/urls.py
2. Ensure 'blog' namespace is registered in test URLconf
3. Verify django.test.Client uses correct root URLconf

---

### Category 6: 404 Errors on HTMX Endpoints (RUNTIME - ~5+ errors)
**Problem**: HTMX endpoints return 404 instead of 200/403

**Failures**:
```
assert 404 in [302, 403]  # Expected 302 or 403 (auth redirect/forbidden)
assert response.status_code == 200  # Expected success
```

**Examples**:
- `/osoul/blog/posts/create-fragment/` → 404
- Blog list/create endpoints not found

**Cause**:
1. URL routes not registered in test environment
2. URL path prefix 'osoul' incorrect?
3. View handler missing

**Fix**:
1. Verify URL patterns in app urls.py match test expectations
2. Check test client setup and root URLconf
3. Verify view exists and is properly registered

---

## Recommended Fix Priority

### Phase 1 (CRITICAL - Unblocks everything)
1. **Add missing module aliases to conftest.py** (~80+ errors fixed)
   - Time: 10 mins
   - Impact: Unblocks most test collection

### Phase 2 (HIGH - Fixes runtime errors)
2. **Verify and fix BlogPost model fields** (~5+ errors fixed)
   - Time: 15 mins
   - Impact: HTMX workflow tests can run

3. **Verify and register URL namespace 'blog'** (~3 errors fixed)
   - Time: 15 mins
   - Impact: URL reverse works in tests

### Phase 3 (MEDIUM - Content gaps)
4. **Create/implement missing service classes** (~2 errors)
   - Time: 20-30 mins
   - Impact: Service tests can run

5. **Create/fix missing handler file** (~1 error)
   - Time: 10 mins
   - Impact: Handler tests can run

---

## Implementation Steps

### Step 1: Fix Module Aliases
**File**: `tests/conftest.py`
**Change**: Add to `_register_aliases()` function:
```python
# www.apps.accounts → accounts
"www.apps.accounts":                    "accounts",
"www.apps.accounts.registration":       "accounts.registration",
"www.apps.accounts.management":         "accounts.management",
"www.apps.accounts.forms":              "accounts.forms",
"www.apps.accounts.services":           "accounts.services",
"www.apps.accounts.views":              "accounts.views",
"www.apps.accounts.filters":            "accounts.filters",
"www.apps.accounts.admin":              "accounts.admin",
"www.apps.accounts.signals":            "accounts.signals",
"www.apps.accounts.middleware":         "accounts.middleware",
```

### Step 2: Check Model Fields
**Command**:
```bash
cd /root/site/websites && WEBSITE=ctc-research.com python -c "from accounts.models import BlogPost; print(BlogPost._meta.fields)"
```

### Step 3: Verify URL Configuration
**Check**: tests/urls.py and ctc-research.com/plugins/accounts/urls.py

### Step 4: Run Tests
```bash
cd /root/site/websites && TEST_CTC_RESEARCH=true pytest tests/ -v --tb=short 2>&1 | tee test_results.txt
```

---

## Database Setup Notes

Database is configured to use PostgreSQL in production, but tests should use SQLite or test database. The test environment should:
1. Use SQLite for speed (already configured in [configs/base/databases.py](configs/base/databases.py))
2. Create test-specific migrations as needed
3. Load fixtures before running integration tests

---

## Next Steps After Fixes

1. ✅ Fix all import/collection errors (Phase 1-2)
2. ⬜ Run full test suite
3. ⬜ Fix remaining runtime failures
4. ⬜ Load fixture data
5. ⬜ Start development server
6. ⬜ Test homepage and pages in browser
7. ⬜ Check application logs
8. ⬜ Redeploy if needed

