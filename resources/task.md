# Repository Modernization — Task Tracker

## Phase 1 — Docker Compose Separation (VERIFY)
- [x] Verify ctc-research/docker-compose.yml exists and is valid
- [x] Verify lms-demo/docker-compose.yml exists and is valid
- [x] Verify VResume/docker-compose.yml exists and is valid
- [x] Verify compose/docker-compose.yml is clean (no website services)
- [x] Confirm no duplicated services
- [x] Run `docker compose config` validation

## Phase 2 — HTMX Standardization
- [x] Create `packages/ui/` directory structure
- [x] Create shared HTMX base fragment
- [x] Create shared loading states template
- [x] Create shared error handler template
- [x] Create shared search bar template
- [x] Create shared HTMX form template
- [x] Create shared HTMX table template
- [x] Update settings.py for all 3 sites to include packages/ui
- [x] Verify templates discoverable

## Phase 3 — Modal & Notification Consolidation
- [x] Move notification.html to packages/ui/notifications/
- [x] Move base_modal.html to packages/ui/modals/
- [x] Create standardized modal trigger pattern
- [x] Ensure all toast types (success/error/warning/info)
- [x] Update template includes across all sites
- [x] Remove duplicate templates

## Phase 4 — CTC Research Courses System
- [ ] Create CourseCategory model (if needed, using Specialization)
- [ ] Create CourseTag model
- [ ] Create HTMX catalog template (catalog.html)
- [ ] Create grid view partial (_grid.html)
- [ ] Create list view partial (_list.html)
- [ ] Create search results partial (_search_results.html)
- [ ] Create filters partial (_filters.html)
- [ ] Create pagination partial (_pagination.html)
- [ ] Add catalog URL routes
- [ ] Create grid/list toggle view
- [ ] Verify HTMX search works

## Phase 5 — Dummy Course Fixtures
- [ ] Create categories.json fixture
- [ ] Create courses.json fixture (8 courses)
- [ ] Create load_course_fixtures management command
- [ ] Verify loaddata succeeds

## Phase 6 — Enrollment Workflow
- [ ] Create CourseEnrollmentLead model
- [ ] Create enrollment lead form
- [ ] Create HTMX enrollment modal template
- [ ] Create enrollment lead view
- [ ] Register EnrollmentViewSet in wagtail_hooks
- [ ] Add CourseEnrollmentLeadViewSet
- [ ] Create migration

## Phase 7 — Cart Architecture
- [ ] Create docs/cart-implementation.md
- [ ] Create PaymentProvider ABC
- [ ] Create StripeProvider
- [ ] Create PaymobProvider
- [ ] Create PayPalProvider
- [ ] Create provider registry

## Phase 8 — Wagtail CMS Integration
- [ ] Register EnrollmentSnippetGroup
- [ ] Add CourseEnrollmentLeadViewSet
- [ ] Add notification management ViewSet
- [ ] Verify permissions and search support

## Phase 9 — JS Bundle Standardization
- [ ] Create/standardize app.js
- [ ] Create/standardize htmx.js
- [ ] Create/standardize notifications.js
- [ ] Create/standardize modals.js
- [ ] Remove duplicate JS
- [ ] Verify bundles load on all sites

## Phase 10 — Traefik Refactor
- [ ] Create infra/traefik/ directory
- [ ] Move traefik config to infra/
- [ ] Update compose references
- [ ] Verify SSL config
- [ ] Verify HTTP→HTTPS redirect config

## Phase 11 — Warehouses & Utilities Separation
- [ ] Create warehouses/ directory
- [ ] Create utilities/ directory
- [ ] Move warehouse compose
- [ ] Move utilities compose
- [ ] Update root docker-compose.yml includes

## Phase 12 — Makefile Refactor
- [ ] Clean up duplicate targets
- [ ] Add make up/down/build/logs
- [ ] Add make ctc-up/ctc-test
- [ ] Add make lms-up/lms-test
- [ ] Add make vresume-up/vresume-test
- [ ] Verify all commands

## Phase 13 — Testing
- [ ] Add course model tests
- [ ] Add enrollment lead tests
- [ ] Add HTMX view tests
- [ ] Add notification rendering tests
- [ ] Create Playwright smoke tests
- [ ] Run pytest

## Phase 14 — GitHub Actions
- [ ] Update test.yml with lint/mypy/coverage
- [ ] Create smoke.yml for Playwright
- [ ] Verify workflow definitions

## Phase 15 — Documentation
- [ ] Create docs/ctc-research/ docs
- [ ] Create docs/lms-demo/ docs
- [ ] Create docs/VResume/ docs

## Phase 16 — Final Validation
- [ ] Docker compose config validation
- [ ] Pytest passing
- [ ] CMS admin accessible
- [ ] HTMX components working
- [ ] Fixtures loaded
- [ ] Final report
