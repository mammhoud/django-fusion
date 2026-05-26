# Requirements Document

**Category Context: Bug Fixes**
- **Category**: Fixes
- **Scope**: Bug fixes, error corrections, problem resolutions, patch implementations
- **Related Specs**: alliance-website-docker-fix, fix-get-translation-template-tag, fix-wagtailsnippets-assets-email-enhancement
- **Common Patterns**: Docker fixes, template issues, email system problems, asset management
- **Avoid Duplicates**: Check existing fixes specs before creating new bug fix specs


## Introduction

This document specifies requirements for fixing multiple critical issues across the ctc-research and structa.cloud projects:

1. **Wagtail Snippet Namespace Error**: Fix the `KeyError: 'wagtailsnippets_handlers_authemailtemplate'` error that occurs when Wagtail tries to generate URLs for the `AuthEmailTemplate` snippet
2. **Structa.cloud Asset/URL Issues**: Fix bundle reading problems and bad gateway/media errors on structa.cloud related to asset URLs
3. **Email Management Enhancement**: Create a CSV export of emails from old specs and a command to send invitation emails
4. **Django-grep Integration**: Add email functionality to the django-grep package for reuse across projects
5. **Spec Organization**: Rename and reorganize existing specs for better clarity and organization

All fixes must work across both ctc-research and structa.cloud/core projects.

---

## Glossary

- **Namespace_Error**: The Django `NoReverseMatch` error with namespace `'wagtailsnippets_handlers_authemailtemplate'` that occurs in Wagtail admin
- **AuthEmailTemplate**: The Wagtail snippet model for email templates in the registration system
- **Asset_URLs**: URLs pointing to static files, media files, and webpack bundles
- **Bad_Gateway_Error**: HTTP 502 errors when assets cannot be loaded
- **Media_Error**: Issues with media file serving and URL generation
- **Email_CSV**: A CSV file containing email addresses extracted from old spec documents
- **Invitation_Email**: An email sent to users inviting them to create passwords and register
- **Django_grep**: The shared package `django_grep` used across both projects
- **Spec_Renaming**: The process of renaming existing spec directories to use enhancement naming without project names
- **Bundle_Reading**: The process of reading and serving webpack bundles and static assets

---

## Requirements

### Requirement 1: Fix Wagtail Snippet Namespace Error

**User Story:** As a site administrator, I want to access the AuthEmailTemplate Wagtail snippet without encountering namespace errors, so that I can manage email templates in both projects.

#### Acceptance Criteria

1. WHEN accessing the Wagtail admin in either ctc-research or structa.cloud, THE system SHALL NOT throw `KeyError: 'wagtailsnippets_handlers_authemailtemplate'`
2. THE `AuthEmailTemplate` snippet SHALL be properly registered with the correct namespace in both projects
3. THE URL reversal for `AuthEmailTemplate` SHALL work correctly in both projects
4. THE snippet registration in `wagtail_hooks.py` SHALL use the correct app label and model name
5. WHEN the snippet is accessed via Wagtail admin, THE system SHALL display the snippet list and edit pages without errors
6. THE fix SHALL work for both `ctc-research/apps/handlers/registration/` and `structa.cloud/core/apps/handlers/registration/`
7. AFTER the fix, THE property-based test for `AuthEmailTemplate` single-active invariant SHALL continue to pass

### Requirement 2: Fix Structa.cloud Asset and URL Issues

**User Story:** As a user, I want structa.cloud to load all assets (CSS, JS, images) correctly without bad gateway errors, so that the site functions properly.

#### Acceptance Criteria

1. WHEN accessing structa.cloud, THE system SHALL load all webpack bundles without 502 bad gateway errors
2. ALL static file URLs SHALL be correctly generated and accessible
3. ALL media file URLs SHALL be correctly generated and accessible
4. THE asset pipeline SHALL work correctly in both development and production environments
5. WHEN an asset cannot be found, THE system SHALL return an appropriate 404 error instead of 502 bad gateway
6. THE webpack configuration SHALL correctly resolve asset paths for structa.cloud
7. ALL CSS and JavaScript bundles SHALL be served with correct MIME types
8. THE fix SHALL not break asset serving on ctc-research

### Requirement 3: Create Email CSV Export from Old Specs

**User Story:** As a developer, I want to extract all email addresses mentioned in old spec documents and export them to a CSV file, so that I can use them for invitation campaigns.

#### Acceptance Criteria

1. THE system SHALL scan all `.kiro/specs/` directories for email addresses
2. Email addresses SHALL be extracted from all markdown files (requirements.md, design.md, tasks.md, bugfix.md)
3. THE extraction SHALL find email patterns like `user@example.com` in the text
4. Duplicate email addresses SHALL be removed from the CSV output
5. THE CSV file SHALL be created at `.kiro/specs/email-list.csv` with columns: `email`, `source_spec`, `source_file`
6. THE CSV SHALL include at minimum the email addresses from the `.env` files and spec documents
7. THE extraction SHALL work for both ctc-research and structa.cloud spec directories
8. WHEN new specs are added, THE CSV SHALL be updateable without losing existing data

### Requirement 4: Create Invitation Email Command

