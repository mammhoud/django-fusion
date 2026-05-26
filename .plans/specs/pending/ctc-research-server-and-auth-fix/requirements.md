# Requirements Document

**Category Context: Authentication & Authorization**
- **Category**: Auth
- **Scope**: Authentication systems, user management, permissions, security
- **Related Specs**: auth-allauth-enhancement, ctc-research-server-and-auth-fix, ctc-structa-admin-auth-integration
- **Common Patterns**: Allauth integration, Django authentication, OAuth, JWT tokens, permission systems
- **Avoid Duplicates**: Check existing auth specs before creating new authentication features


## Introduction

This document specifies requirements for fixing critical server issues on ctc-research.com and implementing a complete, production-ready authentication workflow. The system uses Django with HTMX-based partial rendering, an existing PageHandler architecture, and email-based registration with two-step activation.

The primary objectives are:
1. Diagnose and fix server downtime issues
2. Ensure the authentication system works correctly with HTMX
3. Implement secure email-based registration with password creation
4. Integrate notification system for user feedback
5. Harden security configuration

## Glossary

- **Server**: The Django application running ctc-research.com
- **PageHandler**: Base view class from django_grep.comp.site for HTMX-aware rendering
- **FragmentBaseView**: HTMX-specific view for partial page updates
- **HTMX**: JavaScript library for partial page updates via HTTP headers
- **Registration_System**: Email-based two-step user registration workflow
- **Notification_System**: Client-side notification display triggered via HTMX headers
- **Auth_Component**: Reusable authentication UI components and templates
- **Token_Generator**: Secure, time-limited token system for email confirmation
- **Rate_Limiter**: IP-based request throttling system using Django cache
- **Email_Service**: Multi-sender SMTP email delivery with failover
- **Group_Manager**: Django groups system for role-based permissions
- **Bundle**: JavaScript asset bundle for client-side functionality
- **Configuration_System**: Modular Django settings with environment overrides
- **SECRET_KEY**: Django cryptographic signing key
- **CSRF_Token**: Cross-site request forgery protection token
- **Activation_Link**: Time-limited URL for account activation and password creation

## Requirements

### Requirement 1: Server Diagnostic and Recovery

**User Story:** As a system administrator, I want to diagnose why ctc-research.com is down, so that I can restore service quickly and safely.

#### Acceptance Criteria

1. WHEN the Server is started, THE Server SHALL log all startup errors with full stack traces
2. THE Server SHALL validate all URL routing configurations before accepting requests
3. THE Server SHALL check for template inheritance conflicts during startup
4. THE Server SHALL detect duplicate settings definitions across configuration files
5. THE Server SHALL verify middleware configuration compatibility
6. THE Server SHALL validate static file and bundle configurations
7. IF a configuration conflict is detected, THEN THE Server SHALL log the conflict details and fail to start
8. THE Server SHALL provide a health check endpoint that returns HTTP 200 when operational
9. WHEN HTMX partial rendering fails, THE Server SHALL log the template name and error context
10. THE Server SHALL run without errors before any new features are implemented

### Requirement 2: Architecture Validation

**User Story:** As a developer, I want to confirm the existing architecture patterns are being used correctly, so that new code integrates properly.

#### Acceptance Criteria

1. THE Registration_System SHALL use PageHandler or FragmentBaseView as base classes
2. THE Registration_System SHALL implement HTMX fragment/document rendering strategy
3. THE Registration_System SHALL use existing Auth_Component templates
4. THE Registration_System SHALL use the existing notification Bundle
5. THE Registration_System SHALL NOT create new JavaScript bundles for authentication
6. WHEN a view renders a fragment, THE Server SHALL set appropriate HTMX response headers
7. THE Server SHALL validate that hx-trigger events match Django response headers
8. THE Server SHALL use the existing HTMX authentication templates without modification

### Requirement 3: HTMX-Based Registration Flow

