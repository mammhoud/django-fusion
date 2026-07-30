# CTC Research — ceptor-ai Migration Plan
> **Tags:** #ctc-research #ceptor-ai #migration

**Date:** July 30, 2026  
**Scope:** ~80+ files across `projects/ctc-research/`  
**Goal:** Remove all ceptor-ai imports, migrating to native models, Wagtail blocks, and django-fusion equivalents.

---

## 1. Import Category Breakdown

### Category A: Newsletter (4 files) — LOW effort
These files import `ceptor_ai.models.Newsletter` for Wagtail snippet registration.

| File | Current Import | Migration Target |
|------|---------------|------------------|
| `plugins/accounts/snippets/newsletter/content.py` | `from ceptor_ai.models import Newsletter` | `from apps.core.domain.models.newsletter import Subscriber` (native) |
| `www/apps/snippets/newsletter/content.py` | `from ceptor_ai.models import Newsletter` | Same |
| `www/core/handlers/snippets/newsletter/content.py` | `from ceptor_ai.models.settings.newsletter import Newsletter` | Same |
| `plugins/accounts/management/services/email/service.py` | `from ceptor_ai.services.infrastructure.jobs import dispatch_job` | `from django_fusion.tasks import dispatch_task` (or native Celery) |

**Native Newsletter already exists in:**
- `apps/core/domain/models/newsletter/subscriber.py` → `Subscriber` model (pending/confirmed/unsubscribed/bounced states, double opt-in tokens)
- `apps/core/domain/models/newsletter/campaign.py` → `Campaign` model
- `apps/core/domain/models/settings/newsletter.py` → `Newsletter` snippet
- `apps/core/domain/services/communication/newsletter.py` → `send_confirmation_email()`, `send_campaign_email()`
- `apps/pages/urls.py` → `NewsletterSubscribeView` at `/auth/newsletter/subscribe/`

### Category B: Person/Profile Model (25+ files) — MEDIUM effort
The most pervasive import. ctc-research uses `ceptor_ai.models.Person` as its profile model.

| Pattern | Files | Target |
|---------|-------|--------|
| `from ceptor_ai.models import Person` | ~20 files | `from django.contrib.auth import get_user_model; User = get_user_model()` — OR create a local `apps.core.models.Person` proxy |
| `from ceptor_ai.models import Person as Profile` | 3 files | Same |
| `from ceptor_ai.site.mixins import ProfileContextMixin, ProfileOperationsMixin` | 3 files | Create local mixins in `plugins/profile/mixins.py` porting needed logic |
| `from ceptor_ai.models.tags import *` | 6 files (note.py, certificate.py) | Create local Tag/TagCategory models or use `django-taggit` |

**Strategy:** Replace `Person` with Django's `AUTH_USER_MODEL` everywhere. Create a thin `apps.core.models.Person` proxy if Person-specific fields (newsletter_notifications, sms_notifications, etc.) are needed. The CMS/LMS fusion projects already do this with `PROFILE_MODEL = "auth.User"`.

### Category C: Blocks & StreamFields (15+ files) — HIGH effort
ctc-research uses ceptor-ai's custom Wagtail blocks extensively for page content.

| ceptor-ai Block | Import Path | Files Using | Native Replacement |
|-----------------|-------------|-------------|-------------------|
| `EventSectionBlock` | `ceptor_ai.blocks.pages.event` | 3 files | Recreate as local `blocks/pages/event.py` using Wagtail native `StructBlock` |
| `ServicesSectionBlock` | `ceptor_ai.blocks.pages.services` | 3 files | Recreate as local `blocks/pages/services.py` |
| `BaseStreamBlock` | `ceptor_ai.blocks.stream_blocks` | 4 files (blog/post.py, lms/classes.py) | Use Wagtail's native `StreamBlock` directly; create local `blocks/stream_blocks.py` |
| `ContactMethodBlock` | `ceptor_ai.blocks.contact.contact_methods` | 3 files | Recreate locally |
| `FAQSectionBlock` | `ceptor_ai.blocks.partials.faq` | 3 files | Recreate locally |
| `ContactCardBlock` | `ceptor_ai.blocks.contact.contact_card` | 1 file | Recreate locally |
| `MediaGalleryBlock` | `ceptor_ai.blocks.media.gallery` | 1 file | Recreate locally |
| `PageLinkBlock` | `ceptor_ai.blocks.partials.button` | 1 file | Recreate locally |
| `OverviewBlock` | `ceptor_ai.blocks.content.overview` | 1 file (lms/courses) | Recreate locally |

