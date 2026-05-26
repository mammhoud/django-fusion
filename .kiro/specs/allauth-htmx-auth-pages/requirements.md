# Requirements Document

## Introduction

This feature fully integrates django-allauth with the existing HTMX + SSE fragment-based auth templates on ctc-research.com. It covers six areas:

1. **URL namespace refactor** — merge `pipelines_urls.py` into `urls.py`, rename the namespace from `pipelines` to `plugins`, and update all template references.
2. **Template consolidation** — delete `templates/account/*` entirely; all allauth views point directly at `templates/auth/` fragment templates. Templates use the fragment technique (no `{% extends %}` at the top level) — allauth's adapter overrides the template names to point at `auth/` fragments, and the skeleton is applied via a custom allauth adapter or middleware, not via template inheritance.
3. **Style audit & remediation** — bring all auth pages to the same `auth__*` / `form__*` BEM system; move inline styles to the CSS file.
4. **Missing auth pages** — create HTMX-consistent templates for every allauth page that currently has no custom template.
5. **Social login wiring** — fully wire Google and Facebook social login through allauth's `socialaccount` app (buttons uncommented, URLs wired, OAuth credentials documented).
6. **Logout** — immediate logout via `ACCOUNT_LOGOUT_ON_GET = True`; after logout the redirect page displays an SSE/HTMX notification confirming the user has been signed out.
7. **Email verification** — fix the `send-verification` URL reference and ensure the full verification flow works end-to-end.

---

## Glossary

- **Auth_System**: The combined django-allauth + custom view layer that handles authentication for ctc-research.com.
- **Fragment_Template**: A Django template that renders only a `<section class="fragment--form">` block, intended to be swapped into the page by HTMX.
- **Page_Template**: A Django template that extends `auth/skeleton.html` and renders the full split-layout auth page, including the fragment.
- **BEM_System**: The `auth__*` / `form__*` / `btn--*` CSS naming convention used across all auth pages.
- **HTMX_Request**: An HTTP request carrying the `HX-Request: true` header, indicating the response should be a fragment, not a full page.
- **SSE_Notification**: A server-sent event delivered to the `#sse-notifications` element for real-time feedback.
- **Namespace_plugins**: The Django URL namespace `plugins` that replaces the legacy `pipelines` namespace.
- **Social_Provider**: A third-party OAuth provider (Google, Facebook, etc.) configured through `django-allauth`'s `socialaccount` app.
- **allauth**: The `django-allauth` package that provides account management, email verification, password reset, and social login.
- **Skeleton**: The `auth/skeleton.html` base template that provides the split-layout chrome (welcome panel + form panel).

---

## Requirements

### Requirement 1: URL Namespace Refactor

**User Story:** As a developer, I want a single, consistently named URL namespace for all auth-related routes, so that templates and views use one predictable namespace instead of two overlapping ones.

#### Acceptance Criteria

1. THE Auth_System SHALL merge the contents of `plugins/pipelines_urls.py` into `plugins/urls.py`, resulting in a single file that declares both the allauth include and the custom auth routes.
2. THE Auth_System SHALL set `app_name = "plugins"` in the merged URL configuration, replacing `app_name = "pipelines"`.
3. WHEN the merged file is loaded, THE Auth_System SHALL expose the URL names `plugins:login`, `plugins:logout`, `plugins:register`, `plugins:password_forgot`, `plugins:privacy_modal`, and `plugins:subscribe_newsletter`.
4. THE Auth_System SHALL keep the mount point `path("auth/", include(..., namespace="plugins"))` so that existing URL paths (`/auth/login/`, `/auth/register/`, etc.) remain unchanged.
5. THE Auth_System SHALL delete `plugins/pipelines_urls.py` after its contents have been merged.
6. WHEN a template references `{% url 'pipelines:login' %}`, THE Auth_System SHALL replace that reference with `{% url 'plugins:login' %}` across all templates in `templates/auth/` and `templates/account/`.
7. THE Auth_System SHALL update every `hx-get`, `hx-post`, `hx-push-url`, `href`, and `action` attribute that resolves a `pipelines:*` URL tag to use `plugins:*` instead.

---

### Requirement 2: Template Consolidation — Fragment-Only `auth/` Templates, Delete `account/`

**User Story:** As a developer, I want allauth to render auth pages directly from `auth/` fragment templates without any `{% extends %}` inheritance, so that HTMX can swap fragments in-place and full-page loads are handled by a custom allauth adapter that wraps the fragment in the skeleton.

#### Acceptance Criteria

