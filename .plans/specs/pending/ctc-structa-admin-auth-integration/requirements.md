# Requirements Document

**Category Context: Authentication & Authorization**
- **Category**: Auth
- **Scope**: Authentication systems, user management, permissions, security
- **Related Specs**: auth-allauth-enhancement, ctc-research-server-and-auth-fix, ctc-structa-admin-auth-integration
- **Common Patterns**: Allauth integration, Django authentication, OAuth, JWT tokens, permission systems
- **Avoid Duplicates**: Check existing auth specs before creating new authentication features


## Introduction

This document specifies requirements for the `ctc-structa-admin-auth-integration` feature, which covers five coordinated workstreams across the monorepo:

1. **Port conflict audit and cleanup** — audit `ctc-research/configs/` and `ctc-research/compose/` for hardcoded port references that conflict with the canonical `PORT=5070` (main app) and `PORT=5075` (rqworker), and remove stale utility scripts from the `ctc-research/` base directory.
2. **Utility script migration to management commands** — extract the use cases from the five stale base-directory scripts into proper Django management commands, then delete the originals. Commands that are generic enough apply to both projects.
3. **Structa.cloud parity** — apply the server-diagnostic, health-check, configuration-validation, and security-hardening patterns from `ctc-research-server-and-auth-fix`, and the allauth `PageHandler`/`RegistrationAdapter`/`AuthEmailTemplate` patterns from `auth-allauth-enhancement`, to `structa.cloud/core`.
4. **Feature comparison documentation** — produce a `/docs/` markdown file comparing features present in `ctc-research` but absent from `structa.cloud/core`, and vice versa.
5. **Django Unfold admin panel** — integrate `django-unfold` as the admin panel for `ctc-research`, with navigation groups, branding, and Wagtail admin co-existence.
6. **Allauth integration for ctc-research** — implement the plan from `auth-allauth-enhancement` inside `ctc-research`, connecting allauth to the existing `apps/handlers/registration/` system, the `Person` profile model, and the Unfold admin.

All changes are confined to `ctc-research/` app and config files and `structa.cloud/core/` app and config files. The root `docker-compose.yml` and `ctc-research/docker-compose.yml` are read-only.

---

## Glossary

- **CTC_App**: The Django application running at `ctc-research.com`, served by the `ctc-django-main` container on `PORT=5070`.
- **RQWorker**: The Django-RQ background worker container `ctc-rqworker-main`, assigned `PORT=5075` in the compose environment.
- **Structa_App**: The Django application running at `core.structa.cloud` / `structa.cloud`, served by the `core` container on `PORT=5080`.
- **Port_Audit**: The process of scanning `ctc-research/configs/` and `ctc-research/compose/` for hardcoded port values that do not match the canonical ports.
- **Canonical_Port**: The authoritative port value for a service as declared in `docker-compose.yml` (`5070` for CTC_App, `5075` for RQWorker, `5080` for Structa_App).
- **Utility_Script**: A standalone Python or shell script in the `ctc-research/` base directory that is no longer part of the application runtime (`populate_content.py`, `update_footer_settings.py`, `verify_content.py`, `verify-demo-config.sh`, `worker.py`).
- **Management_Command**: A Django `BaseCommand` subclass invoked via `python com <command_name>`, the proper home for operational scripts.
- **Shared_Command**: A management command whose logic is generic enough to be installed in both `ctc-research` and `structa.cloud/core` (e.g. `verify_deployment`, `validate_config`).
- **CTC_Only_Command**: A management command whose logic is specific to `ctc-research` data models (e.g. `populate_content`, `update_footer_settings`, `verify_content`).
- **Configuration_System**: The Dynaconf + Pydantic `MainSettings` class in `configs/settings/conf.py` and the YAML files in `configs/settings/ENV/`.
- **Health_Check_Endpoint**: An HTTP endpoint at `/health/` that returns `HTTP 200` when the application is operational.
- **Server_Diagnostic**: Startup-time validation that logs configuration conflicts, URL routing errors, and middleware incompatibilities before accepting requests.
- **Unfold_Admin**: The `django-unfold` package providing a modern admin UI that replaces the default Django admin while co-existing with the Wagtail admin.
- **Unfold_Navigation**: The sidebar navigation groups and items configured in `UNFOLD["SIDEBAR"]` within Django settings.
- **Allauth**: The `django-allauth` library providing pluggable authentication, registration, and account management.
- **PageHandler**: Base view class from `django_grep.comp.site` providing HTMX-aware fragment vs full-page rendering.
- **RegistrationAdapter**: A custom `DefaultAccountAdapter` subclass that routes allauth lifecycle events into the existing email service and rate limiter.
- **AuthEmailTemplate**: A Wagtail snippet model storing editable subject and body for each transactional auth email.
- **Registration_System**: The existing email-based two-step user registration workflow in `apps/handlers/registration/`.
- **Person_Profile**: The existing `Person` model in `apps/handlers/models/` representing a user's extended profile.
- **Email_Service**: The multi-sender SMTP email delivery service with failover in `apps/handlers/registration/emails.py`.
- **Token_Generator**: The existing `RegistrationTokenGenerator` using HMAC-SHA256 and Django signing.
- **Rate_Limiter**: IP-based request throttling using Django cache.
- **Notification_System**: Client-side toast notifications triggered via the `HX-Trigger: showNotification` header.
- **Feature_Comparison_Doc**: A markdown file at `/docs/feature-comparison.md` listing features present in one project but absent from the other.
- **Parity_Pattern**: A design or implementation pattern already present in `ctc-research` that is being ported to `structa.cloud/core`, or vice versa.

