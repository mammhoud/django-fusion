# Design Document

## Overview

The deployment verification feature is implemented as a Python script (`verify_deployment.py`) located in `ctc-research.com/core/CI/`. It orchestrates a sequential set of checks against the running Docker environment. Each check is a self-contained function that returns a `CheckResult` (pass/fail + message). The script runs from the host machine using `docker exec` calls into the `website` container and direct HTTP requests to the domain. A final summary is printed at the end.

The script is also exposed as a Makefile target (`make verify`) for convenience.

## Requirements Traceability

This design implements all requirements from the Requirements Document:
- **Requirement 1**: Data Loading Verification → `check_data_loading()`
- **Requirement 2**: Static Asset Verification → `check_static_assets()`
- **Requirement 3**: Database Connectivity Verification → `check_database()`
- **Requirement 4**: Migration Verification → `check_migrations()`
- **Requirement 5**: Django Test Execution → `check_django_tests()`
- **Requirement 6**: New Account Registration → `check_registration()`
- **Requirement 7**: Admin Panel Access Verification → `check_admin_panel()`
- **Requirement 8**: URL Availability Verification → `check_urls()`
- **Requirement 9**: Project Rebuild → `rebuild_project()`
- **Requirement 10**: Docker Cleanup → `docker_cleanup()`
- **Requirement 11**: Comprehensive Selenium Testing → Selenium test suite execution
- **Requirement 12**: Email Invitation System → `send_invites.py` management command

---

## Architecture

```
verify_deployment.py
├── CheckResult (dataclass)
├── run_docker_exec()       # helper: docker exec website <cmd>
├── run_http_check()        # helper: HTTP GET/POST with requests
├── check_data_loading()    # Requirement 1
├── check_static_assets()   # Requirement 2
├── check_database()        # Requirement 3
├── check_migrations()      # Requirement 4
├── check_django_tests()    # Requirement 5
├── check_registration()    # Requirement 6
├── check_admin_panel()     # Requirement 7
├── check_urls()            # Requirement 8
├── rebuild_project()       # Requirement 9
├── docker_cleanup()        # Requirement 10
└── main()                  # orchestrator + summary
```

All checks run sequentially. If `rebuild_project()` fails, `docker_cleanup()` is skipped.

---

## Component Details

### CheckResult

```python
@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
```

### run_docker_exec

Runs a command inside the `website` container via `docker exec`. Returns `(stdout, stderr, returncode)`.

```python
def run_docker_exec(cmd: list[str]) -> tuple[str, str, int]:
    result = subprocess.run(
        ["docker", "exec", "website"] + cmd,
        capture_output=True, text=True
    )
    return result.stdout, result.stderr, result.returncode
```

### run_http_check

Sends HTTP requests and returns response status and content.

```python
def run_http_check(url: str, method: str = "GET", data: dict = None) -> tuple[int, str]:
    response = requests.request(method, url, data=data, timeout=30)
    return response.status_code, response.text
```

### check_data_loading (Requirement 1)

1. Verify fixture files exist: `docker exec website test -f /app/ctc-research-data.json`
2. Run `loaddata ctc-research-data.json` and `loaddata wagtail_pages_dump.json`
3. Query latest record timestamp via `python com shell -c "from django.contrib.auth import get_user_model; ..."`

### check_static_assets (Requirement 2)

1. Run `collectstatic --noinput` via docker exec
2. Check volume for CSS/JS: `docker exec website find /app/assets/staticfiles -name '*.css' | head -1`
3. HTTP GET to `http://localhost:8271/static/` (nginx port from override) for a known file

### check_database (Requirement 3)

1. `python com check --database default`
2. `docker exec website python -c "import psycopg2; psycopg2.connect(...)"`
3. Ping redis: `docker exec website python -c "import redis; redis.Redis.from_url(...).ping()"`

### check_migrations (Requirement 4)

1. `python com migrate --noinput`
2. `python com showmigrations` — parse output for `[ ]` entries
3. `python com migrate --check`

### check_django_tests (Requirement 5)

