# Minimal Architecture — Repo Use Case

## A. Deployment Topology
- Shared workspace root provides base runtime assets/config:
  - `configs/` (settings, ENV yml)
  - `plugins/` (shared Django apps/plugins)
  - `assets/` (static/media/locale)
  - `www/` (project-level runtime package)
- Site-specific overlays:
  - `ctc-research.com/`
  - `structa.cloud/`

## B. Runtime Entry Points
- CLI: `manage.py`
- ASGI: `www/asgi.py`
- WSGI: `www/wsgi.py`
- Settings module: `configs.settings`

## C. Framework/Package Roles
- `django-osoul`: pure Django foundation and reusable base logic.
- `django-rseal`: Wagtail/workflow and automation features.

## D. Ownership Boundaries
- Global checks and shared config validations run from repository root.
- Alliance-related checks and organization tasks run in `structa.cloud/` scope.
- Cross-site asset/static conflict checks must validate both site paths before deploy.
