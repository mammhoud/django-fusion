# Requirements Document

**Category Context: Authentication & Authorization**
- **Category**: Auth
- **Scope**: Authentication systems, user management, permissions, security
- **Related Specs**: auth-allauth-enhancement, ctc-research-server-and-auth-fix, ctc-structa-admin-auth-integration
- **Common Patterns**: Allauth integration, Django authentication, OAuth, JWT tokens, permission systems
- **Avoid Duplicates**: Check existing auth specs before creating new authentication features


## Introduction

This document specifies requirements for enhancing the authentication system of ctc-research.com by integrating django-allauth into the existing HTMX-based registration and login workflow. The enhancement preserves the current PageHandler fragment mechanism, auth skeleton template, and email service while adding allauth-backed views, Wagtail snippet-managed email templates, a "register success" email on sign-in, a fixed notification system on form submission, and a light-mode default for the auth skeleton.

The primary objectives are:
1. Wrap allauth login and signup views inside the existing PageHandler/fragment pattern
2. Manage registration email templates via Wagtail snippets
3. Send a confirmation email on registration and a "register success" email on first sign-in
4. Fix the HX-Trigger notification header so it fires correctly after form submission
5. Set the auth skeleton default theme to light mode
6. Enhance the token generator to bridge allauth's key system with the existing HMAC-SHA256 mechanism

## Glossary

- **Allauth**: The django-allauth library providing pluggable authentication, registration, and account management
- **Auth_Skeleton**: The base template at `assets/templates/layout/auth/skeleton.html` shared by all auth pages
- **PageHandler**: Base view class from `django_grep.comp.site` providing HTMX-aware fragment vs full-page rendering
- **Fragment**: A partial HTML response returned when the request carries an `HX-Request` header
- **HTMX**: JavaScript library for partial page updates via HTTP headers
- **Registration_System**: The existing email-based two-step user registration workflow
- **Allauth_Adapter**: A custom `DefaultAccountAdapter` subclass that hooks allauth events into the existing email service
- **Token_Generator**: The existing `RegistrationTokenGenerator` using HMAC-SHA256 and Django signing
- **Allauth_Token**: The key allauth generates internally for email confirmation (`EmailConfirmationHMAC`)
- **Email_Service**: The existing multi-sender SMTP email delivery service with failover in `emails.py`
- **Email_Template_Snippet**: A Wagtail snippet model that stores editable subject and body for each transactional email
- **Notification_System**: Client-side toast notifications triggered via the `HX-Trigger: showNotification` header
- **HX_Trigger**: The HTMX response header used to fire client-side events after a request completes
- **Rate_Limiter**: IP-based request throttling using Django cache
- **Wagtail_Snippet**: A Wagtail-managed model editable in the Wagtail admin without a full page
- **Light_Theme**: The CSS theme variant where the auth page background and form use light colours
- **Sign_In_Success_Email**: A transactional email sent to the user after their first successful sign-in

## Requirements

### Requirement 1: Allauth Integration with PageHandler Fragment Rendering

**User Story:** As a developer, I want allauth login and signup views to use the PageHandler base class, so that HTMX fragment rendering and the existing auth skeleton work without duplication.

#### Acceptance Criteria

1. THE Registration_System SHALL wrap allauth login and signup views inside subclasses of PageHandler
2. WHEN a request carries an `HX-Request` header, THE Registration_System SHALL return only the form fragment using the existing fragment templates
3. WHEN a request does not carry an `HX-Request` header, THE Registration_System SHALL return the full page using the Auth_Skeleton
4. THE Registration_System SHALL use `assets/templates/layout/auth/skeleton.html` as the base template for all auth pages
5. THE Registration_System SHALL use the existing fragment templates in `apps/templates/registration/fragments/` for partial responses
6. WHEN allauth redirects after login, THE Registration_System SHALL honour the `next` parameter or fall back to the dashboard URL
7. THE Registration_System SHALL preserve all existing URL names (`handlers:register-account`, `handlers:create-password`) so no existing links break

### Requirement 2: Light Theme Default for Auth Skeleton

**User Story:** As a user, I want the login and register pages to load in light mode by default, so that the interface is readable without requiring a theme toggle.

#### Acceptance Criteria