1. `python com test --noinput -k auth`
2. Parse output for `FAILED` or `ERROR` counts
3. Confirm test DB is used (Django default: `test_db_ctc`)

### check_registration (Requirement 6)

1. Check if user exists: `python com shell -c "from django.contrib.auth import get_user_model; ..."`
2. If not exists: POST to registration URL with `mahmoud.ezat@outlook.com`
3. Confirm user record in DB after POST

### check_admin_panel (Requirement 7)

1. GET `/admin/` — expect 200 or 302
2. POST login with superuser credentials, GET `/admin/` — expect 200
3. Check response body for admin UI markers

### check_urls (Requirement 8)

1. GET `https://ctc-research.com/`, `/health/`, `/admin/`
2. Verify Traefik headers (`X-Forwarded-Host`, `Via`)
3. TLS check via `ssl.get_server_certificate()`

### rebuild_project (Requirement 9)

1. `docker compose -f ctc-research.com/docker-compose.yml build --no-cache`
2. `docker compose -f ctc-research.com/docker-compose.yml up -d`
3. Poll `docker inspect website --format '{{.State.Health.Status}}'` until `healthy` or timeout (120s)
4. Confirm all three containers running

### docker_cleanup (Requirement 10)

1. `docker system prune -f` (no `--volumes` flag)
2. Parse output for "Total reclaimed space"
3. Print final summary table

---

## File Structure

```
ctc-research.com/core/CI/
├── __init__.py
├── verify_deployment.py
└── tests/
    ├── __init__.py
    ├── test_auth_selenium.py
    └── test_assets_selenium.py

ctc-research.com/management/commands/
├── __init__.py
└── send_invites.py

ctc-research.com/makefile  (add `verify` target)
```

---

## Selenium Testing Architecture (Requirement 11)

### Test Structure

All Selenium tests use `django_grep.browser` fixtures and follow this pattern:

```python
def test_page_loads(browser):
    browser.get("http://localhost:8270/")
    assert browser.title != ""
    # assertions...
```

### Test Categories

1. **Homepage & Pages**: Load all pages, verify content, test navigation
2. **Authentication**: Register, login, logout, password reset
3. **Invites**: Send invites, verify invite flow
4. **Notifications**: Test all notification types
5. **Error Pages**: 404, 500, 403 error handling
6. **Admin**: Admin login, dashboard, permissions
7. **Profile**: Profile access, edit, update
8. **Assets**: CSS, JS, images load without errors
9. **Translations**: All languages load correctly

### Selenium Fixtures (conftest.py)

```python
@pytest.fixture
def browser():
    # Initialize Selenium WebDriver
    # Point to http://localhost:8270 (ctc-research.com)
    # Yield driver
    # Cleanup
```

### Selenium Test Execution

The Selenium test suite is executed as part of the deployment verification workflow:
1. All Selenium tests are located in `ctc-research.com/core/CI/tests/`
2. Tests are executed using `pytest core/CI/tests/ -v`
3. Test results are captured and reported in the verification summary

---

## Email Invitation System (Requirement 12)

### send_invites.py Management Command

```python
class Command(BaseCommand):
    def handle(self, *args, **options):
        # Read emails.csv
        # For each email:
        #   - Create Invite record
        #   - Send invite email
        #   - Log result
        # Print summary
```

### CSV Format

```csv
email
user1@example.com
user2@example.com
```

### Invite Email Template

- Subject: "You're invited to ctc-research.com"
- Body: Includes unique invite link with token
- Link format: `https://ctc-research.com/invite/{token}/`

### Invitation System Integration

The email invitation system is executed after successful deployment verification:
1. Reads `emails.csv` from workspace root
2. Creates invite records in database
3. Sends invitation emails with unique tokens
4. Logs all operations for audit trail

---

## Correctness Properties