**User Story:** As an administrator, I want to send invitation emails to users from the CSV list, inviting them to create passwords and register with the system.

#### Acceptance Criteria

1. THE system SHALL provide a Django management command `send_invitation_emails`
2. THE command SHALL accept a `--csv-file` argument pointing to the email CSV (default: `.kiro/specs/email-list.csv`)
3. THE command SHALL read email addresses from the CSV and send invitation emails
4. EACH invitation email SHALL include:
   - A personalized greeting
   - A link to create a password
   - A link to register with the system
   - Instructions for using the template system
5. THE email SHALL use the existing `AuthEmailTemplate` system if an active template exists for type `invitation`
6. WHEN no active `AuthEmailTemplate` exists for invitations, THE command SHALL use a default template
7. THE command SHALL log each email sent with timestamp and outcome
8. THE command SHALL support dry-run mode with `--dry-run` flag to preview without sending
9. THE command SHALL respect rate limiting and send emails with appropriate delays
10. THE command SHALL work in both ctc-research and structa.cloud projects

### Requirement 5: Integrate Email Functionality into Django-grep

**User Story:** As a developer, I want the email CSV and invitation functionality to be part of the django-grep package, so that it can be reused across multiple projects.

#### Acceptance Criteria

1. THE django-grep package SHALL include a new module `django_grep.email_tools`
2. THE module SHALL provide:
   - `EmailExtractor` class for scanning files and extracting emails
   - `EmailCSVManager` class for managing the email CSV file
   - `InvitationEmailSender` class for sending invitation emails
3. THE functionality SHALL be accessible via management commands in any Django project using django-grep
4. THE integration SHALL not break existing django-grep functionality
5. THE email tools SHALL be configurable via Django settings
6. THE package SHALL include tests for the new email functionality
7. THE implementation SHALL follow the existing django-grep patterns and conventions

### Requirement 6: Rename and Reorganize Specs

**User Story:** As a developer, I want all spec directories to use consistent, descriptive names without project names, so that the spec organization is clearer and more maintainable.

#### Acceptance Criteria

1. ALL existing spec directories SHALL be renamed to use kebab-case enhancement names
2. Project names (ctc-, structa-, etc.) SHALL be removed from spec directory names
3. THE renaming SHALL maintain all existing spec file contents
4. A mapping document SHALL be created at `.kiro/specs/SPEC_RENAMING.md` showing old and new names
5. THE `.config.kiro` files in each spec SHALL be updated with new feature names
6. AFTER renaming, ALL spec references in documentation SHALL be updated
7. THE renaming SHALL not break any existing task execution or spec workflows
8. SIMILAR specs SHALL be grouped or merged where appropriate for better organization

### Requirement 7: Fix Bundle Reading Implementation

**User Story:** As a developer, I want the bundle reading system to handle asset URLs correctly, especially for structa.cloud, so that media errors are prevented.

#### Acceptance Criteria

1. THE webpack configuration SHALL correctly handle asset paths for both projects
2. THE static file serving SHALL work correctly in Docker containers
3. THE media file serving SHALL work correctly in Docker containers
4. WHEN assets are missing, THE system SHALL log clear error messages instead of throwing 502 errors
5. THE asset URL generation SHALL work correctly with Traefik reverse proxy
6. ALL asset-related middleware SHALL be properly configured for both projects
7. THE fix SHALL handle both development (hot-reload) and production (compiled) asset modes
8. AFTER the fix, the structa.cloud health check SHALL pass asset validation

### Requirement 8: Backward Compatibility and Testing

**User Story:** As a developer, I want all fixes to be backward compatible and thoroughly tested, so that existing functionality continues to work.

#### Acceptance Criteria

1. ALL fixes SHALL maintain backward compatibility with existing code
2. EXISTING tests for `AuthEmailTemplate` and email functionality SHALL continue to pass
3. NEW tests SHALL be added for the email CSV extraction and invitation sending
4. PROPERTY-based tests SHALL be created for email extraction correctness
5. THE fixes SHALL not break any existing management commands
6. BOTH ctc-research and structa.cloud SHALL start without errors after all fixes
7. ALL health checks SHALL pass after the fixes are applied
8. THE Wagtail admin SHALL be fully functional in both projects after fixes

### Requirement 9: Documentation and Deployment

**User Story:** As a system administrator, I want clear documentation for all fixes and a smooth deployment process, so that I can maintain the systems effectively.

#### Acceptance Criteria

1. COMPREHENSIVE documentation SHALL be created for all fixes at `.kiro/specs/fix-wagtailsnippets-assets-email-enhancement/DEPLOYMENT.md`
2. THE documentation SHALL include:
   - Steps to apply each fix
   - Configuration changes required
   - Testing procedures
   - Rollback procedures
3. ALL configuration changes SHALL be documented in the spec files
4. THE deployment SHALL be scriptable and repeatable
5. ROLLBACK procedures SHALL be tested and documented
6. THE fixes SHALL be applied to both projects in a coordinated manner
7. AFTER deployment, a verification checklist SHALL be completed
8. ALL changes SHALL be committed with clear commit messages referencing this spec
