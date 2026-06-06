# Handlers App - Refactoring Status

## Overview
The handlers app has been refactored. Profile-related functionality has been moved to `plugins/profile/`.

## Files Moved to plugins/profile/

### Forms
- `forms/account.py` → `plugins/profile/forms/account.py`
- `forms/billing.py` → `plugins/profile/forms/billing.py`
- `forms/notification.py` → `plugins/profile/forms/notification.py`
- `forms/preferences.py` → `plugins/profile/forms/preferences.py`
- `forms/privacy.py` → `plugins/profile/forms/privacy.py`
- `forms/security.py` → `plugins/profile/forms/security.py`

### Services
- `services/certificates.py` → `plugins/profile/services/certificates.py`
- `services/messages.py` → `plugins/profile/services/messages.py`
- `services/notes.py` → `plugins/profile/services/notes.py`
- `services/person.py` → `plugins/profile/services/person.py`

### Models
- `models/profiles/certificate.py` → `plugins/profile/models/certificate.py`
- `models/profiles/message.py` → `plugins/profile/models/message.py`
- `models/profiles/note.py` → `plugins/profile/models/note.py`
- `models/profiles/privacy_consent.py` → `plugins/profile/models/privacy_consent.py`

### Filters
- `filters/profile.py` → `plugins/profile/filters/profile.py`

### Managers
- `managers/peoples.py` → `plugins/profile/managers/peoples.py`

## Files Duplicated in plugins/accounts/ (Recommended: Remove from handlers)

The following files are identical to files in `plugins/accounts/` and should be removed from handlers:

| handlers file | accounts plugin file | Action |
|---|---|---|
| `filters/location.py` | `plugins/accounts/filters/location.py` | **Remove from handlers** |
| `filters/revision.py` | `plugins/accounts/filters/revision.py` | **Remove from handlers** |
| `filters/user.py` | `plugins/accounts/filters/user.py` | **Remove from handlers** |
| `forms/` (all) | `plugins/accounts/forms/` (all) | **Remove from handlers** |
| `managers/peoples.py` | `plugins/accounts/managers/peoples.py` | **Remove from handlers** |
| `middleware/privacy_consent.py` | `plugins/accounts/middleware/privacy_consent.py` | **Remove from handlers** |
| `models/` (all) | `plugins/accounts/models/` (all) | **Remove from handlers** |
| `processors/` (all) | `plugins/accounts/processors/` (all) | **Remove from handlers** |
| `registration/` (all) | `plugins/accounts/registration/` (all) | **Remove from handlers** |
| `services/` (all) | `plugins/accounts/services/` (all) | **Remove from handlers** |
| `snippets/` (all) | `plugins/accounts/snippets/` (all) | **Remove from handlers** |

## Files Remaining in handlers (Active)

These files are still actively used by the handlers app:

- `urls.py` - Cart/checkout and registration URL routing
- `apps.py` - App configuration
- `site/__init__.py` - Site view imports
- `site/asset_health.py` - Asset health check view
- `site/blog.py` - Blog site views
- `site/media_health.py` - Media health check view
- `site/tags.py` - Tag site views
- `admin/tags.py` - Tag admin interface
- `views/tags.py` - Tag views
- `views/notes.py` - Notes views
- `views/privacy.py` - Privacy views
- `blocks.py` - Wagtail blocks
- `email_templates.py` - Email templates
- `renderers.py` - Custom renderers
- `signals.py` - Django signals
- `urls_privacy.py` - Privacy URLs
- `management/commands/` - All management commands

## Newsletter Snippets (Keep in handlers)

The newsletter snippets in `snippets/newsletter/` are Wagtail admin interfaces for managing newsletters. They are different from `django-rseal/newsletter/` which handles public subscription flows. Keep these in handlers.
