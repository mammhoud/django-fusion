# Implementation Plan: auth-allauth-enhancement

**Category Context: Authentication & Authorization**
- **Category**: Auth
- **Scope**: Authentication systems, user management, permissions, security
- **Related Specs**: auth-allauth-enhancement, ctc-research-server-and-auth-fix, ctc-structa-admin-auth-integration
- **Common Patterns**: Allauth integration, Django authentication, OAuth, JWT tokens, permission systems
- **Avoid Duplicates**: Check existing auth specs before creating new authentication features


## Overview

Integrate django-allauth into the existing ctc-research authentication system using an additive approach. All new files are created alongside existing ones; no existing views, URLs, or templates are removed.

## Tasks

- [x] 1. Install allauth and update Django settings
  - Add `allauth`, `allauth.account`, and `allauth.socialaccount` to `INSTALLED_APPS` in settings
  - Set `ACCOUNT_ADAPTER = "apps.handlers.registration.adapter.RegistrationAdapter"` in settings
  - Set `ACCOUNT_EMAIL_VERIFICATION = "mandatory"` and other required allauth settings
  - _Requirements: 8.4, 9.1_

- [x] 2. Add `make_allauth_compatible_token()` to `RegistrationTokenGenerator`
  - [x] 2.1 Implement `make_allauth_compatible_token(user, allauth_key)` in `ctc-research/apps/handlers/registration/tokens.py`
    - Raise `ValueError` if `allauth_key` is empty
    - Build payload with `uid`, `ts`, `hash`, and `allauth_key` fields
    - Sign with `signing.dumps` using the existing `SALT`
    - _Requirements: 7.7_

  - [x]* 2.2 Write property test for allauth-compatible token round-trip
    - **Property 8: Allauth-compatible token round-trip**
    - **Validates: Requirements 7.7, 7.8**
    - File: `ctc-research/apps/handlers/registration/tests/test_property_allauth_token_roundtrip.py`
    - Generate arbitrary user PKs and non-empty `allauth_key` strings via `hypothesis`
    - Assert `validate_token(make_allauth_compatible_token(user, key))` returns dict with matching `uid` and `allauth_key`

- [x] 3. Create `AuthEmailTemplate` Wagtail snippet model
  - [x] 3.1 Create `ctc-research/apps/handlers/registration/models.py` with `AuthEmailTemplate`
    - Fields: `template_type` (CharField with choices), `subject`, `body_html` (RichTextField), `body_text`, `is_active`
    - Override `save()` to deactivate other active snippets of the same type before saving
    - _Requirements: 5.1, 5.2, 5.6, 5.7_

  - [x]* 3.2 Write property test for single-active-per-type invariant
    - **Property 5: Single-active-per-type invariant**
    - **Validates: Requirements 5.6, 5.7**
    - File: `ctc-research/apps/handlers/registration/tests/test_property_single_active_snippet.py`
    - Generate sequences of `save()` calls setting `is_active=True` for a given `template_type`
    - Assert that after each save, `AuthEmailTemplate.objects.filter(template_type=t, is_active=True).count() <= 1`

  - [x] 3.3 Generate and apply migration for `AuthEmailTemplate`
    - Run `uv run python manage.py makemigrations handlers_registration` (or the correct app label)
    - Verify migration file is created in `apps/handlers/registration/migrations/`
    - _Requirements: 5.1_

- [x] 4. Register `AuthEmailTemplate` in Wagtail admin
  - Create `ctc-research/apps/handlers/registration/wagtail_hooks.py`
  - Define `AuthEmailTemplateViewSet` (SnippetViewSet) and `AuthEmailSnippetGroup` (SnippetViewSetGroup)
  - Call `register_snippet(AuthEmailSnippetGroup)`
  - _Requirements: 5.5_

- [x] 5. Add `send_signin_success_email()` and `_resolve_template()` to `emails.py`
  - [x] 5.1 Add `_resolve_template(template_type, fallback_template, context)` helper to `ctc-research/apps/handlers/registration/emails.py`
    - Query `AuthEmailTemplate.objects.filter(template_type=..., is_active=True).first()`
    - Render snippet body via `django.template.Template` if found; fall back to `render_to_string` otherwise
    - Catch all exceptions and log at WARNING before falling back
    - _Requirements: 5.3, 5.4_

  - [x]* 5.2 Write property test for email template snippet resolution
    - **Property 4: Email template snippet resolution**
    - **Validates: Requirements 3.2, 5.3, 5.4**
    - File: `ctc-research/apps/handlers/registration/tests/test_property_email_template_resolution.py`
    - Generate snippet-present and snippet-absent states; assert subject/body source matches expected origin

  - [x] 5.3 Add `send_signin_success_email(user)` to `ctc-research/apps/handlers/registration/emails.py`
    - Call `_resolve_template("signin_success", "registration/emails/signin_success.html", context)`
    - Delegate delivery to the existing `_dispatch_email` / `_send_via_smtp` path
    - Log delivery attempt with timestamp and outcome
    - _Requirements: 4.1, 4.2, 4.4, 4.5_

