# Requirements Document

## Introduction

The `.kiro/specs-organized` directory contains eight specs across six categories (auth, fixes, integration, docs, modernization) with a significant number of incomplete tasks. This feature defines the requirements for systematically completing all outstanding work across those specs in a prioritized, organized manner.

The specs fall into three completion states:
1. **Partially complete** — most implementation is done but parent tasks or optional property tests remain open (`auth/auth-allauth-enhancement`, `auth/ctc-structa-admin-auth-integration`, `fixes/alliance-website-docker-fix`)
2. **Fully incomplete** — no tasks have been started (`fixes/fix-wagtailsnippets-assets-email-enhancement`, `integration/blog-lms-wagtail-integration`, `docs/comprehensive-project-documentation`, `docs/ctc-docs-and-core-containers`, `modernization/structa-color-update`)

Completion is tracked by updating task status markers in each spec's `tasks.md` file and verifying the underlying work is actually done in the codebase.

---

## Glossary

- **Spec**: A specification directory under `.kiro/specs-organized/` containing `requirements.md`, `design.md`, and `tasks.md`
- **Task**: A single checklist item in a `tasks.md` file, marked `[ ]` (not started), `[-]` (in-progress), or `[x]` (complete)
- **Parent Task**: A top-level task that is considered complete only when all its sub-tasks are complete
- **Optional Task**: A task marked with `*` that may be skipped for a faster MVP but represents a correctness property test
- **Property Test**: A Hypothesis-based test that validates a correctness property over many generated inputs
- **PBT**: Property-Based Testing — the practice of generating arbitrary inputs to verify invariants hold
- **HTMX**: A JavaScript library for making partial-page HTTP requests; responses may include `HX-Request` and `HX-Trigger` headers
- **Allauth**: `django-allauth`, a Django authentication package supporting social login and email verification
- **Unfold**: `django-unfold`, a modern Django admin theme
- **Wagtail**: A Django-based CMS used across both `ctc-research` and `structa.cloud/core`
- **Docsify**: A documentation site generator that renders Markdown files in the browser
- **Traefik**: A reverse proxy and load balancer used for routing between Docker services
- **Round-Trip Property**: The correctness property that `parse(format(x)) == x` for any serializable value `x`
- **Single-Active Invariant**: The constraint that at most one record of a given type may have `is_active=True` at any time

---

## Requirements

### Requirement 1: Close Partially-Complete Parent Tasks in Auth Specs

**User Story:** As a developer, I want all parent tasks in the auth specs to reflect the true completion state of their sub-tasks, so that the task list accurately represents what has been done.

#### Acceptance Criteria

1. WHEN all sub-tasks of a parent task in `auth/ctc-structa-admin-auth-integration` are marked `[x]`, THE Task_Tracker SHALL mark the parent task `[x]` as well.
2. THE Task_Tracker SHALL mark task 2 (`Create ctc-research management commands`) as complete in `auth/ctc-structa-admin-auth-integration/tasks.md` given that sub-tasks 2.1–2.7 are all complete.
3. THE Task_Tracker SHALL mark task 4 (`Port shared commands to structa.cloud/core`) as complete given that sub-tasks 4.1 and 4.2 are all complete.
4. THE Task_Tracker SHALL mark task 5 (`Add health check endpoint and startup diagnostics`) as complete given that sub-tasks 5.1 and 5.2 are all complete.
5. THE Task_Tracker SHALL mark task 7 (`Install and configure Django Unfold for ctc-research`) as complete given that sub-tasks 7.1, 7.2, and 7.3 are all complete.
6. THE Task_Tracker SHALL mark task 9 (`Create structa.cloud/core allauth registration module`) as complete given that sub-tasks 9.1–9.8 are all complete.
7. WHEN the parent task for task 3 in `fixes/alliance-website-docker-fix` has all sub-tasks 3.1–3.5 marked `[x]`, THE Task_Tracker SHALL mark task 3 as `[x]` rather than `[-]`.

### Requirement 2: Complete Optional Property Tests in auth-allauth-enhancement

**User Story:** As a developer, I want the optional property-based tests in `auth/auth-allauth-enhancement` to be written and passing, so that the correctness properties of the allauth integration are verified.

#### Acceptance Criteria

