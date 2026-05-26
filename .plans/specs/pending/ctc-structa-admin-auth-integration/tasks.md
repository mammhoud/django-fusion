# Implementation Plan: ctc-structa-admin-auth-integration

**Category Context: Authentication & Authorization**
- **Category**: Auth
- **Scope**: Authentication systems, user management, permissions, security
- **Related Specs**: auth-allauth-enhancement, ctc-research-server-and-auth-fix, ctc-structa-admin-auth-integration
- **Common Patterns**: Allauth integration, Django authentication, OAuth, JWT tokens, permission systems
- **Avoid Duplicates**: Check existing auth specs before creating new authentication features


## Overview

Eight workstreams implemented incrementally: port fix → management commands → structa.cloud parity → docs → Unfold admin → allauth wiring → property tests. Each task builds on the previous and ends with all code wired together.

## Tasks

- [x] 1. Fix port conflict in ctc-research configs
  - In `ctc-research/configs/settings/conf.py`, change `PORT: int = Field(default=5080, ...)` to `default=5070`
  - In `conf.py` `validate_environment()`, update the warning string referencing `5080` to `5070`
  - In `ctc-research/configs/settings/ENV/security.yml` `default` block only: remove `http://localhost:5080` and `http://127.0.0.1:5080` from `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` (the `5070` entries already present stay; `demo`/`production` blocks are untouched)
  - _Requirements: 1.3, 1.4, 1.5, 1.7_

- [x] 2. Create ctc-research management commands
  - [x] 2.1 Create `populate_content` command
    - Create `ctc-research/apps/handlers/management/commands/populate_content.py`
    - Port logic from base-dir `populate_content.py`; add `--content-file` (required) and `--locale` (optional) args
    - Support page models: `HomePage`, `AboutPage`, `ContactPage`, `TeamPage`, `CoursesPage`, `EventPage`, `ServicesPage`
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 2.2 Create `update_site_settings` command
    - Create `ctc-research/apps/handlers/management/commands/update_site_settings.py`
    - Port logic from base-dir `update_footer_settings.py`; add `--logo-path` (required) and `--social-json` (optional) args
    - _Requirements: 2.4, 2.5_

  - [x] 2.3 Create `verify_content` command
    - Create `ctc-research/apps/handlers/management/commands/verify_content.py`
    - Port logic from base-dir `verify_content.py`; add `--output` arg (default: `docs/added_content.md`)
    - _Requirements: 2.6, 2.7_

  - [x] 2.4 Create `verify_deployment` command in ctc-research
    - Create `ctc-research/apps/handlers/management/commands/verify_deployment.py`
    - Port checks from `verify-demo-config.sh`: Docker Compose config, container running status, network (`traefik-net`), port exposure, env vars (`PORT`, `DEBUG`, `DB_NAME`), Traefik routing file, dependency services, container health
    - Add `--container` arg (default: auto-detect from `RUNNING_ENV`)
    - Exit code `0` on all-pass, `1` on any failure; colour-coded pass/fail/warn output
    - _Requirements: 2.8, 2.9, 2.10, 2.11_

  - [x] 2.5 Create `run_campaign_worker` command
    - Create `ctc-research/apps/handlers/management/commands/run_campaign_worker.py`
    - Port logic from base-dir `worker.py`; add `--task-queue` arg (default: `campaigns-task-queue`)
    - Read `TEMPORAL_SERVER_URL` from settings (default: `localhost:7233`)
    - _Requirements: 2.12, 2.13_

  - [x] 2.6 Create `send_test_email` command in ctc-research
    - Create `ctc-research/apps/handlers/management/commands/send_test_email.py`
    - Port interface from `structa.cloud/core/apps/handlers/management/commands/send_test_email.py`
    - Delegate to `apps.handlers.registration.emails` multi-sender service
    - Add `--email` (required) arg
    - _Requirements: 2.16, 13.3, 13.4_

  - [x] 2.7 Delete original base-directory scripts
    - Delete `ctc-research/populate_content.py`, `ctc-research/update_footer_settings.py`, `ctc-research/verify_content.py`, `ctc-research/verify-demo-config.sh`, `ctc-research/worker.py`
    - _Requirements: 2.14, 2.15_

- [x] 3. Checkpoint — ctc-research commands
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Port shared commands to structa.cloud/core
  - [x] 4.1 Port `validate_config` to structa.cloud/core
    - Create `structa.cloud/core/apps/handlers/management/commands/validate_config.py`
    - Copy from ctc-research version; update `project_root = Path(__file__).resolve().parents[4]` to resolve to `structa.cloud/core`
    - Same `--export-effective` flag, duplicate detection, SECRET_KEY validation
    - _Requirements: 13.1, 13.2_

  - [x] 4.2 Create `verify_deployment` command in structa.cloud/core
    - Create `structa.cloud/core/apps/handlers/management/commands/verify_deployment.py`
    - Identical interface to ctc-research version (`--container` arg, same exit codes, same check list)
    - _Requirements: 2.8, 13.5, 13.6_

