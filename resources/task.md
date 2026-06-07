# Repository Modernization — Task Tracker

**Last Updated:** June 7, 2026  
**Status:** 10 of 16 phases complete (Phases A, B, C, 1-6, 9)  
**Progress:** ~75% complete by effort, ready for Phase 7+

## Phase A — Docker Service Naming (COMPLETE ✅)
- [x] Fixed service naming in ctc-research/docker-compose.yml
- [x] Updated Traefik labels to match service names
- [x] Verified routing configuration

## Phase B — SSL Certificate Backup/Restore (COMPLETE ✅)
- [x] Created backup-certs.sh script
- [x] Created restore-certs.sh script
- [x] Integrated with Traefik startup

## Phase 1 — Docker Compose Separation (COMPLETE ✅)
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
- [x] Create CourseCategory model (if needed, using Specialization)
- [x] Create CourseTag model
- [x] Create HTMX catalog template (catalog.html)
- [x] Create grid view partial (_grid.html)
- [x] Create list view partial (_list.html)
- [x] Create search results partial (_search_results.html)
- [x] Create filters partial (_filters.html)
- [x] Create pagination partial (_pagination.html)
- [x] Add catalog URL routes
- [x] Create grid/list toggle view
- [x] Verify HTMX search works

## Phase 5 — Dummy Course Fixtures
- [x] Create categories.json fixture
- [x] Create courses.json fixture (8 courses)
- [x] Create load_course_fixtures management command
- [x] Verify loaddata succeeds

## Phase 6 — Enrollment Workflow
- [x] Create CourseEnrollmentLead model
- [x] Create enrollment lead form
- [x] Create HTMX enrollment modal template
- [x] Create enrollment lead view
- [x] Register EnrollmentViewSet in wagtail_hooks
- [x] Add CourseEnrollmentLeadViewSet
- [x] Create migration

## Phase 7 — Payment Providers (IN PROGRESS 🚀)
- [ ] Create docs/payment-providers.md
- [ ] Create PaymentProvider ABC in services/payment_providers.py
- [ ] Create StripeProvider implementation
- [ ] Create PayPalProvider implementation
- [ ] Create PaymoProvider implementation
- [ ] Create provider registry
- [ ] Create payment models and migrations
- [ ] Create payment views and URLs
- [ ] Integrate with enrollment workflow
- [ ] Test all providers
- [ ] Create payment documentation

## Phase 8 — Wagtail CMS Integration
- [ ] Register EnrollmentSnippetGroup
- [ ] Add CourseEnrollmentLeadViewSet
- [ ] Add notification management ViewSet
- [ ] Verify permissions and search support

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
- [ ] Review current targets (already comprehensive)
- [ ] Add missing targets if any
- [ ] Create MAKEFILE_REFERENCE.md
- [ ] Verify all commands work

## Phase 13 — Testing
- [ ] Add course model tests
- [ ] Add enrollment lead tests
- [ ] Add HTMX view tests
- [ ] Add notification rendering tests
- [ ] Create Playwright smoke tests
- [ ] Run pytest with coverage

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

---

## Summary

**Completed Phases (10 total):**
- ✅ Phase A - Docker service naming
- ✅ Phase B - SSL certificate backup/restore  
- ✅ Phase C - Template consolidation
- ✅ Phase 1 - Docker compose separation
- ✅ Phase 2 - HTMX standardization
- ✅ Phase 3 - Modal & notification consolidation
- ✅ Phase 4 - CTC Research courses system
- ✅ Phase 5 - Dummy course fixtures
- ✅ Phase 6 - Enrollment workflow
- ✅ Phase 9 - JavaScript bundle standardization

**In Progress (1):**
- 🚀 Phase 7 - Payment providers

**Remaining (5):**
- Phase 8, 10, 11, 12, 13, 14, 15, 16

**Estimated Completion:** Today (10-12 hours remaining)
