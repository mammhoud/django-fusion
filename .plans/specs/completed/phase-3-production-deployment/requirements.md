# Requirements: Phase 3 — Production Deployment & Verification

## Introduction

Phase 3 covers building, deploying, and verifying the structa.cloud application in production Docker containers. All Phase 2 code has been synced — this phase makes it live and verified.

---

## Glossary

- **Docker_Image**: A read-only template used to create Docker containers, built from a Dockerfile
- **Docker_Container**: A runnable instance of a Docker image
- **Healthy_Status**: A container state where the Docker health check returns exit code 0
- **Django_Migration**: A database schema change tracked and applied by Django's migration framework
- **Static_Assets**: CSS, JavaScript, and image files served directly by the web server, collected via `collectstatic`
- **Superuser**: A Django admin account with all permissions, created via management command
- **System_Check**: Django's built-in validation framework that detects configuration errors before startup
- **Fixture**: A JSON or YAML file containing serialized Django model data for loading into the database
- **Health_Endpoint**: An HTTP endpoint that returns a status code indicating service availability
- **Locale**: A language and regional settings combination used for internationalization
- **MO_File**: A compiled binary message catalog file used by gettext for translations
- **ASGI_Module**: The Asynchronous Server Gateway Interface entry point for the Django application
- **RQ_Worker**: A Redis Queue worker process that executes background jobs asynchronously
- **Entrypoint_Script**: The shell script executed when a Docker container starts
- **UV**: A fast Python package manager used to install and manage project dependencies
- **Wagtail_Home_Page**: The root page node required by Wagtail CMS to function correctly
- **LOAD_FIXTURES**: An environment variable that controls whether fixture data is loaded on container startup
- **Cron_Job**: A scheduled task that runs at defined intervals inside the container
- **Traceback**: A Python error stack trace printed to stderr indicating an unhandled exception

---

## Requirements

### Requirement 1: Docker Image Build

**User Story:** As a deployment engineer, I want all Docker images to build without errors, so that the application can be deployed to production.

#### Acceptance Criteria

1. WHEN the build command is executed for the structa.cloud Django image, THE Build_System SHALL complete without errors using `structa.cloud/compose/django/Dockerfile`
2. WHEN the build command is executed for the nginx media image, THE Build_System SHALL complete without errors
3. THE Build_System SHALL produce Docker_Image artifacts for all required services
4. WHEN a Docker_Image build fails, THE Build_System SHALL output a descriptive error message identifying the failing step

---

### Requirement 2: Container Startup

**User Story:** As a deployment engineer, I want all containers to start and reach healthy status, so that the application is fully operational.

#### Acceptance Criteria

1. WHEN the postgres and redis infrastructure containers are started, THE Deployment_System SHALL bring both containers to Healthy_Status within 60 seconds
2. WHEN the website, website-media, and website-worker containers are started, THE Deployment_System SHALL bring all three containers to Healthy_Status within 120 seconds
3. WHEN any container fails to reach Healthy_Status, THE Deployment_System SHALL log the failure reason to the container log
4. THE Deployment_System SHALL start infrastructure containers before application containers

---

### Requirement 3: Django Setup

**User Story:** As a deployment engineer, I want Django setup commands to complete successfully, so that the application database and static files are ready for use.

#### Acceptance Criteria

1. WHEN `migrate --noinput` is executed inside the website container, THE Django_System SHALL apply all pending migrations and report zero unapplied migrations
2. WHEN `collectstatic --noinput` is executed inside the website container, THE Django_System SHALL collect all Static_Assets without errors
3. WHEN the superuser creation command is executed and no superuser exists, THE Django_System SHALL create a superuser account
4. WHEN the superuser creation command is executed and a superuser already exists, THE Django_System SHALL skip creation without error
5. WHEN `python manage.py check` is executed inside the website container, THE Django_System SHALL report zero system check errors

---

### Requirement 4: Data Loading

**User Story:** As a deployment engineer, I want fixture data loaded when present, so that the application starts with the expected initial data.

#### Acceptance Criteria

1. WHEN `dump-data.json` is present in the fixtures directory, THE Django_System SHALL load the fixture without errors
2. WHEN `dump-data.json` is absent, THE Django_System SHALL skip fixture loading without error
3. AFTER fixture loading completes, THE Django_System SHALL verify the database contains the expected record counts from the fixture
4. WHEN fixture loading fails, THE Django_System SHALL log a descriptive error message and halt container startup

---

### Requirement 5: Health Verification

**User Story:** As a deployment engineer, I want all health endpoints to return HTTP 200, so that I can confirm the application is serving requests correctly.

#### Acceptance Criteria