---

## Requirements

### Requirement 1: Port Conflict Audit and Resolution

**User Story:** As a developer, I want all port references inside `ctc-research/configs/` and `ctc-research/compose/` to match the canonical ports, so that local development and container networking are consistent.

#### Acceptance Criteria

1. THE Port_Audit SHALL scan every file under `ctc-research/configs/` and `ctc-research/compose/` for hardcoded port values.
2. WHEN a file contains a reference to port `5080` in a context that applies to the CTC_App (not to Structa_App cross-origin entries), THE Configuration_System SHALL replace that reference with `5070`.
3. THE Configuration_System SHALL replace the default `PORT` field value in `ctc-research/configs/settings/conf.py` from `5080` to `5070`.
4. THE Configuration_System SHALL update the default port warning message in `conf.py` `validate_environment()` to reference `5070` instead of `5080`.
5. WHEN `ctc-research/configs/settings/ENV/security.yml` lists `http://localhost:5080` or `http://127.0.0.1:5080` in `CORS_ALLOWED_ORIGINS` or `CSRF_TRUSTED_ORIGINS` for the `default` environment block, THE Configuration_System SHALL replace those entries with the equivalent `5070` entries.
6. THE Configuration_System SHALL NOT modify `ctc-research/docker-compose.yml` or the root `docker-compose.yml`.
7. THE Configuration_System SHALL NOT remove cross-origin entries for `structa.cloud` ports (`5080`) from `demo` or `production` environment blocks where they are intentionally present for inter-service CORS.
8. WHEN the Port_Audit finds no remaining `5080` references in the `default` block of `ctc-research/configs/settings/ENV/security.yml`, THE Port_Audit SHALL be considered complete.

### Requirement 2: Utility Script Migration to Management Commands

**User Story:** As a developer, I want the use cases from the stale base-directory scripts preserved as proper Django management commands and the originals deleted, so that the project root is clean and the functionality is accessible via `python com <command>`.

#### Script → Command mapping

| Original script | Use case extracted | Command name | Applies to |
|---|---|---|---|
| `populate_content.py` | Populate Wagtail pages with multilingual content from a markdown file | `populate_content` | ctc-research only |
| `update_footer_settings.py` | Upload a logo image and update `GlobalSettings` social links | `update_site_settings` | ctc-research only |
| `verify_content.py` | Generate a markdown report of all published pages and their field values | `verify_content` | ctc-research only |
| `verify-demo-config.sh` | Check Docker container status, network, ports, env vars, Traefik config, and service health | `verify_deployment` | **both projects** |
| `worker.py` | Start a Temporal workflow worker for the campaigns task queue | `run_campaign_worker` | ctc-research only |