### Property 1: Data Loading Idempotence
Running `loaddata` twice on the same fixture produces the same database state as running it once (Django's `loaddata` uses natural keys / pk matching).
- **Type**: example test
- **Test**: Run loaddata, count objects. Run loaddata again, count objects. Counts must be equal.
- **Validates**: Requirement 1.2, 1.3

### Property 2: collectstatic Output Invariant
After `collectstatic`, the staticfiles directory must contain at least one `.css` file and one `.js` file regardless of which theme variant is active.
- **Type**: example test
- **Test**: Run collectstatic, assert `find staticfiles -name '*.css'` and `find staticfiles -name '*.js'` both return results.
- **Validates**: Requirement 2.2

### Property 3: Migration Idempotence
Running `migrate` on an already-migrated database produces no changes and exits 0.
- **Type**: example test
- **Test**: Run migrate, then run `migrate --check`. Exit code must be 0.
- **Validates**: Requirement 4.3

### Property 4: User Registration Idempotence
Attempting to register `mahmoud.ezat@outlook.com` when the user already exists must not create a duplicate and must not raise an unhandled exception.
- **Type**: edge-case test
- **Test**: Create user, attempt registration again, assert user count for that email is still 1.
- **Validates**: Requirement 6.4

### Property 5: Docker Prune Does Not Remove Volumes
After `docker system prune -f`, the `website_static` and `website_media` volumes must still exist.
- **Type**: example test (invariant)
- **Test**: Run prune, assert `docker volume ls` still lists `website_static` and `website_media`.
- **Validates**: Requirement 10.3

### Property 6: Rebuild Failure Blocks Cleanup
If `docker compose build` exits non-zero, `docker system prune` must not be called.
- **Type**: edge-case test
- **Test**: Mock build to fail, assert prune function is never invoked.
- **Validates**: Requirement 9.5

### Property 7: Auth Tests Use Isolated Database
The test database name used during `python com test -k auth` must differ from the production database name `db_ctc`.
- **Type**: example test
- **Test**: Capture Django test output, assert it references `test_db_ctc` or equivalent test DB name, not `db_ctc`.
- **Validates**: Requirement 5.5

### Property 8: Selenium Tests Load All Pages Without 5xx Errors
For every page in the dumped data, loading that page via Selenium must result in HTTP 200 and no JavaScript errors.
- **Type**: example test
- **Test**: For each page URL, load via Selenium, assert HTTP 200, assert no console errors.
- **Validates**: Requirement 11.2

### Property 9: Registration Creates Valid User Record
After successful registration via Selenium, a user record must exist in the database with the registered email and password must be verifiable.
- **Type**: example test
- **Test**: Register user, query DB, assert user exists, assert password is hashable.
- **Validates**: Requirement 11.4

### Property 10: Invite Email Uniqueness
Each invite email sent must have a unique token that cannot be reused.
- **Type**: edge-case test
- **Test**: Send two invites to same email, assert tokens are different, assert both invites exist in DB.
- **Validates**: Requirement 12.3

### Property 11: All Translations Load Without Errors
For each available language, loading the homepage must result in HTTP 200 and correct language content.
- **Type**: example test
- **Test**: For each language code, load homepage with language parameter, assert HTTP 200, assert content is in correct language.
- **Validates**: Requirement 11.2

---

## Error Handling Strategy

- Each check function catches all exceptions and returns a `CheckResult(passed=False, message=str(e))`.
- The orchestrator collects all results and prints a summary table.
- Only `rebuild_project` failure gates `docker_cleanup`.
- All other check failures are non-blocking — the suite continues and reports at the end.
- Selenium test failures are captured and reported in the final summary.
- Email invitation failures are logged but do not block overall verification.

---

## Makefile Integration

Add to `ctc-research.com/makefile`:

```makefile
verify: ## 🔍 Run full deployment verification suite
	@echo -e "$(BLUE)Running deployment verification...$(NC)"
	@$(UV) run python -m core.CI.verify_deployment
	@echo -e "$(GREEN)✅ Verification complete$(NC)"
```

## Validation

The design has been validated against all requirements:
- All 12 requirements have corresponding implementation components
- Error handling strategy covers all failure scenarios
- Correctness properties verify critical behavior
- File structure matches actual implementation
- Makefile integration provides convenient execution
