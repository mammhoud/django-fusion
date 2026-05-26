# Design Document

**Category Context: Bug Fixes**
- **Category**: Fixes
- **Scope**: Bug fixes, error corrections, problem resolutions, patch implementations
- **Related Specs**: alliance-website-docker-fix, fix-get-translation-template-tag, fix-wagtailsnippets-assets-email-enhancement
- **Common Patterns**: Docker fixes, template issues, email system problems, asset management
- **Avoid Duplicates**: Check existing fixes specs before creating new bug fix specs

## Technical Design Overview

This document outlines the technical design for fixing multiple critical issues across ctc-research and structa.cloud projects. The design focuses on maintaining backward compatibility while implementing robust solutions.

## System Architecture

### 1. Wagtail Snippet Namespace Fix

**Problem**: `KeyError: 'wagtailsnippets_handlers_authemailtemplate'` in Wagtail admin.

**Solution**:
- Update `wagtail_hooks.py` in both projects to properly register the `AuthEmailTemplate` snippet
- Ensure correct namespace resolution for snippet URLs
- Maintain single-active template invariant

**Implementation**:
```python
# Updated wagtail_hooks.py
@hooks.register('register_snippets')
def register_email_templates():
    from .models import AuthEmailTemplate
    return AuthEmailTemplate

# Ensure proper URL namespace in urls.py
app_name = 'wagtailsnippets_handlers'
```

### 2. Structa.cloud Asset/URL Fix

**Problem**: Bad gateway errors and asset loading issues.

**Solution**:
- Fix webpack configuration for structa.cloud
- Ensure correct static/media file serving in Docker
- Update Traefik configuration for asset paths

**Implementation**:
- Update `webpack.config.js` for structa.cloud with correct public paths
- Configure nginx/Docker for proper asset serving
- Add health checks for asset availability

### 3. Email CSV and Invitation System

**Problem**: Need to extract emails from specs and send invitations.

**Solution**:
- Create `EmailExtractor` class in django-grep
- Implement `EmailCSVManager` for CSV operations
- Build `InvitationEmailSender` with rate limiting

**Implementation**:
```python
# django_grep/email_tools.py
class EmailExtractor:
    def extract_from_specs(self, spec_dir='.kiro/specs'):
        # Scan and extract emails from markdown files

class InvitationEmailSender:
    def send_invitations(self, csv_file, dry_run=False):
        # Send invitation emails with rate limiting
```

### 4. Spec Reorganization

**Problem**: Inconsistent spec naming with project prefixes.

**Solution**:
- Rename all spec directories to use enhancement naming
- Update `.config.kiro` files with new names
- Create renaming documentation

**Implementation**:
- Script to rename spec directories
- Update all references in documentation
- Maintain mapping for backward reference

## Data Models

### AuthEmailTemplate Model
- Maintain existing model structure
- Ensure proper Wagtail snippet registration
- Keep single-active template constraint

### Email CSV Structure
```csv
email,source_spec,source_file,extracted_at
user@example.com,fix-wagtailsnippets-assets-email-enhancement,bugfix.md,2026-04-06
```

## API Design

### Management Commands
1. `extract_emails_to_csv` - Extract emails from specs to CSV
2. `send_invitation_emails` - Send invitations from CSV
3. `rename_specs` - Rename spec directories consistently

### Django-grep Integration
- New module: `django_grep.email_tools`
- Reusable across both projects
- Configurable via Django settings

## Security Considerations

- Rate limiting for email sending
- CSRF protection for all forms
- Secure token generation for invitation links
- Input validation for email extraction

## Performance Considerations

- Batch processing for email extraction
- Async email sending where possible
- Caching for frequently accessed assets
- Efficient CSV parsing for large email lists

## Testing Strategy

### Unit Tests
- Email extraction correctness
- CSV file operations
- Invitation email formatting
- Wagtail snippet registration

### Integration Tests
- End-to-end email sending
- Asset loading in structa.cloud
- Spec renaming process
- Cross-project compatibility

### Property-Based Tests
- Email extraction preserves all emails
- CSV round-trip consistency
- Invitation email idempotence
- Spec renaming maintains content

## Deployment Plan

### Phase 1: Wagtail and Asset Fixes
1. Apply Wagtail snippet namespace fix
2. Fix structa.cloud asset configuration
3. Test asset loading in both projects

### Phase 2: Email System
1. Implement django-grep email tools
2. Create management commands
3. Test email extraction and sending

### Phase 3: Spec Reorganization
1. Rename spec directories
2. Update documentation
3. Verify all references work

### Phase 4: Validation
1. Run comprehensive tests
2. Verify backward compatibility
3. Update deployment documentation

## Rollback Procedures

1. Revert Wagtail hooks changes
2. Restore original webpack configuration
3. Remove django-grep email tools
4. Rename specs back to original names

Each rollback step should be tested and documented in the deployment guide.
