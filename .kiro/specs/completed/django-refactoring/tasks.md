# Implementation Plan: Django Codebase Refactoring

## Implementation Sequence

### Phase 1: Template Restoration and Basic Setup

**1.1 Restore HTML Templates**
- [x] **1.1.1** Restore templates from structa.cloud to ctc-research
  - Copy templates while ignoring more-recently-modified ctc-research templates
  - Preserve template structure and Template_Inheritance chains
  - Verify template rendering without errors
  - Test all restored templates across supported device sizes

---

### Phase 2: Email and Wagtail Integration

**2.1 Email Command System**
- [x] **2.1.1** Implement CSV-based email testing with `test_email.csv`
- [x] **2.1.2** Create Management_Command for bulk email sending
- [x] **2.1.3** Implement role-based email template selection
- [x] **2.1.4** Implement email delivery status tracking with database persistence

**2.2 Wagtail Integration**
- [x] **2.2.1** Set up Wagtail group and role management
- [x] **2.2.2** Configure Permission_Inheritance system
- [x] **2.2.3** Implement role-based content access control
- [x] **2.2.4** Test Wagtail CMS integration

---

### Phase 3: Django Group and Role Management

**3.1 Django Group System**
- [x] **3.1.1** Create Django groups from CSV role definitions
- [x] **3.1.2** Implement Permission_Inheritance system
- [x] **3.1.3** Configure Role_Hierarchy and permissions
- [x] **3.1.4** Test group-based access control

---

### Phase 4: Privacy Policy Modal

**4.1 HTMX Modal Implementation**
- [x] **4.1.1** Create HTMX-based privacy policy modal component
- [x] **4.1.2** Integrate modal with authentication pages (login, registration, password reset)
- [x] **4.1.3** Implement modal show/hide without full page reload
- [x] **4.1.4** Implement user consent tracking with timestamp persistence

---

### Phase 5: Notes Profile Section

**5.1 Notes System Enhancement**
- [x] **5.1.1** Add notes section to user profiles
- [x] **5.1.2** Implement database persistence for notes
- [x] **5.1.3** Create modal interface for note viewing and editing
- [x] **5.1.4** Add HTMX-based real-time note list updates

---

### Phase 6: Data Tags System

**6.1 Tagging Implementation**
- [x] **6.1.1** Implement tagging system for tagged models
- [x] **6.1.2** Create tag management interface
- [x] **6.1.3** Add tag-based filtering
- [x] **6.1.4** Test tag-based search functionality

---

### Phase 7: Import Fixes and Basic Checks

**7.1 Import System Fixes**
- [x] **7.1.1** Fix all import statements to use correct module paths
- [x] **7.1.2** Resolve all Circular_Import issues
- [x] **7.1.3** Verify import accuracy after fixes
- [x] **7.1.4** Run `python manage.py check` and confirm zero errors

**7.2 Basic System Checks**
- [x] **7.2.1** Run Django system checks (`manage.py check`)
- [x] **7.2.2** Fix database connection issues
- [x] **7.2.3** Verify core Django functionality
- [x] **7.2.4** Test basic Django operations

---

### Phase 8: Data Management

**8.1 Dumped Data Fixes**
- [x] **8.1.1** Review and fix foreign key and relationship inconsistencies in fixture files
- [x] **8.1.2** Verify data relationships after fixes
- [x] **8.1.3** Fix data integrity issues
- [x] **8.1.4** Test fixture loading with `manage.py loaddata`

---

### Phase 9: JSON Data Merging

**9.1 Data Integration**
- [x] **9.1.1** Merge multiple JSON fixture files into a single output file
- [x] **9.1.2** Resolve duplicate primary key conflicts using defined strategy
- [x] **9.1.3** Create comprehensive merged dataset
- [x] **9.1.4** Test merged dataset loading and integrity

---

### Phase 10: Language Testing

**10.1 Language System Testing**
- [x] **10.1.1** Test language switching functionality
- [x] **10.1.2** Verify language-specific content for all supported locales
- [x] **10.1.3** Test language URLs return HTTP 200 with correct language content
- [x] **10.1.4** Verify translation accuracy against source translation files

---

### Phase 11: Package Reorganization

**11.1 Package Structure Update**
- [x] **11.1.1** Reorganize packages so related modules are co-located
- [x] **11.1.2** Update dependency declarations in `pyproject.toml`
- [x] **11.1.3** Fix all internal package references
- [x] **11.1.4** Test that application starts and passes existing tests after reorganization

---

### Phase 12: Import and Namespace Updates

**12.1 Import System Update**
- [x] **12.1.1** Update all import statements to reflect new package paths
- [x] **12.1.2** Resolve all Namespace conflicts
- [x] **12.1.3** Verify no `ImportError` or `ModuleNotFoundError` on startup
- [x] **12.1.4** Run existing unit and integration tests to confirm passing

---

### Phase 13: Comprehensive Testing

**13.1 Testing Suite**
- [x] **13.1.1** Run unit tests and report pass/fail counts
- [x] **13.1.2** Execute integration tests for cross-component interactions
- [x] **13.1.3** Perform system tests for end-to-end user workflows
- [x] **13.1.4** Fix all identified test failures

---

### Phase 14: Error and Log Management

**14.1 Error Resolution**
- [x] **14.1.1** Review error logs and fix root cause of each error
- [x] **14.1.2** Resolve all Django system warnings from `manage.py check`
- [x] **14.1.3** Implement structured logging with configurable log levels
- [x] **14.1.4** Archive logs older than 30 days; remove logs older than 90 days

---

## Optional Tasks

### Blog Maintenance (Optional)

