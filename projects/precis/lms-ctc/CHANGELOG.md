# Precis LMS changelog

## 2026-08-11 - Active deployment and plan closeout

### Changed

- Confirmed `projects/precis/main/` as the canonical LMS runtime after the former
  LMS-Fusion/CMS-Fusion consolidation.
- Added the project-owned `/api/fusion/health` and slash-terminated alias used
  by direct and Traefik deployment smoke checks.
- Made fixture loading explicit for the shipped canonical dump. The default
  command no longer silently loads historical fixture data.
- Rebuilt the backend/frontend images and verified API and rendered page routes
  through the Traefik host.

### Verification

- Focused API and fixture tests: 77 passed.
- Direct and proxy API/page curl checks returned HTTP 200.
- Backend, frontend, worker, PostgreSQL, Redis, and Traefik containers were
  running with no service restarts at closeout.

## 2026-07-30 - ceptor-ai cleanup + enhanced test coverage

### ceptor-ai dependency fully removed
- 0 ceptor_ai imports remaining in any fusion project
- Local models (Organization, Contact, ContactEmail, ContactPhone, Team, Workspace) ported from ceptor_ai
- PrivacyConsentMiddleware, PaymentProcessingMixin, ProfileMixin, dispatch_job stubs created locally
- Newsletter system already fully native (Subscriber, Campaign, email templates)

### tests: 113 tests, 0 failures
- Existing: 86 tests (smoke, API, domain models, fixture content)
- Enhanced: 27 new tests (test_enhanced_api.py)
  - CORS headers verification
  - HTMX request handling (HX-Request header)
  - Error handling (404, 405/400, bad params)
  - Trailing slash redirects for all endpoints
  - Branding detail structure (colors, site_name)
  - Pages fragment/data sub-endpoints
  - Courses filters structure validation
  - Content-Type: application/json on all endpoints
  - Security headers (X-Content-Type-Options)
  - Fusion assets endpoint accessibility
- Fixed: 3 trailing-slash failures in test_fixture_content.py

### API endpoints verified
- /api/fusion/health/ ✅
- /api/fusion/branding/ ✅
- /api/pages/ ✅
- /api/pages/<slug>/fragment/ ✅
- /api/pages/<slug>/data/ ✅
- /api/blog/ ✅
- /api/blog/categories/ ✅
- /api/blog/tags/ ✅
- /api/courses/ ✅
- /api/courses/filters/ ✅
- /api/products/ ✅

## 2026-07-26 — Fusion architecture migration (Phase 5 complete)

### django-fusion + django-bolt integration
- Backend API with django-fusion component system
- django-bolt BoltAPI for high-performance endpoints
- Next.js 14 frontend with fusion types/decoder/store/client
- Django server on port 5076, Next.js on port 3076

### Template reorganization
- App-specific templates moved to plugins/<app>/templates/
- Site-root templates remain in backend/templates/
- SCSS theme single source-of-truth in assets/styles/fusion-theme.scss
- Compiled CSS output to backend/assets/static/css/fusion.css

### Validation
- make check: ✅ (exit 0)
- Backend tests: 135 passed
- Frontend build: ✅ compiled successfully
- Workspace tests: 50 passed
