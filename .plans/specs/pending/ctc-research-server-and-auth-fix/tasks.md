# Implementation Plan: CTC Research Server and Auth Fix

**Category Context: Authentication & Authorization**
- **Category**: Auth
- **Scope**: Authentication systems, user management, permissions, security
- **Related Specs**: auth-allauth-enhancement, ctc-research-server-and-auth-fix, ctc-structa-admin-auth-integration
- **Common Patterns**: Allauth integration, Django authentication, OAuth, JWT tokens, permission systems
- **Avoid Duplicates**: Check existing auth specs before creating new authentication features


## Overview

Fix server stability issues and harden the existing email-based registration system in `ctc-research`. The implementation builds on the existing code in `apps/handlers/registration/` and integrates with the PageHandler architecture. All Python commands use `uv run`.

## Tasks

- [x] 1. Server diagnostics — investigate and fix startup errors
  - Inspect Django startup logs for template errors, URL conflicts, and middleware issues
  - Add `wagtail_i18n_tags` to `INSTALLED_APPS` or the relevant template tag library to fix the `language_selector` tag error in ctc-research templates
  - Verify `apps/handlers/templatetags/` has the correct tag registration; add missing `{% load wagtail_i18n_tags %}` where needed
  - Check `core/urls.py` for duplicate or conflicting URL patterns with `apps/urls.py` and `django_grep.pipelines.urls`
  - Verify `MIDDLEWARE` in `configs/base/middlewares.py` has no ordering conflicts (e.g., `SessionMiddleware` before `AuthenticationMiddleware`)
  - Confirm `whitenoise` static file configuration is correct and `STATICFILES_DIRS` has no missing paths
  - Add a `/health/` endpoint returning `{"status": "healthy"}` to `apps/handlers/urls.py` or `core/urls.py`
  - _Requirements: 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 1.10_

- [x] 2. Configuration conflict resolution
  - [x] 2.1 Audit and deduplicate settings between YAML configs and `.env`
    - Scan `configs/` YAML files and `.env` for duplicate `SECRET_KEY`, `DATABASE_URL`, `EMAIL_*`, and `ALLOWED_HOSTS` definitions
    - Add a `validate_config()` management command in `apps/handlers/management/commands/validate_config.py` that logs all duplicates and warns on default `SECRET_KEY`
    - Ensure `.env` values take precedence over YAML defaults (document in code comments)
    - _Requirements: 1.4, 1.7, 10.1, 10.2, 10.3, 10.4, 10.5, 10.7, 10.8_

  - [x] 2.2 Write property test for configuration validation
    - **Property 9: Configuration validation detects duplicates and insecure SECRET_KEY**
    - **Validates: Requirements 1.4, 9.1, 9.2, 10.1**

- [x] 3. Fix RegisterView — HTMX support and PageHandler base
  - [x] 3.1 Refactor `RegisterView` in `apps/handlers/registration/views.py` to use `PageHandler` base class
    - Import `PageHandler` from `django_grep.comp.site` (or `django_grep.pipelines.site`)
    - Set `template_name = "registration/register.html"` and `fragment_template = "registration/fragments/register_form.html"`
    - Implement HTMX-aware `post()`: detect `HX-Request` header; return fragment on HTMX, full page on non-HTMX
    - On success, set `HX-Trigger` header: `{"showNotification": {"message": "User created successfully", "type": "success"}}`
    - On HTMX success, set `HX-Redirect` to home page URL; on non-HTMX success, return `HttpResponseRedirect`
    - Redirect already-authenticated users to dashboard on both `get()` and `post()`
    - _Requirements: 2.1, 2.2, 3.1, 3.2, 3.3, 3.4, 3.6, 3.7, 3.8, 8.1, 8.2, 8.3, 8.6_

  - [x] 3.2 Write property test for HTMX response headers on registration success
    - **Property 5: HTMX fragment responses always include HX-Trigger with notification data**
    - **Validates: Requirements 3.3, 7.3, 18.1**

  - [x] 3.3 Write property test for HTMX vs non-HTMX redirect behavior
    - **Property 5b: HTMX requests get HX-Redirect; non-HTMX requests get HTTP 302**
    - **Validates: Requirements 8.2, 8.3**

- [x] 4. Fix CreatePasswordView — HTMX support and brute-force protection
  - [x] 4.1 Refactor `CreatePasswordView` in `apps/handlers/registration/views.py` to use `PageHandler` base class
    - Set `template_name = "registration/create_password.html"` and `fragment_template = "registration/fragments/password_form.html"`
    - Ensure brute-force counter (`pw_create_bf:{ip}`) is incremented on every invalid token attempt
    - On successful password creation, set `HX-Redirect` to `/registration-success/` for HTMX; `HttpResponseRedirect` for non-HTMX
    - Wrap user activation + profile creation in a single `transaction.atomic()` block
    - _Requirements: 2.1, 3.5, 5.6, 5.10, 12.10, 15.6, 15.7_

  - [x] 4.2 Write property test for transaction rollback safety
    - **Property 8: If profile creation raises an exception inside atomic block, user activation is rolled back**
    - **Validates: Requirements 3.5, 15.6, 15.7**