#### Acceptance Criteria

1. THE CTC_App SHALL provide a `populate_content` management command that accepts a `--content-file` argument pointing to the markdown content file and populates all Wagtail page models with multilingual translations.
2. THE `populate_content` command SHALL support the same page models as the original script: `HomePage`, `AboutPage`, `ContactPage`, `TeamPage`, `CoursesPage`, `EventPage`, `ServicesPage`.
3. THE `populate_content` command SHALL accept a `--locale` option to limit population to a single language code (default: all locales).
4. THE CTC_App SHALL provide an `update_site_settings` management command that accepts `--logo-path` and updates `GlobalSettings` with the logo image and social link data.
5. THE `update_site_settings` command SHALL accept a `--social-json` option to supply social link data as a JSON string or file path, defaulting to the CTC Research social profiles.
6. THE CTC_App SHALL provide a `verify_content` management command that generates a markdown report of all published Wagtail pages and their field values, writing output to `docs/added_content.md` by default.
7. THE `verify_content` command SHALL accept an `--output` argument to override the report destination path.
8. BOTH the CTC_App AND the Structa_App SHALL provide a `verify_deployment` management command that checks: Docker container status, network connectivity, port exposure, environment variables, Traefik routing config, and service health endpoints.
9. THE `verify_deployment` command SHALL accept a `--container` argument to specify the container name to inspect (default: auto-detected from `RUNNING_ENV`).
10. THE `verify_deployment` command SHALL print a colour-coded summary with pass/fail/warning indicators for each check, matching the behaviour of the original shell script.
11. THE `verify_deployment` command SHALL exit with code `0` when all checks pass and code `1` when any check fails, so it can be used in CI pipelines.
12. THE CTC_App SHALL provide a `run_campaign_worker` management command that starts the Temporal workflow worker for the `campaigns-task-queue`, reading the Temporal server address from `TEMPORAL_SERVER_URL` (default: `localhost:7233`).
13. THE `run_campaign_worker` command SHALL accept a `--task-queue` argument to override the default queue name.
14. AFTER all commands are created, THE CTC_App repository SHALL NOT contain `populate_content.py`, `update_footer_settings.py`, `verify_content.py`, `verify-demo-config.sh`, or `worker.py` in the base directory.
15. THE CTC_App SHALL continue to start and pass its health check after the original script files are removed.
16. WHEN any management command fails, it SHALL exit with a non-zero code and print a human-readable error message to stderr.

### Requirement 3: Structa.cloud Server Diagnostic and Health Check Parity

**User Story:** As a system administrator, I want `structa.cloud/core` to have the same server-diagnostic and health-check capabilities as `ctc-research`, so that I can diagnose issues on both platforms using the same patterns.

#### Acceptance Criteria

1. WHEN the Structa_App is started, THE Structa_App SHALL log all startup errors with full stack traces.
2. THE Structa_App SHALL expose a Health_Check_Endpoint at `/health/` that returns `HTTP 200` when the application is operational.
3. THE Structa_App SHALL validate all URL routing configurations before accepting requests.
4. THE Structa_App SHALL detect duplicate settings definitions across its configuration files at startup.
5. THE Structa_App SHALL verify middleware configuration compatibility at startup.
6. IF a configuration conflict is detected at startup, THEN THE Structa_App SHALL log the conflict details.
7. THE Structa_App SHALL validate that `SECRET_KEY` is at least 50 characters long at startup.
8. WHEN `SECRET_KEY` is the default placeholder value, THE Structa_App SHALL log a critical warning.
9. THE Structa_App SHALL provide a configuration validation command equivalent to the one in `ctc-research`.
10. FOR ALL valid startup sequences, the Health_Check_Endpoint SHALL return `HTTP 200` within 5 seconds of the application becoming ready.