- [x] **B.1** Implement blog post management in user profiles
- [x] **B.2** Add blog templates using Bakerydemo resources
- [x] **B.3** Implement blog tags and categories
- [x] **B.4** Add blog post creation and editing interface
- [x] **B.5** Implement blog search and filtering
- [x] **B.6** Add blog comments and interactions
- [x] **B.7** Implement blog RSS feeds
- [x] **B.8** Add social sharing features

### Profile Section Fixes (Optional)

- [ ] **P.1** Fix profile section layouts
- [ ] **P.2** Implement profile completion tracking
- [ ] **P.3** Add profile customization options
- [ ] **P.4** Implement profile privacy settings
- [ ] **P.5** Add profile analytics dashboard

### Wagtail Bakery Demo Integration (Optional)

- [ ] **W.1** Implement Wagtail page models for blogs
- [ ] **W.2** Add Wagtail sitemap and SEO features

### Services Template Enhancement (Optional)

- [ ] **S.1** Update services template with Wagtail Streamfield sections
- [ ] **S.2** Implement service categories and tags
- [ ] **S.3** Add service filtering and search
- [ ] **S.4** Implement service booking system
- [ ] **S.5** Add service reviews and ratings
- [ ] **S.6** Implement service recommendation engine

### Wagtail Page Model Implementation (Optional)

- [ ] **M.1** Create Wagtail page models for services
- [ ] **M.2** Implement page sections as Streamfield blocks
- [ ] **M.3** Add page tagging and categorization
- [ ] **M.4** Implement page versioning
- [ ] **M.5** Add page publishing workflow with approval steps

### Testing Suite (Optional)

**Unit and Integration Tests**
- [x] **T.1** Write unit tests for blog models: BlogPost, BlogTag, BlogCategory, BlogComment
- [x] **T.2** Write unit tests for blog services: TagService, PostFilterService
- [x] **T.3** Write integration tests for blog views: list, detail, search, comments
- [x] **T.4** Write unit tests for profile blog management views
- [x] **T.5** Write property-based tests for blog search correctness

**Selenium / End-to-End Tests**
- [x] **T.6** Write Selenium tests for blog index page: load, search, filter by tag/category
- [x] **T.7** Write Selenium tests for blog detail page: content, comments, social share
- [x] **T.8** Write Selenium tests for profile blog management: create, edit, delete post
- [x] **T.9** Write Selenium tests for courses search page: search, filter, pagination
- [x] **T.10** Write Selenium tests for services page: load, sections, filtering

**Container Build and Test**
- [x] **T.11** Add Selenium and pytest-selenium to Dockerfile and `pyproject.toml`
- [x] **T.12** Add docker-compose test service with Chrome/Selenium for container testing
- [x] **T.13** Run full test suite inside built container and fix failures

### Search Mixin Refactor (Optional)

- [x] **X.1** Create SearchMixin in django-osoul with Q-based full-text search and HTMX live-search support
- [x] **X.2** Create FilterMixin in django-osoul with declarative `filter_fields`, `filter_by_tag`, and `filter_by_category` support
- [x] **X.3** Refactor BlogPostListView and BlogSearchView to use SearchMixin and FilterMixin from django-osoul
- [x] **X.4** Refactor CourseSearchView to use SearchMixin and FilterMixin from django-osoul
- [x] **X.5** Fix courses search page template to use HTMX live search with the new mixin
- [x] **X.6** Move PostFilterService and TagService to django-osoul as reusable service classes

### Routable Components Tests (NEW)

- [x] **R.1** Create unit tests for RoutableComponent - has_permission, get_route_url, get_breadcrumbs, get_context_data
- [x] **R.2** Create unit tests for FragmentComponent - is_htmx_request, get_fragment_context, render_oob_fragment
- [x] **R.3** Create unit tests for Application - menu_items, has_view_permission
- [x] **R.4** Create unit tests for Site - register, menu_items, get_absolute_url
- [x] **R.5** Create unit tests for FragmentDetector - detect, is_htmx_request, has_oob_swap
- [x] **R.6** Create unit tests for ModelViewset - CRUD operations, permissions
- [x] **R.7** Create unit tests for BaseViewset - parent hierarchy, has_view_permission
- [x] **R.8** Create unit tests for ReadonlyModelViewset - list and detail views

**Test file location:** `tests/unit/test_routable_components.py`

---

## Success Criteria

### Technical Metrics

- [ ] 100% of templates restored and rendering without errors
- [ ] Email delivery rate of at least 99.9% for valid recipients
- [ ] 100% permission accuracy for all role-based access checks
- [ ] 100% of import statements fixed with zero `ImportError` on startup
- [ ] 100% data integrity after fixture loading
- [ ] At least 80% test coverage for critical application paths

### Quality Metrics

- [ ] All templates functional
- [ ] Email system operational
- [ ] Permission system working
- [ ] All imports fixed
- [ ] Data loading complete
- [ ] Language switching works
- [ ] Packages reorganized
- [ ] All tests passing
- [ ] Error logs clean

---

## Dependencies

- Python 3.11 or later
- Django 5.0 or later
- PostgreSQL 14 or later
- Redis (for caching and Celery broker)
- Celery (for asynchronous task execution)
- HTMX (for frontend dynamic interactions)
- Selenium (for end-to-end testing)

---

## Cross-References

- See `.kiro/specs/core-logic-consolidation-and-app-restructure/` for domain model and service layer design
- See `.kiro/specs/ecosystem-architectural-refactoring/` for package reorganization architecture
- See `.kiro/specs/phase-2-website-sync-completion/` for template synchronization details
- See `.kiro/specs/phase-3-production-deployment/` for deployment and production configuration