**User Story:** As a user, I want to register via HTMX modal or fragment, so that I get inline feedback without full page reloads.

#### Acceptance Criteria

1. WHEN a user submits the registration form via HTMX, THE Registration_System SHALL process the request inline
2. WHEN registration succeeds, THE Registration_System SHALL return an HTMX fragment response
3. WHEN registration succeeds, THE Registration_System SHALL trigger a notification via HX-Trigger header
4. WHEN registration succeeds, THE Registration_System SHALL redirect to the home page after notification
5. THE Registration_System SHALL use rollback-safe modifications only
6. THE Registration_System SHALL maintain compatibility with non-HTMX requests
7. WHEN registration fails validation, THE Registration_System SHALL return the form fragment with errors
8. THE Registration_System SHALL include CSRF_Token in all form submissions
9. THE Notification_System SHALL display success message: "User created successfully"
10. THE Registration_System SHALL use the existing notification Bundle for display

### Requirement 4: Registration Logic Conditions

**User Story:** As a system, I want to handle different registration scenarios, so that users can register normally or via invitation.

#### Acceptance Criteria

1. WHEN a user registers via the normal registration page, THE Registration_System SHALL allow password entry directly in the form
2. WHEN a user registers via the normal registration page, THE Email_Service SHALL send an activation email
3. WHEN a user registers via the normal registration page, THE Registration_System SHALL create an inactive account
4. WHEN a user registers via invitation link, THE Registration_System SHALL create an inactive user without password
5. WHEN a user registers via invitation link, THE Email_Service SHALL send a confirmation link
6. WHEN a user registers via invitation link, THE Email_Service SHALL send a secure password creation link
7. WHEN a user registers via management command, THE Registration_System SHALL create an inactive user
8. WHEN a user registers via management command, THE Email_Service SHALL send activation and password creation emails
9. THE Email_Service SHALL use existing Auth_Component email templates
10. THE Email_Service SHALL maintain existing email branding and styling

### Requirement 5: Email and Activation System

**User Story:** As a user, I want to receive a confirmation email with a secure link, so that I can activate my account and create my password.

#### Acceptance Criteria

1. WHEN a user completes registration, THE Email_Service SHALL send an activation email within 30 seconds
2. THE Token_Generator SHALL create secure, time-limited tokens valid for 24 min
3. THE Token_Generator SHALL use HMAC-SHA256 for cryptographic signing
4. THE Token_Generator SHALL encode user ID and timestamp in tokens
5. WHEN a token expires, THE Server SHALL display an "expired link" error message
6. WHEN a user clicks the Activation_Link, THE Server SHALL validate the token before displaying the password form
7. THE Email_Service SHALL log all email delivery attempts with timestamps
8. THE Email_Service SHALL implement failover between multiple SMTP senders
9. WHEN email delivery fails, THE Server SHALL log the error and try the next sender
10. WHEN a user confirms their email, THE Registration_System SHALL activate the account
11. THE Email_Service SHALL use existing Auth_Component email templates
12. THE Email_Service SHALL include unsubscribe links in all emails

### Requirement 6: Group Management System

**User Story:** As a system administrator, I want to ensure required user groups exist, so that users can be assigned appropriate permissions.

#### Acceptance Criteria

1. THE Group_Manager SHALL ensure "Instructor" group exists on startup
2. THE Group_Manager SHALL ensure "Content Manager" group exists on startup
3. WHEN a group is missing, THE Group_Manager SHALL create it automatically
4. WHEN a group is created, THE Server SHALL log the group name and timestamp
5. WHEN a user registers normally, THE Registration_System SHALL assign them to "Content Manager" group
6. WHEN a user registers via invitation, THE Registration_System SHALL assign groups based on invitation parameters
7. THE Group_Manager SHALL validate group assignments before saving users
8. THE Group_Manager SHALL handle concurrent group creation safely

### Requirement 7: Notification System Integration