1. THE Auth_System SHALL delete all files under `templates/account/` (`login.html`, `signup.html`, `password_reset.html`, `email_confirm.html`) — no `account/` templates shall remain.
2. ALL templates under `templates/auth/` SHALL be pure fragment templates: they MUST NOT start with `{% extends %}`. The outermost element SHALL be `<section class="fragment--form">`.
3. THE Auth_System SHALL implement a custom allauth `DefaultAccountAdapter` subclass that overrides `get_login_redirect_url` and template name resolution so that allauth views render `auth/` fragment templates wrapped in `auth/skeleton.html` for full-page requests.
4. WHEN a request carries `HX-Request: true`, THE Auth_System SHALL return only the Fragment_Template content (`<section class="fragment--form">`) without the skeleton chrome.
5. WHEN a request does NOT carry `HX-Request: true`, THE Auth_System SHALL wrap the fragment in `auth/skeleton.html` (the split-layout base) before returning the response.
6. THE Auth_System SHALL map each allauth view to its `auth/` fragment template:
   - Login → `auth/login.html`
   - Signup → `auth/register.html`
   - Password reset request → `auth/forgot_page.html`
   - Password reset from key → `auth/reset_password.html`
   - Email confirmation → `auth/verification_link.html`
   - Password change → `auth/password_change.html`
   - Password set → `auth/password_set.html`
   - Email management → `auth/email_manage.html`
   - Reset done → `auth/password_reset_done.html`
   - Reset key done → `auth/password_reset_key_done.html`
   - Signup closed → `auth/signup_closed.html`
   - Social signup → `auth/social_signup.html`
   - Social connections → `auth/social_connections.html`

---

### Requirement 3: Style Audit and Remediation

**User Story:** As a front-end developer, I want all auth pages to use the same BEM CSS system and colour palette, so that the UI is visually consistent and maintainable.

#### Acceptance Criteria

1. THE Auth_System SHALL rewrite `auth/forgot_password.html` to use the `auth__*` / `form__*` BEM classes, replacing all occurrences of `card shadow-lg`, `form-group`, `btn-gradient`, and `feather-*` icon classes.
2. THE Auth_System SHALL move all CSS rules from the inline `<style>` block in `auth/reset_password.html` into the project's auth CSS file (or a dedicated `auth-reset-password.css` partial), leaving no `<style>` tags in the template.
3. THE Auth_System SHALL use the colour palette `#1E3A8A` (primary), `#10B981` (success), `#EF4444` (danger), `#F59E0B` (warning) consistently across all auth fragment templates.
4. THE Auth_System SHALL document, in a comment block at the top of each auth fragment template, which data fields are implemented and which are placeholders.
5. WHEN a style audit is run (manual review), THE Auth_System SHALL have zero auth pages that use CSS classes outside the `auth__*`, `form__*`, `btn--*`, and Bootstrap utility namespaces.

---

### Requirement 4: Missing Auth Pages

**User Story:** As a user, I want every allauth-provided auth flow to have a styled, HTMX-consistent page, so that I never land on an unstyled default allauth template.

#### Acceptance Criteria

1. THE Auth_System SHALL provide a Fragment_Template (no `{% extends %}`, outermost element `<section class="fragment--form">`) for each of the following currently missing allauth views:
   - `auth/password_change.html` (logged-in password change)
   - `auth/password_set.html` (social users setting a password for the first time)
   - `auth/email_manage.html` (manage email addresses)
   - `auth/password_reset_key_done.html` (password reset success confirmation)
   - `auth/password_reset_done.html` (password reset email sent confirmation)
   - `auth/signup_closed.html` (registration disabled page)
   - `auth/social_signup.html` (social signup completion form)
   - `auth/social_connections.html` (manage connected social accounts)
2. WHEN allauth renders any of the above views, THE Auth_System SHALL produce a response styled with the BEM_System and the split-layout Skeleton (via the adapter for full-page requests).
3. THE Auth_System SHALL wire `auth/reset_password.html` as the template for `account/password_reset_from_key` — this mapping must be set in the adapter and verified.
4. IF a user navigates to a missing-template URL before this requirement is implemented, THEN THE Auth_System SHALL display a styled error page rather than a Django debug traceback.

---

### Requirement 5: Logout — Immediate with SSE Notification

**User Story:** As a user, I want to be logged out immediately when I click "Sign Out", and see a confirmation notification on the redirect page, so that I know the action succeeded without a confirmation step.

#### Acceptance Criteria