- [x] 5. Add health check endpoint and startup diagnostics to structa.cloud/core
  - [x] 5.1 Add `/health/` endpoint
    - Create `structa.cloud/core/apps/handlers/site/health.py` with `health_check(request)` returning `JsonResponse({"status": "ok"}, status=200)`
    - Register `path("health/", health_check, name="health-check")` in `structa.cloud/core/apps/urls.py`
    - _Requirements: 3.2, 3.10_

  - [x] 5.2 Add startup validation in AppConfig.ready()
    - Create `structa.cloud/core/apps/handlers/startup.py` with `run_startup_checks()` validating: SECRET_KEY length ≥ 50, not default placeholder, no duplicate settings, URL routing resolves, middleware list compatibility
    - Call `run_startup_checks()` from `structa.cloud/core/apps/handlers/apps.py` `HandlersConfig.ready()`
    - _Requirements: 3.1, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

- [x] 6. Create feature comparison doc
  - Create `/docs/feature-comparison.md` with a table comparing ctc-research vs structa.cloud/core features
  - Include columns: Feature, ctc-research, structa.cloud/core, Parity Status
  - Cover: registration system, allauth, Unfold admin, LMS, newsletter, blog, validate_config, verify_deployment, send_test_email, health check, startup diagnostics
  - Mark allauth and Unfold as newly added by this spec
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10_

- [x] 7. Install and configure Django Unfold for ctc-research
  - [x] 7.1 Add django-unfold dependency
    - Add `django-unfold` to `ctc-research/pyproject.toml` dependencies
    - _Requirements: 7.1_

  - [x] 7.2 Configure INSTALLED_APPS and UNFOLD settings
    - Add `"unfold"`, `"unfold.contrib.filters"`, `"unfold.contrib.forms"` to `INSTALLED_APPS` before `"django.contrib.admin"` in ctc-research settings
    - Add `UNFOLD` dict with `SITE_TITLE`, `SITE_HEADER`, `SITE_URL`, and `SIDEBAR` navigation groups: "Content", "Users & Auth", "LMS", "Registration", "System" — each with the items specified in the design
    - _Requirements: 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_

  - [x] 7.3 Create SocialAccount inline on User admin
    - Create `ctc-research/apps/handlers/registration/admin.py`
    - Implement `SocialAccountInline(TabularInline)` with `model = SocialAccount`, `readonly_fields`, guarded by `try/except ImportError`
    - Implement `UserAdmin(ModelAdmin)` with `inlines = [SocialAccountInline]`; unregister default User and register with `UserAdmin`
    - _Requirements: 7.11, 8.11_

- [x] 8. Checkpoint — Unfold admin
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Create structa.cloud/core allauth registration module
  - [x] 9.1 Create registration package skeleton
    - Create `structa.cloud/core/apps/handlers/registration/__init__.py` and `apps.py`
    - Create `structa.cloud/core/apps/handlers/registration/migrations/` with `__init__.py`
    - _Requirements: 5.1_

  - [x] 9.2 Create AuthEmailTemplate model
    - Create `structa.cloud/core/apps/handlers/registration/models.py`
    - Implement `AuthEmailTemplate` Wagtail snippet with fields: `template_type` (CharField, choices: `registration_confirmation`, `signin_success`), `subject`, `body_html` (RichTextField), `body_text`, `is_active` (BooleanField)
    - Override `save()` to deactivate all other active records of the same `template_type` (single-active invariant)
    - _Requirements: 5.2, 5.5, 5.11_

  - [x] 9.3 Create RegistrationAdapter
    - Create `structa.cloud/core/apps/handlers/registration/adapter.py`
    - Implement `RegistrationAdapter(DefaultAccountAdapter)` registered as `ACCOUNT_ADAPTER`
    - Delegate `send_confirmation_mail` to `send_registration_email()`; emit `user_logged_in` signal on login
    - _Requirements: 5.1_

  - [x] 9.4 Create email service functions
    - Create `structa.cloud/core/apps/handlers/registration/emails.py`
    - Implement `_resolve_template(template_type)`, `send_registration_email(user, request)`, `send_signin_success_email(user, request)`
    - `_resolve_template` falls back to file-based template on DB error; `site_name="Structa"`, `DEFAULT_FROM_EMAIL` fallback `support@structa.cloud`
    - _Requirements: 5.3, 5.4, 5.6_

  - [x] 9.5 Create token generator
    - Create `structa.cloud/core/apps/handlers/registration/tokens.py`
    - Implement `RegistrationTokenGenerator` with `make_allauth_compatible_token(user, allauth_key)` and `validate_token(token)`
    - Raise `ValueError` when `allauth_key` is empty; return `{"expired": True}` on expired token
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8_

  - [x] 9.6 Create allauth views
    - Create `structa.cloud/core/apps/handlers/registration/allauth_views.py`
    - Implement `AllauthLoginView` and `AllauthSignupView` as `PageHandler` subclasses
    - Return fragment on `HX-Request`, full page otherwise; set `HX-Trigger: showNotification` JSON header on every HTMX response
    - _Requirements: 5.8, 5.9, 5.10_

  - [x] 9.7 Create signals, URLs, and wagtail_hooks
    - Create `structa.cloud/core/apps/handlers/registration/signals.py` — `user_logged_in` → `send_signin_success_email` on first login
    - Create `structa.cloud/core/apps/handlers/registration/urls.py` — URL patterns for login/signup
    - Create `structa.cloud/core/apps/handlers/registration/wagtail_hooks.py` — register `AuthEmailTemplate` under "Auth & Email"
    - _Requirements: 5.4, 5.7_

  - [x] 9.8 Wire allauth settings for structa.cloud/core
    - Add `"allauth"`, `"allauth.account"`, `"allauth.socialaccount"` to `INSTALLED_APPS` in structa.cloud/core settings
    - Set `ACCOUNT_ADAPTER = "apps.handlers.registration.adapter.RegistrationAdapter"`
    - Include allauth URL patterns and registration URLs in `structa.cloud/core/apps/urls.py`
    - _Requirements: 5.1_

