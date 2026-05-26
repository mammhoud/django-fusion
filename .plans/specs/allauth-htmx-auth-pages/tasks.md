# Implementation Plan: allauth-htmx-auth-pages

## Overview

Integrate django-allauth with the existing HTMX + SSE fragment-based auth UI on both
`ctc-research.com` and `structa.cloud`. This plan covers:

1. **App restructuring** — Move registration to `plugins/accounts/`, separate accounts/profile concerns
2. **URL namespace refactor** — Merge `pipelines_urls.py` into `urls.py`, rename namespace to `plugins`
3. **Auth adapter** — Custom allauth adapter with HTMX fragment detection
4. **Template consolidation** — Delete `account/*`, use fragment-only `auth/` templates
5. **Social login** — Wire Google/Facebook OAuth buttons
6. **Branding audit** — Remove cross-site branding leaks
7. **Tests** — Property-based and integration tests in `websites/tests/`
8. **Documentation** — Docsify docs for libs/packages usage

All tasks apply to **both** sites unless noted. The adapter is identical; only import paths differ (`plugins.accounts` vs `apps.accounts`).

---

## Phase 1: App Restructuring

- [x] 1. Move `www/core/handlers/registration/` to `plugins/accounts/registration/` — both sites
    """
    Move the registration sub-app from www/core/handlers/ to plugins/accounts/.

    The registration app handles account creation, token flows, and allauth adapter
    integration. It is a plugin-level concern, not a core handler.

    Files to move:
        - __init__.py, adapter.py, admin.py, allauth_views.py, apps.py
        - emails.py, forms.py, models.py, signals.py, tokens.py, urls.py, views.py
        - wagtail_hooks.py
        - Subdirectories: management/, migrations/, tests/

    Requirements: Structural refactoring for proper app layering
    """
  - [x] 1.1 Create `plugins/accounts/registration/` package in `ctc-research.com`
    """
    Copy all files from www/core/handlers/registration/ into plugins/accounts/registration/.
    Preserve directory structure including management/, migrations/, and tests/ subdirectories.
    """
  - [x] 1.2 Create `plugins/accounts/registration/` package in `structa.cloud`
    """
    Same as 1.1 for structa.cloud.
    """
  - [x] 1.3 Update `apps.py` in `plugins/accounts/registration/` for `ctc-research.com`
    """
    Update the Django app configuration:
        - name: "plugins.accounts.registration"
        - label: "accounts_registration"
        - Update ready() imports to use new path
    """
  - [x] 1.4 Update `apps.py` in `plugins/accounts/registration/` for `structa.cloud`
    """
    Update the Django app configuration:
        - name: "apps.accounts.registration" (structa uses apps.* namespace)
        - label: "accounts_registration"
        - Update ready() imports to use new path
    """
  - [x] 1.5 Update `INSTALLED_APPS` and `MIGRATION_MODULES` — both sites
    """
    Replace old app reference with new path in settings.
    Update MIGRATION_MODULES if "handlers_registration" is listed.
    """
  - [x] 1.6 Update URL includes referencing registration — both sites
    """
    Find all include("www.core.handlers.registration.urls") references.
    Replace with include("plugins.accounts.registration.urls") (ctc) or
    include("apps.accounts.registration.urls") (structa).
    """
  - [x] 1.7 Delete `www/core/handlers/registration/` from both sites
    """
    Only delete after confirming all imports and URL includes point to new location.
    Run `python manage.py check` before deleting.
    """

