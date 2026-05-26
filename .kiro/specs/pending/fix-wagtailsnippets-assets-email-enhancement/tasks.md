# Implementation Tasks

**Category Context: Bug Fixes**
- **Category**: Fixes
- **Scope**: Bug fixes, error corrections, problem resolutions, patch implementations
- **Related Specs**: alliance-website-docker-fix, fix-get-translation-template-tag, fix-wagtailsnippets-assets-email-enhancement
- **Common Patterns**: Docker fixes, template issues, email system problems, asset management
- **Avoid Duplicates**: Check existing fixes specs before creating new bug fix specs

## Task List

### Task 1: Fix Wagtail Snippet Namespace Error

- [x] **1.1 Investigate Wagtail snippet namespace error**
  - [x] Reproduce the `KeyError: 'wagtailsnippets_handlers_authemailtemplate'` error
  - [x] Identify root cause in wagtail_hooks.py registration
  - [x] Document current snippet registration approach

- [x] **1.2 Update wagtail_hooks.py in both projects**
  - [x] Fix snippet registration in structa.cloud
  - [x] Ensure consistent namespace usage
  - [x] Test snippet access in Wagtail admin

- [x] **1.3 Verify URL reversal works**
  - [x] Test URL generation for AuthEmailTemplate
  - [x] Verify namespace resolution in both projects
  - [x] Ensure backward compatibility

- [x] **1.4 Run property-based tests**
  - [x] Verify single-active template invariant still holds
  - [x] Test snippet CRUD operations
  - [x] Confirm no regression in existing functionality

### Task 2: Fix Structa.cloud Asset and URL Issues

- [x] **2.1 Diagnose asset loading problems**
  - [x] Reproduce bad gateway errors on structa.cloud
  - [x] Identify webpack configuration issues
  - [x] Document current asset serving setup

- [x] **2.2 Update webpack configuration**
  - [x] Fix public path configuration for structa.cloud
  - [x] Ensure correct asset resolution in Docker
  - [x] Test bundle loading in development

- [x] **2.3 Fix static and media file serving**
  - [x] Update nginx configuration for structa.cloud
  - [x] Ensure proper Docker volume mounts
  - [x] Test media file uploads and serving

- [x] **2.4 Implement asset health checks**
  - [x] Create health check endpoint for assets
  - [x] Add asset validation to deployment checks
  - [x] Monitor asset availability in production

### Task 3: Create Email CSV Export System

- [x] **3.1 Implement EmailExtractor class**
  - [x] Create `django_grep.email_tools.EmailExtractor`
  - [x] Implement email pattern matching in markdown files
  - [x] Add duplicate detection and removal

- [x] **3.2 Create CSV management system**
  - [x] Implement `EmailCSVManager` class
  - [x] Add CSV read/write operations with proper encoding
  - [x] Include source tracking (spec, file, timestamp)

- [x] **3.3 Build management command**
  - [x] Create `extract_emails_to_csv` command
  - [x] Add options for spec directory and output file
  - [x] Implement progress reporting and logging

- [x] **3.4 Test email extraction**
  - [x] Extract emails from existing specs
  - [x] Verify CSV format and content
  - [x] Test with both ctc-research and structa.cloud specs

### Task 4: Create Invitation Email System

- [x] **4.1 Design invitation email template**
  - [x] Create default invitation email template
  - [x] Support AuthEmailTemplate system for customization
  - [x] Include personalized greeting and registration links

- [x] **4.2 Implement InvitationEmailSender**
  - [x] Create `InvitationEmailSender` class in django-grep
  - [x] Add rate limiting and error handling
  - [x] Implement dry-run mode for testing

- [x] **4.3 Build send_invitation_emails command**
  - [x] Create management command with CSV input
  - [x] Add batch processing with configurable delays
  - [x] Implement comprehensive logging

- [x] **4.4 Test invitation system**
  - [x] Send test invitations in dry-run mode
  - [x] Verify email content and links
  - [x] Test rate limiting and error recovery

### Task 5: Integrate Email Tools into Django-grep

