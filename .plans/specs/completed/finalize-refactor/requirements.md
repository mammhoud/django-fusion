# Requirements: Finalize Refactor

## Overview

This spec covers the final phase of the workspace refactor: unifying the virtual environment, deduplicating the structa.cloud app namespace, extending django-grep as the centralized testing tool, adding Selenium tests for ctc-research.com, resolving all import errors, building and running ctc-research containers with fresh data, and adding backup management commands.

---

## Glossary

- **Workspace_Root**: The top-level directory containing all sub-projects and the unified virtual environment.
- **Unified_Venv**: The single shared Python virtual environment at `.venv/` managed by `uv`, used by all packages in the workspace.
- **django-osoul**: Foundation library providing models, mixins, UI components, CI models, and contrib utilities. Has no dependency on wagtail, celery, or django-rseal.
- **django-rseal**: Automation library providing pipelines, email tooling, workflows, management commands, and contrib utilities. Depends on django-osoul, wagtail, and celery.
- **django-grep**: Centralized testing framework providing seeders, test base classes, assertions, factories, fixtures, mixins, Selenium base, and pytest plugin.
- **nawaai**: AI/MCP toolkit providing crafts_ai components. Has no Django imports (pure Python).
- **Shim**: A thin Python module that re-exports symbols from their new canonical location to preserve backward compatibility with existing import paths.
- **INSTALLED_APPS**: Django configuration list of application module paths used to register apps with the Django framework.
- **Selenium_Test**: An automated browser test that drives a real or headless browser to verify end-to-end behaviour.
- **SeleniumTestCase**: The base test class in `django_grep.tests.selenium_base` that provides browser driver setup and teardown.
- **pytest11**: A setuptools entry point that registers a pytest plugin automatically when the package is installed.
- **BACKUP_DIR**: Environment variable specifying the filesystem path where backup files are written.
- **Entrypoint**: The shell script executed when a Docker container starts, responsible for running migrations and starting the application server.
- **ctc-research**: The `ctc-research.com` Django project, one of the two production sites in this workspace.
- **structa.cloud**: The second Django production site in this workspace.
- **uv**: The Python package and project manager used for dependency resolution and virtual environment management across this workspace.
- **Boundary_Check**: Verification that a package does not import from packages outside its declared dependency set.

---

## R1 — Workspace venv Unification

### R1.1
THE Workspace_Root SHALL maintain a single Unified_Venv at `.venv/` as the canonical virtual environment for all packages.

#### Acceptance Criteria
1. WHEN `uv sync --frozen` is executed at the Workspace_Root, THE Unified_Venv SHALL be created or updated with all workspace dependencies.
2. THE root `pyproject.toml` SHALL declare all workspace members including `ctc-research.com`, `structa.cloud`, and all packages under `venv/libs/`.
3. WHEN `python -c "import django_grep"` is executed inside the Unified_Venv, THE command SHALL exit with code 0.

### R1.2
THE root `pyproject.toml` SHALL declare the unified venv path and all workspace members so that sub-packages resolve dependencies from the shared environment.

#### Acceptance Criteria
1. THE root `pyproject.toml` SHALL contain a `[tool.uv]` section with `venv = ".venv"`.
2. THE root `pyproject.toml` SHALL list all sub-packages as workspace members.
3. WHEN a sub-package is installed via `uv sync`, THE sub-package SHALL be importable from the Unified_Venv without a separate `pip install`.

### R1.3
THE sub-packages (`ctc-research.com`, `structa.cloud`, `venv/libs/*`) SHALL NOT maintain separate virtual environments for production use.

#### Acceptance Criteria
1. WHEN the workspace is set up, no sub-package directory SHALL contain an active `.venv/` that overrides the Workspace_Root Unified_Venv.
2. THE Unified_Venv SHALL be the sole environment used by Docker containers and CI pipelines.

---

## R2 — structa.cloud Apps Deduplication

### R2.1
THE `structa.cloud/apps/apps/` duplicate namespace SHALL be merged into `structa.cloud/apps/` and the duplicate directory SHALL be removed.