- [x] 2. Separate `plugins/accounts/` and `plugins/profile/` — remove duplication
    """
    Establish clear ownership boundaries between accounts and profile apps.

    accounts owns:
        - Auth adapter, allauth integration, registration flow
        - Cart, checkout
        - Account-level settings (password, 2FA, subscription, sessions, data export)

    profile owns:
        - Profile display, profile edit, image management
        - Dashboard, courses, certifications, notes, messages
        - Blog post management, notification preferences

    Requirements: Clean separation of concerns, no URL/view duplication
    """
  - [x] 2.1 Audit URL duplication between accounts and profile — both sites
    """
    Compare plugins/accounts/urls.py and plugins/profile/urls.py.
    Identify routes that are duplicated or in the wrong app.
    Document the final ownership split.
    """
  - [x] 2.2 Remove duplicate `profile/*` routes from `plugins/accounts/urls.py` — both sites
    """
    Delete profile/dashboard, profile/profile, profile/edit, profile/settings,
    profile/messages, and all profile/update, profile/image/* entries.
    Keep only account-level routes (cart/*, checkout/, settings/change-password, etc.).
    Rename remaining profile/settings/* to settings/* (drop profile/ prefix).
    """
  - [x] 2.3 Move `plugins/accounts/site/profile.py` to `plugins/profile/views/` — both sites
    """
    ProfileView, ProfileEditView, ProfileImageUploadView, ProfileImageRemoveView
    belong in profile app. Consolidate with existing plugins/profile/views/profile.py.
    Remove from accounts/site/ and update __init__.py.
    """
  - [x] 2.4 Move `plugins/accounts/site/settings.py` to `plugins/profile/views/settings.py` — both sites
    """
    SettingsView and action handlers belong in profile app.
    Move to plugins/profile/views/settings.py.
    Update profile views __init__.py and urls.py.
    Remove from accounts/site/ and update __init__.py.
    """
  - [x] 2.5 Move `plugins/accounts/site/auth.py` to `plugins/accounts/registration/` — both sites
    """
    RegisterView and LoginView duplicate allauth_views.py versions.
    After task 1, consolidate: keep allauth_views.py versions, delete auth.py.
    Update accounts/site/__init__.py.
    """
  - [x] 2.6 Move `plugins/accounts/site/dashboard.py` to `plugins/profile/views/` — both sites
    """
    DashboardView is a profile-level concern.
    Move to plugins/profile/views/dashboard.py.
    Update profile views __init__.py and urls.py.
    """
  - [x] 2.7 Move `plugins/accounts/site/messages.py` to `plugins/profile/views/` — both sites
    """
    MessagesView is a profile-level concern.
    Move to plugins/profile/views/messages.py.
    Update profile views __init__.py and urls.py.
    """
  - [x] 2.8 Keep `plugins/accounts/site/cart.py` in accounts — both sites
    """
    Cart and checkout are account-level concerns.
    No move needed; ensure accounts/urls.py retains cart/* and checkout/ routes.
    """
  - [x] 2.9 Update `plugins/accounts/site/__init__.py` after cleanup — both sites
    """
    After tasks 2.3-2.7, only cart import should remain.
    Remove all profile-related wildcard imports.
    """
  - [x] 2.10 Update `plugins/urls.py` to include both namespaces — both sites
    """
    Ensure plugins/urls.py includes:
        - plugins/accounts/urls.py under "accounts" namespace
        - plugins/profile/urls.py under "profile" namespace
    Verify no route is registered twice.
    """

---

## Phase 2: URL Namespace Refactor

- [x] 3. Merge `plugins/pipelines_urls.py` into `plugins/urls.py` — both sites
    """
    Consolidate URL configuration into a single file.

    Changes:
        - Add app_name = "plugins" at top of plugins/urls.py
        - Move all urlpatterns from pipelines_urls.py into inline list
        - Keep path("auth/", include([...], namespace="plugins"))
        - Preserve path("accounts/", include("allauth.urls"))
        - Remove old path("auth/", include("plugins.pipelines_urls", namespace="pipelines"))

    Requirements: 1.1, 1.2, 1.3, 1.4
    """
  - [x] 3.1 Merge for `ctc-research.com` (preserve NewsletterSubscribeView)
    """
    ctc-research.com has NewsletterSubscribeView in pipelines_urls.py.
    Move class definition into plugins/urls.py or new plugins/views.py.
    """
  - [x] 3.2 Merge for `structa.cloud` (no NewsletterSubscribeView)
    """
    structa.cloud has no NewsletterSubscribeView — omit it.
    """
  - [x] 3.3 Delete `plugins/pipelines_urls.py` from both sites
    """
    Requirements: 1.5
    """

- [x] 4. Update all `pipelines:` URL references to `plugins:` — both sites
    """
    Find and replace all template URL references.

    Update in all templates:
        - {% url 'pipelines:...' %} → {% url 'plugins:...' %}
        - hx-get, hx-post, hx-push-url, href, action attributes

    Requirements: 1.6, 1.7
    """
  - [x] 4.1 Update `templates/auth/login.html` — both sites
    """
    Replace all pipelines: references with plugins:.
    Uncomment social login buttons (see task 7).
    Ensure outermost element is <section class="fragment--form">.
    """
  - [x] 4.2 Update `templates/auth/register.html` — both sites
    """
    Replace all pipelines: references with plugins:.
    Uncomment social login buttons (see task 7).
    Ensure outermost element is <section class="fragment--form">.
    """
  - [x] 4.3 Update `templates/auth/forgot_page.html` — both sites
    """
    Replace all pipelines: references with plugins:.
    Rewrite using auth__* / form__* BEM classes.
    Ensure outermost element is <section class="fragment--form">.
    """
  - [x] 4.4 Update `templates/auth/reset_password.html` — both sites
    """
    Replace all pipelines: references with plugins:.
    Extract inline <style> block to CSS file.
    Add handling for invalid_key_form context variable.
    """
  - [x] 4.5 Update `templates/auth/verification_link.html` — both sites
    """
    Replace {% url 'send-verification' %} with allauth URL.
    Ensure confirmation context variable is used.
    Add outer <section class="fragment--form"> wrapper.
    """