1. WHEN the `auth-allauth-enhancement` spec is being completed, THE Test_Suite SHALL include a property test in `ctc-research/apps/handlers/registration/tests/test_property_allauth_token_roundtrip.py` that validates the allauth-compatible token round-trip property (task 2.2).
2. THE Test_Suite SHALL include a property test in `test_property_single_active_snippet.py` that asserts `AuthEmailTemplate.objects.filter(template_type=t, is_active=True).count() <= 1` after each save (task 3.2).
3. THE Test_Suite SHALL include a property test in `test_property_email_template_resolution.py` that verifies the correct template source (snippet vs file fallback) is used under both snippet-present and snippet-absent conditions (task 5.2).
4. THE Test_Suite SHALL include a property test in `test_property_signin_success_email.py` that asserts `send_signin_success_email` is called for users with `last_login=None` and not called for users with an existing `last_login` datetime (task 7.1).
5. THE Test_Suite SHALL include a property test in `test_property_allauth_htmx_routing.py` that asserts requests with `HX-Request` header receive a fragment response and requests without it receive a full-page response (task 8.1).
6. THE Test_Suite SHALL include a property test in `test_property_login_redirect.py` that asserts the redirect target equals the `next` parameter when present and falls back to the dashboard URL when absent (task 8.2).
7. THE Test_Suite SHALL include a property test in `test_property_allauth_hx_trigger.py` that asserts every HTMX form response contains an `HX-Trigger` header with valid JSON including `showNotification.message` and `showNotification.type` (task 8.3).
8. THE Test_Suite SHALL include a property test in `test_property_confirmation_email.py` that asserts `send_registration_email` is called exactly once per valid signup (task 8.4).
9. WHEN all eight property tests are written, THE Test_Suite SHALL pass with `@settings(max_examples=100)` for each test.

### Requirement 3: Complete fix-wagtailsnippets-assets-email-enhancement

**User Story:** As a developer, I want all nine task groups in the `fixes/fix-wagtailsnippets-assets-email-enhancement` spec completed, so that the Wagtail snippet namespace error is resolved, asset issues are fixed, and the email tooling is in place.

#### Acceptance Criteria

1. WHEN task 1 is executed, THE System SHALL resolve the `KeyError: 'wagtailsnippets_handlers_authemailtemplate'` error in both `ctc-research` and `structa.cloud` by correcting the snippet registration in `wagtail_hooks.py`.
2. WHEN task 2 is executed, THE System SHALL eliminate bad-gateway errors on `structa.cloud` by correcting the webpack public path and nginx static/media configuration.
3. WHEN task 3 is executed, THE Email_Extractor SHALL extract email addresses from markdown files in spec directories and write them to a CSV file with source tracking (spec, file, timestamp).
4. WHEN task 4 is executed, THE Invitation_System SHALL send personalized invitation emails from a CSV input file with rate limiting, dry-run mode, and error recovery.
5. WHEN task 5 is executed, THE Django_Grep_Package SHALL expose the email extraction and invitation sending tools as reusable Django management commands.
6. WHEN task 6 is executed, THE Spec_Directory SHALL have consistent naming conventions across all spec directories with a documented mapping of any renames.
7. WHEN task 7 is executed, THE Bundle_Reader SHALL correctly load webpack bundles in both development and production Docker environments.
8. WHEN task 8 is executed, THE Test_Suite SHALL pass all existing tests with no regressions and include new tests covering email extraction, invitation sending, and asset fixes.
9. WHEN task 9 is executed, THE Deployment_Documentation SHALL include step-by-step deployment instructions, rollback scripts, and post-deployment validation steps.
10. IF any sub-task in tasks 1–9 fails, THEN THE System SHALL log the failure with enough context to reproduce and diagnose the issue.

### Requirement 4: Complete blog-lms-wagtail-integration

**User Story:** As a developer, I want all five phases of the `integration/blog-lms-wagtail-integration` spec completed, so that the Blog and LMS apps are fully implemented, tested, and documented.

#### Acceptance Criteria