1. THE Auth_Skeleton SHALL apply the light theme CSS class or data attribute by default on page load
2. WHEN no user preference is stored, THE Auth_Skeleton SHALL render with the light colour scheme
3. THE Auth_Skeleton SHALL NOT apply a dark theme class unless the user has explicitly selected dark mode
4. WHEN the light theme is active, THE Auth_Skeleton SHALL set `data-theme="light"` on the root element

### Requirement 3: Registration Email Confirmation Flow

**User Story:** As a new user, I want to receive a confirmation email after I submit the registration form, so that I can verify my address and set my password.

#### Acceptance Criteria

1. WHEN a user submits a valid registration form, THE Email_Service SHALL send a confirmation email to the provided address within 30 seconds
2. THE Email_Service SHALL use the confirmation email subject and body stored in the Email_Template_Snippet if one exists, falling back to the default template
3. THE confirmation email SHALL contain a secure token link that allows the user to set their password
4. THE Token_Generator SHALL generate a token that is valid for 24 min and is invalidated once the password is set
5. WHEN the confirmation link is clicked, THE Registration_System SHALL validate the token before displaying the password creation form
6. IF the token has expired, THEN THE Registration_System SHALL display an "expired link" error and offer to resend the confirmation
7. IF the token has already been used, THEN THE Registration_System SHALL display an "already activated" message and link to the login page
8. THE Email_Service SHALL attempt delivery via the primary SMTP sender, then the secondary sender, then the Django default backend
9. THE Email_Service SHALL log every delivery attempt with sender identity, recipient, and outcome

### Requirement 4: Sign-In Success Email

**User Story:** As a registered user, I want to receive a "registration success" email after I sign in for the first time, so that I have confirmation my account is active.

#### Acceptance Criteria

1. WHEN a user signs in successfully for the first time after activating their account, THE Email_Service SHALL send a Sign_In_Success_Email to the user's address
2. THE Sign_In_Success_Email SHALL use the subject and body stored in the Email_Template_Snippet for the `signin_success` template type if one exists
3. THE Email_Service SHALL send the Sign_In_Success_Email asynchronously so it does not delay the login response
4. THE Email_Service SHALL log the Sign_In_Success_Email delivery attempt with timestamp and outcome
5. IF the Sign_In_Success_Email delivery fails, THEN THE Email_Service SHALL log the error and continue without blocking the user session

### Requirement 5: Wagtail Snippet for Email Template Management

**User Story:** As a site administrator, I want to manage registration and sign-in email subjects and bodies from the Wagtail admin, so that I can update messaging without a code deployment.

#### Acceptance Criteria

1. THE Wagtail_Snippet SHALL provide a model named `AuthEmailTemplate` with fields: `template_type` (choice), `subject` (CharField), `body_html` (RichTextField), `body_text` (TextField), `is_active` (BooleanField)
2. THE `template_type` field SHALL support at least the values: `registration_confirmation`, `signin_success`
3. THE Email_Service SHALL query the active Email_Template_Snippet for the matching `template_type` before rendering the default file template
4. WHEN no active snippet exists for a given type, THE Email_Service SHALL fall back to the file-based template without error
5. THE Wagtail_Snippet SHALL be registered in the Wagtail admin under a group labelled "Auth & Email"
6. THE Wagtail_Snippet SHALL enforce that only one active snippet exists per `template_type` at a time
7. WHEN an admin saves a new active snippet for a type, THE Wagtail_Snippet SHALL deactivate any previously active snippet of the same type

### Requirement 6: Notification Fix on Form Submission

**User Story:** As a user, I want to see a success or error notification immediately after submitting the login or register form, so that I know whether my action succeeded.

#### Acceptance Criteria

1. WHEN a registration form submission succeeds, THE Notification_System SHALL display a success notification with the message "Account created! Check your email."
2. WHEN a login form submission succeeds, THE Notification_System SHALL display a success notification with the message "Welcome back!"
3. WHEN a form submission fails validation, THE Notification_System SHALL display an error notification describing the first validation error
4. WHEN a rate limit is exceeded, THE Notification_System SHALL display an error notification with the message "Too many attempts. Please try again later."
5. THE Registration_System SHALL set the `HX-Trigger` response header with a valid JSON payload of the form `{"showNotification": {"message": "...", "type": "..."}}` on every HTMX form submission response
6. THE `HX-Trigger` header SHALL be present on both success and error responses so the notification bundle fires in all cases
7. WHEN the form is submitted via a non-HTMX request, THE Registration_System SHALL display the notification inline in the rendered page without relying on the `HX-Trigger` header
8. THE Notification_System SHALL display the notification at the `/notifications` endpoint target element after the HTMX swap completes