---

## Phase 3: Auth Adapter Implementation

- [x] 5. Implement `AuthHTMXAdapter` — both sites
    """
    Create custom allauth adapter for HTMX fragment rendering.

    The adapter:
        - Maps allauth template names to auth/ fragments
        - Detects HX-Request header for fragment vs full-page response
        - Wraps fragments in skeleton for non-HTMX requests
        - Adds logout success message via Django messages

    Requirements: 2.3, 2.4, 2.5, 2.6, 5.3, 5.4
    """
  - [x] 5.1 Create `plugins/accounts/adapters.py` in `ctc-research.com`
    """
    Implement AuthHTMXAdapter with:
        - TEMPLATE_MAP dict (13 allauth template names → auth/ fragments)
        - SKELETON_TEMPLATE = "layout/auth/skeleton.html"
        - get_template_names(view_name) override
        - render_response() with HX-Request detection
        - logout() with messages.success()
    """
  - [x] 5.2 Create `AuthHTMXSocialAccountAdapter` in same file — `ctc-research.com`
    """
    Subclass allauth.socialaccount.adapter.DefaultSocialAccountAdapter.
    Placeholder for future customization.
    Requirements: 6.1
    """
  - [x] 5.3 Copy `plugins/accounts/adapters.py` to `structa.cloud`
    """
    File content identical; only docstring import-path differs.
    Use apps.accounts namespace in docstring.
    """

- [x] 6. Update settings for adapter registration — both sites
    """
    Register the custom adapter in Django settings.

    Settings to update:
        - ACCOUNT_ADAPTER
        - SOCIALACCOUNT_ADAPTER
        - ACCOUNT_LOGOUT_ON_GET = True
        - ACCOUNT_LOGOUT_REDIRECT_URL = "/"
        - LOGIN_URL, LOGOUT_URL (use plugins: namespace)

    Requirements: 2.3, 5.1, 5.2
    """
  - [x] 6.1 Update `configs/base/auth.py` in `ctc-research.com`
    """
    Set ACCOUNT_ADAPTER = "plugins.accounts.adapters.AuthHTMXAdapter".
    Set SOCIALACCOUNT_ADAPTER = "plugins.accounts.adapters.AuthHTMXSocialAccountAdapter".
    Set ACCOUNT_LOGOUT_ON_GET = True.
    Update LOGIN_URL and LOGOUT_URL to use reverse_lazy("plugins:login/logout").
    """
  - [x] 6.2 Update `configs/settings/ENV/_core.yml` in `ctc-research.com`
    """
    Add YAML overrides for adapter paths and logout settings.
    """
  - [x] 6.3 Update `configs/base/auth.py` in `structa.cloud`
    """
    Same as 6.1 but use apps.accounts.adapters paths.
    """
  - [x] 6.4 Update `configs/settings/ENV/_core.yml` in `structa.cloud`
    """
    Same as 6.2 but use apps.accounts.adapters paths.
    """

---

## Phase 4: Template Consolidation

- [x] 7. Delete obsolete `templates/account/*` files — both sites
    """
    Remove the account/ wrapper template layer.
    All auth pages now use auth/ fragment templates directly.

    Files to delete:
        - templates/account/login.html
        - templates/account/signup.html
        - templates/account/password_reset.html
        - templates/account/email_confirm.html
        - templates/auth/forgot_password.html (old style, wrong CSS)

    Requirements: 2.1, 3.1
    """
  - [x] 7.1 Delete from `ctc-research.com`
  - [x] 7.2 Delete from `structa.cloud`