**User Story:** As a user, I want to see success notifications after registration, so that I know my action completed successfully.

#### Acceptance Criteria

1. THE Notification_System SHALL load the existing notification Bundle correctly
2. THE Notification_System SHALL display notifications triggered by HX-Trigger headers
3. WHEN registration succeeds, THE Server SHALL set HX-Trigger header with notification data
4. THE Notification_System SHALL display the message "User created successfully" on success
5. THE Notification_System SHALL auto-dismiss notifications after 5 seconds
6. THE Notification_System SHALL support error, success, warning, and info notification types
7. WHEN multiple notifications are triggered, THE Notification_System SHALL queue them
8. THE Notification_System SHALL be accessible via keyboard navigation
9. THE Notification_System SHALL announce notifications to screen readers
10. WHEN a notification is dismissed, THE Notification_System SHALL remove it from the DOM

### Requirement 8: Post-Registration Redirect

**User Story:** As a user, I want to be redirected to the home page after successful registration, so that I can start using the application.

#### Acceptance Criteria

1. WHEN registration completes successfully, THE Server SHALL redirect to the home page
2. WHEN the request is HTMX-based, THE Server SHALL use HX-Redirect header for redirection
3. WHEN the request is non-HTMX, THE Server SHALL use HTTP 302 redirect
4. THE Server SHALL preserve notification state across redirects
5. THE Server SHALL include CSRF_Token in redirect responses
6. WHEN a user is already authenticated, THE Registration_System SHALL redirect to dashboard
7. THE Server SHALL log all redirects with source and destination URLs

### Requirement 9: Security Hardening

**User Story:** As a security administrator, I want to ensure the system uses secure configuration, so that user data is protected.

#### Acceptance Criteria

1. THE Configuration_System SHALL generate a new SECRET_KEY if the current key is a default value
2. THE Configuration_System SHALL validate that SECRET_KEY is at least 50 characters long
3. THE Configuration_System SHALL remove duplicate settings between YAML and .env files
4. THE Configuration_System SHALL document environment variable precedence clearly
5. THE Configuration_System SHALL validate that CSRF protection works with HTMX requests
6. WHEN in production, THE Server SHALL enforce HTTPS for all requests
7. WHEN in production, THE Server SHALL set Secure flag on all cookies
8. WHEN in production, THE Server SHALL set HSTS headers with max-age of 31536000 seconds
9. THE Rate_Limiter SHALL limit registration attempts to 5 per hour per IP address
10. THE Rate_Limiter SHALL use Django cache backend for rate limit tracking
11. THE Server SHALL validate all user input against XSS attacks
12. THE Server SHALL sanitize all user-provided data before storage

### Requirement 10: Configuration Conflict Resolution

**User Story:** As a developer, I want to eliminate configuration conflicts, so that the system behaves predictably.

#### Acceptance Criteria

1. THE Configuration_System SHALL identify duplicate SECRET_KEY definitions
2. THE Configuration_System SHALL identify duplicate database configuration
3. THE Configuration_System SHALL identify duplicate email configuration
4. THE Configuration_System SHALL identify duplicate ALLOWED_HOSTS settings
5. WHEN duplicate configurations are found, THE Configuration_System SHALL log warnings
6. THE Configuration_System SHALL document which configuration source takes precedence
7. THE Configuration_System SHALL validate that .env values override YAML defaults
8. THE Configuration_System SHALL provide a configuration validation command
9. THE Configuration_System SHALL export effective configuration for debugging

### Requirement 11: Final Validation Checklist

**User Story:** As a quality assurance engineer, I want to validate all functionality works correctly, so that the system is production-ready.

#### Acceptance Criteria

