# Final Cleanup Checklist
**Spec:** Django Project Reorganization & Email Automation
**Task:** 16.2 - Create cleanup checklist
**Requirements:** 21.4-21.9
**Date:** 2025-04-07

---

## Executive Summary

This document is the result of a final duplication scan performed after all consolidation tasks (Tasks 3–15) are complete. It catalogs remaining duplications, assigns categories, estimates effort, and prioritizes cleanup actions.

**Scan Results:**
- **Exact Duplicates Remaining:** 4 file pairs (1,317 lines each side)
- **Near-Identical Files:** 3 file pairs with minor site-specific differences
- **Acceptable Duplications:** 2 file pairs (site-specific logic)
- **Utilities Already Consolidated:** validators.py, text.py, responses.py, datetime_utils.py ✅

---

## 1. Duplication Scan Results

### 1.1 Exact Duplicates (Still Present)

| # | File (ctc-research.com) | File (structa.cloud) | Lines | Status |
|---|------------------------|----------------------|-------|--------|
| 1 | `apps/handlers/site/mixins.py` | `apps/handlers/site/mixins.py` | 907 | ⚠️ Import order differs only |
| 2 | `core/CI/models/interaction/call.py` | `alliance/CI/models/interaction/call.py` | 87 | ❌ Exact duplicate |
| 3 | `core/CI/models/interaction/notification.py` | `alliance/CI/models/interaction/notification.py` | 124 | ❌ Exact duplicate |
| 4 | `apps/handlers/models/forms/submission.py` | `apps/handlers/models/forms/submission.py` | 121 | ❌ Exact duplicate |
| 5 | `core/CI/models/integrations.py` | `alliance/CI/models/integrations.py` | 178 | ❌ Exact duplicate |

**Total duplicated lines:** ~1,417 lines (each side)

### 1.2 Near-Identical Files (Minor Differences)

| # | File | Difference Summary | Lines Diff |
|---|------|--------------------|------------|
| 1 | `apps/handlers/site/cart.py` | ctc-research uses Course model; structa uses generic product fields | ~50 lines |
| 2 | `apps/handlers/site/dashboard.py` | ctc-research has LMS-specific analytics; structa has generic version | ~150 lines |
| 3 | `apps/handlers/site/settings.py` | ctc-research has LMS notification fields; structa has generic version | ~20 lines |
| 4 | `apps/handlers/services/__init__.py` | ctc-research exports FormSubmissionService/notes; structa exports notifications | ~3 lines |
| 5 | `apps/handlers/registration/adapter.py` | ctc-research has rate limiting; structa has URL fallback | ~15 lines |

### 1.3 Already Consolidated (No Action Needed) ✅

| Component | Consolidated To | Status |
|-----------|----------------|--------|
| `utils/validators.py` | `libs/django-fusion/src/django_fusion/utils/validators.py` | ✅ Done |
| `utils/text.py` | `libs/django-fusion/src/django_fusion/utils/text.py` | ✅ Done |
| `utils/responses.py` | `libs/django-fusion/src/django_fusion/utils/responses.py` | ✅ Done |
| `utils/datetime.py` | `libs/django-fusion/src/django_fusion/utils/datetime_utils.py` | ✅ Done |
| `views/mixins.py` | `libs/django-fusion/src/django_fusion/views/mixins.py` | ✅ Done |
| `templatetags/` | `libs/django-fusion/src/django_fusion/templatetags/` | ✅ Done |
| `filters/` | Identical in both sites — shared via django-fusion | ✅ Acceptable |
| `snippets/` | Identical in both sites — shared via django-fusion | ✅ Acceptable |
| `blocks.py` | Identical in both sites — shared via django-fusion | ✅ Acceptable |
| `managers/peoples.py` | Near-identical, only import path differs (`core` vs `alliance`) | ✅ Acceptable |

---

## 2. Cleanup Decisions

### Category A: Requires Deletion (Exact Duplicates → Move to django-fusion)

---

#### A1. `CI/models/interaction/call.py`
- **Files:**
  - `ctc-research.com/core/CI/models/interaction/call.py` (87 lines)
  - `structa.cloud/alliance/CI/models/interaction/call.py` (87 lines)
- **Decision:** DELETE both, move to `libs/django-fusion/src/django_fusion/CI/models/interaction/call.py`
- **Justification:** Files are byte-for-byte identical. No site-specific logic.
- **Effort:** Low
- **Priority:** High
- **Risk:** Medium — requires Django migration in both sites
- **Steps:**
  1. Create `libs/django-fusion/src/django_fusion/CI/models/interaction/` directory
  2. Copy `call.py` to django-fusion
  3. Add `Call` to django-fusion's `__init__.py` exports
  4. Update import in `ctc-research.com/core/CI/models/interaction/__init__.py`
  5. Update import in `structa.cloud/alliance/CI/models/interaction/__init__.py`
  6. Create migration in both sites: `python manage.py makemigrations --empty core` / `alliance`
  7. Write data migration to move table ownership if needed
  8. Run `python manage.py migrate` in both sites
  9. Delete both original files
  10. Run tests

