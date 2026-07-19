# Remaining Phases - Quick Checklist (Phases 7-16)

**Status:** 📋 READY TO START  
**Estimated Duration:** 10-12 hours  
**Target:** Complete all remaining phases  

---

## Phase 7: Payment Providers (1-2 hours)

### Tasks
- [ ] Create abstract PaymentProvider class
  - [ ] `ctc-research/plugins/lms/services/payment_providers.py`
  - [ ] Methods: initialize_payment(), verify_payment()
  
- [ ] Create StripeProvider implementation
  - [ ] Stripe API integration
  - [ ] Session creation
  - [ ] Payment verification
  
- [ ] Create PayPalProvider implementation
  - [ ] PayPal API integration
  - [ ] Order creation
  - [ ] Payment verification
  
- [ ] Create PaymoProvider (Mobipay) implementation
  - [ ] Paymo API integration
  - [ ] Payment initialization
  - [ ] Verification

- [ ] Create provider registry
  - [ ] Dynamic provider selection
  - [ ] Configuration-based loading

- [ ] Create documentation
  - [ ] `docs/PAYMENT_PROVIDERS.md`
  - [ ] Integration guide
  - [ ] API reference

### Files to Create
- [ ] `plugins/lms/services/payment_providers.py` (~300 lines)
- [ ] `docs/PAYMENT_PROVIDERS.md` (~200 lines)

### Testing
- [ ] Test Stripe provider
- [ ] Test PayPal provider
- [ ] Test Paymo provider
- [ ] Test provider registry

---

## Phase 8: Wagtail CMS Integration (1-2 hours)

### Tasks
- [ ] Register CourseEnrollmentLead snippet
  - [ ] `plugins/lms/snippets.py`
  - [ ] Snippet group setup
  - [ ] Admin configuration

- [ ] Create AdminViewSet
  - [ ] Search fields
  - [ ] List display
  - [ ] Filters

- [ ] Add export functionality
  - [ ] CSV export
  - [ ] Filter options
  - [ ] Bulk actions

- [ ] Register in Wagtail
  - [ ] Add to wagtail_hooks.py
  - [ ] Setup menu icons
  - [ ] Configure permissions

### Files to Create
- [ ] `plugins/lms/snippets.py` (~200 lines)
- [ ] Update `plugins/lms/wagtail_hooks.py`

### Testing
- [ ] Test snippet registration
- [ ] Test admin interface
- [ ] Test export functionality
- [ ] Test filters and search

---

## Phase 9: JS Bundle Standardization (1-2 hours)

### Tasks
- [ ] Move JS to workspace root ✅ (Already done: assets/static/js/)

- [ ] Create bundle/minification config
  - [ ] webpack.config.js or similar
  - [ ] Production build
  - [ ] Development build

- [ ] Update site settings.py
  - [ ] `ctc-research/settings.py`
  - [ ] `lms/settings.py`
  - [ ] `VResume/settings.py`
  - [ ] Add assets/static to STATICFILES_DIRS

- [ ] Update base templates
  - [ ] Include JS in correct order
  - [ ] Verify loading
  - [ ] Test functionality

- [ ] Delete duplicate JS
  - [ ] Find duplicates in each site
  - [ ] Delete old versions
  - [ ] Verify no breakage

### Files to Update
- [ ] All three sites' settings.py
- [ ] All three sites' base templates
- [ ] Create build configuration

### Testing
- [ ] Test notifications
- [ ] Test modals
- [ ] Test forms
- [ ] Test HTMX integration
- [ ] Verify on all 3 sites

---

## Phase 10: Traefik Refactor (30 min)