1. WHEN a GET request is sent to `/health/`, THE Web_Server SHALL return HTTP 200
2. WHEN a GET request is sent to `/health/assets/`, THE Web_Server SHALL return HTTP 200
3. WHEN a GET request is sent to `/health/media/`, THE Web_Server SHALL return HTTP 200
4. WHEN a GET request is sent to `/admin/`, THE Web_Server SHALL return HTTP 200 or HTTP 302 redirect to the login page
5. WHEN any health endpoint returns a non-200 status code, THE Monitoring_System SHALL log the failure with the actual status code received

---

### Requirement 6: Translation Compilation

**User Story:** As a deployment engineer, I want translation messages compiled for all locales, so that the application displays correctly in all supported languages.

#### Acceptance Criteria

1. WHEN `compilemessages` is executed inside the website container, THE Django_System SHALL compile message catalogs for all configured Locale values without errors
2. AFTER `compilemessages` completes, THE Django_System SHALL have generated MO_File artifacts for each configured Locale
3. WHEN language switching is tested in the running application, THE Web_Server SHALL serve translated content for each supported Locale
4. WHEN `compilemessages` encounters a missing or malformed message file, THE Django_System SHALL log a descriptive error identifying the affected Locale

---

### Requirement 7: Entrypoint Script Alignment

**User Story:** As a deployment engineer, I want the structa.cloud entrypoint script to match the ctc-research patterns, so that both projects have consistent and reliable startup behavior.

#### Acceptance Criteria

1. THE Entrypoint_Script SHALL execute `makemigrations` followed by `migrate` on container startup
2. THE Entrypoint_Script SHALL execute `collectstatic` on container startup
3. THE Entrypoint_Script SHALL invoke `django_rseal.scripts.superuser` for superuser creation on container startup
4. THE Entrypoint_Script SHALL execute the Wagtail_Home_Page setup command on container startup
5. WHEN the `LOAD_FIXTURES` environment variable is set to `true`, THE Entrypoint_Script SHALL load fixture data on container startup
6. THE Entrypoint_Script SHALL configure a Cron_Job for error report generation on container startup
7. THE Entrypoint_Script SHALL use `alliance.asgi:application` as the ASGI_Module in the start script

---

### Requirement 8: Dockerfile Alignment

**User Story:** As a deployment engineer, I want the structa.cloud Dockerfile to match the ctc-research pattern, so that both projects build consistently using the same dependency management approach.

#### Acceptance Criteria

1. THE Dockerfile SHALL install venv and libs editable packages explicitly using `pip install -e`
2. THE Dockerfile SHALL set the `UV_PROJECT_ENVIRONMENT` environment variable before running `uv sync`
3. THE Dockerfile SHALL execute `uv sync --frozen` to install dependencies from the lockfile
4. WHEN a worker service is defined in docker-compose.yml, THE Dockerfile SHALL copy the rqworker-start script into the image

---

### Requirement 9: RQ Worker

**User Story:** As a deployment engineer, I want the RQ worker container to start and process background jobs, so that asynchronous tasks are handled reliably.

#### Acceptance Criteria

1. WHEN the website-worker container is started, THE RQ_Worker SHALL reach Healthy_Status within 120 seconds
2. WHEN a background job is submitted to the Redis queue, THE RQ_Worker SHALL process the job without error
3. WHEN the RQ_Worker encounters a job processing error, THE RQ_Worker SHALL log the error with a full Traceback and continue processing subsequent jobs
4. THE RQ_Worker SHALL maintain a persistent connection to the Redis queue and reconnect automatically after a connection interruption

---

### Requirement 10: Clean Logs on Startup

**User Story:** As a deployment engineer, I want container logs to be free of errors and tracebacks on startup, so that I can confirm the application started cleanly.

#### Acceptance Criteria

1. WHEN all containers have reached Healthy_Status, THE Deployment_System SHALL have produced no Python Traceback entries in any container log
2. WHEN all containers have reached Healthy_Status, THE Deployment_System SHALL have produced no CRITICAL or ERROR level log messages in any container log
3. WHEN a CRITICAL or ERROR log message is detected during startup, THE Monitoring_System SHALL surface the message for immediate review
4. THE Deployment_System SHALL complete the full startup sequence with only INFO and DEBUG level log messages under normal operating conditions

---

## Cross-References

- **Phase 2 Spec**: `.kiro/specs/phase-2-website-sync-completion/` — Phase 3 depends on all Phase 2 code being synced
- **CTC Research Deployment Spec**: `.kiro/specs/ctc-research-deployment-verification/` — Entrypoint and Dockerfile patterns are aligned with ctc-research patterns defined in that spec
- **Core Logic Consolidation Spec**: `.kiro/specs/core-logic-consolidation-and-app-restructure/` — The `alliance.asgi:application` module referenced in Req 7 is defined by the restructured app layout