### Requirement 4: Structa.cloud Security Hardening Parity

**User Story:** As a security administrator, I want `structa.cloud/core` to apply the same security hardening patterns as `ctc-research`, so that both platforms have consistent security posture.

#### Acceptance Criteria

1. WHEN in production, THE Structa_App SHALL enforce HTTPS for all requests.
2. WHEN in production, THE Structa_App SHALL set the `Secure` flag on all cookies.
3. WHEN in production, THE Structa_App SHALL set HSTS headers with `max-age` of `31536000` seconds.
4. THE Structa_App SHALL validate that CSRF protection works with HTMX requests.
5. THE Structa_App SHALL set `X-Frame-Options: DENY` in all responses.
6. THE Structa_App SHALL set `X-Content-Type-Options: nosniff` in all responses.
7. THE Rate_Limiter in Structa_App SHALL limit login attempts to 5 per IP per hour.
8. THE Structa_App SHALL sanitize all user-provided data before storage.
9. WHEN in production, THE Structa_App SHALL use `SECURE_PROXY_SSL_HEADER` to trust the `X-Forwarded-Proto` header from Traefik.

### Requirement 5: Structa.cloud Allauth Integration Parity

**User Story:** As a developer, I want `structa.cloud/core` to have the same allauth `PageHandler`/`RegistrationAdapter`/`AuthEmailTemplate` integration as `ctc-research`, so that both platforms share a consistent authentication architecture.

#### Acceptance Criteria

1. THE Structa_App SHALL include a `RegistrationAdapter` subclassing `DefaultAccountAdapter` registered as `ACCOUNT_ADAPTER` in its settings.
2. THE Structa_App SHALL include an `AuthEmailTemplate` Wagtail snippet model with fields `template_type`, `subject`, `body_html`, `body_text`, and `is_active`.
3. WHEN a user submits a valid registration form on Structa_App, THE Email_Service SHALL send a confirmation email within 30 seconds.
4. WHEN a user signs in for the first time on Structa_App, THE Email_Service SHALL send a Sign_In_Success_Email asynchronously.
5. THE Structa_App SHALL enforce that at most one active `AuthEmailTemplate` exists per `template_type` at any time.
6. WHEN no active `AuthEmailTemplate` exists for a given type, THE Email_Service SHALL fall back to the file-based template without error.
7. THE Structa_App SHALL register `AuthEmailTemplate` in the Wagtail admin under a group labelled "Auth & Email".
8. WHEN a request to Structa_App carries an `HX-Request` header, THE Structa_App SHALL return only the form fragment.
9. WHEN a request to Structa_App does not carry an `HX-Request` header, THE Structa_App SHALL return the full page using the auth skeleton.
10. THE Structa_App SHALL set the `HX-Trigger` response header with a valid JSON `showNotification` payload on every HTMX form submission response, whether the form is valid or invalid.
11. FOR ALL valid `AuthEmailTemplate` records, saving a new active record for the same `template_type` SHALL deactivate all previously active records of that type (single-active invariant).

### Requirement 6: Feature Comparison Documentation

**User Story:** As a developer, I want a markdown document in `/docs/` that lists features present in `ctc-research` but absent from `structa.cloud/core`, and vice versa, so that I can plan future parity work.

#### Acceptance Criteria