**Strategy:** Create a new `blocks/` package in `plugins/` with individual block files. Each block becomes a Wagtail-native `StructBlock` or `StreamBlock`. Block templates (HTML) can be reused from ceptor-ai's templates directory.

**django-fusion note:** django-fusion does NOT provide contrib Wagtail blocks (no `django_fusion.contrib.blocks`). Blocks must be recreated locally per project or promoted into django-fusion as shared components.

### Category D: Base Classes & Mixins (8 files) — MEDIUM effort

| Import | Files | Target |
|--------|-------|--------|
| `from ceptor_ai.models import ContentBase` | lms/classes.py | Create local `ContentBase` abstract model with shared fields |
| `from ceptor_ai.models import ModelCacheMixin` | lms/courses/info.py | Port caching mixin locally |
| `from ceptor_ai.models import CachingStorage` | lms/views/courses.py | Port locally or use Django's cache framework |
| `from ceptor_ai.models.default import DefaultBase` | contact.py | Create local `DefaultBase` (already has stub in `www/core/content/models/base.py`) |
| `from ceptor_ai.models.default import TemplateRenderMixin` | lms/migrations | Port locally |
| `from ceptor_ai.contrib.snippets.base import BaseSnippetViewSet` | lms/snippets/reviews.py | Use Wagtail's `SnippetViewSet` directly |
| `from ceptor_ai.models import BaseTag, BaseTagCategory` | blog/tags.py (3 files) | Create local `BaseTag`/`BaseTagCategory` or use django-taggit |

### Category E: Core/Infrastructure Services (10 files) — HIGH effort

| Import | Files | Target |
|--------|-------|--------|
| `from ceptor_ai.services.infrastructure.base import BaseService` | 5 files (enrollments, legacy, courses, lessons, person) | Create local `BaseService` abstract class |
| `from ceptor_ai.services.infrastructure.token import TokenService` | 3 files | Port token service logic locally |
| `from ceptor_ai.services.infrastructure.jobs import dispatch_job` | email/service.py (2 files) | Use `django_fusion.tasks` or native Django background tasks |
| `from ceptor_ai.services.content.form_submission import FormSubmissionService` | 1 file | Port locally |
| `from ceptor_ai.handlers.models.forms.submission import FormSubmission` | 1 file | Create local `FormSubmission` model |
| `from ceptor_ai.site.payments import PaymentProcessingMixin` | lms/views/cart.py, lms/urls.py | Port payment processing locally |
| `from ceptor_ai.models import GlobalSettings` | update_site_settings.py | Use Wagtail `SiteSettings` or Django settings |

### Category F: Company/Contact Models (10 files) — MEDIUM effort

| Import | Files | Target |
|--------|-------|--------|
| `from ceptor_ai.handlers.models.manage_company import Organization` | 6 files | Create local `Organization` model or use existing |
| `from ceptor_ai.contrib.core.models import Contact, ContactEmail, ContactPhone` | 5 files | Create local `Contact`/`ContactEmail`/`ContactPhone` models |
| `from ceptor_ai.contrib.core.models import Corporate as Company` | 5 files | Create local `Company` model |
| `from ceptor_ai.models.users.team import Team` | 2 files | Create local `Team` model |
| `from ceptor_ai.models.workspace import Workspace` | 2 files | Create local `Workspace` model or remove |
| `from ceptor_ai.models.users.users import Person` | 1 file | See Category B |

### Category G: Auth/Token (3 files) — LOW effort

| Import | Files | Target |
|--------|-------|--------|
| `from ceptor_ai.workflows.pipelines.models.token import Token` | basic_auth.py, auth_utils.py | Use Django's built-in auth token or `django_fusion` auth |

### Category H: Settings/Config (1 file) — LOW effort

| Import | Files | Target |
|--------|-------|--------|
| `import ceptor_ai.models.cache` and `import ceptor_ai.models.default` | lms/migrations/0001_initial.py | Squash migration to remove ceptor-ai model bases |

**File:** `settings.py` — Remove `"ceptor_ai"` from `INSTALLED_APPS`, `ceptor_ai` from `django_fusion` shims comment, and ceptor-ai model references.

---

## 2. Migration Phases (Recommended Order)

### Phase 1: Foundation (Day 1–2)
**Goal:** Create local replacements for base classes that everything else depends on.

