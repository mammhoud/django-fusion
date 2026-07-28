# Phases 6-16 Implementation Plan
## Complete Remaining Phases Roadmap

**Date:** June 7, 2026  
**Current Status:** Phase 5 Complete (Fixtures Ready)  
**Target:** Complete All 16 Phases  
**Estimated Duration:** 8-12 hours  

---

## Overview

We have completed Phases 1-5 with full course system consolidation and fixtures. Now we need to complete the remaining 11 phases efficiently:

- **Phase 6:** Enrollment Workflow (2-3 hours)
- **Phase 7:** Cart Architecture (1-2 hours)
- **Phase 8:** Wagtail CMS Integration (1-2 hours)
- **Phase 9:** JS Bundle Standardization (1-2 hours)
- **Phase 10:** Traefik Refactor (30 min)
- **Phase 11:** Infrastructure Separation (30 min)
- **Phase 12:** Makefile Refactor (1-2 hours)
- **Phase 13:** Testing (2-3 hours)
- **Phase 14:** GitHub Actions (30 min)
- **Phase 15:** Documentation (1-2 hours)
- **Phase 16:** Final Validation (1-2 hours)

---

## Phase 6: Enrollment Workflow (2-3 hours)

### Objective
Create course enrollment capture system with lead tracking and email notifications.

### Tasks

#### 6.1 Verify CourseEnrollmentLead Model
- ✅ Model exists: `plugins/lms/models/courses/enrollment_lead.py`
- Status values: PENDING, CONFIRMED, REJECTED, CANCELED
- Email tracking and timestamps
- Course relationship

#### 6.2 Create Enrollment Form
File: `ctc-research/plugins/lms/forms/enrollment.py`
```python
class CourseEnrollmentForm(forms.ModelForm):
    class Meta:
        model = CourseEnrollmentLead
        fields = ['email', 'full_name', 'phone', 'notes']
```

#### 6.3 Create Enrollment Modal Template
File: `ctc-research/plugins/lms/templates/courses/_enrollment_modal.html`
- HTMX POST to `/learning/enrollment/create/<id>/`
- Form validation display
- Success message

#### 6.4 Create Enrollment View
File: `ctc-research/plugins/lms/views/enrollment.py`
```python
class EnrollmentCreateView(CreateView):
    model = CourseEnrollmentLead
    form_class = CourseEnrollmentForm
    # Send confirmation email
    # Return success HTMX response
```

#### 6.5 Create Email Templates
- `plugins/lms/templates/email/enrollment_confirmation.html`
- `plugins/lms/templates/email/enrollment_success.html`

#### 6.6 Register ViewSets
- Add CourseEnrollmentLeadViewSet to `plugins/lms/viewsets.py`
- Register in `plugins/lms/wagtail_hooks.py`

#### 6.7 Create Migration
```bash
python manage.py makemigrations plugins.lms
python manage.py migrate
```

### Expected Output
- Enrollment form displays in modal when user clicks "Enroll"
- Form submission sends HTMX request
- Success email sent to user
- Lead stored in database
- Admin can view all leads

---

## Phase 7: Cart Architecture (1-2 hours)

### Objective
Abstract payment provider architecture for multiple payment gateways.

### Tasks

#### 7.1 Create Abstract Base Class
File: `ctc-research/plugins/lms/services/payment_providers.py`
```python
class PaymentProvider(ABC):
    @abstractmethod
    def initialize_payment(self, course_id, amount):
        pass
    
    @abstractmethod
    def verify_payment(self, transaction_id):
        pass
```

#### 7.2 Create Stripe Provider
```python
class StripeProvider(PaymentProvider):
    def initialize_payment(self, course_id, amount):
        # Create stripe session
        pass
    
    def verify_payment(self, transaction_id):
        # Verify with stripe API
        pass
```

#### 7.3 Create PayPal Provider
```python
class PayPalProvider(PaymentProvider):
    # PayPal implementation
    pass
```

#### 7.4 Create Paymo Provider (Mobipay)
```python
class PaymoProvider(PaymentProvider):
    # Paymo/Mobipay implementation
    pass
```

#### 7.5 Create Provider Registry
```python
PAYMENT_PROVIDERS = {
    'stripe': StripeProvider,
    'paypal': PayPalProvider,
    'paymo': PaymoProvider,
}
```

#### 7.6 Documentation
File: `docs/PAYMENT_PROVIDERS.md`
- Architecture overview
- Provider implementations
- Integration guide

### Expected Output
- Clean abstraction for payment providers
- Easy to add new providers
- Unified payment flow

---

## Phase 8: Wagtail CMS Integration (1-2 hours)

### Objective
Register snippets and viewsets for admin management.

### Tasks