1. THE Feature_Comparison_Doc SHALL be created at `/docs/feature-comparison.md`.
2. THE Feature_Comparison_Doc SHALL contain a section listing features present in `ctc-research` but not in `structa.cloud/core`.
3. THE Feature_Comparison_Doc SHALL contain a section listing features present in `structa.cloud/core` but not in `ctc-research`.
4. THE Feature_Comparison_Doc SHALL document that `ctc-research` has a full `apps/handlers/registration/` subfolder with `RegistrationAdapter`, `Token_Generator`, and invitation-based registration, while `structa.cloud/core` does not yet have a `registration/` subfolder.
5. THE Feature_Comparison_Doc SHALL document that `ctc-research` has an LMS with courses, modules, lessons, quizzes, and certificates, and that `structa.cloud/core` has an LMS with the same structural layout but different content scope.
6. THE Feature_Comparison_Doc SHALL document that `ctc-research` has a newsletter app and that `structa.cloud/core` does not.
7. THE Feature_Comparison_Doc SHALL document that `ctc-research` has a blog app and that `structa.cloud/core` also has a blog app.
8. THE Feature_Comparison_Doc SHALL document that `structa.cloud/core` is an Alliance CMS foundation and that `ctc-research` is an LMS-first platform.
9. THE Feature_Comparison_Doc SHALL include a "Parity Status" column or section for each feature indicating whether it is planned, in-progress, or not applicable for the other platform.
10. WHEN this spec is implemented, THE Feature_Comparison_Doc SHALL reflect the allauth and Unfold admin features as newly added to `ctc-research` and planned for `structa.cloud/core`.

### Requirement 7: Django Unfold Admin Panel for ctc-research

**User Story:** As a site administrator, I want a modern, well-organised admin panel for `ctc-research` using `django-unfold`, so that I can manage content, users, and LMS data efficiently.

#### Acceptance Criteria

1. THE CTC_App SHALL install `django-unfold` and list it in `INSTALLED_APPS` before `django.contrib.admin`.
2. THE CTC_App SHALL configure `UNFOLD` settings with a `SITE_TITLE`, `SITE_HEADER`, and `SITE_URL` matching the CTC Research branding.
3. THE Unfold_Navigation SHALL define at minimum the following groups: "Content", "Users & Auth", "LMS", "Registration", and "System".
4. THE Unfold_Navigation "Users & Auth" group SHALL include links to the `User`, `Group`, and allauth `SocialAccount` admin views.
5. THE Unfold_Navigation "LMS" group SHALL include links to the LMS course, module, lesson, quiz, and certificate admin views.
6. THE Unfold_Navigation "Registration" group SHALL include links to the `Person` profile, `AuthEmailTemplate`, and registration-related admin views.
7. THE Unfold_Navigation "Content" group SHALL include links to the blog and pages admin views.
8. THE Unfold_Navigation "System" group SHALL include links to Django sites, redirects, and log entries.
9. THE CTC_App SHALL co-exist with the Wagtail admin: the Unfold admin SHALL be accessible at `/admin/` and the Wagtail admin SHALL remain accessible at `/cms/` or its configured URL.
10. WHEN a user accesses `/admin/`, THE CTC_App SHALL render the Unfold admin interface.
11. THE Unfold_Admin SHALL display allauth `SocialAccount` records linked to each user in the "Users & Auth" section.
12. THE CTC_App SHALL NOT break any existing Wagtail admin functionality after Unfold is installed.
13. WHEN `django-unfold` is installed, THE CTC_App SHALL start without errors and pass its health check.

### Requirement 8: Allauth Integration for ctc-research

**User Story:** As a developer, I want the `auth-allauth-enhancement` plan fully implemented in `ctc-research`, connecting allauth to the existing `Registration_System`, `Person_Profile`, and Unfold admin, so that the authentication system is production-ready.

#### Acceptance Criteria

