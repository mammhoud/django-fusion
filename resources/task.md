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

## Phase 7 — Payment Providers (COMPLETE ✅)
- [x] Create docs/payment-providers.md
- [x] Create PaymentProvider ABC in services/payment_providers.py
- [x] Create StripeProvider implementation
- [x] Create PayPalProvider implementation
- [x] Create PaymoProvider implementation
- [x] Create provider registry
- [x] Create payment models and migrations
- [x] Create payment views and URLs
- [x] Integrate with enrollment workflow
- [x] Test all providers
- [x] Create payment documentation

## Phase 8 — Wagtail CMS Integration (COMPLETE ✅)
- [x] Register EnrollmentSnippetGroup
- [x] Add PaymentTransactionViewSet
- [x] Add PaymentRefundViewSet
- [x] Add PaymentWebhookLogViewSet
- [x] Configure permissions and search support
- [x] Add filtering and export capabilities
- [x] Create comprehensive documentation

## Phase 10 — Traefik Refactor (COMPLETE ✅)
- [x] Create infra/traefik/ directory
- [x] Move traefik config to infra/
- [x] Update compose references
- [x] Verify SSL config
- [x] Verify HTTP→HTTPS redirect config

## Phase 11 — Warehouses & Utilities Separation (COMPLETE ✅)
- [x] Create warehouses/ directory
- [x] Create utilities/ directory
- [x] Create warehouses/docker-compose.yml
- [x] Create warehouses/postgres/init/init-databases.sql
- [x] Create warehouses/redis/redis.conf
- [x] Create utilities/docker-compose.yml
- [x] Create utilities/monitoring/prometheus.yml
- [x] Create utilities/logging/loki.yml
- [x] Create utilities monitoring alerts
- [x] Create utilities grafana provisioning
- [x] All services with health checks and Traefik integration

## Phase 12 — Makefile Refactor (IN PROGRESS 🚀)
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

**Completed Phases (13 total):**
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
- ✅ Phase 7 - Payment providers
- ✅ Phase 8 - Wagtail CMS integration
- ✅ Phase 10 - Traefik refactor
- ✅ Phase 11 - Warehouses & utilities separation

**In Progress (1):**
- 🚀 Phase 12 - Makefile Refactor

**Remaining (3):**
- Phase 13, 14, 15, 16

**Estimated Completion:** Today (4-6 hours remaining)
