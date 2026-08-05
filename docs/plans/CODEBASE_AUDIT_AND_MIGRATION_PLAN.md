# Structa Cloud — Codebase Audit & Migration Recommendations
> Generated: August 2, 2026  
> Scope: `projects/lms-fusion/backend/apps/` + `projects/cms-fusion/backend/apps/`  
> Framework target: django-fusion (canonical imports, no shims/re-exports)

---

## 🔴 Priority 1 — Immediate (high-impact, low-risk)

### 1.1 Delete triplicated management commands (10 commands × 3 apps)
Each of these commands is identically duplicated across 3 apps in each project (6 copies total across LMS+CMS):

| Command | Duplicates |
|---------|-----------|
| `verify_deployment.py` | `core/`, `handlers/`, `accounts/` |
| `validate_config.py` | `core/`, `handlers/`, `accounts/` |
| `update_site_settings.py` | `core/`, `handlers/`, `accounts/` |
| `test_email_csv.py` | `core/`, `handlers/`, `accounts/` |
| `send_test_email.py` | `core/`, `handlers/`, `accounts/` |
| `send_invites.py` | `core/`, `handlers/`, `accounts/` |
| `send_error_report.py` | `core/`, `handlers/`, `accounts/` |
| `run_campaign_worker.py` | `core/`, `handlers/`, `accounts/` |
| `create_privacy_policies.py` | `core/`, `handlers/`, `accounts/` |
| `create_groups_from_csv.py` | `core/`, `handlers/`, `accounts/` |

**Action**: Keep only the `apps/core/` copy. Delete from `handlers/` and `accounts/` in both LMS and CMS. Verify the remaining copy imports canonical paths from django-fusion (most already use `django_fusion.management.commands.base.BaseCommand`).

### 1.2 Remove 6 shim/re-export files
These files only re-export symbols from django-fusion. Replace ALL consumers with canonical imports, then delete:

| File | Re-exports | Canonical import |
|------|-----------|-----------------|
| `apps/content/models/base.py` | `BaseModel as DefaultBase` | `from django_fusion.models.base import BaseModel as DefaultBase` |
| `apps/core/middleware/privacy.py` | `PrivacyConsentMiddleware` | `from django_fusion.core.middlewares.privacy_consent import PrivacyConsentMiddleware` |
| `apps/pages/branding/context_processors.py` | `fusion_branding_context` | `from django_fusion.contrib.branding.context_processors import fusion_branding_context` |
| `apps/pages/accounts/models/manage/__init__.py` | `Event`, `Service` | Direct imports from `apps.handlers.models.manage.*` |
| `apps/pages/accounts/management/middleware/privacy.py` | `PrivacyConsentMiddleware` | `from django_fusion.core.middlewares.privacy_consent import PrivacyConsentMiddleware` |
| `apps/pages/accounts/management/services/groups.py` | `RoleHierarchyManager` | `from django_fusion.management.services.groups import RoleHierarchyManager` |

### 1.3 Fix non-canonical relative imports in managers
The `apps/pages/accounts/management/managers/enrollments.py` still uses `from ..models.courses.detail import LessonProgress` — the canonical path is `from apps.pages.lms.models.courses.progress import LessonProgress`.

---

## 🟠 Priority 2 — Short-term (significant deduplication)

### 2.1 Merge duplicate service layers
Both projects have 3 duplicate service layers importing from each other:

```
apps/core/services/           → own implementations
apps/handlers/management/services/  → imports from apps.pages.accounts.management.services
apps/pages/accounts/management/services/  → canonical (keep this)
apps/pages/profile/services/  → imports from apps.pages.accounts.management.services
```

**Action**: Delete `apps/core/services/email/`, `apps/core/services/messages.py`, `apps/core/services/certificates.py`, `apps/core/services/notes.py` — they are duplicated from `apps/pages/accounts/management/services/`. Do the same for `apps/handlers/management/services/` equivalents. Keep only `apps/pages/accounts/management/services/` as canonical.

### 2.2 Delete duplicate models between LMS and CMS
These model sets are identical between both projects — move shared base models to django-fusion:

| Model file | Found in | Action |
|-----------|---------|--------|
| `handlers/models/profiles/note.py` | both LMS + CMS | Identical. If not already in django-fusion, migrate base class there. |
| `handlers/models/profiles/message.py` | both LMS + CMS | Same pattern. |
| `handlers/models/profiles/certificate.py` | both LMS + CMS | Same pattern. |
| `handlers/models/manage/event.py` | both LMS + CMS | Same pattern. Already uses `django_fusion.models.base.BaseModel`. |
| `handlers/models/manage/service.py` | both LMS + CMS | Same pattern. |
| `handlers/models/manage/company.py` | both LMS + CMS | Same pattern. |

### 2.3 Consolidate app structure — CMS should mirror LMS
LMS has richer structure. CMS is missing:
- `apps/core/filters/`, `apps/core/managers/`, `apps/core/processors/`, `apps/core/schemas/`, `apps/core/services/`, `apps/core/snippets/`, `apps/core/views/`
- `apps/components/` (block components)
- `apps/pages/components/`, `apps/pages/events/`

CMS has unique: `apps/handlers/managers/`, `apps/handlers/processors/`, `apps/handlers/services/`

**Action**: Decide whether to merge into shared `apps/` or keep project-specific. Current divergence suggests both projects should converge to the same app structure under `projects/configs/` or a shared `apps/` location.

---

## 🟡 Priority 3 — Medium-term (architectural improvements)