1. THE Registration_System SHALL wrap allauth login and signup views inside subclasses of `PageHandler` (`AllauthLoginView`, `AllauthSignupView`).
2. WHEN a request carries an `HX-Request` header, THE Registration_System SHALL return only the form fragment using the existing fragment templates.
3. WHEN a request does not carry an `HX-Request` header, THE Registration_System SHALL return the full page using the `Auth_Skeleton`.
4. THE Registration_System SHALL preserve all existing URL names (`handlers:register-account`, `handlers:create-password`) so no existing links break.
5. THE RegistrationAdapter SHALL be registered in settings as `ACCOUNT_ADAPTER = "apps.handlers.registration.adapter.RegistrationAdapter"`.
6. WHEN allauth confirms a user's email, THE RegistrationAdapter SHALL delegate to `send_registration_email()` from the existing Email_Service.
7. WHEN allauth logs a user in, THE RegistrationAdapter SHALL emit a `user_logged_in` signal that the Sign_In_Success_Email handler listens to.
8. THE Token_Generator SHALL expose a `make_allauth_compatible_token(user, allauth_key)` method that embeds the allauth key in the signed payload.
9. FOR ALL valid tokens produced by `make_allauth_compatible_token`, calling `validate_token` SHALL return a payload containing both `uid` and `allauth_key` fields (round-trip property).
10. WHEN a user activates their account, THE Registration_System SHALL create or update the `Person_Profile` with the user's first name, last name, email, `is_registered=True`, and `registration_date` set to the current timestamp.
11. THE Unfold_Admin SHALL display allauth `SocialAccount` records inline on the user detail page.
12. THE Rate_Limiter SHALL limit registration attempts to 5 per IP per hour using the existing `reg_rate_limit:{ip}` cache key.
13. WHEN a rate limit is exceeded, THE Registration_System SHALL return `HTTP 429` and set the `HX-Trigger` header with an error notification payload.
14. THE Registration_System SHALL use database transactions for all multi-step operations involving user creation and email sending.
15. WHEN a transaction fails, THE Registration_System SHALL roll back all changes and return an error response.
16. THE Registration_System SHALL NOT modify the existing `User` model schema.
17. THE Registration_System SHALL NOT delete or rename existing URL patterns or template files.

### Requirement 9: Allauth Token Round-Trip and Security

**User Story:** As a security engineer, I want the allauth-compatible token mechanism to be cryptographically sound and verifiable, so that account activation links cannot be forged or replayed.

#### Acceptance Criteria

1. THE Token_Generator SHALL use Django's `signing.dumps` / `signing.loads` with the salt `ctc-registration-password-create` for all token operations.
2. THE Token_Generator SHALL include `uid`, `ts` (ISO-8601 timestamp), `hash` (HMAC-SHA256 of user state), and `allauth_key` in the payload of `make_allauth_compatible_token`.
3. THE Token_Generator SHALL invalidate tokens when the user's password or `is_active` state changes.
4. THE Token_Generator SHALL use constant-time comparison when validating token signatures to prevent timing attacks.
5. WHEN `make_allauth_compatible_token` is called with an empty `allauth_key`, THE Token_Generator SHALL raise a `ValueError`.
6. WHEN `validate_token` is called on an expired allauth-compatible token, THE Token_Generator SHALL return `{"expired": True}`.
7. FOR ALL valid `(user, allauth_key)` pairs, the round-trip `validate_token(make_allauth_compatible_token(user, allauth_key))` SHALL return a dict where `uid == str(user.pk)` and `allauth_key` equals the original key.
8. THE Token_Generator SHALL generate tokens that are valid for 24 min and are invalidated once the password is set.

### Requirement 10: Notification System Correctness

**User Story:** As a user, I want to see accurate success or error notifications immediately after submitting any auth form, so that I always know whether my action succeeded.

#### Acceptance Criteria

1. WHEN a registration form submission succeeds, THE Notification_System SHALL display a success notification with the message "Account created! Check your email."
2. WHEN a login form submission succeeds, THE Notification_System SHALL display a success notification with the message "Welcome back!"
3. WHEN a form submission fails validation, THE Notification_System SHALL display an error notification describing the first validation error.
4. WHEN a rate limit is exceeded, THE Notification_System SHALL display an error notification with the message "Too many attempts. Please try again later."
5. THE Registration_System SHALL set the `HX-Trigger` response header with a valid JSON payload of the form `{"showNotification": {"message": "...", "type": "..."}}` on every HTMX form submission response.
6. THE `HX-Trigger` header SHALL be present on both success and error responses.
7. WHEN the form is submitted via a non-HTMX request, THE Registration_System SHALL display the notification inline in the rendered page.
8. FOR ALL HTMX form submissions to `AllauthLoginView` or `AllauthSignupView`, the response SHALL include an `HX-Trigger` header whose value is valid JSON containing `showNotification.message` and `showNotification.type`.