#### Acceptance Criteria
1. WHEN the merge is complete, the path `structa.cloud/apps/apps/` SHALL NOT exist.
2. All subdirectories previously under `structa.cloud/apps/apps/` SHALL be accessible under `structa.cloud/apps/`.
3. WHEN `python -c "from apps.handlers import urls"` is executed inside the structa.cloud project, THE command SHALL exit with code 0.

### R2.2
THE `INSTALLED_APPS` and URL configurations in structa.cloud SHALL reference the `apps.*` namespace, not `apps.apps.*`.

#### Acceptance Criteria
1. THE structa.cloud settings files SHALL contain no occurrences of the string `apps.apps.`.
2. THE structa.cloud URL configuration SHALL resolve all app URL includes without import errors.

---

## R3 — django-grep as Centralized Testing Tool

### R3.1
THE `django_grep.tests` module SHALL expose `SeleniumTestCase`, `BaseTestCase`, `BaseAPITestCase`, fixtures, and assertions as the canonical test base for all Django projects in this workspace.

#### Acceptance Criteria
1. WHEN `from django_grep.tests import SeleniumTestCase` is executed, THE import SHALL succeed without errors.
2. WHEN `from django_grep.tests import BaseTestCase, BaseAPITestCase` is executed, THE import SHALL succeed without errors.
3. THE `django_grep.tests` module SHALL export at minimum: `SeleniumTestCase`, `BaseTestCase`, `BaseAPITestCase`, `BaseAssertions`.

### R3.2
THE `django-grep` package SHALL declare `selenium>=4.0` as an optional dependency under the `[selenium]` extras group.

#### Acceptance Criteria
1. THE `django-grep/pyproject.toml` SHALL contain `[project.optional-dependencies]` with a `selenium` key listing `selenium>=4.0`.
2. WHEN `uv pip install "django-grep[selenium]"` is executed, THE selenium package SHALL be installed.

### R3.3
THE `django-grep` package SHALL register a `pytest11` entry point so its fixtures are auto-registered in any project that installs it.

#### Acceptance Criteria
1. THE `django-grep/pyproject.toml` SHALL contain a `[project.entry-points."pytest11"]` section pointing to `django_grep.tests.pytest_plugin`.
2. WHEN `pytest --fixtures` is run in a project that has `django-grep` installed, THE fixtures from `django_grep.tests.pytest_plugin` SHALL appear in the output.

### R3.4
THE `django-grep` package SHALL contain a `tests/selenium/` directory with site-agnostic Selenium base tests.

#### Acceptance Criteria
1. THE path `venv/libs/django-grep/tests/selenium/` SHALL exist and contain at minimum `conftest.py` and `test_site_health.py`.
2. WHEN `pytest venv/libs/django-grep/tests/selenium/ --collect-only` is executed, THE collection SHALL succeed with exit code 0.

### R3.5
THE `django-grep` package SHALL include a `.env.example` file documenting the environment variables `SELENIUM_BASE_URL`, `SELENIUM_BROWSER`, and `SELENIUM_HEADLESS`.

#### Acceptance Criteria
1. THE file `venv/libs/django-grep/.env.example` SHALL exist.
2. THE `.env.example` file SHALL document `SELENIUM_BASE_URL`, `SELENIUM_BROWSER`, and `SELENIUM_HEADLESS` with example values.

---

## R4 — ctc-research Selenium Tests

### R4.1
THE `ctc-research.com/tests/selenium/` directory SHALL contain Selenium tests that use `SeleniumTestCase` from `django_grep.tests`.

#### Acceptance Criteria
1. THE path `ctc-research.com/tests/selenium/` SHALL exist and contain at minimum `conftest.py`, `test_homepage.py`, `test_auth.py`, and `test_admin.py`.
2. WHEN `pytest ctc-research.com/tests/selenium/ --collect-only` is executed, THE collection SHALL succeed with exit code 0.

### R4.2
THE ctc-research Selenium tests SHALL cover: homepage loads, login page loads, admin login page loads, and static/media asset HTTP 200 responses.