---

#### A2. `CI/models/interaction/notification.py`
- **Files:**
  - `ctc-research.com/core/CI/models/interaction/notification.py` (124 lines)
  - `structa.cloud/alliance/CI/models/interaction/notification.py` (124 lines)
- **Decision:** DELETE both, move to `libs/django-fusion/src/django_fusion/CI/models/interaction/notification.py`
- **Justification:** Files are byte-for-byte identical. No site-specific logic.
- **Effort:** Low
- **Priority:** High
- **Risk:** Medium — requires Django migration in both sites
- **Steps:**
  1. Copy `notification.py` to `libs/django-fusion/src/django_fusion/CI/models/interaction/`
  2. Update imports in both sites
  3. Create and run migrations in both sites
  4. Delete both original files
  5. Run tests

---

#### A3. `apps/handlers/models/forms/submission.py`
- **Files:**
  - `ctc-research.com/apps/handlers/models/forms/submission.py` (121 lines)
  - `structa.cloud/apps/handlers/models/forms/submission.py` (121 lines)
- **Decision:** DELETE both, move to `libs/django-fusion/src/django_fusion/handlers/models/forms/submission.py`
- **Justification:** Files are byte-for-byte identical. No site-specific logic.
- **Effort:** Low
- **Priority:** Medium
- **Risk:** Medium — requires Django migration in both sites
- **Steps:**
  1. Create `libs/django-fusion/src/django_fusion/handlers/models/forms/` directory
  2. Copy `submission.py` to django-fusion
  3. Update imports in both sites
  4. Create and run migrations in both sites
  5. Delete both original files
  6. Run tests

---

#### A4. `core/CI/models/integrations.py`
- **Files:**
  - `ctc-research.com/core/CI/models/integrations.py` (178 lines)
  - `structa.cloud/alliance/CI/models/integrations.py` (178 lines)
- **Decision:** DELETE both, move to `libs/django-fusion/src/django_fusion/CI/models/integrations.py`
- **Justification:** Files are byte-for-byte identical. No site-specific logic.
- **Effort:** Low
- **Priority:** Medium
- **Risk:** Medium — requires Django migration in both sites
- **Steps:**
  1. Copy `integrations.py` to `libs/django-fusion/src/django_fusion/CI/models/`
  2. Update imports in both sites
  3. Create and run migrations in both sites
  4. Delete both original files
  5. Run tests

---

### Category B: Requires Refactoring (Near-Identical → Merge with site-specific overrides)

---

#### B1. `apps/handlers/site/mixins.py`
- **Files:**
  - `ctc-research.com/apps/handlers/site/mixins.py` (907 lines)
  - `structa.cloud/apps/handlers/site/mixins.py` (907 lines)
- **Decision:** MERGE into django-fusion, keep site-specific subclasses if needed
- **Difference:** Only import ordering differs (lines 13-16). Functionally identical.
- **Justification:** 907 lines of duplicated view/model mixin logic. High value consolidation.
- **Effort:** Medium
- **Priority:** High
- **Risk:** High — 20+ views in each site inherit from these mixins
- **Steps:**
  1. Normalize import order in both files (trivial fix — 2 lines)
  2. Move unified `mixins.py` to `libs/django-fusion/src/django_fusion/pipelines/site/mixins.py`
  3. Update `from apps.handlers.site.mixins import X` → `from django_fusion.pipelines.site.mixins import X` in both sites
  4. Run full test suite in both sites
  5. Delete both original files
  6. **⚠️ Do not execute without running tests first**

---

#### B2. `apps/handlers/site/cart.py`
- **Files:**
  - `ctc-research.com/apps/handlers/site/cart.py`
  - `structa.cloud/apps/handlers/site/cart.py`
- **Decision:** KEEP with justification — site-specific business logic
- **Difference:** ctc-research integrates with `Course` model (LMS); structa uses generic product fields
- **Justification:** The cart logic is fundamentally different between sites. ctc-research is LMS-focused; structa is generic e-commerce. Merging would require complex abstraction.
- **Effort:** High (if merged)
- **Priority:** Low
- **Recommendation:** Keep separate. Document the shared base pattern in django-fusion as an abstract `BaseCartMixin`.

---

#### B3. `apps/handlers/site/dashboard.py`
- **Files:**
  - `ctc-research.com/apps/handlers/site/dashboard.py`
  - `structa.cloud/apps/handlers/site/dashboard.py`
- **Decision:** KEEP with justification — site-specific analytics
- **Difference:** ctc-research has 150+ lines of LMS-specific enrollment analytics, learning streaks, course recommendations. structa has a generic placeholder.
- **Justification:** The LMS analytics are ctc-research specific. The generic version in structa is intentionally minimal.
- **Effort:** High (if merged)
- **Priority:** Low
- **Recommendation:** Keep separate. The shared base `get_context_data` pattern is already in `ProfileContextMixin` in `mixins.py`.

---

### Category C: Acceptable Duplication (Keep as-is)