- [x] **5.1 Create django-grep email module**
  - [x] Add `django_grep/email_tools/` directory structure
  - [x] Implement base classes and utilities
  - [x] Add configuration via Django settings

- [x] **5.2 Update django-grep package**
  - [x] Add new dependencies if needed
  - [x] Update setup.py and requirements
  - [x] Ensure backward compatibility

- [x] **5.3 Create comprehensive tests**
  - [x] Unit tests for email extraction
  - [x] Integration tests for CSV operations
  - [x] Property-based tests for correctness

- [x] **5.4 Update documentation**
  - [x] Add email tools to django-grep documentation
  - [x] Create usage examples and API reference
  - [x] Document configuration options

### Task 6: Reorganize Spec Directories

- [x] **6.1 Analyze current spec naming**
  - [x] List all existing spec directories
  - [x] Identify naming inconsistencies
  - [x] Plan new naming convention

- [x] **6.2 Create spec renaming script**
  - [x] Write script to rename spec directories
  - [x] Update .config.kiro files with new names
  - [x] Maintain mapping of old to new names

- [x] **6.3 Execute spec renaming**
  - [x] Backup existing spec directories
  - [x] Run renaming script
  - [x] Verify all spec files are preserved

- [x] **6.4 Update documentation references**
  - [x] Update README files with new spec names
  - [x] Fix any broken links in documentation
  - [x] Create SPEC_RENAMING.md mapping document

### Task 7: Fix Bundle Reading Implementation

- [x] **7.1 Debug bundle reading issues**
  - [x] Identify specific bundle loading failures
  - [x] Trace webpack build and serve process
  - [x] Document current bundle configuration

- [x] **7.2 Update bundle configuration**
  - [x] Fix webpack dev server configuration
  - [x] Ensure hot-reload works in development
  - [x] Optimize production bundle generation

- [x] **7.3 Test asset serving**
  - [x] Test static file serving in Docker
  - [x] Verify media file uploads work
  - [x] Ensure Traefik routing handles assets correctly

- [x] **7.4 Implement asset monitoring**
  - [x] Add asset health checks to monitoring
  - [x] Create alerts for asset failures
  - [x] Log asset serving statistics

### Task 8: Comprehensive Testing and Validation

- [x] **8.1 Run all existing tests**
  - [x] Execute test suites for both projects
  - [x] Verify no regression in functionality
  - [x] Fix any test failures

- [x] **8.2 Create new test coverage**
  - [x] Write tests for email extraction
  - [x] Add tests for invitation system
  - [x] Create integration tests for asset fixes

- [x] **8.3 Perform cross-project testing**
  - [x] Test fixes in both ctc-research and structa.cloud
  - [x] Verify compatibility between projects
  - [x] Test deployment in different environments

- [x] **8.4 Validate backward compatibility**
  - [x] Ensure existing APIs still work
  - [x] Verify data migration safety
  - [x] Test rollback procedures

### Task 9: Documentation and Deployment

- [x] **9.1 Create deployment documentation**
  - [x] Write DEPLOYMENT.md with step-by-step instructions
  - [x] Document configuration changes
  - [x] Include troubleshooting guide

- [x] **9.2 Prepare deployment scripts**
  - [x] Create scripts for each deployment phase
  - [x] Add validation checks to scripts
  - [x] Implement rollback scripts

- [x] **9.3 Execute deployment**
  - [x] Deploy fixes to staging environment
  - [x] Run comprehensive validation tests
  - [x] Deploy to production with monitoring

- [x] **9.4 Post-deployment validation**
  - [x] Monitor system health after deployment
  - [x] Verify all fixes are working
  - [x] Update documentation with lessons learned

## Success Criteria

1. Wagtail snippet namespace error is resolved in both projects
2. Structa.cloud assets load without bad gateway errors
3. Email CSV extraction works for all spec directories
4. Invitation email system sends emails correctly
5. Django-grep email tools are reusable across projects
6. Spec directories are consistently named and organized
7. All existing tests pass with new implementations
8. Deployment documentation is complete and accurate