#### 8.1 Register EnrollmentSnippetGroup
File: `ctc-research/plugins/lms/snippets.py`
```python
@register_snippet
class CourseEnrollmentLeadAdmin(ModelAdmin):
    model = CourseEnrollmentLead
    menu_label = 'Course Leads'
    menu_icon = 'link'
```

#### 8.2 Create AdminViewSet
```python
class CourseEnrollmentLeadAdminViewSet(ModelAdminViewSet):
    model = CourseEnrollmentLead
    search_fields = ['email', 'full_name']
    list_display = ['email', 'course', 'status', 'created_at']
```

#### 8.3 Register Notification Management
```python
@register_snippet
class NotificationTemplate(models.Model):
    pass
```

#### 8.4 Add Admin Filters
- Filter by course
- Filter by status
- Filter by date

#### 8.5 Export Leads Feature
- CSV export
- Email export
- Filter before export

### Expected Output
- Admin panel shows enrollment leads
- Can manage lead status
- Can view all course enrollments
- Can export lead data

---

## Phase 9: JS Bundle Standardization (1-2 hours)

### Objective
Create standard JavaScript modules used across all sites.

### Tasks

#### 9.1 Create app.js
File: `assets/static/js/app.js`
- Initialize Bootstrap
- Setup HTMX
- Initialize AOS (animate on scroll)
- Setup event listeners

#### 9.2 Create htmx.js
File: `assets/static/js/htmx-config.js`
- HTMX global configuration
- Custom headers
- Request/response interceptors
- Error handling

#### 9.3 Create notifications.js
File: `assets/static/js/notifications.js`
- showNotification() function
- showAlert() function
- showPopup() function
- Auto-dismiss logic

#### 9.4 Create modals.js
File: `assets/static/js/modals.js`
- Modal creation
- Modal event handling
- Bootstrap integration

#### 9.5 Create forms.js
File: `assets/static/js/forms.js`
- Form validation
- HTMX form submission
- Loading indicators

#### 9.6 Remove Duplicates
- Find all duplicate JS across sites
- Delete duplicates
- Use shared modules

#### 9.7 Update Base Templates
- Include in base templates of all 3 sites
- Verify loading order
- Test functionality

### Expected Output
- Single JS codebase
- Shared across all sites
- No duplicates
- Clean and maintainable

---

## Phase 10: Traefik Refactor (30 min)

### Objective
Move Traefik configuration to infra directory.

### Tasks

#### 10.1 Create infra/traefik directory
```bash
mkdir -p infra/traefik
```

#### 10.2 Move Traefik Config
```bash
mv compose/traefik/* infra/traefik/
```

#### 10.3 Update Compose References
```yaml
# docker-compose.yml
traefik:
  build:
    context: ./infra/traefik
```

#### 10.4 Verify SSL Config
- Certificate generation working
- HTTP to HTTPS redirect functional
- Domain routing correct

### Expected Output
- Traefik config in dedicated directory
- All references updated
- SSL working
- Clean infrastructure organization

---

## Phase 11: Infrastructure Separation (30 min)

### Objective
Organize warehouses and utilities into separate directories.

### Tasks

#### 11.1 Create Directory Structure
```
warehouses/
├── docker-compose.yml
├── postgres/
├── redis/
└── adminer/

utilities/
├── docker-compose.yml
├── blinko/
└── monitoring/
```

#### 11.2 Move Services
```bash
mkdir -p warehouses utilities
# Move relevant services
```

#### 11.3 Update Root Compose
```yaml
# docker-compose.yml
services:
  include:
    - ./warehouses/docker-compose.yml
    - ./utilities/docker-compose.yml
```

#### 11.4 Update Documentation
- Explain new structure
- Update deployment docs

### Expected Output
- Clean infrastructure organization
- Logical separation of concerns
- Easy to maintain and scale

---

## Phase 12: Makefile Refactor (1-2 hours)

### Objective
Clean up and standardize Makefile deployment commands.

### Tasks

#### 12.1 Check Current Makefile
✅ Already has comprehensive deployment targets:
- `make docker-deploy-full` - Full deployment
- `make docker-deploy-warehouse` - Deploy warehouse
- `make docker-deploy-traefik` - Deploy Traefik
- `make docker-deploy-websites` - Deploy all websites
- `make docker-status` - Show service status
- `make docker-logs-all` - Show all logs

#### 12.2 Add Missing Targets
- `make full-site-check` - Already exists ✓
- `make populate-data-all` - Already exists ✓
- Add `make verify-all` - Run all checks

#### 12.3 Create Documentation
File: `docs/MAKEFILE_REFERENCE.md`
- All targets documented
- Usage examples
- Common workflows

