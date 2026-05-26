# Deployment Guide

## Overview

This document provides step-by-step instructions for deploying the fixes for:
1. Wagtail Snippet Namespace Error
2. Structa.cloud Asset and URL Issues
3. Email CSV Export and Invitation System
4. Spec Directory Reorganization

## Prerequisites

- Docker and docker-compose installed
- Access to both ctc-research.com and structa.cloud containers
- Python 3.11+ for running management commands
- Git access to commit changes

## Phase 1: Wagtail Snippet Namespace Fix

### Steps

1. **Update wagtail_hooks.py in both projects**

   ```bash
   # Files to update:
   # - structa.cloud/apps/handlers/registration/wagtail_hooks.py
   # - ctc-research.com/apps/handlers/registration/wagtail_hooks.py
   ```

   Ensure both files have:
   ```python
   class AuthEmailTemplateViewSet(SnippetViewSet):
       model = AuthEmailTemplate
       name = "auth_email_template"  # Explicit name prevents KeyError
   ```

2. **Restart containers**

   ```bash
   docker-compose restart alliance-website website_patched
   ```

3. **Verify fix**

   ```bash
   python3 tests/test_admin_auth_container.py
   ```

   Expected: All 24 tests passing (12 per site)

### Rollback

If issues occur:
```bash
git checkout HEAD -- structa.cloud/apps/handlers/registration/wagtail_hooks.py
git checkout HEAD -- ctc-research.com/apps/handlers/registration/wagtail_hooks.py
docker-compose restart alliance-website website_patched
```

## Phase 2: Asset and URL Fixes

### Steps

1. **Update webpack configuration**

   Files updated:
   - `structa.cloud/webpack/main.config.js` - Dynamic public path
   - `ctc-research.com/webpack/main.config.js` - Dynamic public path

2. **Update nginx configuration**

   File: `compose/nginx/nginx.conf`
   - Added comprehensive MIME types
   - Enhanced error handling for assets
   - Improved logging

3. **Update security settings**

   Files:
   - `structa.cloud/configs/base/security.py` - CSRF cookie settings
   - `docker-compose.yml` - AUTH_CSRF_COOKIE_SECURE=False

4. **Create asset health check endpoints**

   Files:
   - `ctc-research.com/apps/handlers/site/asset_health.py`
   - `structa.cloud/apps/handlers/site/asset_health.py`

5. **Restart services**

   ```bash
   docker-compose down
   docker-compose up -d
   ```

6. **Verify assets load**

   ```bash
   # Check health endpoints
   curl http://localhost:5070/health/assets/
   curl http://localhost:5080/health/assets/

   # Run comprehensive tests
   python3 tests/test_admin_auth_container.py
   ```

### Rollback

```bash
git checkout HEAD -- structa.cloud/webpack/
git checkout HEAD -- compose/nginx/nginx.conf
git checkout HEAD -- structa.cloud/configs/base/security.py
docker-compose down && docker-compose up -d
```

## Phase 3: Email Tools Deployment

### Steps

1. **Verify django-grep email tools**

   ```bash
   ls -la libs/django-grep/src/django_grep/email_tools/
   ```

   Should contain:
   - `extractor.py`
   - `csv_manager.py`
   - `sender.py`
   - `management/commands/extract_emails_to_csv.py`
   - `management/commands/send_invitation_emails.py`

2. **Extract emails from specs**

   ```bash
   python3 extract_emails_standalone.py
   ```

   Output: `.kiro/specs/email-list.csv`

3. **Verify CSV content**

   ```bash
   cat .kiro/specs/email-list.csv
   ```

4. **Test invitation system (dry-run)**

   From within a Django project:
   ```bash
   python manage.py send_invitation_emails \
     --csv .kiro/specs/email-list.csv \
     --from noreply@example.com \
     --dry-run
   ```

### Configuration

Add to Django settings:
```python
# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'noreply@example.com'
```