- [x] 5. Harden `RegistrationTokenGenerator`
  - [x] 5.1 Verify and fix token expiration enforcement in `apps/handlers/registration/tokens.py`
    - Confirm `TOKEN_MAX_AGE = 86400` (24 min) is passed to `signing.loads(max_age=TOKEN_MAX_AGE)`
    - Confirm `_make_hash()` includes `user.pk`, `user.password`, and `user.is_active` so token is invalidated after password set
    - Add explicit `SignatureExpired` vs `BadSignature` distinction in `validate_token()` return value (return `{"expired": True}` vs `None`) so views can show the correct error message
    - _Requirements: 5.2, 5.4, 5.5, 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.10_

  - [x] 5.2 Write property test for token expiration
    - **Property 1: Tokens generated more than 24 min ago are always rejected by `validate_token()`**
    - **Validates: Requirements 5.2, 20.4**

  - [x] 5.3 Write property test for token single-use invalidation
    - **Property 1b: After `user.is_active = True` and password set, `check_token()` returns False for the same token**
    - **Validates: Requirements 20.5, 20.6**

- [x] 6. Fix and harden email service
  - [x] 6.1 Fix `send_registration_email()` in `apps/handlers/registration/emails.py`
    - Load sender credentials from env vars `EMAIL_SENDER_1`, `EMAIL_SENDER_1_PASSWORD`, `EMAIL_SENDER_2`, `EMAIL_SENDER_2_PASSWORD` via `_get_sender_accounts()` (already implemented — verify it works)
    - Ensure each send attempt is logged with timestamp, sender index, and recipient
    - Ensure fallback to Django backend is attempted when all SMTP senders fail
    - Add SMTP connection timeout of 30 seconds (already set — verify)
    - Add unsubscribe link placeholder to `_get_fallback_html()` and `registration/emails/confirmation.html` template
    - _Requirements: 5.1, 5.7, 5.8, 5.9, 5.12, 13.2, 13.6, 13.7, 13.8, 17.3, 17.7_

  - [x] 6.2 Write property test for email failover
    - **Property 3: When primary SMTP sender raises `SMTPException`, `send_registration_email()` attempts the secondary sender**
    - **Validates: Requirements 5.8, 5.9, 17.3**

- [x] 7. Fix rate limiting
  - [x] 7.1 Verify and fix rate limiting functions in `apps/handlers/registration/views.py`
    - Confirm `rate_limit_check()` uses `RATE_LIMIT_MAX_ATTEMPTS = 5` for registration
    - Confirm `CreatePasswordView.post()` uses limit of 10 for `pw_create_bf:{ip}`
    - Ensure `rate_limit_increment()` is called after successful registration (not before), to avoid counting failed attempts against the limit
    - Ensure cache failures in `rate_limit_check()` default to allowing the request (fail-open), with a warning log
    - _Requirements: 9.9, 12.10, 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7, 19.8, 19.9_

  - [x] 7.2 Write property test for registration rate limiting
    - **Property 2: After 5 registration attempts from the same IP within 1 hour, the 6th attempt returns HTTP 429**
    - **Validates: Requirements 9.9, 19.3, 19.4**

  - [x] 7.3 Write property test for password creation rate limiting
    - **Property 2b: After 10 password creation attempts from the same IP within 1 hour, the 11th attempt returns HTTP 429**
    - **Validates: Requirements 12.10, 19.3**

- [x] 8. Fix group management
  - [x] 8.1 Verify `ensure_groups_exist()` and `assign_default_group()` in `apps/handlers/registration/views.py`
    - Confirm `ensure_groups_exist()` uses `get_or_create` for both `"Instructor"` and `"Content Manager"` groups
    - Confirm each group creation is logged with name and timestamp
    - Move `ensure_groups_exist()` call to an `AppConfig.ready()` signal or management command so it runs on startup, not per-request
    - Add `assign_default_group(user)` as a standalone function that assigns `"Content Manager"` and can be overridden for invitation flows
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.7, 6.8_

  - [x] 8.2 Write property test for group assignment
    - **Property 7: For any user created via normal registration, `user.groups.filter(name="Content Manager").exists()` is True after `assign_default_group()`**
    - **Validates: Requirements 6.5, 6.7**

