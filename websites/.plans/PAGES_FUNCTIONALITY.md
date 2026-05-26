# Pages & Functionalities Inventory (Two Websites)

## Shared Runtime Entry
- `manage.py` → Django CLI entrypoint.
- `www/asgi.py`, `www/wsgi.py` → deployment app entrypoints.
- `www/urls.py` → health, Django admin, Wagtail admin/docs, i18n patterns, plugins routes.

## CTC Research (`ctc-research.com`)
### Main Functional Domains
- **Accounts/Auth** (`plugins/accounts/`): registration, login, profile settings, notifications, email flows.
- **Blog** (`plugins/blog/`): posts, tags, list/detail fragments and views.
- **Profile** (`plugins/profile/`): user profile pages, settings, privacy/certification/notes.
- **LMS** (`plugins/lms/`): courses, lessons, enrollments, progress, certificates.

### Templates/Pages
- Base templates under `templates/` and app templates under `plugins/templates/` + `www/core/templates/`.
- Wagtail pages/blocks under `www/core/content/models/pages` and `.../blocks`.

## Structa Cloud (`structa.cloud`) — Alliance Scope
### Main Functional Domains
- **Alliance LMS + Accounts + Blog + Profile** via `plugins/` thin-layer modules.
- Delegated business logic to shared packages: `django_osoul`, `django_rseal`, `django_grep`.

### Templates/Pages
- Project templates in `structa.cloud/templates/`.
- Shared/plugin templates in `structa.cloud/plugins/templates/`.

## Notification System
- Canonical HTMX notification trigger helper: `plugins/accounts/services/notifications.py`.
- Registration views now consume shared notification helper instead of local duplicate function.

## Asset/Bundle Reachability
- Root check targets validate asset directories and settings-path assumptions.
- Site checks validate Django project boot and management command viability.

## Current Known Blockers
- Internal package imports missing in active `.venv` (`django_grep`, `django_osoul`, `django_rseal`).
- `pytest` unavailable in `.venv` for Alliance targeted tests under current proxy/network restrictions.