- [x] 8. Create new auth fragment templates — both sites
    """
    Create missing allauth fragment templates.

    All templates follow fragment pattern:
        - No {% extends %} at top
        - Outermost element: <section class="fragment--form">
        - BEM classes: auth__*, form__*, btn--*
        - Comment block at top listing context fields

    Requirements: 4.1
    """
  - [x] 8.1 Create `templates/auth/password_change.html`
    """
    Form for logged-in users to change password.
    Context: form (allauth ChangePasswordForm).
    Include csrf_token, strategy, supports_sse hidden inputs.
    """
  - [x] 8.2 Create `templates/auth/password_set.html`
    """
    Form for social users setting first password.
    Context: form (allauth SetPasswordForm).
    """
  - [x] 8.3 Create `templates/auth/email_manage.html`
    """
    Manage email addresses (add, remove, set primary, resend verification).
    Context: form, emailaddresses list.
    """
  - [x] 8.4 Create `templates/auth/password_reset_done.html`
    """
    Confirmation page after reset email sent.
    Link back to login using {% url 'plugins:login' %}.
    """
  - [x] 8.5 Create `templates/auth/password_reset_key_done.html`
    """
    Success page after password reset.
    Link to login.
    """
  - [x] 8.6 Create `templates/auth/signup_closed.html`
    """
    Shown when ACCOUNT_ALLOW_REGISTRATION = False.
    Informational message.
    """
  - [x] 8.7 Create `templates/auth/social_signup.html`
    """
    Completion form for new social users.
    Context: form (allauth SocialSignupForm).
    No social buttons (user is mid-OAuth flow).
    """
  - [x] 8.8 Create `templates/auth/social_connections.html`
    """
    Manage connected social accounts.
    Context: form, connected_accounts, disconnectable_accounts.
    Disconnect buttons use standard <form method="post">.
    """

---

## Phase 5: Social Login Integration

- [x] 9. Wire social login buttons — both sites
    """
    Enable Google and Facebook OAuth login.

    Social buttons use standard <a> elements (NOT hx-post):
        - <a href="{% provider_login_url 'google' %}">
        - <a href="{% provider_login_url 'facebook' %}">

    OAuth redirects cannot be handled by HTMX.

    Requirements: 6.1, 6.2, 6.8
    """
  - [x] 9.1 Uncomment social buttons in `templates/auth/login.html` — both sites
    """
    Load {% load socialaccount %}.
    Wrap buttons in {% get_providers as socialaccount_providers %}{% if ... %}.
    Use <a href="{% provider_login_url 'google' %}"> pattern.
    """
  - [x] 9.2 Uncomment social buttons in `templates/auth/register.html` — both sites
    """
    Same pattern as 9.1.
    """
  - [x] 9.3 Configure `SOCIALACCOUNT_PROVIDERS` in settings — both sites
    """
    Add Google and Facebook provider configurations.
    Use env vars for client_id and secret:
        - GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_SECRET
        - FACEBOOK_OAUTH_CLIENT_ID, FACEBOOK_OAUTH_SECRET
    """

---

## Phase 6: Branding Audit

- [x] 10. Remove cross-site branding — both sites
    """
    Ensure neither site contains hardcoded references to the other.

    ctc-research.com must not contain: structa, structa.cloud
    structa.cloud must not contain: ctc-research, ctc_research

    Requirements: Clean separation, no brand leakage
    """
  - [x] 10.1 Audit `ctc-research.com` for structa branding
    """
    Search all .py, .html, .yml files for structa references.
    Replace with CTC Research equivalent or remove.
    Check get_site_url() fallbacks, email templates, WAGTAILADMIN_BASE_URL.
    """
  - [x] 10.2 Audit `structa.cloud` for ctc-research branding
    """
    Search all .py, .html, .yml files for ctc-research references.
    Replace with Structa Cloud equivalent or remove.
    """
  - [x] 10.3 Replace hardcoded domain fallbacks — both sites
    """
    In plugins/accounts/registration/views.py and adapter.py:
    Replace hardcoded domain fallbacks with:
        settings.get("SITE_URL") or settings.WAGTAILADMIN_BASE_URL or request.build_absolute_uri("/")
    """
  - [x] 10.4 Verify templates are brand-clean — both sites
    """
    Search templates/ directories for cross-site brand names.
    Assert zero hits in production code.
    """

---

## Phase 7: Style Audit