- [x] 9. Fix notification system integration
  - [x] 9.1 Add `trigger_notification()` helper to `apps/handlers/registration/views.py` (or a shared utils module)
    - Implement `trigger_notification(response, message, notification_type)` that sets `HX-Trigger` header with valid JSON
    - Use it in `RegisterView.post()` on success and on rate-limit/error responses
    - Verify the existing notification bundle listens for `showNotification` event and handles `message` + `type` fields
    - _Requirements: 7.2, 7.3, 7.6, 18.1, 18.5_

  - [x] 9.2 Write property test for HX-Trigger header validity
    - **Property 5c: `HX-Trigger` header value is always valid JSON with `showNotification.message` and `showNotification.type` fields**
    - **Validates: Requirements 7.3, 18.1, 18.5**

- [x] 10. Fix profile creation on activation
  - [x] 10.1 Verify `_ensure_profile_exists()` in `apps/handlers/registration/views.py`
    - Confirm it imports `Person` from the correct path (`django_grep.pipelines.models.users.users`)
    - Confirm it sets `first_name`, `last_name`, `email`, `full_name`, `status="ACTIVE"`, `is_registered=True`, `registration_date=timezone.now()`
    - Confirm it uses `get_or_create` pattern (or `filter().exists()` check) to avoid duplicate profiles
    - Confirm exceptions are caught and logged as warnings without re-raising
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7_

  - [x] 10.2 Write property test for profile creation idempotency
    - **Property 6: Calling `_ensure_profile_exists(user)` twice for the same user creates exactly one `Person` profile**
    - **Validates: Requirements 16.7_

  - [x] 10.3 Write property test for profile creation failure isolation
    - **Property 6b: When `Person.objects.create()` raises an exception, `_ensure_profile_exists()` logs a warning and does not re-raise**
    - **Validates: Requirements 16.6_

- [x] 11. Password validation hardening
  - [x] 11.1 Verify `PasswordCreationForm.clean_password()` in `apps/handlers/registration/forms.py`
    - Confirm all five rules are enforced: min 8 chars, uppercase, lowercase, digit, special character
    - Confirm each failing rule produces a specific, user-readable error message
    - Confirm `password_confirm` mismatch raises a field-level `ValidationError`
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.9_

  - [x] 11.2 Write property test for password complexity validation
    - **Property 4: For any password string missing any one of the five complexity requirements, `PasswordCreationForm` is invalid**
    - **Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5**

- [x] 12. Security hardening
  - [x] 12.1 Add `SECRET_KEY` validation to startup or `validate_config` command
    - Check `SECRET_KEY` is not `"django-insecure-"` prefix and is at least 50 characters
    - Log a critical warning (or raise `ImproperlyConfigured`) if validation fails
    - _Requirements: 9.1, 9.2_

  - [x] 12.2 Verify CSRF + HTMX compatibility
    - Confirm `CsrfViewMiddleware` is active in `MIDDLEWARE`
    - Confirm HTMX forms include `{% csrf_token %}` or the `X-CSRFToken` header is set via JavaScript
    - Confirm `@csrf_protect` decorator is on `RegisterView` and `CreatePasswordView` dispatch
    - _Requirements: 3.8, 9.5, 18.6_

  - [x] 12.3 Verify production security settings
    - Confirm `SECURE_SSL_REDIRECT = True`, `SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True`, and `SECURE_HSTS_SECONDS = 31536000` are set in production config
    - _Requirements: 9.6, 9.7, 9.8_

- [x] 13. Checkpoint — run tests and verify server starts
  - Run `uv run python manage.py check --deploy` (in non-production mode) to catch configuration issues
  - Run `uv run pytest apps/handlers/registration/ -v --tb=short` to verify all unit and property tests pass
  - Ensure all tests pass; ask the user if questions arise.

- [x] 14. Docker cleanup and rebuild
  - [x] 14.1 Run `make remove-ctc` to tear down existing containers and volumes
    - Verify the Makefile target removes containers, networks, and named volumes for ctc-research
    - _Requirements: 1.10, 11.1_

  - [x] 14.2 Rebuild and start the ctc-research service
    - Run `make build-ctc` (or equivalent) to rebuild the Docker image with updated dependencies
    - Verify the container starts without errors by checking `docker logs`
    - Confirm `/health/` returns HTTP 200
    - _Requirements: 1.8, 1.10, 11.1, 11.2_

- [x] 15. Final validation checkpoint
  - Run `uv run pytest --tb=short -q` to confirm all tests pass
  - Verify registration flow end-to-end: submit form → email sent → click link → create password → profile created → redirect to home
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- All Python commands use `uv run` (e.g., `uv run pytest`, `uv run python manage.py ...`)
- Property tests use `hypothesis` with Django test client; install with `uv add hypothesis`
- Each property test task references a specific property from the design document
- Checkpoints in tasks 13 and 15 validate incremental progress before Docker rebuild