#### Acceptance Criteria
1. THE `test_homepage.py` file SHALL contain a test that performs an HTTP GET to `/` and asserts a 200 response.
2. THE `test_auth.py` file SHALL contain a test that performs an HTTP GET to `/accounts/login/` and asserts the login form is present.
3. THE `test_admin.py` file SHALL contain a test that performs an HTTP GET to `/admin/` and asserts either a redirect or a login form is present.

### R4.3
THE ctc-research Selenium tests SHALL be configurable via environment variables `SELENIUM_BASE_URL` and `SELENIUM_HEADLESS`.

#### Acceptance Criteria
1. THE `ctc-research.com/tests/selenium/conftest.py` SHALL read `SELENIUM_BASE_URL` from the environment, defaulting to `http://localhost:8270`.
2. THE `ctc-research.com/tests/selenium/conftest.py` SHALL read `SELENIUM_HEADLESS` from the environment to control headless mode.

---

## R5 — Import Fixes Before Build

### R5.1
THE ctc-research.com project SHALL have all Python import errors resolved before the container build.

#### Acceptance Criteria
1. WHEN `python manage.py check` is executed inside the ctc-research container, THE command SHALL exit with code 0 and report 0 errors.
2. THE `django_rseal.pipelines.urls` module SHALL be importable without errors.
3. THE `django_osoul.CI` package SHALL be importable without errors.

### R5.2
THE ctc-research Entrypoint script SHALL use `uv run python` consistently for all Python invocations.

#### Acceptance Criteria
1. THE ctc-research Entrypoint script SHALL contain no direct references to `/app/.venv/bin/python` for management command invocations.
2. WHEN the container starts, THE Entrypoint SHALL execute `uv run python manage.py migrate` without errors.

### R5.3
THE `django_rseal.contrib.enums` module SHALL re-export all enum symbols from `django_osoul.contrib.enums` to preserve backward compatibility.

#### Acceptance Criteria
1. WHEN `from django_rseal.contrib.enums import Environment, Runtime, Module` is executed, THE import SHALL succeed.
2. WHEN `from django_rseal.contrib.enums import FileUploadStorage, FileUploadStrategy` is executed, THE import SHALL succeed.

### R5.4
THE `django_rseal.contrib.models` module SHALL re-export `Contact`, `ContactEmail`, `ContactPhone`, and `Corporate` from their canonical locations.

#### Acceptance Criteria
1. WHEN `from django_rseal.contrib.models import Contact, ContactEmail, ContactPhone` is executed, THE import SHALL succeed.
2. WHEN `from django_rseal.contrib.models import Corporate` is executed, THE import SHALL succeed.

---

## R6 — Docker Build: ctc-research Only

### R6.1
THE ctc-research Docker Compose configuration SHALL define `website`, `website-media`, and `website-worker` services.

#### Acceptance Criteria
1. THE `ctc-research.com/docker-compose.yml` SHALL define services named `website`, `website-media`, and `website-worker`.
2. WHEN `docker compose -f ctc-research.com/docker-compose.yml build website` is executed, THE build SHALL complete without errors.

### R6.2
THE `website` service in `ctc-research.com/docker-compose.yml` SHALL declare `depends_on` for the `postgres` and `redis` services.

#### Acceptance Criteria
1. THE `ctc-research.com/docker-compose.yml` `website` service SHALL contain a `depends_on` entry for `postgres` with `condition: service_healthy`.
2. THE `ctc-research.com/docker-compose.yml` `website` service SHALL contain a `depends_on` entry for `redis` with `condition: service_started`.

### R6.3
THE build context in `ctc-research.com/docker-compose.yml` SHALL correctly reference `../venv/libs` so workspace packages are available during the build.

#### Acceptance Criteria
1. THE Dockerfile used by the `website` service SHALL successfully copy workspace library packages from the build context.
2. WHEN `docker compose up website` is executed after a successful build, THE container SHALL start without Python import errors.

---

## R7 — Load Fresh Data