#### 12.4 Test All Commands
```bash
make help
make check WEBSITE=ctc
make test
make build-assets-all
make docker-deploy-full
```

#### 12.5 Add Quick Start
```bash
# Quick deployment commands
make setup          # First-time setup
make up             # Start all services
make down           # Stop all services
make logs           # View logs
make clean          # Clean everything
```

### Expected Output
- Clean, organized Makefile
- All deployment commands working
- Easy to use and remember
- Well documented

---

## Phase 13: Testing (2-3 hours)

### Objective
Create comprehensive test coverage for courses, enrollment, and components.

### Tasks

#### 13.1 Create Course Model Tests
File: `ctc-research/plugins/lms/tests/test_course_models.py`
```python
class CourseModelTest(TestCase):
    def test_course_creation(self):
        pass
    
    def test_course_slug_generation(self):
        pass
    
    def test_course_current_price(self):
        pass
```

#### 13.2 Create Enrollment Lead Tests
File: `ctc-research/plugins/lms/tests/test_enrollment_lead.py`
```python
class EnrollmentLeadTest(TestCase):
    def test_enrollment_lead_creation(self):
        pass
    
    def test_enrollment_email_sending(self):
        pass
```

#### 13.3 Create HTMX View Tests
File: `ctc-research/plugins/lms/tests/test_views.py`
```python
class CourseViewTest(TestCase):
    def test_course_list_view(self):
        pass
    
    def test_enrollment_modal_htmx(self):
        pass
```

#### 13.4 Create Component Tests
File: `ctc-research/assets/tests/test_notifications.py`
```python
class NotificationsTest(TestCase):
    def test_notification_rendering(self):
        pass
```

#### 13.5 Create Playwright Smoke Tests
File: `tests/e2e/test_smoke.py`
```python
async def test_course_catalog_loads():
    pass

async def test_enrollment_flow():
    pass
```

#### 13.6 Run Test Coverage
```bash
pytest --cov=plugins.lms
pytest --cov=ctc-research
```

#### 13.7 Create GitHub Actions Workflow
File: `.github/workflows/test-coverage.yml`
- Run pytest with coverage
- Generate coverage report
- Comment on PR

### Expected Output
- 70%+ test coverage
- All critical paths tested
- Smoke tests passing
- GitHub Actions running

---

## Phase 14: GitHub Actions (30 min)

### Objective
Setup CI/CD workflows for automated testing and deployment.

### Tasks

#### 14.1 Verify Existing Workflows
- ✅ lint.yml - Python linting
- ✅ test.yml - Test suite
- ✅ docker-smoke.yml - Docker testing
- ✅ release.yml - Release process

#### 14.2 Update test.yml
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: make test
      - run: pytest --cov
```

#### 14.3 Create smoke.yml
```yaml
name: E2E Smoke Tests
on: [push]
jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: make docker-up
      - run: npx playwright test
