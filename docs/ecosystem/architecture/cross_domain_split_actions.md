# Cross-Domain Leakage Split Actions

## Task 6.7 Implementation Strategy

### Approach

Given the extensive cross-domain leakage (127+ modules in structa.cloud, 139+ in ctc-research.com), we'll use a phased approach:

1. **Phase 1**: Identify and document the root causes
2. **Phase 2**: Create domain-specific modules for shared functionality
3. **Phase 3**: Refactor imports to use new modules
4. **Phase 4**: Verify and test

### Root Cause Analysis

#### 1. accounts ↔ lms Leakage
**Issue**: accounts/signals.py imports from apps.lms.models (Instructor, Student)
**Root Cause**: User creation triggers LMS profile creation
**Solution**: Use Django signals in LMS domain to listen for User creation, not vice versa

#### 2. content ↔ accounts Leakage
**Issue**: content/signals/user.py imports from apps.accounts.models (Person)
**Root Cause**: User creation triggers Person creation
**Solution**: Move Person model to accounts domain (where it belongs), content listens via signals

#### 3. accounts ↔ messaging Leakage
**Issue**: accounts/email_templates.py, accounts/services/email/ import messaging
**Root Cause**: Email functionality is in accounts but should be in messaging
**Solution**: Create messaging domain or move email to crafts_ai

#### 4. content ↔ forms Leakage
**Issue**: content/models/contact.py, content/models/pages/base.py import forms
**Root Cause**: Contact forms are in content but belong to forms domain
**Solution**: Extract form models to forms domain

#### 5. lms ↔ alliance Leakage
**Issue**: lms domain references "alliance" (structa.cloud's LMS)
**Root Cause**: Different project names for same domain
**Solution**: This is expected and acceptable - same domain, different projects

### Implementation Plan

#### Step 1: Fix accounts ↔ lms Leakage

**File**: structa.cloud/apps/accounts/signals.py
**Action**: Remove LMS imports, let LMS domain listen for User creation

```python
# BEFORE (accounts/signals.py)
from apps.lms.models import Instructor, Student

@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    if instance.is_staff:
        Instructor.objects.get_or_create(...)
    else:
        Student.objects.get_or_create(...)

# AFTER (accounts/signals.py)
# Remove this signal entirely

# NEW (lms/signals.py)
@receiver(post_save, sender=User)
def create_lms_profiles(sender, instance, created, **kwargs):
    if instance.is_staff:
        Instructor.objects.get_or_create(...)
    else:
        Student.objects.get_or_create(...)
```

#### Step 2: Fix content ↔ accounts Leakage

**File**: structa.cloud/apps/content/signals/user.py
**Action**: Move Person model to accounts domain

```python
# BEFORE (content/signals/user.py)
from apps.accounts.models import Person

# AFTER (content/signals/user.py)
# Import Person from accounts (same domain)
from apps.accounts.models import Person
# This is now acceptable - both in accounts domain
```

#### Step 3: Fix content ↔ forms Leakage

**File**: structa.cloud/apps/content/models/contact.py
**Action**: Move to forms domain

```
structa.cloud/apps/content/models/contact.py
  → structa.cloud/apps/forms/models/contact.py
```

#### Step 4: Fix accounts ↔ messaging Leakage

**File**: structa.cloud/apps/accounts/services/email/
**Action**: Move to messaging domain or crafts_ai

```
structa.cloud/apps/accounts/services/email/
  → structa.cloud/apps/messaging/services/email/
```

### Files to Split (Priority Order)

#### High Priority (Clear Domain Ownership)

1. **accounts/signals.py** (structa.cloud, ctc-research.com)
   - Remove LMS imports
   - Move LMS profile creation to lms/signals.py

2. **accounts/services/email/** (both projects)
   - Move to messaging domain or crafts_ai

3. **content/models/contact.py** (both projects)
   - Move to forms domain

#### Medium Priority (Requires Refactoring)

1. **accounts/site/courses.py** (both projects)
   - Move to lms/site/courses.py

2. **accounts/site/certifications.py** (both projects)
   - Move to lms/site/certifications.py

3. **accounts/managers/enrollments.py** (ctc-research.com)
   - Move to lms/managers/enrollments.py

#### Lower Priority (Complex Dependencies)

1. **lms/managers/** (both projects)
   - Refactor to use dependency injection instead of direct user imports

2. **accounts/site/dashboard.py** (both projects)
   - Refactor to separate user dashboard from course dashboard

### Implementation Notes

- Each split requires:
  1. Create target file/directory
  2. Copy code
  3. Update imports in both projects
  4. Run tests
  5. Delete original file
  6. Commit

- Use find-and-replace carefully to update imports
- Test after each split to ensure no import errors
- Verify tests still pass

### Expected Outcome

After completing all splits:
- Eliminate unnecessary cross-domain imports
- Maintain functionality
- Improve code organization
- Reduce coupling between domains

