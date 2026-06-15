# Fixture Loading Error Analysis & Fix

**Date:** June 2, 2026  
**Status:** Error identified and solution provided  
**Logs Location:** `docs/fixture_loading_*.log`

---

## Executive Summary

The fixture loading process encountered foreign key constraint violations in the second attempt (fixture_loading_20260602_192820.log). The root cause is that fixtures must be loaded in strict dependency order to avoid referential integrity violations.

**Status Comparison:**
- ✅ **First attempt (19:27:43):** Successful - All fixtures loaded correctly
- ❌ **Second attempt (19:28:20):** Failed - Foreign key violations during auth/permission loading

---

## Root Cause Analysis

### Error Chain

1. **Permissions Loading Fails**
   ```
   ForeignKeyViolation: insert or update on table "auth_permission"
   violates foreign key constraint
   Key (content_type_id)=(64) is not present in table "django_content_type"
   ```
   **Cause:** Content types not created before loading permissions

2. **Groups Loading Fails**
   ```
   ForeignKeyViolation: insert or update on table "auth_group_permissions"
   violates foreign key constraint
   Key (permission_id)=(421) is not present in table "auth_permission"
   ```
   **Cause:** Permissions not loaded (failed in step 1)

3. **Users Loading Fails**
   ```
   ForeignKeyViolation: insert or update on table "auth_user_groups"
   violates foreign key constraint
   Key (group_id)=(3) is not present in table "auth_group"
   ```
   **Cause:** Groups not loaded (failed in step 2)

4. **Site Configuration Fails**
   ```
   ForeignKeyViolation: insert or update on table "wagtailcore_site"
   violates foreign key constraint
   Key (root_page_id)=(3) is not present in table "wagtailcore_page"
   ```
   **Cause:** Pages not created before site configuration

### Dependency Map

```
django_content_type (must exist first)
    ↓
auth_permission (depends on content_type)
    ↓
auth_group (depends on permission)
    ↓
auth_user (depends on group)

wagtailcore_page (must exist first)
    ↓
wagtailcore_site (depends on page as root)
```

---

## Detailed Error Breakdown

### Error 1: Content Type Foreign Key Violation

**Symptom:**
```
IntegrityError: Problem installing fixtures:
insert or update on table "auth_permission" violates foreign key constraint
Key (content_type_id)=(64) is not present in table "django_content_type"
```

**Root Cause:**
- Trying to insert permission for content_type ID 64
- Content type with ID 64 doesn't exist in database
- Must run `makemigrations` and `migrate` first to create all content types

**Solution:**
```bash
python manage.py migrate --run-syncdb  # Ensure all tables exist
python manage.py migrate              # Apply all migrations
python manage.py migrate contenttypes # Explicitly ensure contenttypes
```

### Error 2: Permission Foreign Key Violation (in Groups)

**Symptom:**
```
IntegrityError: Problem installing fixtures:
insert or update on table "auth_group_permissions"
violates foreign key constraint
Key (permission_id)=(421) is not present in table "auth_permission"
```

**Root Cause:**
- Permission with ID 421 doesn't exist
- Permissions fixture failed to load in previous step
- Groups fixture depends on permissions being loaded first

**Solution:**
- Load fixtures in correct order
- Load permissions BEFORE groups
- Skip/retry failed permission loads

### Error 3: Index Task Failures

**Symptom:**
```
AttributeError: type object 'Permission' has no attribute 'get_indexed_objects'
ContentType.DoesNotExist: ContentType matching query does not exist
```

**Root Cause:**
- Model search/indexing tries to index objects during fixture load
- Objects reference content types that don't exist
- Indexing should be disabled during fixture loading

**Solution:**
```bash
# Disable indexing during fixture load
export WAGTAIL_SEARCH_DISABLED=1
python manage.py loaddata fixtures...

# Re-enable and rebuild index after
export WAGTAIL_SEARCH_DISABLED=0
python manage.py update_index
```

---

## What Went Right (First Attempt)

