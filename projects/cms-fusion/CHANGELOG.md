# CMS Fusion — Changelog

## [Unreleased]

### Added

- Unified the CMS Fusion django-fusion asset pipeline: webpack bundle metadata,
  component manifests, and explicit top/bottom links now share one deduplicated
  public-link contract through `FUSION_ASSET_PIPELINE`.
- Documented the source → webpack → collectstatic → browser-link workflow and
  added asset contract coverage for settings, fixtures, media, CSS, and JS.

### Fixed

- CMS fixture loading now resolves directly from `cms-fusion/assets/fixtures`.


## 2026-07-30 — ceptor-ai cleanup + enhanced test coverage

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
- /api/fusion/assets/ ✅

## 2026-07-26 — Fusion architecture migration (Phase 5 complete)

### django-fusion + django-bolt integration
- Backend API with django-fusion component system
- django-bolt BoltAPI for high-performance endpoints
- Next.js 14 frontend with fusion types/decoder/store/client
- Django server on port 5075, Next.js on port 3075

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
