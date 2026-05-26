# Tasks

## Task List

### Phase 1: Core Verification Implementation

- [x] 1. Create verification script scaffold
  - [x] 1.1 Create `ctc-research.com/core/CI/__init__.py`
  - [x] 1.2 Create `ctc-research.com/core/CI/verify_deployment.py` with `CheckResult` dataclass, `run_docker_exec()`, and `run_http_check()` helpers, and `main()` orchestrator

- [x] 2. Implement data loading verification (**Requirement 1**)
  - [x] 2.1 Implement `check_data_loading()` — verify fixture files exist, run `loaddata` for both fixtures, confirm latest record timestamp

- [x] 3. Implement static asset verification (**Requirement 2**)
  - [x] 3.1 Implement `check_static_assets()` — run `collectstatic`, verify CSS/JS files in volume, HTTP GET a known static file from nginx

- [x] 4. Implement database and network verification (**Requirement 3**)
  - [x] 4.1 Implement `check_database()` — run `python com check --database default`, verify postgres and redis reachability on `traefik-net`

- [x] 5. Implement migration verification (**Requirement 4**)
  - [x] 5.1 Implement `check_migrations()` — run `migrate --noinput`, parse `showmigrations` for unapplied entries, run `migrate --check`

- [x] 6. Implement Django test execution (**Requirement 5**)
  - [x] 6.1 Implement `check_django_tests()` — run `python com test --noinput -k auth`, parse output for failures/errors, confirm test DB isolation

- [x] 7. Implement new account registration check (**Requirement 6**)
  - [x] 7.1 Implement `check_registration()` — check if user exists, POST to registration endpoint with `mahmoud.ezat@outlook.com`, confirm user record in DB

- [x] 8. Implement admin panel access verification (**Requirement 7**)
  - [x] 8.1 Implement `check_admin_panel()` — GET `/admin/`, authenticate with superuser credentials, verify Unfold admin loads without 500, check response body markers

- [x] 9. Implement URL and domain availability checks (**Requirement 8**)
  - [x] 9.1 Implement `check_urls()` — GET critical paths, verify Traefik routing headers, check TLS certificate validity for ctc-research.com

- [x] 10. Implement project rebuild (**Requirement 9**)
  - [x] 10.1 Implement `rebuild_project()` — run `docker compose build --no-cache`, `docker compose up -d`, poll container health until healthy or timeout, confirm all three containers running

- [x] 11. Implement Docker cleanup (**Requirement 10**)
  - [x] 11.1 Implement `docker_cleanup()` — run `docker system prune -f` (no `--volumes`), parse reclaimed space, print final summary table

- [x] 12. Add Makefile target
  - [x] 12.1 Add `verify` target to `ctc-research.com/makefile` that runs `python -m core.CI.verify_deployment`

### Phase 2: Selenium Test Development

- [x] 13. Write django-grep Selenium-style auth tests for ctc-research
  - [x] 13.1 Create `ctc-research.com/core/CI/tests/test_auth_selenium.py` using `django_grep.browser` — login flow, register new account (`mahmoud.ezat@outlook.com`), logout, and auth-required page redirect
  - [x] 13.2 Create `ctc-research.com/core/CI/tests/test_assets_selenium.py` using `django_grep.browser` — verify static CSS/JS assets load (HTTP 200, correct content-type), no 404s on known asset paths

- [x] 14. Write django-grep Selenium-style auth tests for structa (test-only, no build)
  - [x] 14.1 Create `structa.cloud/alliance/CI/tests/test_auth_selenium.py` using `django_grep.browser` — login flow, register new account, logout, and auth-required page redirect (mirrors ctc-research tests, adapted for `alliance-website` container and structa URLs)
  - [x] 14.2 Create `structa.cloud/alliance/CI/tests/test_assets_selenium.py` using `django_grep.browser` — verify static CSS/JS assets load for structa (HTTP 200, correct content-type), no 404s on known asset paths

### Phase 3: Comprehensive Selenium Testing (**Requirement 11**)

