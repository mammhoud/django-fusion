# Database Schema Fix Summary

## Issue
**Error**: `column profiles.profile_visibility does not exist`

**Root Cause**: The database schema was out of sync with the model definition. The `profile_visibility` field is defined in the `Person` model but was missing from the database table.

## Solution Applied

### 1. Created Migration: `0002_add_missing_profile_fields.py`

This migration safely adds the missing `profile_visibility` column using PostgreSQL conditional logic (`DO $$ ... END $$`) to avoid errors if the column already exists.

**Features**:
- ✅ Checks if column exists before adding it
- ✅ Sets default value to 'public'
- ✅ Adds NOT NULL constraint
- ✅ Adds CHECK constraint for valid values ('public', 'members', 'private')
- ✅ Provides reverse migration for rollback

### 2. Field Definition in Model

```python
profile_visibility = models.CharField(
    max_length=20,
    choices=[
        ('public', _('Public - Anyone can see your profile')),
        ('members', _('Members Only - Only registered members can see your profile')),
        ('private', _('Private - Only you can see your profile')),
    ],
    default='public',
    verbose_name=_("Profile Visibility"),
)
```

**Location**: `/root/xellent/django_fusion.pipelines/models/users/users.py` (Line ~204)

## How to Apply Fix

### Option 1: Using Make Command (Recommended)
```bash
# Reset migrations and rebuild database
make rm
```

### Option 2: Manual Migration
```bash
# Apply just this migration
python manage.py migrate pipelines 0002
```

### Option 3: Fresh Start
```bash
# If you have no important data
make reset-db
make m
```

## Verification Steps

After applying the migration, verify the fix:

```bash
# 1. Check migration status
python manage.py showmigrations pipelines

# 2. Verify column exists in database
python manage.py dbshell
\d profiles  # Should show profile_visibility column
\q

# 3. Test the application
make dev
# Visit http://127.0.0.1:8000/courses/
```

## Prevention

To prevent similar issues in the future:

1. **Always run migrations after model changes**:
   ```bash
   make makemigrations
   make m
   ```

2. **Check migration status regularly**:
   ```bash
   python manage.py showmigrations
   ```

3. **Verify database schema matches models**:
   ```bash
   python manage.py migrate --check
   ```

## Related Files

- **Model**: `/root/xellent/django_fusion.pipelines/models/users/users.py`
- **Initial Migration**: `/root/xellent/django_fusion.pipelines/migrations/0001_initial.py`
- **Fix Migration**: `/root/xellent/django_fusion.pipelines/migrations/0002_add_missing_profile_fields.py`
- **Error Location**: `/root/xellent/assets/templates/partials/auth_buttons.html:9`

## Status

- [x] Migration created
- [ ] Migration applied (run `make rm`)
- [ ] Error verified as fixed
- [ ] Application tested

---

**Created**: 2026-02-04T16:46:34Z
**Fixed By**: Antigravity AI Assistant