### Requirement 11: Backward Compatibility and Rollback Safety

**User Story:** As a developer, I want all changes to be additive and rollback-safe, so that existing user accounts, URL patterns, and templates continue to work if any part of this feature is reverted.

#### Acceptance Criteria

1. THE Registration_System SHALL NOT modify the existing `User` model schema.
2. THE Registration_System SHALL NOT delete or rename existing URL patterns.
3. THE Registration_System SHALL NOT remove existing template files.
4. WHEN allauth is disabled or removed, THE Registration_System SHALL fall back to the existing custom views without data loss.
5. THE CTC_App SHALL maintain all existing property-based tests passing after the enhancement is applied.
6. THE Structa_App SHALL maintain all existing tests passing after the parity changes are applied.
7. THE CTC_App SHALL start and pass its health check after Unfold is installed.
8. THE CTC_App SHALL start and pass its health check after allauth views are wired up.
9. WHEN a database transaction fails during user creation or email sending, THE Registration_System SHALL roll back all changes automatically.
10. THE Configuration_System SHALL preserve existing settings during the port-conflict fix; only the specific conflicting values SHALL be updated.

### Requirement 12: Logging and Observability

**User Story:** As a system administrator, I want comprehensive logging across both platforms for auth events, email delivery, and configuration validation, so that I can diagnose issues quickly.

#### Acceptance Criteria

1. THE CTC_App SHALL log all registration attempts with timestamp and IP address.
2. THE CTC_App SHALL log all email delivery attempts with sender identity, recipient, and outcome.
3. THE CTC_App SHALL log all token validation attempts with outcome.
4. THE CTC_App SHALL log all rate limit violations with IP address and timestamp.
5. WHEN an unexpected error occurs in the CTC_App, THE CTC_App SHALL log the full stack trace.
6. THE Structa_App SHALL log all startup configuration warnings.
7. THE Structa_App SHALL log all email delivery attempts with outcome.
8. WHEN the Sign_In_Success_Email delivery fails, THE Email_Service SHALL log the error at `ERROR` level and continue without blocking the user session.
9. THE CTC_App SHALL log all Unfold admin access events at `INFO` level.
10. THE CTC_App SHALL log all allauth adapter lifecycle events (`pre_signup`, `pre_login`, `send_confirmation_mail`) at `DEBUG` level.

### Requirement 13: Shared Management Commands Parity

**User Story:** As a developer, I want the generic operational commands available in both Django projects, so that I can use the same workflow on both platforms.

#### Commands that apply to both projects

| Command | Already in ctc-research | Already in structa.cloud/core | Action |
|---|---|---|---|
| `validate_config` | ✅ exists | ❌ missing | Port to structa.cloud/core |
| `verify_deployment` | ❌ (new from Req 2) | ❌ (new from Req 2) | Create in both |
| `send_test_email` | ❌ missing | ✅ exists | Port to ctc-research |

#### Acceptance Criteria

1. THE Structa_App SHALL provide a `validate_config` management command with the same interface as the one in `ctc-research` (`--export-effective` flag, duplicate detection, SECRET_KEY validation).
2. THE `validate_config` command in Structa_App SHALL resolve paths relative to `structa.cloud/core/` as its project root.
3. THE CTC_App SHALL provide a `send_test_email` management command with the same interface as the one in `structa.cloud/core` (`--email` argument, delegates to the existing Email_Service).
4. THE `send_test_email` command in CTC_App SHALL use the multi-sender failover Email_Service from `apps/handlers/registration/emails.py`.
5. BOTH projects SHALL expose the `verify_deployment` command as specified in Requirement 2, criterion 8–11.
6. FOR ALL shared commands, the command interface (argument names, output format, exit codes) SHALL be identical between the two projects so that the same CI script can invoke either.
7. WHEN a shared command is updated in one project, the corresponding command in the other project SHALL be updated in the same change to keep them in sync.