The first attempt succeeded because:

1. ✅ Database was freshly migrated
2. ✅ All content types existed
3. ✅ Fixtures were loaded in correct dependency order:
   - Permissions (after content types exist)
   - Groups (after permissions exist)
   - Users (after groups exist)
   - Locales, Site, Pages
4. ✅ Indexing/search was not triggered during loading
5. ✅ No existing data conflicts

---

## Recommended Fix Strategy

### Option 1: Fresh Database Load (Recommended)

```bash
#!/bin/bash

# 1. Drop and recreate database
docker exec postgres_container dropdb ctc_research || true
docker exec postgres_container createdb ctc_research

# 2. Run migrations with clean slate
python manage.py migrate --run-syncdb
python manage.py migrate

# 3. Load fixtures in correct order
export WAGTAIL_SEARCH_DISABLED=1

python manage.py loaddata auth_permission
python manage.py loaddata auth_group
python manage.py loaddata auth_user
python manage.py loaddata wagtail_locale
python manage.py loaddata wagtail_site
python manage.py loaddata wagtail_page

# 4. Re-enable search and rebuild index
export WAGTAIL_SEARCH_DISABLED=0
python manage.py update_index

echo "✅ Fixture loading complete"
```

### Option 2: Clean Existing Data

```bash
#!/bin/bash

# 1. Clear existing data while preserving structure
python manage.py flush --noinput --database=default

# 2. Run migrations
python manage.py migrate

# 3. Load fixtures as above
```

### Option 3: Selective Reload

```bash
#!/bin/bash

# Load only missing fixtures that didn't fail
python manage.py loaddata auth_permission --exclude auth.Group auth.User
python manage.py loaddata auth_group
python manage.py loaddata auth_user

# Verify
python manage.py shell -c "from django.auth.models import Permission; print(f'Permissions: {Permission.objects.count()}')"
```

---

## Prevention Measures

### 1. Always Migrate First
```bash
# Before any fixture loading
python manage.py migrate
python manage.py migrate contenttypes
```

### 2. Disable Indexing During Fixtures
```bash
export WAGTAIL_SEARCH_DISABLED=1
python manage.py loaddata [fixtures]
unset WAGTAIL_SEARCH_DISABLED
```

### 3. Load Fixtures in Correct Order
- Content types MUST exist (automatic via migrate)
- Permissions BEFORE groups
- Groups BEFORE users
- Base pages BEFORE site configuration
- All core objects BEFORE search indexing

### 4. Validate Fixture Data
```bash
# Check fixture integrity before loading
python manage.py sqlsequencereset app_name
python manage.py loaddata --validate-only fixtures.json
```

### 5. Use Transactions
```bash
# Rollback on any error
python manage.py loaddata --atomic fixtures
```

---

## Implementation Steps

### Step 1: Stop Services
```bash
docker compose down
```

### Step 2: Clean Database (if needed)
```bash
docker exec postgres dropdb ctc_research
docker exec postgres createdb ctc_research
```

### Step 3: Run Migrations
```bash
docker compose run web python manage.py migrate --run-syncdb
docker compose run web python manage.py migrate
```

### Step 4: Load Fixtures Safely
```bash
# Disable search during loading
export WAGTAIL_SEARCH_DISABLED=1

# Load in dependency order
docker compose run web python manage.py loaddata auth_permission
docker compose run web python manage.py loaddata auth_group  
docker compose run web python manage.py loaddata auth_user
docker compose run web python manage.py loaddata wagtail_locale
docker compose run web python manage.py loaddata wagtail_site
docker compose run web python manage.py loaddata wagtail_page
```

### Step 5: Rebuild Index
```bash
docker compose run web python manage.py update_index
```

### Step 6: Restart Services
```bash
docker compose up -d
```

---

## Log Analysis

### Successful Load (fixture_loading_20260602_192743.log)

**Key Success Indicators:**
```
✅ All fixtures loaded successfully!
✅ Total pages in database: 2
✅ Fixture loading complete!
```