| # | Files | Reason to Keep |
|---|-------|----------------|
| C1 | `apps/handlers/site/tags.py` | Only whitespace differences (trailing spaces). Functionally identical. Low value to consolidate. |
| C2 | `apps/handlers/services/messages.py` | Only whitespace differences. Functionally identical. Low value to consolidate. |
| C3 | `apps/handlers/managers/peoples.py` | Only import path differs (`core` vs `alliance`). Site-specific module structure. |
| C4 | `apps/handlers/renderers.py` | Only logger import differs (`core` vs `alliance`). Site-specific. |
| C5 | `apps/handlers/site/notes.py` | Only logger import differs. Site-specific. |
| C6 | `apps/handlers/registration/adapter.py` | ctc-research has rate limiting; structa has URL fallback. Intentionally different. |
| C7 | `apps/handlers/models/snippets.py` | structa has `AuthEmailTemplate` model not in ctc-research. Site-specific feature. |

---

## 3. Prioritized Cleanup Plan

### Priority Matrix

| Item | Impact | Effort | Risk | Priority Score | Action |
|------|--------|--------|------|----------------|--------|
| A1: call.py | High | Low | Medium | **1** | Execute |
| A2: notification.py | High | Low | Medium | **2** | Execute |
| B1: mixins.py | Very High | Medium | High | **3** | Plan + Execute carefully |
| A3: submission.py | Medium | Low | Medium | **4** | Execute |
| A4: integrations.py | Medium | Low | Medium | **5** | Execute |
| B2: cart.py | Low | High | High | **6** | Keep (document) |
| B3: dashboard.py | Low | High | High | **7** | Keep (document) |

---

## 4. High-Priority Cleanup Items (Ready to Execute)

### 4.1 Fix mixins.py Import Order ✅ COMPLETED

The only difference between the two `mixins.py` files was import ordering on lines 13-16. This has been fixed — both files are now byte-for-byte identical.

**Fix applied:** Normalized `structa.cloud/apps/handlers/site/mixins.py` import order to match `ctc-research.com/apps/handlers/site/mixins.py`. No functional change.

**Verification:** `diff ctc-research.com/apps/handlers/site/mixins.py structa.cloud/apps/handlers/site/mixins.py` → no output (files identical).

---

### 4.2 Migration Plan for Model Consolidation (call.py, notification.py)

Before executing model consolidation, the following must be confirmed:

**Prerequisites:**
- [ ] Database backups taken for both sites
- [ ] Staging environment available for testing
- [ ] django-fusion CI/models directory structure created
- [ ] Both sites' test suites passing before migration

**Migration Steps (per model):**
```bash
# 1. Add model to django-fusion
# 2. In each site, create empty migration:
python manage.py makemigrations core --empty --name="move_call_to_django_fusion"

# 3. Edit migration to use SeparateDatabaseAndState:
# This keeps the DB table but changes Django's model reference
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [...]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],  # No DB changes needed
            state_operations=[
                migrations.DeleteModel(name='Call'),
            ],
        ),
    ]

# 4. Run migration
python manage.py migrate

# 5. Verify data intact
python manage.py shell -c "from django_fusion.CI.models.interaction.call import Call; print(Call.objects.count())"
```

---

## 5. Effort Summary

| Category | Items | Total Effort | Timeline |
|----------|-------|-------------|----------|
| A: Requires Deletion | 4 items | Low × 4 = ~4-8 days | Week 1-2 |
| B: Requires Refactoring | 2 items | Medium + High = ~5-10 days | Week 2-3 |
| C: Acceptable | 7 items | 0 (keep as-is) | N/A |
| **TOTAL** | **13 items** | **~9-18 days** | **3-4 weeks** |

---

## 6. Success Criteria

- [ ] `call.py` consolidated to django-fusion, deleted from both sites
- [ ] `notification.py` consolidated to django-fusion, deleted from both sites
- [ ] `submission.py` consolidated to django-fusion, deleted from both sites
- [ ] `integrations.py` consolidated to django-fusion, deleted from both sites
- [x] `mixins.py` import order normalized ✅ (completed in Task 16.3)
- [ ] `mixins.py` consolidated to django-fusion (after testing)
- [ ] All tests passing in both sites after each consolidation
- [ ] No broken imports in either site
- [ ] Database migrations successful in both sites

---

## 7. Files NOT to Touch (Acceptable Duplication)

The following files have minor differences that are intentional and site-specific. They should **not** be consolidated:

- `apps/handlers/site/cart.py` — LMS vs generic e-commerce logic
- `apps/handlers/site/dashboard.py` — LMS analytics vs generic dashboard
- `apps/handlers/site/settings.py` — LMS notification fields vs generic
- `apps/handlers/managers/peoples.py` — Only import path differs
- `apps/handlers/renderers.py` — Only logger import differs
- `apps/handlers/site/notes.py` — Only logger import differs
- `apps/handlers/registration/adapter.py` — Intentionally different features
- `apps/handlers/models/snippets.py` — structa has extra model

---

**End of Cleanup Checklist**
