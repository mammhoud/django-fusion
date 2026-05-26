# Requirements Document

## Introduction

This feature defines a comprehensive deployment verification and testing workflow for the ctc-research.com Django website. The workflow covers data loading validation, static asset verification, database connectivity checks, migration verification, Django test execution, user registration testing, admin panel access checks, URL/domain availability verification via Traefik, project rebuild, and Docker cleanup. The goal is to ensure every deployment is fully functional before being considered production-ready.

## Glossary

- **Verification_Suite**: The collection of automated and manual checks that constitute the deployment verification workflow.
- **Django_App**: The ctc-research.com Django application running inside the `website` Docker container.
- **Fixture**: A JSON data dump file (e.g., `ctc-research-data.json`, `wagtail_pages_dump.json`) used to seed the database.
- **Migration**: A Django database schema migration file applied via `python com migrate`.
- **Static_Assets**: CSS, JavaScript, and image files collected via `collectstatic` and served by the `website-media` nginx container.
- **Traefik**: The reverse proxy and load balancer routing traffic to ctc-research.com services.
- **Admin_Panel**: The Django admin interface at `/admin/` and the Django Unfold admin control panel.
- **Docker_Network**: The `traefik-net` external Docker network connecting all services.
- **RQ_Worker**: The `website-worker` container processing background jobs via Redis Queue.
- **Health_Endpoint**: The `/health/` HTTP endpoint exposed by the Django_App for liveness checks.
- **Selenium_Tests**: Automated browser-based tests using Selenium WebDriver to verify end-to-end functionality.
- **nginx**: The web server serving static assets from the `website-media` container.
- **Redis**: In-memory data structure store used for caching and task queue (RQ) operations.
- **PostgreSQL**: The relational database management system used for the application database (`db_ctc`).
- **psycopg2**: PostgreSQL database adapter for Python used by Django.
- **TLS_Certificate**: Transport Layer Security certificate used for HTTPS encryption on ctc-research.com domain.
- **emails.csv**: CSV file containing email addresses for invitation system.
- **Invite_Record**: Database record representing an invitation sent to a user email address.
- **Unique_Token**: Cryptographically secure unique identifier generated for each invitation link.

---

## Requirements

### Requirement 1: Data Loading Verification

**User Story:** As a deployment engineer, I want to verify that fixture data is loaded with the latest date, so that the production database reflects the most recent data dump.

#### Acceptance Criteria

1. WHEN the deployment verification runs, THE Verification_Suite SHALL confirm that the fixture file `ctc-research-data.json` exists in `/app/` inside the `website` container.
2. WHEN `loaddata` is executed for `ctc-research-data.json`, THE Django_App SHALL load all records without errors and report the count of objects loaded.
3. WHEN `loaddata` is executed for `wagtail_pages_dump.json`, THE Django_App SHALL load all Wagtail page records without errors.
4. WHEN fixture loading completes, THE Verification_Suite SHALL query the database and confirm that the most recently modified record timestamp matches the expected latest date from the fixture file.
5. IF a fixture file is missing or corrupted, THEN THE Verification_Suite SHALL report the specific missing file path and exit with a non-zero status code.

---

### Requirement 2: Static Asset Verification

**User Story:** As a deployment engineer, I want to verify that static assets are served with no errors or warnings, so that the website renders correctly for end users.

#### Acceptance Criteria

1. WHEN the deployment verification runs, THE Verification_Suite SHALL execute `collectstatic --noinput` inside the `website` container and confirm it exits with status code 0.
2. WHEN `collectstatic` completes, THE Verification_Suite SHALL confirm that the `website_static` Docker volume contains at least one CSS file and at least one JavaScript file.
3. WHEN the `website-media` nginx container is queried for a known static file path, THE Verification_Suite SHALL receive an HTTP 200 response with no error-level nginx log entries.
4. IF `collectstatic` produces any `ERROR` or `WARNING` log lines, THEN THE Verification_Suite SHALL capture and display those lines before failing the check.

---

### Requirement 3: Database Connectivity and Docker Network Verification

**User Story:** As a deployment engineer, I want to verify that the database is working correctly with proper connection and Docker network configuration, so that the application can persist and retrieve data reliably.

#### Acceptance Criteria

1. WHEN the deployment verification runs, THE Verification_Suite SHALL execute `python com check --database default` inside the `website` container and confirm it exits with status code 0.
2. WHEN the database check runs, THE Verification_Suite SHALL confirm that the `postgres` container is reachable from the `website` container on the `traefik-net` Docker network.
3. WHEN the database check runs, THE Verification_Suite SHALL confirm that the `redis` container is reachable from the `website` container on the `traefik-net` Docker network.
4. WHEN the database check runs, THE Verification_Suite SHALL confirm that the database name `db_ctc` exists and is accessible with the configured credentials.
5. IF the database connection fails, THEN THE Verification_Suite SHALL display the connection error message and the current `DB_HOST` and `DB_NAME` environment variable values.