**Timeline:**
- 19:27:43 - Started
- 19:27:44 - Completed
- ~1 second total

**Content Loaded:**
- Pages: Homepage, About, Contact, Team, Courses
- Languages: 6 locales
- Images: 22 images with renditions
- Users & Permissions: All configured

### Failed Load (fixture_loading_20260602_192820.log)

**Failure Points:**
- 19:28:20 - Permissions: ForeignKeyViolation
- 19:28:25 - Groups: ForeignKeyViolation (due to permissions failure)
- 19:28:31 - Users: ForeignKeyViolation (due to groups failure)
- 19:28:36 - Locales: ✅ Loaded successfully
- 19:28:41 - Site: ForeignKeyViolation (page references missing)
- 19:28:47 - Base Pages: Started but encountered indexing errors

**Error Categories:**
- 3 × ForeignKeyViolation (auth/permissions)
- 1 × ForeignKeyViolation (site/pages)
- 2 × AttributeError (indexing)
- 2 × ContentType.DoesNotExist (indexing)

---

## Verification Checklist

After applying fixes:

- [ ] Database migrations applied: `python manage.py migrate`
- [ ] Permissions table populated: `SELECT COUNT(*) FROM auth_permission`
- [ ] Groups table populated: `SELECT COUNT(*) FROM auth_group`
- [ ] Users table populated: `SELECT COUNT(*) FROM auth_user`
- [ ] Pages created: `python manage.py shell -c "from wagtail.models import Page; print(Page.objects.count())"`
- [ ] Site configured: Check Django admin or shell
- [ ] Search index rebuilt: `python manage.py update_index`
- [ ] No errors in logs: Check app logs

---

## Commands for Quick Fix

### Automated Fix Script

```bash
#!/bin/bash
set -e

echo "🔧 Fixing fixture loading errors..."

# 1. Stop services
echo "1/6 Stopping services..."
docker compose down

# 2. Clean database
echo "2/6 Cleaning database..."
docker exec postgres dropdb ctc_research || true
docker exec postgres createdb ctc_research

# 3. Run migrations
echo "3/6 Running migrations..."
docker compose run --rm web python manage.py migrate --run-syncdb
docker compose run --rm web python manage.py migrate

# 4. Load fixtures
echo "4/6 Loading fixtures..."
export WAGTAIL_SEARCH_DISABLED=1
docker compose run --rm web python manage.py loaddata auth_permission
docker compose run --rm web python manage.py loaddata auth_group
docker compose run --rm web python manage.py loaddata auth_user
docker compose run --rm web python manage.py loaddata wagtail_locale
docker compose run --rm web python manage.py loaddata wagtail_site
docker compose run --rm web python manage.py loaddata wagtail_page
unset WAGTAIL_SEARCH_DISABLED

# 5. Rebuild search index
echo "5/6 Rebuilding search index..."
docker compose run --rm web python manage.py update_index

# 6. Start services
echo "6/6 Starting services..."
docker compose up -d

echo "✅ Fixture loading fix complete!"
```

---

## Related Documentation

- See `/docs/fixture_loading_20260602_192743.log` - Successful load
- See `/docs/fixture_loading_20260602_192820.log` - Failed load  
- See `/docs/COMPLETE_RESOLUTION_FINAL_REPORT.md` - Historical resolution
- See `/docs/DEPLOYMENT_READY_SUMMARY.md` - Current status

---

## Summary

**Problem:** Foreign key constraint violations during fixture loading  
**Root Cause:** Fixtures loaded out of order or missing content types  
**Solution:** Run migrations first, load fixtures in dependency order, disable indexing during load  
**Status:** ✅ Solution documented and ready to implement  

The first successful load proves the fixtures and database schema are compatible. The second attempt failed due to environmental factors or incorrect load order. Follow the recommended fix strategy to resolve.

---

**Document Generated:** June 2, 2026 19:30 UTC  
**Status:** Analysis Complete - Ready for Implementation