1. WHEN Phase 1 is complete, THE Blog_App SHALL provide BlogPost, Category, Tag, and Comment models with Wagtail page type registration, publishing workflow, versioning, SEO fields, and REST API endpoints.
2. WHEN Phase 2 is complete, THE LMS_App SHALL provide Course, Module, Lesson, Enrollment, Progress, Assessment, and Certificate models with Wagtail page type registration, enrollment system, progress tracking, assessment scoring, and REST API endpoints.
3. WHEN Phase 3 is complete, THE Plugin_Installer SHALL verify Django and Wagtail version compatibility, add apps to `INSTALLED_APPS`, run migrations, and display an installation summary.
4. WHEN Phase 4 is complete, THE Documentation SHALL cover model schemas, API reference, installation guide, configuration guide, feature guides for Blog and LMS, troubleshooting guide, and dependency list.
5. WHEN Phase 5 is complete, THE Test_Suite SHALL include unit tests for all Blog and LMS models, integration tests for end-to-end workflows, and property-based tests for round-trip serialization, idempotence, constraint invariants, and filtering correctness.
6. THE Blog_App SHALL enforce that only published posts are returned by the public list API endpoint.
7. THE LMS_App SHALL enforce that a student cannot enroll in a draft course.
8. THE LMS_App SHALL enforce that each student-course pair has at most one active Enrollment record.
9. WHEN a student completes all lessons in a course, THE LMS_App SHALL generate exactly one Certificate for that enrollment.
10. FOR ALL valid BlogPost objects, THE Serializer SHALL satisfy the round-trip property: `deserialize(serialize(post)) == post`.
11. FOR ALL valid Course objects, THE Serializer SHALL satisfy the round-trip property: `deserialize(serialize(course)) == course`.

### Requirement 5: Complete comprehensive-project-documentation

**User Story:** As a developer, I want all five phases of the `docs/comprehensive-project-documentation` spec completed, so that the workspace has an automated documentation generation system with data integrity validators.

#### Acceptance Criteria

1. WHEN Phase 1 is complete, THE Project_Scanner SHALL detect all projects in the workspace, identify their type (Node.js, Python, etc.), and extract entry points.
2. WHEN Phase 1 is complete, THE Metadata_Parser SHALL extract npm scripts, dependencies, build tool configuration, styling configuration, and implemented API endpoints from each project.
3. WHEN Phase 2 is complete, THE Pretty_Printer SHALL produce valid JSON output with ISO 8601 date formatting and graceful null/empty value handling.
4. WHEN Phase 2 is complete, THE Round_Trip_Serializer SHALL verify that serializing then deserializing any data model produces an equivalent object.
5. WHEN Phase 2 is complete, THE Idempotence_Checker SHALL verify that running the documentation generator multiple times produces identical output and does not create duplicate entries.
6. WHEN Phase 3 is complete, THE Documentation_Renderer SHALL generate documentation files for npm scripts, dependencies, build tools, development server, styling, API endpoints, configuration, deployment, quick start guides, troubleshooting guides, and navigation structure.
7. WHEN Phase 4 is complete, THE Test_Suite SHALL include property-based tests for pretty printer output validity, round-trip serialization, idempotence of documentation updates, and metamorphic consistency between documentation sections and source files.
8. WHEN Phase 5 is complete, THE Documentation_System SHALL be configured to run in CI/CD and serve documentation via Docsify.
9. FOR ALL data models in the system, THE Pretty_Printer SHALL produce output that is valid JSON parseable by a standard JSON parser.
10. IF the documentation generator is run twice on the same workspace without changes, THEN THE Documentation_System SHALL produce byte-identical output on both runs.

### Requirement 6: Complete ctc-docs-and-core-containers

**User Story:** As a developer, I want all tasks in the `docs/ctc-docs-and-core-containers` spec completed, so that the `docs` and `ctc-core` Docker services are running and accessible via Traefik.

#### Acceptance Criteria

1. WHEN task 1 is complete, THE Postgres_Init_Scripts SHALL create the `db_structa` database and grant all privileges to the `postgres` user on container initialization.
2. WHEN task 2 is complete, THE Nginx_Config SHALL serve the docsify `index.html` at the root path, serve markdown files with `Content-Type: text/markdown; charset=utf-8`, and enable gzip compression.
3. WHEN task 3 is complete, THE Docs_Directory SHALL contain a valid `index.html` that causes nginx to return HTTP 200 on first deploy.
4. WHEN task 4 is complete, THE Docker_Compose SHALL define a `docs` service using `nginx:alpine` with the docsify content bind-mounted read-only and connected to `traefik-net`.
5. WHEN task 5 is complete, THE Docker_Compose SHALL define a `ctc-core` service built from the Django Dockerfile, connected to `traefik-net`, using `db_structa` as its database, and exposing a `/health/` endpoint on port 5080.
6. WHEN task 7 is complete, THE Traefik_Config SHALL route HTTPS traffic for the `ctc-core` domain to the `ctc-core` service on port 5080 and route `/static/` and `/media/` paths to the nginx service.
7. WHEN task 8 is complete, THE Test_Suite SHALL include property-based tests verifying: container name matches Traefik service URL hostname, Redis DB index and DB name are unique across all services, each service has all required configuration fields, and Traefik routing config covers all defined services.
8. THE Docker_Compose SHALL assign a unique Redis database index to the `ctc-core` service that does not conflict with any other service's Redis database index.
9. IF the `ctc-core` service health check fails after startup, THEN THE Docker_Compose SHALL restart the container up to three times before marking it unhealthy.