1. **Create `apps/core/models/base.py`** — Local `DefaultBase`, `ContentBase`, `ModelCacheMixin`, `TemplateRenderMixin`
2. **Create `apps/core/services/base.py`** — Local `BaseService` and `TokenService`
3. **Replace `Person` → `AUTH_USER_MODEL`** across all forms, views, services
4. **Remove `"ceptor_ai"` from `INSTALLED_APPS`** in `settings.py`

### Phase 2: Blocks (Day 3–5)
**Goal:** Recreate all ceptor-ai blocks as local Wagtail-native blocks.

1. Create `blocks/` package at `plugins/blocks/`
2. Port each block: `EventSectionBlock`, `ServicesSectionBlock`, `BaseStreamBlock`, `ContactMethodBlock`, `FAQSectionBlock`, `ContactCardBlock`, `MediaGalleryBlock`, `PageLinkBlock`, `OverviewBlock`
3. Copy/resolve templates from ceptor-ai
4. Update all model imports from `ceptor_ai.blocks.*` → `plugins.blocks.*`
5. Squash migrations referencing ceptor-ai model bases

### Phase 3: Domain Models (Day 6–8)
**Goal:** Replace ceptor-ai domain models with local equivalents.

1. **Newsletter** → Already native in CMS/LMS pattern; copy pattern over
2. **Company/Contact/Organization** → Create local models
3. **FormSubmission** → Create local model
4. **Tags** → Create `BaseTag`/`BaseTagCategory` or use django-taggit
5. **GlobalSettings** → Use Wagtail `SiteSettings`

### Phase 4: Services & Mixins (Day 9–10)
**Goal:** Port remaining service-layer code.

1. **PaymentProcessingMixin** → Port to local
2. **FormSubmissionService** → Port to local
3. **ProfileContextMixin / ProfileOperationsMixin** → Create locally
4. **dispatch_job** → Replace with Django background tasks or Celery
5. **PrivacyConsentMiddleware** → Port to local (already exists in `www/core/handlers/middleware/privacy.py`)

### Phase 5: Cleanup & Validation (Day 11–12)
1. Full `rg "ceptor"` search — must return zero results
2. Run `python manage.py check`
3. Run full test suite
4. Remove empty `libs/ceptor-ai` directory ✅ (already done)
5. Update `cli.py` to remove ceptor-ai from LIBS dict
6. Update `pyproject.toml` to remove any ceptor-ai dependency references

---

## 3. File Count Summary

| Category | Files | Effort |
|----------|-------|--------|
| A: Newsletter | 4 | Low |
| B: Person/Profile | 25+ | Medium |
| C: Blocks & StreamFields | 15+ | High |
| D: Base Classes & Mixins | 8 | Medium |
| E: Core Services | 10 | High |
| F: Company/Contact | 10 | Medium |
| G: Auth/Token | 3 | Low |
| H: Settings/Config | 1 | Low |
| **Total** | **~80** | **~12 days** |

---

## 4. Newsletter URL Routing Fix (Current State)

The LMS server at port 5074 has only one newsletter URL registered:

| URL | Status | Code |
|-----|--------|------|
| `GET /auth/newsletter/subscribe/` | CSRF-protected form | 405 (needs POST) |
| `POST /auth/newsletter/subscribe/` | Works (CSRF OK in browser) | 403 (no CSRF token in curl) |
| `/newsletter/confirm/<token>/` | **NOT REGISTERED** | 404 |
| `/newsletter/unsubscribe/<token>/` | **NOT REGISTERED** | 404 |

**Missing routes:** The native newsletter service in `apps/core/domain/services/communication/newsletter.py` generates URLs like `/newsletter/confirm/{token}/` and `/newsletter/unsubscribe/{token}/`, but these URL patterns are not registered in the URL conf. They need to be added to `apps/pages/urls.py` or `www/urls.py`.

---

## 5. Key Risks & Notes

1. **Migration data integrity** — Squashing migrations with ceptor-ai model bases may require careful migration planning
2. **Block templates** — ceptor-ai blocks reference templates (e.g., `blocks/media/simple_image.html`); these templates must be ported too
3. **The `www/` vs `plugins/` duplication** — ctc-research has parallel code in both `www/apps/` and `plugins/` directories; the migration should consolidate into one canonical location
4. **django-fusion does NOT provide blocks** — No `django_fusion.contrib.blocks` exists; all blocks must be local to ctc-research
5. **ceptor-ai is already removed from libs/** — ✅ The empty directory is gone; no runtime risk from stale imports (they'll fail clearly)