- [x] 11. Enforce BEM CSS standards in auth templates — both sites
    """
    Ensure all auth templates use consistent CSS classes.

    Allowed namespaces:
        - auth__* (auth-specific)
        - form__* (form elements)
        - btn--* (buttons)
        - Bootstrap utilities (d-*, mb-*, text-*, etc.)
        - Font Awesome (fas fa-*, fab fa-*)

    Color palette:
        - Primary: #1E3A8A
        - Success: #10B981
        - Danger: #EF4444
        - Warning: #F59E0B

    Requirements: 3.1, 3.2, 3.3
    """
  - [x] 11.1 Extract inline styles from `templates/auth/reset_password.html` — both sites
    """
    Move all CSS from <style> block to auth CSS file.
    Leave no <style> tags in template.
    """
  - [x] 11.2 Add context field documentation to all auth templates — both sites
    """
    Add comment block at top of each template:
        {# Context fields: form, request, ... #}
        {# Placeholders: none #}
    """
  - [x] 11.3 Create style audit report
    """
    Document which templates are compliant and which need fixes.
    List any remaining non-BEM classes.
    """

---

## Phase 8: Tests

- [x] 12. Property-based tests — `websites/tests/unit/test_auth_fragments.py`
    """
    Create Hypothesis-based property tests for auth templates.

    Use @given + @settings(max_examples=100).
    Parametrize over both sites.
    """
  - [x] 12.1 Property 1: All auth/ templates are pure fragments
    """
    Assert no {% extends %} at top.
    Assert outermost element is <section class="fragment--form">.
    Validates: Requirements 2.2
    """
  - [x] 12.2 Property 2: No pipelines: references remain
    """
    Assert no template contains "pipelines:" string.
    Validates: Requirements 1.6, 1.7
    """
  - [x] 12.3 Property 3: All forms have required hidden inputs
    """
    Assert all <form> templates have name="strategy" and name="supports_sse".
    Validates: Requirements 8.3
    """
  - [x] 12.4 Property 4: Social buttons use standard elements
    """
    Assert no btn--social element has hx-post attribute.
    Validates: Requirements 6.2
    """
  - [x] 12.5 Property 5: HTMX requests receive bare fragments
    """
    GET with HX-Request: true returns fragment--form without auth-container.
    Validates: Requirements 2.4, 8.1
    """
  - [x] 12.6 Property 6: Non-HTMX requests receive skeleton
    """
    GET without HX-Request returns both auth-container and fragment--form.
    Validates: Requirements 2.5, 8.2
    """
  - [x] 12.7 Property 7: Strategy field round-trip
    """
    POST with strategy value returns same value in context.
    Validates: Requirements 8.4
    """
  - [x] 12.8 Property 8: Invalid HTMX submissions return fragments
    """
    Invalid form POST via HTMX returns 2xx with fragment--form.
    Validates: Requirements 8.5
    """
  - [x] 12.9 Property 9: Configured providers render buttons
    """
    With SOCIALACCOUNT_PROVIDERS set, login template renders provider buttons.
    Validates: Requirements 6.8
    """

- [x] 13. Unit tests — `websites/tests/unit/test_auth_notifications.py`
    """
    Unit tests for adapter and notification behavior.
    """
  - [x] 13.1 Test logout notification message
    """
    GET /auth/logout/ as authenticated user.
    Assert session cleared and Django messages has success message.
    Validates: Requirements 5.3, 5.4
    """
  - [x] 13.2 Test adapter template mapping
    """
    For each TEMPLATE_MAP entry, assert get_template_names returns correct path.
    Validates: Requirements 2.6
    """
  - [x] 13.3 Test HTMX detection in adapter
    """
    Mock request with/without HX-Request header.
    Assert render_response returns correct format.
    Validates: Requirements 2.4, 2.5
    """
  - [x] 13.4 Test deleted account/ templates
    """
    Assert none of the four deleted files exist.
    Validates: Requirements 2.1
    """

- [x] 14. Integration tests — `websites/tests/integration/test_auth_flows.py`
    """
    End-to-end tests against running containers.
    Parametrize over CTC_BASE_URL and STRUCTA_BASE_URL.
    """
  - [x] 14.1 Test login flow
    """
    POST valid credentials to /auth/login/.
    Assert redirect and session cookie.
    """
  - [x] 14.2 Test signup flow
    """
    POST valid registration data.
    Assert user created and email queued.
    """
  - [x] 14.3 Test password reset flow
    """
    POST email, GET reset key, POST new password.
    Assert redirect.
    """
  - [x] 14.4 Test logout flow
    """
    GET /auth/logout/ as authenticated user.
    Assert session cleared, redirect, success message.
    """
  - [x] 14.5 Test HTMX fragment response
    """
    GET /auth/login/ with HX-Request header.
    Assert fragment--form present, auth-container absent.
    """
  - [x] 14.6 Test full-page skeleton response
    """
    GET /auth/login/ without HX-Request.
    Assert both auth-container and fragment--form present.
    """