```

#### 14.4 Verify All Workflows
- Lint passing
- Tests passing
- Docker builds successful
- E2E tests passing

### Expected Output
- All CI workflows working
- Automated testing on every push
- PR comments with results
- Release ready

---

## Phase 15: Documentation (1-2 hours)

### Objective
Create comprehensive documentation for each site and deployment.

### Tasks

#### 15.1 Create CTC Research Docs
File: `docs/ctc-research/README.md`
- Architecture overview
- Setup guide
- Course system guide
- Deployment guide

#### 15.2 Create LMS Demo Docs
File: `docs/lms-demo/README.md`
- Architecture overview
- Setup guide
- Enrollment system
- Deployment guide

#### 15.3 Create VResume Docs
File: `docs/VResume/README.md`
- Resume builder overview
- Setup guide
- Usage guide
- Deployment guide

#### 15.4 Create Deployment Guide
File: `docs/DEPLOYMENT.md`
- Local development setup
- Docker deployment
- Production deployment
- Monitoring and logs

#### 15.5 Create Architecture Docs
File: `docs/ARCHITECTURE.md`
- System overview
- Technology stack
- Integration points
- Data flow

#### 15.6 Create Troubleshooting Guide
File: `docs/TROUBLESHOOTING.md`
- Common issues
- Solutions
- Debug tips
- Support contacts

### Expected Output
- Complete documentation set
- Easy to follow guides
- Setup reproducible
- Troubleshooting resources available

---

## Phase 16: Final Validation (1-2 hours)

### Objective
Verify all systems working and production ready.

### Tasks

#### 16.1 Docker Validation
```bash
docker compose config                    # Validate compose syntax
docker compose ps                        # Check all services running
docker compose exec postgres pg_dump    # Backup database
```

#### 16.2 Application Validation
```bash
make check WEBSITE=ctc                   # Django checks
make check WEBSITE=structa               # LMS checks
make check WEBSITE=vresume               # VResume checks
```

#### 16.3 Test Validation
```bash
make test                                 # Run all tests
make tests-websites                      # Run website tests
pytest --cov                             # Coverage report
```

#### 16.4 Asset Validation
```bash
make build-assets-all                    # Build assets
make collectstatic-site WEBSITE=ctc      # Collect static
```

#### 16.5 Migration Validation
```bash
make migrate-site WEBSITE=ctc             # Run migrations
python manage.py showmigrations           # Show pending
```

#### 16.6 Fixture Validation
```bash
cd ctc-research
python manage.py load_course_fixtures    # Load fixtures
python manage.py shell -c "from plugins.lms.models import Course; print(Course.objects.count())"
```

#### 16.7 Page Validation
- Visit all critical pages
- Verify layout and styling
- Test all interactive elements
- Check responsive design

#### 16.8 API Validation
- Test all API endpoints
- Verify response formats
- Check error handling
- Test pagination

#### 16.9 Generate Final Report
File: `FINAL_DEPLOYMENT_REPORT.md`
- All systems operational ✅
- All tests passing ✅
- All assets compiled ✅
- Database migrations applied ✅
- Fixtures loaded ✅
- Production ready ✅

### Expected Output
- All validation checks passing
- Production ready status confirmed
- Deployment report generated
- Ready for live deployment

---

## Implementation Strategy

### Sequential Execution
1. Phase 6: Enrollment (complete enrollment system)
2. Phase 7: Payments (setup payment providers)
3. Phase 8: Wagtail CMS (integrate admin)
4. Phase 9: JS Bundles (standardize JavaScript)
5. Phase 10-11: Infrastructure (organize directories)
6. Phase 12: Makefile (standardize deployment)
7. Phase 13: Testing (achieve test coverage)
8. Phase 14: GitHub Actions (setup CI/CD)
9. Phase 15: Documentation (document everything)
10. Phase 16: Validation (final checks)

### Parallel Opportunities
- Phases 10-11 can run in parallel (30 min each)
- Documentation can be written alongside implementation
- Tests can be added as features are completed

---

## Success Criteria

### Phase 6
- ✅ Enrollment form works
- ✅ Emails send
- ✅ Leads stored in DB
- ✅ Admin can view leads

### Phase 7
- ✅ Payment providers abstracted
- ✅ Easy to add new providers
- ✅ Unified payment flow

### Phase 8
- ✅ Snippets registered
- ✅ ViewSets functional
- ✅ Admin management working

### Phase 9
- ✅ JS modules created
- ✅ No duplicates
- ✅ Shared across sites

### Phase 10-11
- ✅ Infrastructure organized
- ✅ All references updated
- ✅ Services running

### Phase 12
- ✅ All Make commands working
- ✅ Deployment smooth
- ✅ Well documented

### Phase 13
- ✅ 70%+ test coverage
- ✅ All critical paths tested
- ✅ Smoke tests passing

### Phase 14
- ✅ CI/CD workflows active
- ✅ Automated testing on every push
- ✅ Deployment automated

### Phase 15
- ✅ Comprehensive documentation
- ✅ Setup guides complete
- ✅ Troubleshooting available

### Phase 16
- ✅ All systems validated
- ✅ All tests passing
- ✅ Production ready

---

## Timeline Estimate

| Phase | Duration | Status |
|-------|----------|--------|
| 6 | 2-3 hrs | Ready |
| 7 | 1-2 hrs | Ready |
| 8 | 1-2 hrs | Ready |
| 9 | 1-2 hrs | Ready |
| 10 | 30 min | Ready |
| 11 | 30 min | Ready |
| 12 | 1-2 hrs | Ready |
| 13 | 2-3 hrs | Ready |
| 14 | 30 min | Ready |
| 15 | 1-2 hrs | Ready |
| 16 | 1-2 hrs | Ready |
| **Total** | **14-18 hrs** | **Ready** |

---

## Deliverables Checklist

- [ ] Phase 6: Enrollment workflow complete
- [ ] Phase 7: Payment providers implemented
- [ ] Phase 8: Wagtail CMS integrated
- [ ] Phase 9: JS bundles standardized
- [ ] Phase 10: Traefik refactored
- [ ] Phase 11: Infrastructure organized
- [ ] Phase 12: Makefile updated
- [ ] Phase 13: Tests created (70%+ coverage)
- [ ] Phase 14: GitHub Actions setup
- [ ] Phase 15: Documentation complete
- [ ] Phase 16: Final validation done

---

## Ready to Begin

All phases are planned and documented. Starting implementation with Phase 6.

**Next:** Implement Phase 6 - Enrollment Workflow