1. THE Server SHALL start without errors or warnings
2. WHEN accessing ctc-research.com, THE Server SHALL return HTTP 200
3. WHEN a user registers via the normal page, THE Registration_System SHALL create an account
4. WHEN a user registers via HTMX fragment, THE Registration_System SHALL process inline
5. WHEN a user registers via invitation link, THE Registration_System SHALL send password creation email
6. WHEN a user registers via management command, THE Registration_System SHALL create inactive account
7. WHEN a user clicks email confirmation link, THE Server SHALL display password creation form
8. WHEN a user creates a password, THE Registration_System SHALL activate the account
9. WHEN registration succeeds, THE Notification_System SHALL display success message
10. WHEN registration succeeds, THE Server SHALL redirect to home page
11. WHEN a user is assigned to a group, THE Group_Manager SHALL persist the assignment
12. THE Configuration_System SHALL have no duplicate settings conflicts

### Requirement 12: Password Creation Security

**User Story:** As a user, I want to create a secure password, so that my account is protected.

#### Acceptance Criteria

1. THE Registration_System SHALL require passwords to be at least 8 characters long
2. THE Registration_System SHALL require at least 1 uppercase letter in passwords
3. THE Registration_System SHALL require at least 1 lowercase letter in passwords
4. THE Registration_System SHALL require at least 1 number in passwords
5. THE Registration_System SHALL require at least 1 special character in passwords
6. WHEN a password fails validation, THE Registration_System SHALL display specific error messages
7. THE Registration_System SHALL validate that password and confirmation match
8. THE Registration_System SHALL hash passwords using PBKDF2 before storage
9. THE Registration_System SHALL never log or display passwords in plain text
10. THE Rate_Limiter SHALL limit password creation attempts to 10 per hour per IP

### Requirement 13: Email Template System

**User Story:** As a user, I want to receive professional, branded emails, so that I trust the registration process.

#### Acceptance Criteria

1. THE Email_Service SHALL use HTML email templates with inline CSS
2. THE Email_Service SHALL include a plain text fallback for all emails
3. THE Email_Service SHALL include the site logo in email headers
4. THE Email_Service SHALL include the user's name in email greetings
5. THE Email_Service SHALL include a clear call-to-action button
6. THE Email_Service SHALL include expiration time in activation emails
7. THE Email_Service SHALL include support contact information in email footers
8. THE Email_Service SHALL include a fallback URL if the button doesn't work
9. THE Email_Service SHALL be responsive and render correctly on mobile devices
10. THE Email_Service SHALL pass email accessibility validation

### Requirement 14: Error Handling and Logging

**User Story:** As a system administrator, I want comprehensive error logging, so that I can diagnose issues quickly.

#### Acceptance Criteria

1. THE Server SHALL log all registration attempts with timestamp and IP address
2. THE Server SHALL log all email delivery attempts with success/failure status
3. THE Server SHALL log all token validation attempts with outcome
4. THE Server SHALL log all rate limit violations with IP address
5. WHEN an unexpected error occurs, THE Server SHALL log full stack trace
6. THE Server SHALL log all group assignments with user and group names
7. THE Server SHALL log all password creation attempts with outcome
8. THE Server SHALL log all configuration validation errors
9. THE Server SHALL rotate log files when they exceed 10MB
10. THE Server SHALL retain log files for at least 30 days

### Requirement 15: Rollback Safety

**User Story:** As a developer, I want to ensure changes can be rolled back safely, so that we can recover from issues quickly.

#### Acceptance Criteria

1. THE Registration_System SHALL maintain backward compatibility with existing user accounts
2. THE Registration_System SHALL not modify existing database schema without migrations
3. THE Registration_System SHALL not delete existing templates or views
4. THE Configuration_System SHALL preserve existing settings during updates
5. WHEN a rollback is needed, THE Server SHALL restore previous functionality without data loss
6. THE Registration_System SHALL use database transactions for all multi-step operations
7. WHEN a transaction fails, THE Server SHALL rollback all changes automatically
8. THE Server SHALL maintain audit logs of all configuration changes

### Requirement 16: Profile Creation Integration

**User Story:** As a user, I want a profile created automatically when I register, so that I can use profile features immediately.

