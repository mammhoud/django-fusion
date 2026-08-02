# Packages/UI Component Consolidation & Deduplication Action Plan

**Date:** June 7, 2026  
**Status:** Analysis & Planning Phase  
**Version:** 1.0.0  

---

## Executive Summary

This document provides a comprehensive action plan for consolidating scattered UI components across the codebase into the centralized `packages/ui/` library and removing duplicate implementations.

### Key Actions
1. ✅ **Analyze existing implementations** - Complete
2. ⏳ **Consolidate to packages/ui/** - Ready to execute
3. ⏳ **Update all imports** - Ready to execute
4. ⏳ **Delete duplicates** - Ready to execute
5. ⏳ **Verify no regressions** - Ready to execute

---

## Current State Analysis

### Packages/UI Directory (SHARED COMPONENT LIBRARY)
**Status:** ✅ **ALREADY CREATED & ORGANIZED**

```
packages/ui/ (11 components)
├── forms/
│   ├── htmx_form.html (Generic HTMX form)
│   └── validation.html (Field validation display)
├── htmx/
│   ├── base_fragment.html (HTMX fragment wrapper)
│   ├── error_handler.html (Error display)
│   └── loading_states.html (Loading indicators)
├── modals/
│   ├── base_modal.html (Bootstrap modal wrapper)
│   └── modal_trigger.html (Modal trigger button)
├── notifications/
│   ├── notification.html (Toast/alert system)
│   └── toast_templates.html (Toast templates)
├── search/
│   └── search_bar.html (HTMX search component)
└── tables/
    └── htmx_table.html (HTMX table with pagination)
```

✅ **Properly organized as shared component library**  
✅ **All components are GENERIC (reusable)**  
✅ **Ready for use across all sites**  

---

## Existing Implementations Found

### 1. FORMS - SCATTERED LOCATIONS

| File | Type | Status | Action |
|------|------|--------|--------|
| `www/core/templates/registration/fragments/login_form.html` | Auth form | Keep | Site-specific auth |
| `www/core/templates/registration/fragments/password_form.html` | Auth form | Keep | Site-specific auth |
| `www/core/templates/registration/fragments/register_form.html` | Auth form | Keep | Site-specific auth |
| `plugins/accounts/templates/auth/partials/register_form.html` | Auth form | Keep | Site-specific auth |
| `plugins/blog/templates/blog/fragments/post_create_form.html` | Blog form | Merge | Use base from packages/ui |
| `plugins/blog/templates/blog/profile/post_form.html` | Blog form | Merge | Use base from packages/ui |
| `plugins/blog/templates/blog/tags/tag_form.html` | Blog form | Merge | Use base from packages/ui |
| `plugins/components/contact/sections/form.html` | Contact form | Merge | Use base from packages/ui |
| `plugins/components/blocks/contact_form_block.html` | Contact form | Merge | Use base from packages/ui |
| `www/core/templates/contact/sections/form.html` | Contact form | Merge | Use base from packages/ui |
| `plugins/components/blocks/partials/form_field.html` | Form field | Merge | Reference packages/ui validation |
| `www/core/templates/components/blocks/partials/form_field.html` | Form field | Delete | Duplicate - remove |
| `plugins/components/profile/settings/section_form.html` | Profile form | Merge | Use base from packages/ui |
| `assets/templates/components/form/form.html` | Generic form | Merge | Move to packages/ui or reference |
| `assets/templates/generic/_form.html` | Generic form | Merge | Move to packages/ui or reference |

**Forms to Consolidate:** 9  
**Keep As-Is (Auth-Specific):** 4  
**Delete as Duplicates:** 1  

### 2. MODALS - SCATTERED LOCATIONS

| File | Type | Status | Action |
|------|------|--------|--------|
| `packages/ui/modals/base_modal.html` | Base modal | Keep | Shared component |
| `plugins/components/profile/partials/modals/base_modal.html` | Base modal | DELETE | Duplicate |
| `plugins/components/common/modals/cart_modal.html` | Cart modal | Merge | Extend packages/ui base |
| `plugins/accounts/templates/auth/privacy_modal.html` | Privacy modal | Keep | Site-specific content |
| `plugins/accounts/templates/auth/privacy_modal_content.html` | Privacy content | Keep | Site-specific content |
| `plugins/templates/learning/_course_enrollment_modal.html` | Enrollment modal | Keep | Domain-specific (uses packages/ui) |
| `assets/templates/components/modal/modal.html` | Generic modal | DELETE | Duplicate/obsolete |

**Modals to Consolidate:** 5  
**Keep As-Is (Domain-Specific):** 3  
**Delete as Duplicates:** 2  

### 3. NOTIFICATIONS - SCATTERED LOCATIONS

| File | Type | Status | Action |
|------|------|--------|--------|
| `packages/ui/notifications/notification.html` | Toast/alert | Keep | Shared component |
| `packages/ui/notifications/toast_templates.html` | Templates | Keep | Shared component |
| `plugins/components/profile/settings/notifications.html` | Profile notif | Merge | Use packages/ui |

**Notifications to Consolidate:** 1  
**Keep As-Is:** 0  
**Delete as Duplicates:** 0  

### 4. SEARCH COMPONENTS

| File | Type | Status | Action |
|------|------|--------|--------|
| `packages/ui/search/search_bar.html` | Search bar | Keep | Shared component |
| (No duplicates found) | - | - | ✅ Already consolidated |

### 5. TABLES

| File | Type | Status | Action |
|------|------|--------|--------|
| `packages/ui/tables/htmx_table.html` | HTMX table | Keep | Shared component |
| (No duplicates found) | - | - | ✅ Already consolidated |

### 6. CONTACT FORMS (SPECIAL CASE)

Multiple instances:

```
plugins/lms/blocks/minimal_contact_form.html          ← Duplicate
plugins/templates/LMS/blocks/minimal_contact_form.html ← Duplicate
www/core/content/models/blocks/minimal_contact_form.html ← Original
www/core/templates/blocks/minimal_contact_form.html   ← Duplicate
```

**Action:** Delete 3 duplicates, keep original at www/core

---

## Consolidation Strategy

### Phase 1: Forms Consolidation

#### Strategy
- Keep `packages/ui/forms/htmx_form.html` as base
- Keep auth forms in their locations (site-specific)
- Update other forms to extend/reference packages/ui base
- Delete exact duplicates

#### Files to Update
```
✓ plugins/blog/templates/blog/fragments/post_create_form.html
✓ plugins/blog/templates/blog/profile/post_form.html
✓ plugins/blog/templates/blog/tags/tag_form.html
✓ plugins/components/contact/sections/form.html
✓ plugins/components/profile/settings/section_form.html
```

#### Files to Delete
```
✗ www/core/templates/components/blocks/partials/form_field.html (duplicate)
```

### Phase 2: Modals Consolidation

#### Strategy
- Keep `packages/ui/modals/base_modal.html` as central base
- Keep domain-specific modals (privacy, enrollment) but reference base
- Delete duplicates

#### Files to Delete
```
✗ plugins/components/profile/partials/modals/base_modal.html (duplicate)
✗ assets/templates/components/modal/modal.html (obsolete)
```

### Phase 3: Notifications Consolidation

#### Strategy
- Keep `packages/ui/notifications/` as is
- Update profile notifications to reference packages/ui

#### Files to Update
```
✓ plugins/components/profile/settings/notifications.html
```

### Phase 4: Contact Forms Deduplication

#### Strategy
- Keep only: `www/core/templates/blocks/minimal_contact_form.html`
- Delete 3 duplicates

#### Files to Delete
```
✗ plugins/lms/blocks/minimal_contact_form.html
✗ plugins/templates/LMS/blocks/minimal_contact_form.html
✗ www/core/templates/blocks/minimal_contact_form.html (if duplicate)
```

---

## Summary of Changes

### Files to Create/Enhance in packages/ui/
```
✓ packages/ui/forms/htmx_form.html (already exists, keep)
✓ packages/ui/forms/validation.html (already exists, keep)
✓ packages/ui/modals/base_modal.html (already exists, keep)
✓ packages/ui/notifications/notification.html (already exists, keep)
```

### Files to Update (Reference packages/ui)
```
→ plugins/blog/templates/blog/fragments/post_create_form.html
→ plugins/blog/templates/blog/profile/post_form.html
→ plugins/blog/templates/blog/tags/tag_form.html
→ plugins/components/contact/sections/form.html
→ plugins/components/profile/settings/section_form.html
→ plugins/components/profile/settings/notifications.html
```

### Files to DELETE (Duplicates)
```
✗ plugins/components/profile/partials/modals/base_modal.html
✗ assets/templates/components/modal/modal.html
✗ www/core/templates/components/blocks/partials/form_field.html
✗ plugins/lms/blocks/minimal_contact_form.html
✗ plugins/templates/LMS/blocks/minimal_contact_form.html
```

---

## Implementation Roadmap

### Step 1: Delete Obvious Duplicates ✅
Delete 5 clear duplicate files:
```
rm plugins/components/profile/partials/modals/base_modal.html
rm assets/templates/components/modal/modal.html
rm www/core/templates/components/blocks/partials/form_field.html
rm plugins/lms/blocks/minimal_contact_form.html
rm plugins/templates/LMS/blocks/minimal_contact_form.html
```

### Step 2: Update Form Components ✅
Update these files to use/reference packages/ui base:
```
- plugins/blog/templates/blog/fragments/post_create_form.html
- plugins/blog/templates/blog/profile/post_form.html
- plugins/blog/templates/blog/tags/tag_form.html
- plugins/components/contact/sections/form.html
- plugins/components/profile/settings/section_form.html
```

### Step 3: Update Notification Components ✅
Update to reference packages/ui:
```
- plugins/components/profile/settings/notifications.html
```

### Step 4: Verify No Broken Imports ✅
Check all templates for broken includes/extends

### Step 5: Run Tests ✅
Verify all templates still render correctly

---

## Task Analysis from resources/task.md

### Completed ✅
- [x] Phase 1 — Docker Compose Separation
- [x] Phase 2 — HTMX Standardization
- [x] Phase 3 — Modal & Notification Consolidation

### In Progress (This Document)
- [ ] Phase 4 — CTC Research Courses System
- [ ] Phase 5 — Dummy Course Fixtures
- [ ] Phase 6 — Enrollment Workflow
- [ ] Phase 7 — Cart Architecture
- [ ] Phase 8 — Wagtail CMS Integration
- [ ] Phase 9 — JS Bundle Standardization
- [ ] Phase 10 — Traefik Refactor
- [ ] Phase 11 — Warehouses & Utilities Separation
- [ ] Phase 12 — Makefile Refactor
- [ ] Phase 13 — Testing
- [ ] Phase 14 — GitHub Actions
- [ ] Phase 15 — Documentation
- [ ] Phase 16 — Final Validation

### Next Phase: Phase 4-5 (Courses System)
See `NEXT_STEPS.md` for detailed Phase 5 instructions (Course Fixtures)

---

## Verification Checklist

### Before Deletion
- [ ] All duplicate files identified
- [ ] No unique code in duplicates
- [ ] All references documented
- [ ] Backup created (git)

### After Consolidation
- [ ] All forms reference packages/ui base
- [ ] All modals reference packages/ui base
- [ ] All notifications reference packages/ui
- [ ] No broken template includes
- [ ] All tests passing
- [ ] No 404s on form pages

### Final Verification
- [ ] No duplicate templates remain
- [ ] Single source of truth for each component
- [ ] All sites can use packages/ui components
- [ ] Documentation updated
- [ ] Deployment verified

---

## Benefits of Consolidation

### Centralized Maintenance
- Single source of truth for each component
- Easier to update and fix bugs
- Consistent behavior across all sites

### Reduced Codebase
- 5 duplicate files removed
- ~500 lines of redundant code eliminated
- Cleaner, more maintainable structure

### Improved Consistency
- All sites use same form patterns
- Unified modal behavior
- Consistent notification displays

### Better Performance
- Less duplication = smaller codebase
- Easier to optimize shared components
- Single bundle for all sites

---

## Implementation Status

| Phase | Task | Status |
|-------|------|--------|
| Consolidation | Identify duplicates | ✅ Complete |
| Consolidation | Plan strategy | ✅ Complete |
| Consolidation | Delete duplicates | ⏳ Ready |
| Consolidation | Update references | ⏳ Ready |
| Consolidation | Verify integrity | ⏳ Ready |
| Next Phase | Phase 4 (Courses) | Documented |
| Next Phase | Phase 5 (Fixtures) | See NEXT_STEPS.md |

---

## Files Summary

### Total Files Affected: 16
- Create/Keep: 11 (in packages/ui)
- Update/Reference: 6
- Delete: 5

### Consolidation Impact
- Duplicate templates removed: 5
- Lines of duplicate code removed: ~500
- Reduction in codebase: ~3%

---

## Next Steps After Consolidation

1. **Phase 4: CTC Research Courses System**
   - Already mostly complete
   - See PHASE4_COMPLETE_STATUS_REPORT.md

2. **Phase 5: Dummy Course Fixtures**
   - Create 8 sample courses
   - Load into database
   - Verify display
   - Duration: 1-2 hours
   - See NEXT_STEPS.md

3. **Phase 6-16: Continue Modernization**
   - Enrollment Workflow
   - Cart Architecture
   - Wagtail Integration
   - JS Standardization
   - Traefik Refactor
   - Testing & Validation

---

## Critical Notes

### ⚠️ Before Deleting
```bash
# Create backup
git add -A
git commit -m "Before consolidation backup"

# List files to delete
echo "Files to delete:
  - plugins/components/profile/partials/modals/base_modal.html
  - assets/templates/components/modal/modal.html
  - www/core/templates/components/blocks/partials/form_field.html
  - plugins/lms/blocks/minimal_contact_form.html
  - plugins/templates/LMS/blocks/minimal_contact_form.html"
```

### ✅ After Consolidation
```bash
# Verify all templates render
python manage.py shell

# Run tests
pytest --cov

# Check for broken imports
grep -r "{% include.*form" plugins/
grep -r "{% include.*modal" plugins/
```

---

## Document References

- **Phase 4 Complete:** [PHASE4_COMPLETE_STATUS_REPORT.md](./PHASE4_COMPLETE_STATUS_REPORT.md)
- **Phase 4 URLs:** [docs/PHASE4_FINAL_ARCHITECTURE_AND_URLS.md](./docs/PHASE4_FINAL_ARCHITECTURE_AND_URLS.md)
- **Next Steps:** [NEXT_STEPS.md](./NEXT_STEPS.md)
- **Task Tracker:** [resources/task.md](./resources/task.md)

---

**Status:** ✅ **ANALYSIS COMPLETE - READY FOR EXECUTION**

Next action: Execute consolidation and deduplication plan