1. THE Auth_System SHALL set `ACCOUNT_LOGOUT_ON_GET = True` in Django settings so that a GET request to the logout URL signs the user out immediately without a confirmation page.
2. AFTER logout, THE Auth_System SHALL redirect the user to the configured `ACCOUNT_LOGOUT_REDIRECT_URL` (e.g. the home page or login page).
3. THE redirect page SHALL display an SSE/HTMX notification (using the existing `#sse-notifications` element or Django messages framework rendered via HTMX) confirming "You have been signed out successfully."
4. THE notification SHALL use the `auth__message alert-success` styling pattern.
5. THE Auth_System SHALL NOT render `account/logout.html` — no logout confirmation template is needed.

---

### Requirement 6: Social Login Integration

**User Story:** As a user, I want to sign in or register using my Google or Facebook account, so that I can access the platform without creating a separate password.

#### Acceptance Criteria

1. THE Auth_System SHALL uncomment the social login button blocks in `auth/login.html` and `auth/register.html`.
2. THE social login buttons SHALL use standard `<a>` or `<form>` elements pointing to allauth's `socialaccount_login` URL (e.g. `{% url 'socialaccount_login' provider='google' %}`), NOT `hx-post` — OAuth redirects cannot be handled by HTMX.
3. WHEN a user clicks "Continue with Google", THE Auth_System SHALL redirect the user to Google's OAuth consent screen via allauth's `socialaccount_login` URL for the `google` provider.
4. WHEN a user clicks "Continue with Facebook", THE Auth_System SHALL redirect the user to Facebook's OAuth dialog via allauth's `socialaccount_login` URL for the `facebook` provider.
5. WHEN a social login completes successfully, THE Auth_System SHALL redirect the user to the `next` parameter URL if present, otherwise to the default login redirect URL.
6. IF a social login fails or is cancelled, THEN THE Auth_System SHALL display a styled error message using the `auth__message alert-danger` pattern on the login page.
7. THE Auth_System SHALL provide the `auth/social_signup.html` fragment template so that new social users can complete their profile before being admitted.
8. WHERE the `SOCIALACCOUNT_PROVIDERS` setting includes `google`, THE Auth_System SHALL render the Google button; WHERE it includes `facebook`, THE Auth_System SHALL render the Facebook button — buttons are conditionally rendered using `{% get_providers %}` from `allauth.socialaccount.templatetags`.
9. THE Auth_System SHALL document the required `SOCIALACCOUNT_PROVIDERS` settings and OAuth app credentials in a `SOCIAL_LOGIN_SETUP.md` file under `docs/ctc-research.com/`.

---

### Requirement 7: Email Verification Flow

**User Story:** As a new user, I want to receive and act on a verification email, so that my account is secured and I can access all platform features.

#### Acceptance Criteria

1. THE Auth_System SHALL replace the bare `{% url 'send-verification' %}` references in `auth/verification_link.html` with allauth's own `account_email_verification_sent` URL or the equivalent namespaced URL.
2. WHEN an authenticated user visits the email verification page, THE Auth_System SHALL display the user's email address and a "Send Verification Email" button that posts to the correct allauth resend-verification endpoint.
3. WHEN an unauthenticated user visits the email verification page, THE Auth_System SHALL display a "Resend Verification Email" button with a 60-second cooldown timer.
4. WHEN allauth sends a verification email and the user clicks the link, THE Auth_System SHALL render `auth/verification_link.html` (via the adapter) styled with the BEM_System.
5. IF the verification link has expired or is invalid, THEN THE Auth_System SHALL display a styled error message and offer a "Resend Verification Email" action.
6. THE Auth_System SHALL ensure the allauth `confirmation` context variable is available in the fragment so that the fragment can display the email address being confirmed.

---

### Requirement 8: HTMX Fragment Detection

**User Story:** As a developer, I want the auth views to correctly detect HTMX requests and return either a full page or a bare fragment, so that navigation works both with and without JavaScript.

#### Acceptance Criteria

1. WHEN a request carries `HX-Request: true`, THE Auth_System SHALL return only the Fragment_Template content wrapped in `<section class="fragment--form">`.
2. WHEN a request does not carry `HX-Request: true`, THE Auth_System SHALL wrap the fragment in `auth/skeleton.html` via the custom adapter before returning the response.
3. THE Auth_System SHALL preserve the `strategy` hidden input (`htmx` or `document`) and the `supports_sse` hidden input in all auth forms so that the server can choose the correct response strategy.
4. FOR ALL auth form submissions, parsing the `strategy` field then serialising it back SHALL produce the same value (round-trip property).
5. IF a form submission is invalid, THEN THE Auth_System SHALL return the fragment with inline validation errors, not a full-page redirect, when the request is an HTMX_Request.