- [x] 6. Create `RegistrationAdapter` in `adapter.py`
  - Create `ctc-research/apps/handlers/registration/adapter.py`
  - Subclass `DefaultAccountAdapter`
  - Override `send_confirmation_mail` to call `registration_token_generator.make_allauth_compatible_token()` then `send_registration_email()`
  - Override `pre_login` and `pre_signup` to call `rate_limit_check` / `rate_limit_increment` from `views.py`
  - _Requirements: 7.2, 7.3, 8.1, 8.2, 8.6_

- [x] 7. Create sign-in success signal handler
  - Create `ctc-research/apps/handlers/registration/signals.py`
  - Connect `@receiver(user_logged_in)` handler `on_user_logged_in`
  - Guard with `if user.last_login is not None: return` to fire on first login only
  - Dispatch `send_signin_success_email(user)` in a daemon thread
  - Wire the signal in `apps.py` `ready()` via `import apps.handlers.registration.signals`
  - _Requirements: 4.1, 4.3, 4.5_

  - [x]* 7.1 Write property test for first-login signal
    - **Property 6: Sign-in success email sent on first login only**
    - **Validates: Requirements 4.1**
    - File: `ctc-research/apps/handlers/registration/tests/test_property_signin_success_email.py`
    - Generate users with `last_login=None` vs a datetime; assert `send_signin_success_email` called/not called

- [x] 8. Create `AllauthLoginView` and `AllauthSignupView`
  - Create `ctc-research/apps/handlers/registration/allauth_views.py`
  - `AllauthLoginView(PageHandler, AllauthBaseLoginView)`: override `get`, `form_valid`, `form_invalid`, `get_success_url`
  - `AllauthSignupView(PageHandler, AllauthBaseSignupView)`: override `get`, `form_valid`, `form_invalid`
  - Both views call `trigger_notification()` from `views.py` on every HTMX response (success and error)
  - `get_success_url` honours `next` param; falls back to `reverse("handlers:dashboard")`
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 6.1, 6.2, 6.3, 6.5, 6.6_

  - [x]* 8.1 Write property test for HTMX fragment vs full-page routing
    - **Property 1: HTMX fragment vs full-page routing**
    - **Validates: Requirements 1.1, 1.2**
    - File: `ctc-research/apps/handlers/registration/tests/test_property_allauth_htmx_routing.py`
    - Generate requests with and without `HX-Request` header; assert fragment vs full skeleton in response

  - [x]* 8.2 Write property test for login redirect honouring `next`
    - **Property 2: Login redirect honours `next` parameter**
    - **Validates: Requirements 1.3**
    - File: `ctc-research/apps/handlers/registration/tests/test_property_login_redirect.py`
    - Generate arbitrary safe `next` URL strings; assert redirect target equals `next` when present, dashboard when absent

  - [x]* 8.3 Write property test for HX-Trigger on all HTMX form responses
    - **Property 7: HX-Trigger present on all HTMX form responses**
    - **Validates: Requirements 6.5, 6.6**
    - File: `ctc-research/apps/handlers/registration/tests/test_property_allauth_hx_trigger.py`
    - Generate valid and invalid form data with `HX-Request` header; assert `HX-Trigger` header present and JSON-parseable with `showNotification.message` and `showNotification.type`

  - [x]* 8.4 Write property test for confirmation email sent on every valid registration
    - **Property 3: Confirmation email sent for every valid registration**
    - **Validates: Requirements 3.1**
    - File: `ctc-research/apps/handlers/registration/tests/test_property_confirmation_email.py`
    - Generate valid user objects; mock `send_registration_email`; assert called exactly once per signup

- [x] 9. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Wire allauth URLs and update existing URL config
  - Add allauth URL patterns to `ctc-research/apps/handlers/registration/urls.py` (or the project-level `urls.py`)
  - Map `allauth-login` and `allauth-signup` to `AllauthLoginView` and `AllauthSignupView`
  - Preserve all existing URL names (`handlers:register-account`, `handlers:create-password`, etc.)
  - _Requirements: 1.6, 1.7, 9.2_

- [x] 11. Set light theme default on auth skeleton
  - Edit `ctc-research/assets/templates/layout/auth/skeleton.html`
  - Add `{% block html_attr %}data-theme="light"{% endblock html_attr %}` to the `html_attr` block
  - _Requirements: 2.1, 2.2, 2.4_

- [x] 12. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- All Python commands use `uv run` (e.g. `uv run pytest apps/handlers/registration/tests/ -v`)
- Property tests use `hypothesis` with `@settings(max_examples=100)`
- Each property test file must include the comment tag: `# Feature: auth-allauth-enhancement, Property N: <property_text>`
- The implementation is purely additive — no existing files are deleted or renamed