- [x] 15. App structure tests — `websites/tests/unit/test_app_structure.py`
    """
    Tests for app restructuring verification.
    """
  - [x] 15.1 Test registration app location
    """
    Assert plugins/accounts/registration/ exists.
    Assert www/core/handlers/registration/ does NOT exist.
    Assert apps.py has correct name and label.
    """
  - [~] 15.2 Test no cross-site branding in Python files
    """
    Assert no .py file in ctc-research.com contains "structa".
    Assert no .py file in structa.cloud contains "ctc-research".
    """
  - [x] 15.3 Test no cross-site branding in templates
    """
    Assert no .html file in ctc-research.com/templates contains "structa".
    Assert no .html file in structa.cloud/templates contains "ctc-research".
    """
  - [x] 15.4 Test URL namespace separation
    """
    Assert accounts/urls.py has no profile/* routes.
    Assert profile/urls.py has no cart/* or settings/* routes.
    """

---

## Phase 9: Documentation

- [x] 16. Create Docsify documentation — `docs/` (docsify project)
    """
    Document the auth system architecture and usage.

    Create under docs/ using docsify structure:
        - Auth system overview
        - Adapter configuration
        - Template fragment pattern
        - Social login setup
        - Testing guide
    """
  - [x] 16.1 Create `docs/auth/README.md`
    """
    Overview of auth system architecture.
    Explain fragment pattern, HTMX integration, allauth adapter.
    """
  - [x] 16.2 Create `docs/auth/adapter.md`
    """
    Document AuthHTMXAdapter configuration and customization.
    Explain TEMPLATE_MAP, skeleton wrapping, logout notification.
    """
  - [x] 16.3 Create `docs/auth/templates.md`
    """
    Document fragment template pattern.
    List all auth/ templates with context fields.
    Explain BEM CSS standards.
    """
  - [x] 16.4 Create `docs/auth/social-login.md`
    """
    Document social login setup.
    Include:
        - INSTALLED_APPS entries
        - SOCIALACCOUNT_PROVIDERS configuration
        - OAuth app creation steps (Google, Facebook)
        - Callback URL configuration
    """
  - [x] 16.5 Create `docs/auth/testing.md`
    """
    Document test patterns for auth system.
    Explain property-based tests, integration tests.
    """
  - [x] 16.6 Update `docs/_sidebar.md` with auth section
    """
    Add navigation links to new auth documentation.
    """
  - [x] 16.7 Document libs/packages usage
    """
    Create docs/libs/ documenting:
        - django-allauth usage
        - Hypothesis property-based testing
        - HTMX integration patterns
    """

---

## Checkpoints

- [x] 17. Checkpoint after Phase 2 (URL refactor)
    """
    Verify URL resolution before touching templates.
    Confirm reverse("plugins:login"), reverse("plugins:logout"), etc. work.
    Run python manage.py check.
    """

- [x] 18. Checkpoint after Phase 4 (Template consolidation)
    """
    Verify adapter + URL + templates work together.
    Manually test login, logout, register flows.
    Confirm HTMX fragment swapping works.
    """

- [x] 19. Final checkpoint
    """
    Run full test suite:
        pytest websites/tests/unit/test_auth_fragments.py
        pytest websites/tests/unit/test_auth_notifications.py
        pytest websites/tests/unit/test_app_structure.py
        pytest websites/tests/integration/test_auth_flows.py

    Confirm all non-optional tests pass.
    """

---

## Notes

- Tasks marked with `*` in sub-task numbers are optional for MVP.
- Each task references requirements for traceability.
- The adapter file is identical between sites; only import paths differ.
- `structa.cloud` has no `NewsletterSubscribeView` — task 3.2 omits it.
- Social buttons must use `<a href="...">`, never `hx-post` — OAuth redirects cannot be handled by HTMX.
- Property tests requiring Django test client (12.5-12.9) depend on tasks 1-8 being complete.
- **App ownership boundary:**
    - `plugins/accounts/`: auth adapter, allauth integration, registration, cart, checkout, account settings
    - `plugins/profile/`: profile display, edit, image, dashboard, courses, certifications, notes, messages, blog
- **Registration migration (task 1):** Moving a Django app requires updating INSTALLED_APPS, MIGRATION_MODULES, and URL includes. Run `python manage.py migrate --run-syncdb` after move.
- **Branding (task 10):** Only acceptable cross-site reference is in `websites/tests/` (shared test suite). All production code must be brand-clean.