### R7.1
THE ctc-research Entrypoint SHALL load fixture data from `wagtail_pages_dump.json` and `ctc-research-data.json` when the `LOAD_FIXTURES` environment variable is set to `true`.

#### Acceptance Criteria
1. WHEN `LOAD_FIXTURES=true` is set and the container starts, THE Entrypoint SHALL execute `uv run python manage.py loaddata wagtail_pages_dump.json ctc-research-data.json`.
2. WHEN `LOAD_FIXTURES` is not set or is set to `false`, THE Entrypoint SHALL skip the `loaddata` step.

### R7.2
THE data loading step SHALL be idempotent so it is safe to re-run without causing duplicate data errors.

#### Acceptance Criteria
1. WHEN the `loaddata` command is executed twice in sequence on the same database, THE second execution SHALL complete without raising integrity errors.

---

## R8 — Backup Management Commands in django-grep

### R8.1
THE `django-grep` package SHALL include a `backup_db` management command that dumps the database to a timestamped file in `BACKUP_DIR`.

#### Acceptance Criteria
1. WHEN `python manage.py backup_db` is executed, THE command SHALL create a file at `BACKUP_DIR/db_YYYYMMDD_HHMMSS.json` (or `.sql.gz` for PostgreSQL).
2. WHEN the backup completes, THE command SHALL log a success message including the output file path.
3. WHEN the backup fails, THE command SHALL log an error message and exit with a non-zero status code.

### R8.2
THE `django-grep` package SHALL include a `backup_media` management command that archives the media directory to a timestamped `.tar.gz` file in `BACKUP_DIR`.

#### Acceptance Criteria
1. WHEN `python manage.py backup_media` is executed, THE command SHALL create a file at `BACKUP_DIR/media_YYYYMMDD_HHMMSS.tar.gz`.
2. WHEN the archive completes, THE command SHALL log a success message including the output file path.
3. WHEN the archive fails, THE command SHALL log an error message and exit with a non-zero status code.

### R8.3
THE `django-grep` package `.env.example` SHALL document the `BACKUP_DIR` and `DB_BACKUP_COMPRESS` environment variables.

#### Acceptance Criteria
1. THE `venv/libs/django-grep/.env.example` SHALL contain entries for `BACKUP_DIR` and `DB_BACKUP_COMPRESS` with example values and descriptions.

---

## R9 — Running Logs: No Errors

### R9.1
THE ctc-research container startup logs SHALL contain no Python import errors or tracebacks.

#### Acceptance Criteria
1. WHEN `docker compose up website` is executed, THE container logs SHALL contain no lines matching `ImportError` or `ModuleNotFoundError`.
2. WHEN `docker compose up website` is executed, THE container logs SHALL contain no Python traceback blocks.

### R9.2
THE `python manage.py check` command SHALL pass with 0 errors inside the ctc-research container.

#### Acceptance Criteria
1. WHEN `docker exec website uv run python manage.py check` is executed, THE command SHALL exit with code 0.
2. THE output SHALL contain the text `System check identified no issues`.

### R9.3
THE ctc-research Selenium test suite SHALL be collectable without import errors.

#### Acceptance Criteria
1. WHEN `pytest ctc-research.com/tests/selenium/ --collect-only` is executed, THE command SHALL exit with code 0.
2. THE collection output SHALL list at minimum the tests in `test_homepage.py`, `test_auth.py`, and `test_admin.py`.

---

## Cross-References

- **django-refactoring spec** (`.kiro/specs/django-refactoring/`): Defines the package boundary rules and module responsibilities that this spec implements.
- **ecosystem-architectural-refactoring spec** (`.kiro/specs/ecosystem-architectural-refactoring/`): Defines the high-level architecture that the package moves in this spec realise.
- **ctc-research-deployment-verification spec** (`.kiro/specs/ctc-research-deployment-verification/`): Covers post-deployment verification steps that depend on the Docker build work in R6 and R7.
- **phase-3-production-deployment spec** (`.kiro/specs/phase-3-production-deployment/`): Covers production deployment steps that build on the container work completed in this spec.