---

### Requirement 4: Migration Verification

**User Story:** As a deployment engineer, I want to verify that all Django migrations run correctly, so that the database schema is up to date with the application code.

#### Acceptance Criteria

1. WHEN the deployment verification runs, THE Verification_Suite SHALL execute `python com migrate --noinput` inside the `website` container and confirm it exits with status code 0.
2. WHEN migrations complete, THE Verification_Suite SHALL execute `python com showmigrations` and confirm that no migration is listed with an `[ ]` (unapplied) status.
3. WHEN migrations complete, THE Verification_Suite SHALL execute `python com migrate --check` and confirm it exits with status code 0, indicating no pending migrations remain.
4. IF any migration fails, THEN THE Verification_Suite SHALL capture the full traceback and display the name of the failing migration file.

---

### Requirement 5: Django Test Execution

**User Story:** As a deployment engineer, I want to run Django tests filtered to authentication flows after login, so that core auth functionality is confirmed working on the deployed instance.

#### Acceptance Criteria

1. WHEN the deployment verification runs, THE Verification_Suite SHALL execute `python com test --noinput -k auth` inside the `website` container to run all test cases matching the `auth` pattern.
2. WHEN the test run completes, THE Verification_Suite SHALL confirm that all matched tests pass with 0 failures and 0 errors.
3. WHEN the test run completes, THE Verification_Suite SHALL display the total number of tests run, failures, and errors.
4. IF any test fails, THEN THE Verification_Suite SHALL display the full test failure output including the test name, assertion error, and traceback.
5. WHILE tests are running, THE Verification_Suite SHALL use a dedicated test database and SHALL NOT modify the production database.

---

### Requirement 6: New Account Registration

**User Story:** As a deployment engineer, I want to register a new account with a specific email address, so that the user registration flow is confirmed working end-to-end on the deployed instance.

#### Acceptance Criteria

1. WHEN the deployment verification runs, THE Verification_Suite SHALL send an HTTP POST request to the registration endpoint with email `mahmoud.ezat@outlook.com` and a valid password.
2. WHEN the registration request is processed, THE Django_App SHALL return an HTTP 200 or 302 response indicating successful registration or redirect.
3. WHEN registration completes, THE Verification_Suite SHALL confirm that a user record with email `mahmoud.ezat@outlook.com` exists in the database.
4. IF a user with email `mahmoud.ezat@outlook.com` already exists, THEN THE Verification_Suite SHALL skip creation and log that the user already exists.
5. IF registration fails with an HTTP error response, THEN THE Verification_Suite SHALL display the response status code and response body.

---

### Requirement 7: Admin Panel Access Verification

**User Story:** As a deployment engineer, I want to verify that the Django admin and Django Unfold admin control pages are accessible, so that administrative functions are available after deployment.

#### Acceptance Criteria

1. WHEN the deployment verification runs, THE Verification_Suite SHALL send an HTTP GET request to `/admin/` and confirm it returns HTTP 200 or 302 (redirect to login).
2. WHEN the deployment verification runs, THE Verification_Suite SHALL authenticate with superuser credentials and confirm that `/admin/` returns HTTP 200 after login.
3. WHEN the admin panel is accessed, THE Verification_Suite SHALL confirm that the Django Unfold admin interface loads without HTTP 500 errors.
4. WHEN the admin panel is accessed, THE Verification_Suite SHALL confirm that the response body contains expected admin UI markers (e.g., `<title>` containing "Site administration" or the Unfold branding).
5. IF the admin panel returns HTTP 500, THEN THE Verification_Suite SHALL capture and display the error response body and the last 20 lines of the Django application log.

---

### Requirement 8: URL Availability and Domain Verification

**User Story:** As a deployment engineer, I want to verify that all critical URLs are available through the ctc-research.com domain via Traefik, so that end users can access the site correctly.

#### Acceptance Criteria

1. WHEN the deployment verification runs, THE Verification_Suite SHALL send HTTP GET requests to the following paths and confirm each returns a non-5xx HTTP status code: `/`, `/health/`, `/admin/`, `/api/` (if applicable).
2. WHEN URL checks run against the ctc-research.com domain, THE Verification_Suite SHALL confirm that Traefik routes requests correctly by verifying the `X-Forwarded-Host` or `Via` response headers are present.
3. WHEN the domain check runs, THE Verification_Suite SHALL confirm that `https://ctc-research.com` resolves and returns HTTP 200 or 301/302.
4. WHEN the domain check runs, THE Verification_Suite SHALL confirm that the TLS_Certificate for ctc-research.com is valid and not expired.
5. IF any critical URL returns HTTP 5xx, THEN THE Verification_Suite SHALL display the URL, status code, and the last 20 lines of the Traefik access log.

---

### Requirement 9: Project Rebuild