### Requirement 7: Token Mechanism Enhancement for Allauth Compatibility

**User Story:** As a developer, I want the existing token generator to interoperate with allauth's email confirmation key system, so that both mechanisms can coexist without duplication.

#### Acceptance Criteria

1. THE Token_Generator SHALL remain the authoritative token source for the password-creation flow
2. THE Allauth_Adapter SHALL override `send_confirmation_mail` to delegate to the existing Email_Service instead of allauth's default mailer
3. THE Allauth_Adapter SHALL convert the allauth `EmailConfirmationHMAC` key into a payload compatible with the Token_Generator's `validate_token` interface
4. THE Token_Generator SHALL continue to use HMAC-SHA256 signing via Django's `signing.dumps` / `signing.loads` with the existing salt `ctc-registration-password-create`
5. THE Token_Generator SHALL continue to invalidate tokens when the user's password or `is_active` state changes
6. WHEN allauth generates a confirmation key, THE Allauth_Adapter SHALL store the allauth key alongside the Token_Generator token so either can be used to validate the link
7. THE Token_Generator SHALL expose a `make_allauth_compatible_token(user, allauth_key)` method that embeds the allauth key in the signed payload
8. FOR ALL valid tokens produced by `make_allauth_compatible_token`, calling `validate_token` SHALL return a payload containing both `uid` and `allauth_key` fields (round-trip property)

### Requirement 8: Allauth Adapter and Signal Integration

**User Story:** As a developer, I want allauth lifecycle events (signup, login, email confirmation) to trigger the existing email service and notification logic, so that behaviour is consistent regardless of which auth path is used.

#### Acceptance Criteria

1. THE Allauth_Adapter SHALL subclass `allauth.account.adapter.DefaultAccountAdapter`
2. WHEN allauth confirms a user's email, THE Allauth_Adapter SHALL call `send_registration_email` from the existing Email_Service
3. WHEN allauth logs a user in, THE Allauth_Adapter SHALL emit a Django signal `user_signed_in` that the Sign_In_Success_Email handler listens to
4. THE Allauth_Adapter SHALL be registered in Django settings as `ACCOUNT_ADAPTER = "apps.handlers.registration.adapter.RegistrationAdapter"`
5. WHEN allauth raises a validation error during signup, THE Allauth_Adapter SHALL format the error as a `showNotification` HX-Trigger payload
6. THE Allauth_Adapter SHALL preserve the existing rate limiting logic by calling `rate_limit_check` and `rate_limit_increment` from `views.py`

### Requirement 9: Backward Compatibility and Rollback Safety

**User Story:** As a developer, I want the allauth enhancement to be additive, so that existing user accounts and URL patterns continue to work if the feature is rolled back.

#### Acceptance Criteria

1. THE Registration_System SHALL not modify the existing `User` model schema
2. THE Registration_System SHALL not delete or rename existing URL patterns
3. THE Registration_System SHALL not remove existing template files
4. WHEN allauth is disabled or removed, THE Registration_System SHALL fall back to the existing custom views without data loss
5. THE Registration_System SHALL use database transactions for all multi-step operations involving user creation and email sending
6. WHEN a transaction fails, THE Registration_System SHALL roll back all changes and return an error response
7. THE Registration_System SHALL maintain all existing property-based tests passing after the enhancement is applied

### Requirement 10: Security and Rate Limiting

**User Story:** As a security administrator, I want the allauth-enhanced auth system to maintain the same rate limiting and brute-force protections as the existing system.

#### Acceptance Criteria

1. THE Rate_Limiter SHALL limit registration attempts to 5 per IP per hour using the existing `reg_rate_limit:{ip}` cache key
2. THE Rate_Limiter SHALL limit password creation attempts to 10 per IP per hour using the existing `pw_create_bf:{ip}` cache key
3. WHEN a rate limit is exceeded, THE Registration_System SHALL return HTTP 429 and set the `HX-Trigger` header with an error notification
4. THE Registration_System SHALL include a CSRF token in every form rendered by allauth views
5. WHEN allauth processes a login attempt with an invalid password, THE Rate_Limiter SHALL increment the brute-force counter for that IP
6. THE Token_Generator SHALL use constant-time comparison when validating token signatures to prevent timing attacks