- [x] 10. Wire allauth for ctc-research
  - Add `"allauth"`, `"allauth.account"`, `"allauth.socialaccount"` to `INSTALLED_APPS` in ctc-research settings (if not already present)
  - Set `ACCOUNT_ADAPTER = "apps.handlers.registration.adapter.RegistrationAdapter"` in ctc-research settings
  - Include allauth URL patterns in `ctc-research/core/urls.py`
  - Verify `AllauthLoginView` and `AllauthSignupView` are wired to existing URL names (`handlers:register-account`, `handlers:create-password`)
  - _Requirements: 8.1, 8.4, 8.5, 8.14, 8.16, 8.17_

- [x] 11. Checkpoint — allauth wiring
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Write property-based tests
  - [x] 12.1 Write property test for token round-trip (P1)
    - Create `ctc-research/tests/test_property_token_roundtrip.py`
    - Use `@given(st.integers(min_value=1), st.text(min_size=1))` to generate user PKs and allauth_key strings
    - Assert `validate_token(make_allauth_compatible_token(user, key))` returns `uid == str(user.pk)` and `allauth_key == key`
    - `@settings(max_examples=100)`; tag: `# Feature: ctc-structa-admin-auth-integration, Property 1`
    - _Requirements: 8.9, 9.7_

  - [x] 12.2 Write property test for single-active AuthEmailTemplate invariant (P2)
    - Create `ctc-research/tests/test_property_single_active_snippet.py`
    - Generate sequences of `AuthEmailTemplate` saves with `is_active=True` for a given `template_type`
    - Assert count of active records for that type equals exactly 1 after each save
    - `@settings(max_examples=100)`; tag: `# Feature: ctc-structa-admin-auth-integration, Property 2`
    - _Requirements: 5.5, 5.11_

  - [x] 12.3 Write property test for HX-Trigger on HTMX responses (P3)
    - Create `ctc-research/tests/test_property_hx_trigger.py`
    - Generate valid and invalid form data with `HX-Request` header for `AllauthLoginView` and `AllauthSignupView`
    - Assert response contains `HX-Trigger` header with valid JSON containing `showNotification.message` and `showNotification.type`
    - `@settings(max_examples=100)`; tag: `# Feature: ctc-structa-admin-auth-integration, Property 3`
    - _Requirements: 10.5, 10.8_

  - [x] 12.4 Write property test for security headers (P4)
    - Create `structa.cloud/core/tests/test_property_security_headers.py`
    - Generate URL paths from the URL conf; assert every response contains `X-Frame-Options: DENY` and `X-Content-Type-Options: nosniff`
    - `@settings(max_examples=100)`; tag: `# Feature: ctc-structa-admin-auth-integration, Property 4`
    - _Requirements: 4.5, 4.6_

  - [x] 12.5 Write property test for health check (P5)
    - Create `structa.cloud/core/tests/test_property_health_check.py`
    - Generate valid config states (non-empty SECRET_KEY, valid DB config); assert GET `/health/` returns HTTP 200
    - `@settings(max_examples=100)`; tag: `# Feature: ctc-structa-admin-auth-integration, Property 5`
    - _Requirements: 3.2, 3.10_

  - [x] 12.6 Write property test for command exit codes (P6)
    - Create `ctc-research/tests/test_property_command_exit_codes.py`
    - Mock `handle()` to raise exceptions or call `sys.exit(1)`; assert process exit code is non-zero and error written to stderr
    - `@settings(max_examples=100)`; tag: `# Feature: ctc-structa-admin-auth-integration, Property 6`
    - _Requirements: 2.16_

  - [x] 12.7 Write property test for shared command interface parity (P7)
    - Create `ctc-research/tests/test_property_command_parity.py`
    - Compare argument parsers of `validate_config`, `verify_deployment`, `send_test_email` between ctc-research and structa.cloud/core
    - Assert the set of argument names is identical for each shared command
    - `@settings(max_examples=100)`; tag: `# Feature: ctc-structa-admin-auth-integration, Property 7`
    - _Requirements: 13.6_

- [x] 13. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests use Hypothesis (`@settings(max_examples=100)`) and must carry the feature/property tag comment
- Do NOT modify `docker-compose.yml` or `ctc-research/docker-compose.yml`
- All changes are additive and rollback-safe