### Tasks
- [ ] Create infra/traefik directory
- [ ] Move Traefik config
  - [ ] Create infra/traefik/
  - [ ] Move compose/traefik/* → infra/traefik/
  - [ ] Keep docker-compose.traefik.yml reference

- [ ] Update compose references
  - [ ] Update docker-compose.traefik.yml paths
  - [ ] Update any script references

- [ ] Verify SSL working
  - [ ] Test certificate generation
  - [ ] Test HTTP→HTTPS redirect
  - [ ] Test domain routing

### Files to Move
- [ ] compose/traefik/* → infra/traefik/

### Testing
- [ ] Validate docker-compose config
- [ ] Test service startup
- [ ] Test SSL certificates
- [ ] Test domain routing

---

## Phase 11: Infrastructure Separation (30 min)

### Tasks
- [ ] Create warehouses/ directory
  - [ ] Move database compose
  - [ ] Move cache compose
  - [ ] Move adminer

- [ ] Create utilities/ directory
  - [ ] Move blinko compose
  - [ ] Move monitoring tools

- [ ] Update root compose
  - [ ] Update includes
  - [ ] Verify references

### Directories to Create
- [ ] warehouses/
- [ ] utilities/

### Testing
- [ ] Validate all docker-compose files
- [ ] Test service startup

---

## Phase 12: Makefile Refactor (1 hour)

### Tasks
- [ ] Review current Makefile ✅ (Already comprehensive)

- [ ] Add missing targets
  - [ ] [ ] make setup (first-time setup)
  - [ ] [ ] make up (start services)
  - [ ] [ ] make down (stop services)
  - [ ] [ ] make logs (view all logs)
  - [ ] [ ] make clean (clean all)
  - [ ] [ ] make verify-all (run all checks)

- [ ] Create documentation
  - [ ] `docs/MAKEFILE_REFERENCE.md`
  - [ ] All targets documented
  - [ ] Usage examples

- [ ] Test all commands
  - [ ] Test each new target
  - [ ] Verify output
  - [ ] Check error handling

### Files to Update
- [ ] `Makefile`
- [ ] Create `docs/MAKEFILE_REFERENCE.md` (~150 lines)

### Testing
- [ ] make help
- [ ] make docker-up
- [ ] make docker-down
- [ ] make test
- [ ] All other key targets

---

## Phase 13: Testing (2-3 hours)

### Tasks
- [ ] Create course model tests
  - [ ] `ctc-research/plugins/lms/tests/test_models.py`
  - [ ] Course creation
  - [ ] Slug generation
  - [ ] Price calculations

- [ ] Create enrollment lead tests
  - [ ] `ctc-research/plugins/lms/tests/test_enrollment.py`
  - [ ] Lead creation
  - [ ] Email sending
  - [ ] Status updates

- [ ] Create HTMX view tests
  - [ ] `ctc-research/plugins/lms/tests/test_views.py`
  - [ ] Enrollment form
  - [ ] Status updates
  - [ ] CSV export/import

- [ ] Create component tests
  - [ ] Notification rendering
  - [ ] Modal display
  - [ ] Form validation

- [ ] Create Playwright E2E tests
  - [ ] `tests/e2e/test_smoke.py`
  - [ ] Catalog page loads
  - [ ] Enrollment flow
  - [ ] Admin functionality

- [ ] Run pytest with coverage
  - [ ] Target: 70%+ coverage
  - [ ] Generate reports
  - [ ] Upload to CI

### Files to Create
- [ ] `plugins/lms/tests/__init__.py`
- [ ] `plugins/lms/tests/test_models.py` (~150 lines)
- [ ] `plugins/lms/tests/test_enrollment.py` (~200 lines)
- [ ] `plugins/lms/tests/test_views.py` (~200 lines)
- [ ] `tests/e2e/test_smoke.py` (~150 lines)

### Testing Commands
```bash
pytest --cov=plugins.lms          # Coverage report
pytest plugins/lms/tests/         # Unit tests
pytest tests/e2e/                 # E2E tests
```

---

## Phase 14: GitHub Actions (30 min)

### Tasks
- [ ] Review existing workflows
  - [ ] lint.yml ✅
  - [ ] test.yml ✅
  - [ ] docker-smoke.yml ✅
  - [ ] release.yml ✅

- [ ] Update test.yml
  - [ ] Add pytest coverage
  - [ ] Add coverage report
  - [ ] Comment on PR

- [ ] Create smoke.yml (if needed)
  - [ ] E2E tests
  - [ ] Check all URLs
  - [ ] Verify functionality

- [ ] Verify all workflows
  - [ ] Run on push
  - [ ] Run on PR
  - [ ] Generate reports

### Files to Update
- [ ] `.github/workflows/test.yml`
- [ ] Maybe create `.github/workflows/smoke.yml`

### Testing
- [ ] Trigger workflow on push
- [ ] Verify test results
- [ ] Check coverage reports
- [ ] Verify PR comments

---

## Phase 15: Documentation (1-2 hours)

### Tasks
- [ ] Create CTC Research docs
  - [ ] `docs/ctc-research/README.md`
  - [ ] Architecture
  - [ ] Setup guide
  - [ ] Course system
  - [ ] Deployment

- [ ] Create LMS Demo docs
  - [ ] `docs/lms/README.md`
  - [ ] Architecture
  - [ ] Setup guide
  - [ ] Enrollment system
  - [ ] Deployment

- [ ] Create VResume docs
  - [ ] `docs/VResume/README.md`
  - [ ] Resume builder
  - [ ] Setup guide
  - [ ] Deployment

- [ ] Create deployment guide
  - [ ] `docs/DEPLOYMENT.md`
  - [ ] Local setup
  - [ ] Docker deployment
  - [ ] Production deployment
  - [ ] Monitoring

- [ ] Create architecture guide
  - [ ] `docs/ARCHITECTURE.md`
  - [ ] System overview
  - [ ] Technology stack
  - [ ] Data flow

- [ ] Create troubleshooting guide
  - [ ] `docs/TROUBLESHOOTING.md`
  - [ ] Common issues
  - [ ] Solutions
  - [ ] Debug tips

### Files to Create
- [ ] `docs/ctc-research/README.md` (~200 lines)
- [ ] `docs/lms/README.md` (~200 lines)
- [ ] `docs/VResume/README.md` (~200 lines)
- [ ] `docs/DEPLOYMENT.md` (~300 lines)
- [ ] `docs/ARCHITECTURE.md` (~250 lines)
- [ ] `docs/TROUBLESHOOTING.md` (~200 lines)

### Testing
- [ ] Verify all docs are readable
- [ ] Check all links work
- [ ] Test setup instructions

---

## Phase 16: Final Validation (1-2 hours)

### Tasks
- [ ] Docker validation
  - [ ] `docker compose config` (validate syntax)
  - [ ] `docker compose ps` (check services)
  - [ ] All services running
  - [ ] Health checks passing

- [ ] Application validation
  - [ ] `make check` for all sites
  - [ ] Django checks passing
  - [ ] No migration errors

- [ ] Test validation
  - [ ] `make test` passing
  - [ ] Coverage 70%+
  - [ ] No warnings

- [ ] Asset validation
  - [ ] `make build-assets-all` succeeds
  - [ ] Static files collected
  - [ ] CSS/JS loading

- [ ] Migration validation
  - [ ] `make migrate-site` for all sites
  - [ ] All migrations applied
  - [ ] No pending migrations

- [ ] Fixture validation
  - [ ] Load course fixtures
  - [ ] Verify in admin
  - [ ] Verify in web UI

- [ ] Page validation
  - [ ] Visit critical pages
  - [ ] Check layout
  - [ ] Test interactive elements
  - [ ] Responsive design OK

- [ ] API validation
  - [ ] Test all endpoints
  - [ ] Check responses
  - [ ] Verify error handling
  - [ ] Test pagination

- [ ] Generate final report
  - [ ] `FINAL_DEPLOYMENT_REPORT.md`
  - [ ] All systems operational
  - [ ] Production ready

### Files to Create
- [ ] `FINAL_DEPLOYMENT_REPORT.md` (~300 lines)

### Validation Commands
```bash
docker compose config                          # Validate
make check WEBSITE=ctc                         # Django checks
make test                                      # Run tests
make build-assets-all                          # Build assets
make populate-data-all                         # Load fixtures
```

---

## Overall Checklist

### Before Starting
- [ ] All Phase 6 code reviewed
- [ ] All infrastructure scripts ready
- [ ] JavaScript modules created
- [ ] Docker config updated
- [ ] Template consolidation script ready

### Parallel Work
- [ ] Phase 7 (Payments) - 1-2 hours
- [ ] Phase 8 (Wagtail) - 1-2 hours  
- [ ] Phase 9 (JS) - 1-2 hours
- [ ] Phase 10-11 (Infrastructure) - 1 hour
- [ ] Phase 12 (Makefile) - 1 hour
- [ ] Phase 13 (Testing) - 2-3 hours
- [ ] Phase 14 (GitHub Actions) - 30 min
- [ ] Phase 15 (Documentation) - 1-2 hours
- [ ] Phase 16 (Validation) - 1-2 hours

### Completion Check
- [ ] All 16 phases complete
- [ ] All tests passing
- [ ] All documentation written
- [ ] All systems validated
- [ ] Production ready

---

## Quick Start

```bash
# Phase 7
# [Create payment providers files]

# Phase 8
# [Create Wagtail snippets]

# Phase 9
bash scripts/consolidate-templates.sh
# [Update settings.py for all 3 sites]
# [Add JS includes to base templates]
# [Delete old JS files]

# Phase 10-11
# [Move config files]

# Phase 12
# [Update Makefile]

# Phase 13
pytest --cov=plugins.lms

# Phase 14
# [Run GitHub Actions]

# Phase 15
# [Create documentation]

# Phase 16
docker compose config
make check
make test
```

---

## Success Criteria

- ✅ All 16 phases complete
- ✅ All tests passing (70%+ coverage)
- ✅ All systems operational
- ✅ All documentation complete
- ✅ Production ready
- ✅ Zero blockers

---

**Target:** All phases complete by end of day  
**Status:** Ready to start Phase 7  