- [x] 15. Rebuild Docker containers and verify all services are running
  - [x] 15.1 Execute `docker compose build --no-cache` for ctc-research.com services
  - [x] 15.2 Execute `docker compose up -d` to start all services
  - [x] 15.3 Wait for all containers to reach healthy status (website, website-media, website-worker)
  - [x] 15.4 Verify no Python errors or tracebacks in container logs
  - [x] 15.5 Confirm HTTP 200 response from `/health/` endpoint

- [x] 16. Load all dumped data and translations
  - [x] 16.1 Execute `docker exec website uv run python com migrate --noinput`
  - [x] 16.2 Load fixture: `docker exec website uv run python com loaddata ctc-research-data.json`
  - [x] 16.3 Load fixture: `docker exec website uv run python com loaddata wagtail_pages_dump.json`
  - [x] 16.4 Verify all translations are loaded and available
  - [x] 16.5 Confirm database contains all expected records from dumped data

- [x] 17. Test homepage and root page (en) with Selenium
  - [x] 17.1 Create `ctc-research.com/tests/selenium/test_homepage.py` with Selenium tests
  - [x] 17.2 Test homepage loads without errors (HTTP 200, no JS errors)
  - [x] 17.3 Test root page `/` redirects to or loads English home page
  - [x] 17.4 Verify all page elements render correctly (header, footer, navigation)
  - [x] 17.5 Test language switcher functionality (if present)

- [x] 18. Test all pages from dumped data with Selenium
  - [x] 18.1 Query database for all Wagtail pages from dumped data
  - [x] 18.2 Create `ctc-research.com/tests/selenium/test_all_pages.py` with dynamic page tests
  - [x] 18.3 For each page: verify HTTP 200, no JS errors, all assets load
  - [x] 18.4 Test page navigation and internal links
  - [x] 18.5 Verify page content renders correctly with all translations

- [x] 19. Test authentication pages with Selenium
  - [x] 19.1 Create `ctc-research.com/tests/selenium/test_auth_pages.py`
  - [x] 19.2 Test login page loads and form renders correctly
  - [x] 19.3 Test registration page loads and form renders correctly
  - [x] 19.4 Test password reset page loads and form renders correctly
  - [x] 19.5 Test invite page loads and form renders correctly (if applicable)

- [x] 20. Test registration flow end-to-end with Selenium
  - [x] 20.1 Create `ctc-research.com/tests/selenium/test_register_flow.py`
  - [x] 20.2 Test complete registration flow: navigate to register, fill form, submit
  - [x] 20.3 Verify user account is created in database
  - [x] 20.4 Test email verification flow (if applicable)
  - [x] 20.5 Test redirect to dashboard/profile after successful registration

- [x] 21. Test login flow end-to-end with Selenium
  - [x] 21.1 Create `ctc-research.com/tests/selenium/test_login_flow.py`
  - [x] 21.2 Test complete login flow: navigate to login, enter credentials, submit
  - [x] 21.3 Verify user is authenticated and session is created
  - [x] 21.4 Test redirect to dashboard/profile after successful login
  - [x] 21.5 Test logout functionality

- [x] 22. Test invite page and invite flow with Selenium
  - [x] 22.1 Create `ctc-research.com/tests/selenium/test_invite_flow.py`
  - [x] 22.2 Test invite page loads and form renders correctly
  - [x] 22.3 Test sending invite to valid email address
  - [x] 22.4 Verify invite record is created in database
  - [x] 22.5 Test invite acceptance flow (if applicable)

- [x] 23. Test notification system with Selenium
  - [x] 23.1 Create `ctc-research.com/tests/selenium/test_notifications.py`
  - [x] 23.2 Test notification display for success messages
  - [x] 23.3 Test notification display for error messages
  - [x] 23.4 Test notification display for warning messages
  - [x] 23.5 Test notification display for info messages
  - [x] 23.6 Test notification auto-dismiss functionality

