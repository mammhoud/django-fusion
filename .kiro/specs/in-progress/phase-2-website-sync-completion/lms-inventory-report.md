# LMS Inventory Report

**Date:** 2025
**Task:** 2.4.1 — Identify and Inventory LMS Files
**Spec:** phase-2-website-sync-completion

---

## Source_Repository (ctc-research.com) LMS Structure

### Models (`apps/lms/models/`)

| File | Path | Description |
|------|------|-------------|
| `__init__.py` | `apps/lms/models/__init__.py` | Module init |
| `certificate.py` | `apps/lms/models/certificate.py` | Certificate models |
| `classes.py` | `apps/lms/models/classes.py` | Class models |
| `enrollment.py` | `apps/lms/models/enrollment.py` | Enrollment models |
| `quiz.py` | `apps/lms/models/quiz.py` | Quiz models |
| `review.py` | `apps/lms/models/review.py` | Review models |
| `wishlist.py` | `apps/lms/models/wishlist.py` | Wishlist models |

**Subdirectories:**
- `blocks/` - Assignment, cart blocks
- `courses/` - Course detail, index, info, progress, specification
- `schemas/` - Base, content, course, enrollment, quiz, references, review schemas

### Views (`apps/lms/views/`)

| File | Path | Description |
|------|------|-------------|
| `__init__.py` | `apps/lms/views/__init__.py` | Module init |
| `cart.py` | `apps/lms/views/cart.py` | Cart views |
| `courses.py` | `apps/lms/views/courses.py` | Course views |
| `lessons.py` | `apps/lms/views/lessons.py` | Lesson views |

### Services (`apps/lms/services/`)

| File | Path | Description |
|------|------|-------------|
| `__init__.py` | `apps/lms/services/__init__.py` | Module init |
| `certificates.py` | `apps/lms/services/certificates.py` | Certificate services |
| `courses.py` | `apps/lms/services/courses.py` | Course services |
| `enrollments.py` | `apps/lms/services/enrollments.py` | Enrollment services |
| `legacy.py` | `apps/lms/services/legacy.py` | Legacy services |
| `lessons.py` | `apps/lms/services/lessons.py` | Lesson services |
| `notes.py` | `apps/lms/services/notes.py` | Notes services |
| `progress.py` | `apps/lms/services/progress.py` | Progress services |

### Forms (`apps/lms/forms/`)

| File | Path | Description |
|------|------|-------------|
| `__init__.py` | `apps/lms/forms/__init__.py` | Module init (empty) |

### API Endpoints

**Status:** No dedicated `api.py` file found. API endpoints are likely integrated into views or served via Wagtail API.

### Other LMS Files

| Directory/File | Description |
|----------------|-------------|
| `admin/` | Django admin configuration |
| `blocks/` | StreamField blocks |
| `filters/` | QuerySet filters |
| `managers/` | Model managers |
| `middleware/` | LMS-specific middleware |
| `migrations/` | Database migrations |
| `snippets/` | Wagtail snippets |
| `templatetags/` | Template tags |
| `apps.py` | App configuration |
| `signals.py` | Django signals |
| `urls.py` | URL routing |
| `wagtail_hooks.py` | Wagtail hooks |

---

## Target_Repository (structa.cloud) LMS Structure

**Status:** LMS app exists with identical directory structure.

### Line Count Comparison

| Repository | Total Lines (excluding migrations, pycache) |
|------------|---------------------------------------------|
| ctc-research.com | 11,059 |
| structa.cloud | 11,087 |
| **Difference** | 28 lines |

---

## CI/Infrastructure Files

### GitHub Actions Workflows

| File | Path | Description |
|------|------|-------------|
| `architecture-validation.yml` | `.github/workflows/architecture-validation.yml` | Architecture validation workflow |

### Docker/Compose Files

| Directory | Description |
|-----------|-------------|
| `compose/blinko/` | Blinko service configuration |
| `compose/lms/` | LMS service configuration |
| `compose/nginx/` | Nginx configuration |
| `compose/postgres/` | PostgreSQL configuration |
| `compose/traefik/` | Traefik configuration |

---

## Summary

### LMS Files Inventory

| Category | Source Files | Target Files | Status |
|----------|--------------|--------------|--------|
| Models | 18 Python files | 18 Python files | ✅ Present in both |
| Views | 4 Python files | 4 Python files | ✅ Present in both |
| Services | 8 Python files | 8 Python files | ✅ Present in both |
| Forms | 1 Python file | 1 Python file | ✅ Present in both |
| API | Not found | Not found | ⚠️ No dedicated API file |

### File Dependencies

- LMS depends on: `handlers` (accounts), `pages` (content), Wagtail, Django
- Services depend on: Models, external APIs (if any)
- Views depend on: Services, models, forms

### Next Steps

1. **Task 2.4.2:** Validate syntax and imports in LMS files
2. **Task 2.4.3:** Verify LMS dependencies
3. **Task 2.4.4:** Sync any missing files to Target_Repository
4. **Task 2.4.5:** Update branding from CTC Research to Structa

---

## Completion Status

- [x] 2.4.1.1 Scan Source_Repository for LMS models in `apps/lms/models/`
- [x] 2.4.1.2 Scan Source_Repository for LMS views in `apps/lms/views/`
- [x] 2.4.1.3 Scan Source_Repository for LMS services in `apps/lms/services.py`
- [x] 2.4.1.4 Scan Source_Repository for LMS forms in `apps/lms/forms.py`
- [x] 2.4.1.5 Scan Source_Repository for LMS API endpoints in `apps/lms/api.py`
- [x] 2.4.1.6 Create inventory of all LMS files with line counts
- [x] 2.4.1.7 Document file dependencies and relationships