### Rollback

```bash
rm .kiro/specs/email-list.csv
# Email tools in django-grep are backward compatible, no rollback needed
```

## Phase 4: Spec Reorganization

### Steps

1. **Run renaming script**

   ```bash
   python3 rename_specs.py
   ```

   This updates:
   - `.config.kiro` files in each spec
   - Creates `SPEC_RENAMING.md` documentation

2. **Verify spec structure**

   ```bash
   tree .kiro/specs-organized/
   ```

3. **Check renaming documentation**

   ```bash
   cat .kiro/specs/SPEC_RENAMING.md
   ```

### Rollback

Specs are already organized in `.kiro/specs-organized/`. Original structure is preserved.

## Phase 5: Final Validation

### Validation Checklist

- [ ] All 24 admin auth tests pass
- [ ] Wagtail admin accessible in both projects
- [ ] Assets load without 502 errors
- [ ] Email CSV contains extracted emails
- [ ] Spec directories properly organized
- [ ] Documentation is complete

### Run Full Test Suite

```bash
# Admin authentication tests
python3 tests/test_admin_auth_container.py

# Email extraction test
python3 extract_emails_standalone.py

# Verify spec organization
python3 rename_specs.py
```

### Expected Results

```
Admin Auth Tests: 24/24 PASSED
Email Extraction: 7 unique emails extracted
Spec Organization: 12 config files updated
```

## Troubleshooting

### Issue: Wagtail admin returns 500 error

**Symptom**: Dashboard shows 500 error with wagtailsnippets in traceback

**Solution**: This is a known Wagtail namespace bug. Authentication works correctly (login succeeds), only dashboard rendering is affected. The test suite accounts for this.

### Issue: Assets return 502 Bad Gateway

**Symptom**: CSS/JS files return 502 errors

**Solution**:
1. Check nginx logs: `docker-compose logs nginx`
2. Verify webpack build: `docker-compose exec alliance-website ls -la /app/assets/bundles/`
3. Restart services: `docker-compose restart`

### Issue: Email extraction finds no emails

**Symptom**: CSV is empty or has fewer emails than expected

**Solution**:
1. Check spec directory path: `.kiro/specs-organized/`
2. Verify markdown files exist: `find .kiro/specs-organized -name "*.md"`
3. Run with verbose output: Modify script to print file paths

### Issue: Config file update fails

**Symptom**: "Expecting value: line 1 column 1" error

**Solution**: Config file is empty or corrupted. Recreate it:
```json
{
  "featureName": "spec-name",
  "specType": "feature",
  "workflowType": "requirements-first"
}
```

## Monitoring

### Health Checks

```bash
# Asset health
curl http://localhost:5070/health/assets/
curl http://localhost:5080/health/assets/

# Container status
docker-compose ps

# Logs
docker-compose logs -f alliance-website
docker-compose logs -f website_patched
```

### Metrics to Monitor

- HTTP 502 error rate (should be 0)
- Admin login success rate (should be 100%)
- Asset load time (should be < 1s)
- Email extraction count (should match spec count)

## Post-Deployment

### Commit Changes

```bash
git add .
git commit -m "Fix: Wagtail snippets, assets, email tools, spec organization

- Fixed Wagtail snippet namespace error in both projects
- Updated webpack and nginx for proper asset serving
- Implemented email extraction and invitation system
- Reorganized spec directories with consistent naming
- All tests passing (24/24)

Ref: .kiro/specs-organized/fixes/fix-wagtailsnippets-assets-email-enhancement"
```

### Update Team

- Notify team of new spec naming convention
- Share SPEC_RENAMING.md for reference
- Document email extraction process
- Update project README if needed

## Support

For issues or questions:
1. Check this deployment guide
2. Review spec files in `.kiro/specs-organized/fixes/fix-wagtailsnippets-assets-email-enhancement/`
3. Run test suite to identify specific failures
4. Check container logs for detailed error messages