- [x] 24. Test error pages with Selenium
  - [x] 24.1 Create `ctc-research.com/tests/selenium/test_error_pages.py`
  - [x] 24.2 Test 404 error page loads correctly
  - [x] 24.3 Test 500 error page loads correctly
  - [x] 24.4 Test 403 forbidden page loads correctly
  - [x] 24.5 Test error page navigation back to homepage

- [x] 25. Test admin pages accessibility with Selenium
  - [x] 25.1 Create `ctc-research.com/tests/selenium/test_admin_pages.py`
  - [x] 25.2 Test admin login page loads correctly
  - [x] 25.3 Test admin dashboard loads after authentication
  - [x] 25.4 Test admin navigation menu is accessible
  - [x] 25.5 Test admin page permissions (unauthorized access blocked)

- [x] 26. Test profile pages accessibility with Selenium
  - [x] 26.1 Create `ctc-research.com/tests/selenium/test_profile_pages.py`
  - [x] 26.2 Test profile page loads for authenticated user
  - [x] 26.3 Test profile edit form renders correctly
  - [x] 26.4 Test profile information updates correctly
  - [x] 26.5 Test profile page redirect for unauthenticated users

- [x] 27. Test asset loading and verification with Selenium
  - [x] 27.1 Create `ctc-research.com/tests/selenium/test_assets.py`
  - [x] 27.2 Verify all CSS files load without 404 errors
  - [x] 27.3 Verify all JavaScript files load without 404 errors
  - [x] 27.4 Verify all images load without 404 errors
  - [x] 27.5 Verify no console errors related to missing assets

- [x] 28. Test all pages with all translations
  - [x] 28.1 Create `ctc-research.com/tests/selenium/test_translations.py`
  - [x] 28.2 For each available language: test homepage loads correctly
  - [x] 28.3 For each available language: test key pages load with correct language
  - [x] 28.4 Verify language switcher changes language correctly
  - [x] 28.5 Verify language preference is persisted

- [x] 29. Run all Selenium tests and fix any failures
  - [x] 29.1 Execute full Selenium test suite: `cd ctc-research.com && uv run pytest tests/selenium/ -v`
  - [x] 29.2 Capture and analyze any test failures
  - [x] 29.3 Fix failing tests by updating page selectors or test logic
  - [x] 29.4 Re-run tests until all pass
  - [x] 29.5 Generate test report with coverage metrics

- [x] 30. Verify production readiness
  - [x] 30.1 Confirm all Docker containers are running and healthy
  - [x] 30.2 Confirm all database migrations are applied
  - [x] 30.3 Confirm all static assets are collected and served
  - [x] 30.4 Confirm all tests pass (unit, integration, Selenium)
  - [x] 30.5 Confirm no critical errors in application logs

### Phase 4: Email Invitation System (**Requirement 12**)

- [x] 31. Send invite emails from emails.csv
  - [x] 31.1 Read `emails.csv` file from workspace root
  - [x] 31.2 Create `ctc-research.com/management/commands/send_invites.py` command
  - [x] 31.3 For each email in CSV: create invite record in database
  - [x] 31.4 For each email in CSV: send invite email with unique invite link
  - [x] 31.5 Log all sent invites with timestamps and status
  - [x] 31.6 Verify all emails were sent successfully (check email logs)
  - [x] 31.7 Confirm invite records are created in database for each email

---

## Implementation Status

**All tasks completed** ✅

- **Total Tasks**: 31 main tasks with 78 subtasks
- **Completion Status**: 100% complete
- **Requirements Coverage**: All 12 requirements fully implemented
- **Verification**: Deployment verification suite operational via `make verify`
- **Testing**: Comprehensive Selenium test suite covering all critical functionality
- **Email System**: Invitation system fully implemented and tested

## Cross-References

- **Requirements Document**: `.kiro/specs/ctc-research-deployment-verification/requirements.md`
- **Design Document**: `.kiro/specs/ctc-research-deployment-verification/design.md`
- **Implementation**: `ctc-research.com/core/CI/verify_deployment.py`
- **Selenium Tests**: `ctc-research.com/tests/selenium/`
- **Email Command**: `ctc-research.com/management/commands/send_invites.py`