### Requirement 7: Complete structa-color-update

**User Story:** As a developer, I want all eight tasks in the `modernization/structa-color-update` spec completed, so that the structa.cloud UI uses the updated color palette with verified accessibility compliance.

#### Acceptance Criteria

1. WHEN task 1 is complete, THE Color_Audit SHALL produce a mapping of all current SCSS color variables to their usage locations across all SCSS files.
2. WHEN task 2 is complete, THE SCSS_Files SHALL define updated color variables for both light and dark themes in `_master.scss` using CSS custom properties.
3. WHEN task 3 is complete, THE Component_Styles SHALL apply the new color palette to buttons, forms, cards, typography, borders, and shadows.
4. WHEN task 4 is complete, THE Color_System SHALL meet WCAG AA contrast ratio requirements (minimum 4.5:1 for normal text, 3:1 for large text) for all text/background combinations.
5. WHEN task 5 is complete, THE HTML_Templates SHALL use CSS variables rather than inline color styles for all color values.
6. WHEN task 6 is complete, THE Test_Suite SHALL validate the new color palette in both light and dark themes across all interactive states (hover, focus, active) and viewport sizes.
7. WHEN task 7 is complete, THE Wagtail_Data SHALL be restored and verified to be accessible through the Wagtail admin interface with the new color palette applied.
8. WHEN task 8 is complete, THE Color_Update SHALL be verified across all major browsers, mobile viewports, and print styles with no performance regression.

### Requirement 8: Prioritized Execution Order

**User Story:** As a developer, I want the completion work to be executed in a logical order that minimizes risk and maximizes early value, so that the most impactful and lowest-risk items are addressed first.

#### Acceptance Criteria

1. THE Completion_Plan SHALL address partially-complete specs (Requirement 1) before fully-incomplete specs, since they require the least new work.
2. THE Completion_Plan SHALL address `fixes/alliance-website-docker-fix` parent task closure (Requirement 1, criterion 7) as the first action since it is a single status update with no new code required.
3. THE Completion_Plan SHALL address `auth/ctc-structa-admin-auth-integration` parent task closures (Requirement 1, criteria 1–6) as the second action since they are status updates only.
4. THE Completion_Plan SHALL address `auth/auth-allauth-enhancement` optional property tests (Requirement 2) before the fully-incomplete specs, since the implementation they test already exists.
5. THE Completion_Plan SHALL address `docs/ctc-docs-and-core-containers` (Requirement 6) before `integration/blog-lms-wagtail-integration` (Requirement 4), since the container infrastructure is a prerequisite for running the integrated apps.
6. THE Completion_Plan SHALL address `modernization/structa-color-update` (Requirement 7) before `docs/comprehensive-project-documentation` (Requirement 5), since the color update is a bounded, self-contained change.
7. WHEN a spec's tasks depend on infrastructure from another spec, THE Completion_Plan SHALL sequence the infrastructure spec first.

### Requirement 9: Verification and Traceability

**User Story:** As a developer, I want each completed task to be verifiable and traceable back to its source spec, so that I can confirm the work is genuinely done and not just marked complete.

#### Acceptance Criteria

1. WHEN a task is marked `[x]` in a `tasks.md` file, THE corresponding code, file, or configuration change SHALL exist in the repository.
2. THE Test_Suite SHALL pass without errors after each spec's tasks are completed before moving to the next spec.
3. WHEN a property test is written, THE property test SHALL carry a comment tag in the format `# Feature: <spec-name>, Property N: <property_text>` for traceability.
4. WHEN a parent task is closed, THE parent task marker SHALL be updated to `[x]` only after all its sub-tasks are confirmed `[x]`.
5. IF a task cannot be completed due to a missing dependency or blocker, THEN THE Completion_Plan SHALL document the blocker and skip to the next unblocked task rather than leaving the spec in an ambiguous state.