#### Acceptance Criteria

1. WHEN a user activates their account, THE Registration_System SHALL create a Person profile
2. THE Registration_System SHALL populate profile with user's first name, last name, and email
3. THE Registration_System SHALL set profile status to "ACTIVE"
4. THE Registration_System SHALL set is_registered flag to true
5. THE Registration_System SHALL set registration_date to current timestamp
6. WHEN profile creation fails, THE Server SHALL log a warning but not fail registration
7. THE Registration_System SHALL handle existing profiles gracefully without duplication

### Requirement 17: Round-Trip Email Testing

**User Story:** As a quality assurance engineer, I want to verify email delivery works end-to-end, so that users receive their activation emails.

#### Acceptance Criteria

1. FOR ALL valid registration requests, THE Email_Service SHALL deliver activation emails within 30 seconds
2. FOR ALL delivered emails, THE Email_Service SHALL log delivery confirmation
3. FOR ALL failed email deliveries, THE Email_Service SHALL try the failover sender
4. FOR ALL email templates, rendering then sending then receiving SHALL produce readable content
5. THE Email_Service SHALL validate SMTP credentials before attempting delivery
6. THE Email_Service SHALL handle temporary SMTP failures with retry logic
7. THE Email_Service SHALL timeout SMTP connections after 30 seconds

### Requirement 18: HTMX Response Header Validation

**User Story:** As a developer, I want to ensure HTMX headers are set correctly, so that client-side behavior works as expected.

#### Acceptance Criteria

1. WHEN returning a fragment response, THE Server SHALL set HX-Trigger header with notification data
2. WHEN redirecting via HTMX, THE Server SHALL set HX-Redirect header with target URL
3. WHEN swapping content, THE Server SHALL set HX-Retarget header if target changes
4. WHEN updating multiple elements, THE Server SHALL use HX-Trigger-After-Swap for timing control
5. THE Server SHALL validate that HX-Trigger values are valid JSON
6. THE Server SHALL include CSRF_Token in all HTMX responses
7. THE Server SHALL set appropriate Content-Type headers for fragment responses

### Requirement 19: Rate Limiting Implementation

**User Story:** As a security administrator, I want to prevent abuse of the registration system, so that the service remains available for legitimate users.

#### Acceptance Criteria

1. THE Rate_Limiter SHALL track registration attempts by IP address
2. THE Rate_Limiter SHALL use a sliding window of 1 hour for rate limiting
3. THE Rate_Limiter SHALL allow maximum 5 registration attempts per IP per hour
4. WHEN rate limit is exceeded, THE Server SHALL return HTTP 429 status
5. WHEN rate limit is exceeded, THE Server SHALL display user-friendly error message
6. THE Rate_Limiter SHALL use Django cache backend for counter storage
7. THE Rate_Limiter SHALL handle cache failures gracefully without blocking requests
8. THE Rate_Limiter SHALL reset counters after the time window expires
9. THE Rate_Limiter SHALL log all rate limit violations with IP and timestamp

### Requirement 20: Token Security and Validation

**User Story:** As a security engineer, I want to ensure activation tokens are secure and single-use, so that accounts cannot be hijacked.

#### Acceptance Criteria

1. THE Token_Generator SHALL use Django's signing framework for token generation
2. THE Token_Generator SHALL include user ID in token payload
3. THE Token_Generator SHALL include timestamp in token payload
4. THE Token_Generator SHALL include user state hash in token payload
5. WHEN a user's password is set, THE Token_Generator SHALL invalidate all previous tokens
6. WHEN a token is used, THE Server SHALL verify the user state hash matches current state
7. THE Token_Generator SHALL use constant-time comparison for token validation
8. THE Token_Generator SHALL prevent timing attacks on token validation
9. WHEN a token is invalid, THE Server SHALL not reveal why it's invalid
10. THE Token_Generator SHALL use a unique salt for registration tokens