### 3.1 Duplicate file names across apps (high collision risk)
These filenames appear in 5+ different app directories, increasing the risk of import shadowing:

| File | LMS count | CMS count |
|------|----------|----------|
| `tags.py` | 16 | 17 |
| `privacy.py` | 14 | 11 |
| `notes.py` | 10 | 8 |
| `urls.py` | 9 | 9 |
| `base.py` | 9 | 8 |
| `courses.py` | 7 | 6 |
| `certificates.py` | 7 | 6 |
| `services.py` | 7 | 6 |
| `enrollment.py` | 6 | 6 |
| `profile.py` | 6 | 5 |

**Action**: Rename ambiguous files with qualified names (e.g., `notes.py` → `notes_service.py` or `note_models.py` depending on role).

### 3.2 Migrate cross-app service dependencies to django-fusion
These services are imported from hardcoded app paths. They should be in django-fusion:

| Service | Current path | Used by |
|---------|-------------|---------|
| `CertificateService` | `apps.pages.accounts.management.services` | profile, lms, handlers |
| `MessageService` | `apps.pages.accounts.management.services` | profile, handlers |
| `PersonService` | `apps.pages.accounts.management.services` | profile |
| `NotificationService` | `apps.pages.accounts.management.services` | handlers, profile |
| `NotesService` | `apps.pages.accounts.management.services` | handlers, profile |
| `EnrollmentManager` | `apps.pages.lms.management.managers` | lms, profile |

**Action**: Extract base classes/traits into `django_fusion.services.*` and `django_fusion.management.managers.*`. Site projects keep only concrete subclasses.

### 3.3 Remove duplicate `populate_*` and `send_bulk_*` commands
These already exist in django-fusion and the site copies just re-import:

- `populate_homepage.py` → `from django_fusion.management.commands.populate_homepage import Command as FusionCommand`
- `populate_courses.py` → same pattern
- `populate_content.py` → same pattern
- `send_bulk_emails.py` → same pattern
- `verify_content.py` → same pattern

**Action**: These are thin wrappers. If no site-specific overrides exist, delete them and add the django-fusion command directly to the app's management. If site-specific logic exists in the wrapper (check diff), merge it upstream.

### 3.4 Consolidate `apps/domain/` — already uses django-fusion heavily
`apps/domain/` models already import from django-fusion for:
- `AbstractWorkspace`, `AbstractCertificationTemplate`, `AbstractCoupon`, `AbstractNewsletter`, `AbstractEmailSettings`, `AbstractBrandSettings`, `AbstractGlobalSettings`, `DefaultBase`, `TaggedPerson`, `BaseTag`, `BaseTagCategory`

Verify domain models have no site-specific field additions that should be upstreamed.

---

## 🟢 Priority 4 — Long-term (code quality)

### 4.1 Migrate inter-app model imports to django-fusion
Many cross-app model imports could be eliminated by having django-fusion provide abstract bases:

```
apps/pages/blog/models/index.py → from apps.pages.accounts.models.profiles.contact import Person
apps/content/models/pages/base.py → from apps.handlers.models.manage.service import Service
apps/pages/lms/management/managers/module.py → from apps.pages.accounts.models import LessonProgress
apps/core/site/blog.py → from apps.pages.blog.forms import ...
```

### 4.2 Standardize on direct canonical imports
Current mixed usage: some files use `from ..models import X`, others use `from apps.pages.lms.models import X`. Standardize ALL to direct imports: `from apps.<app>.<module> import <Symbol>`.

### 4.3 Delete empty/unused directories
Check and remove:
- `apps/core/processors/selectors.py` — commented-out imports
- `apps/handlers/management/processors/contacts.py` — commented-out imports
- Any `__init__.py` files in directories with no other content

### 4.4 Remove `SILENCED_SYSTEM_CHECKS` references from docs
Found in:
- `docs/plans/legacy/merge-cleanup.md`
- `docs/dev/technical/architecture/architecture-notes.md`

### 4.5 Update stale comment references
`configs/settings/ENV` → `configs/Env` in:
- 6 copies of `validate_config.py` across LMS + CMS
- `startup.py` in both projects
- `tools/README.md` in both projects
- `management/README.md`

---

## 📊 Summary Statistics

| Category | Count |
|----------|-------|
| Triplicated management commands (per project) | 10 × 3 = 30 files |
| Shims/re-exports to remove | 6 |
| Duplicate service layers | 3 (core, handlers, accounts) |
| Duplicate file names (5+ occurrences) | 10 filenames |
| Cross-app service dependencies to migrate | 6 |
| Thin wrapper commands (already in django-fusion) | 5 |
| Stale comment references | ~15 files |

---

## 🛠️ Implementation Tips

1. **Work one app at a time**: Start with `apps/core/` then `apps/handlers/` then `apps/accounts/`.
2. **Test after each deletion**: Run `DJANGO_SETTINGS_MODULE=settings python -c "import django; django.setup()"` to catch import errors immediately.
3. **Use `git mv` for renames**: Preserves git history.
4. **Check all consumers before deleting**: Use `rg "from apps\.<old_path>"` to find all imports of a module you're about to move/delete.
5. **Prefer django-fusion canonical imports**: `from django_fusion.X.Y import Z` over `from apps.X.Y import Z` whenever the symbol already exists in django-fusion.
6. **No shims**: Delete shim files entirely — don't leave forwarding imports.
7. **Bulk comment updates**: Use `sed -i 's|configs/settings/ENV|configs/Env|g'` but target specific files, not whole directories (avoids timeouts).
8. **Run the full Django check**: `python manage.py check --deploy` after structural changes.