**User Story:** As a deployment engineer, I want to rebuild the project after all verifications pass, so that the deployment is finalized with a clean, confirmed build.

#### Acceptance Criteria

1. WHEN all prior verification steps pass, THE Verification_Suite SHALL execute `docker compose build --no-cache` for the ctc-research.com services.
2. WHEN the rebuild completes, THE Verification_Suite SHALL execute `docker compose up -d` to restart all services with the new images.
3. WHEN services restart after rebuild, THE Verification_Suite SHALL wait for the `website` container health check to return healthy status before proceeding.
4. WHEN services restart after rebuild, THE Verification_Suite SHALL confirm the `website`, `website-media`, and `website-worker` containers are all in `running` state.
5. IF the rebuild fails, THEN THE Verification_Suite SHALL display the Docker build error output and SHALL NOT proceed to the Docker prune step.

---

### Requirement 10: Docker Cleanup

**User Story:** As a deployment engineer, I want to prune unused Docker data after a confirmed successful deployment, so that disk space is reclaimed and the host remains clean.

#### Acceptance Criteria

1. WHEN the rebuild and restart are confirmed successful, THE Verification_Suite SHALL execute `docker system prune -f` to remove stopped containers, dangling images, and unused networks.
2. WHEN the prune runs, THE Verification_Suite SHALL display the amount of disk space reclaimed.
3. THE Verification_Suite SHALL NOT prune Docker volumes during the automated cleanup to prevent accidental data loss.
4. IF the prune command fails, THEN THE Verification_Suite SHALL log the error and continue without treating it as a blocking failure.
5. WHEN cleanup completes, THE Verification_Suite SHALL display a final summary showing which verification steps passed, which failed, and the total disk space reclaimed.

---

### Requirement 11: Comprehensive Selenium Testing

**User Story:** As a deployment engineer, I want to run comprehensive Selenium tests across all pages, authentication flows, and user interactions, so that the website is fully functional and production-ready.

#### Acceptance Criteria

1. WHEN the deployment verification runs, THE Verification_Suite SHALL execute all Selenium_Tests for the ctc-research.com website.
2. WHEN Selenium_Tests run, THE Verification_Suite SHALL test all pages from the dumped data with all available translations.
3. WHEN Selenium_Tests run, THE Verification_Suite SHALL verify that all Static_Assets (CSS, JS, images) load without 404 errors.
4. WHEN Selenium_Tests run, THE Verification_Suite SHALL test the complete registration flow end-to-end.
5. WHEN Selenium_Tests run, THE Verification_Suite SHALL test the complete login flow end-to-end.
6. WHEN Selenium_Tests run, THE Verification_Suite SHALL test the invite page and invite flow.
7. WHEN Selenium_Tests run, THE Verification_Suite SHALL test all notification types (success, error, warning, info).
8. WHEN Selenium_Tests run, THE Verification_Suite SHALL test error pages (404, 500, 403).
9. WHEN Selenium_Tests run, THE Verification_Suite SHALL test admin pages accessibility and permissions.
10. WHEN Selenium_Tests run, THE Verification_Suite SHALL test profile pages accessibility and functionality.
11. IF any Selenium_Test fails, THEN THE Verification_Suite SHALL capture the failure details and display them in the final report.

---

### Requirement 12: Email Invitation System

**User Story:** As a deployment engineer, I want to send invite emails to all addresses in emails.csv, so that users can be invited to the platform.

#### Acceptance Criteria

1. WHEN the deployment verification completes successfully, THE Verification_Suite SHALL read the `emails.csv` file from the workspace root.
2. WHEN emails are read from the CSV, THE Verification_Suite SHALL create an Invite_Record in the database for each email address.
3. WHEN an Invite_Record is created, THE Verification_Suite SHALL send an invite email to the address with a Unique_Token invite link.
4. WHEN invite emails are sent, THE Verification_Suite SHALL log each sent invite with timestamp and delivery status.
5. WHEN all invites are sent, THE Verification_Suite SHALL verify that all emails were sent successfully by checking email logs.
6. IF an email fails to send, THEN THE Verification_Suite SHALL log the failure and continue with the next email.
7. WHEN all invites are complete, THE Verification_Suite SHALL display a summary of sent invites and any failures.

---

## Cross-References

- **Design Document**: See `.kiro/specs/ctc-research-deployment-verification/design.md` for implementation details
- **Task List**: See `.kiro/specs/ctc-research-deployment-verification/tasks.md` for completed implementation tasks
- **Implementation**: Located in `ctc-research.com/core/CI/verify_deployment.py`
- **Selenium Tests**: Located in `ctc-research.com/core/CI/tests/` directory (test_auth_selenium.py, test_assets_selenium.py)
- **Email Invitation Command**: Located in `ctc-research.com/management/commands/send_invites.py`

## Validation Status

All requirements have been implemented as verified by the task completion status in `tasks.md`. The verification suite is operational and integrated into the deployment workflow via the `make verify` command.
