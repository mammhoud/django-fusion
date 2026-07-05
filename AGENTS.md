# Structa Cloud – AI Agent Instructions

## Project Overview
Structa Cloud is a Django monorepo under `applications/`, with multiple site projects, shared configuration, shared frontend assets, and local reusable Django libraries. Do not assume this repo uses a generic `core/customizer/design/components` app layout.

## Actual Monorepo Layout
- `applications/Makefile` is the primary Makefile for application, Django, asset, test, and site orchestration targets.
- `applications/configs/` contains shared Django configuration and settings used across sites.
- `applications/assets/` contains shared frontend assets, shared templates, static files, locale files, and asset scripts.
- `applications/libs/` contains local reusable libraries that are developed alongside the sites.
- `applications/scripts/`, `applications/tasks/`, and `applications/webpack/` contain shared automation, task, and build tooling.
- `applications/www/` contains shared/core Django code used by the application stack.

## Canonical Site Paths
Use these canonical paths when working on site-specific code:
- `applications/ctc-research/` — CTC Research site.
- `applications/lms-demo/` — Structa/LMS demo site.
- `applications/VResume/` — VResume site. Note the directory is capitalized, even though some Makefile aliases use `vresume`.

Each site can contain its own `assets/`, `plugins/`, `templates/`, `tests/`, `www/`, and site-level `Makefile` as applicable.

## Shared Settings
Shared settings live under `applications/configs/`:
- `applications/configs/base/` for base configuration modules.
- `applications/configs/settings/` for environment/site settings.
- `applications/configs/tests/` for test settings and test configuration helpers.

Prefer adding common settings in `applications/configs/` rather than duplicating them inside individual sites. Keep site-specific overrides in the relevant site path.

## Shared Frontend Assets
Shared frontend assets live under `applications/assets/`:
- `applications/assets/templates/` for templates shared across sites.
- `applications/assets/static/` for shared static files.
- `applications/assets/scripts/` for shared frontend/build scripts.
- `applications/assets/locale/` for shared localization assets.

When adding shared styles, scripts, images, or templates, place them in `applications/assets/` unless they are truly site-specific.

## Local Libraries
Local reusable libraries live under `applications/libs/`:
- `applications/libs/django-grep/`
- `applications/libs/django-fusion/`
- `applications/libs/django-rseal/`

Treat these as first-class local packages. Make reusable framework-level changes in the appropriate library instead of copying logic into site projects.

## Makefile Delegation
- The root `Makefile` should be a thin entrypoint that delegates application and site work to `applications/Makefile`.
- `applications/Makefile` is the canonical dispatcher for Django checks, tests, migrations, asset builds, Docker/site commands, and `WEBSITE=...` selection.
- Site Makefiles live in each `applications/<site>/` directory, for example:
  - `applications/ctc-research/Makefile`
  - `applications/lms-demo/Makefile`
  - `applications/VResume/Makefile`
- Prefer invoking site work through `applications/Makefile` unless a site Makefile target is explicitly needed.
- Preserve existing website aliases in `applications/Makefile`; do not invent new canonical site names without updating the dispatcher.

## Template Conventions
- Component template categories should not repeat the same folder name twice; for example, use `components/blocks/contact/contact_profile.html` instead of `components/blocks/contact/contact/contact_profile.html`.
Template locations are intentionally layered. Check all relevant paths before adding or moving templates:
- Shared templates: `applications/assets/templates/`.
- Site root templates: `applications/<site>/templates/`.
- Site asset templates: `applications/<site>/assets/templates/`.
- Site Django app templates: `applications/<site>/www/**/templates/`.
- Plugin templates: any template paths under `applications/<site>/plugins/`, including plugin-level `templates/` directories.

Use `{% include %}` for reusable components and pass only the required context. Prefer shared templates for cross-site UI and site templates for site-specific presentation.

## Fragment Naming Convention
Use `fragment_name` only for fragment identifiers and context keys. Do not introduce alternate names such as `fragment`, `name`, `fragment_slug`, or `fragment_key` for the same concept unless maintaining backwards compatibility with existing code.

## Code Style & Standards
- **Python**: Follow PEP 8. Use type hints for new or modified functions where practical. Keep formatting compatible with Black's 88-character default.
- **Django**: Prefer class-based views where appropriate. Keep business logic out of views and in services/modules that match the existing local structure.
- **Wagtail/Django templates**: Follow the existing panel, model, and template patterns in the relevant site or library.
- **SCSS/CSS**: Follow existing project conventions and use BEM-style names for reusable component classes. Do not use IDs for styling.
- **Imports**: Never wrap imports in `try`/`except` blocks.

## Testing & Validation
- Use `rg` instead of recursive `grep` for code searches.
- Run the narrowest relevant checks first, then broader tests when practical.
- For Django site work, prefer commands delegated through `applications/Makefile` with the appropriate `WEBSITE=...` value.
- For shared library work, run tests or checks that cover both the library and affected sites when practical.

## Infrastructure & Proxy
- Traefik proxy (`default-proxy`) serves SSL on port 443. Certs are obtained via Let's Encrypt DNS-01 (Cloudflare) using Traefik's native `certificatesResolvers` block in `proxy/traefik/dynamic.yml`.
- Nginx media server (`shared-media`) serves static/media files for all sites.
- ACME store lives at `proxy/acme/acme.json` (mode 0600), bind-mounted into the proxy at `/etc/traefik/acme/`. The directory is git-tracked (via `.gitkeep`); `acme.json` is gitignored.
- Cloudflare credentials are read from env vars on the proxy container (`CF_DNS_API_TOKEN` recommended, or `CF_API_EMAIL` + `CF_API_KEY`). Local values come from `proxy/.env` (gitignored; copy from `proxy/.env.example`).
- HTTPS routers opt into LE via `tls: { certResolver: letsencrypt }` in the per-site router file. The catchall router intentionally has no certResolver — Traefik falls back to its internal default cert for unmatched hosts.
- The rollout is staged (see `proxy/LETSENCRYPT.md`): Stage 1 enables LE for `vresume.structa.cloud` on the Let's Encrypt **staging** CA; Stage 2 flips to the production CA and enables LE for ctc-research / structa-cloud / media / dashboard; Stage 3 deletes `proxy/traefik/dynamic/certs.yml`.
- `proxy/traefik/dynamic/certs.yml` (static self-signed certs) is kept as a fallback until Stage 3. Until it's deleted, removing `certResolver` from a router causes it to fall back to the SAN-matched self-signed cert.
- `proxy/scripts/manage-certs.sh` now provides `bootstrap-acme`, `status`, and `check-expiry` for the LE flow; the self-signed commands are retained as a legacy fallback.
- Health checks on backend services must include the correct `Host` header (set via `hostname` in Traefik healthCheck config).
- Media subdomains: `media.structa.cloud`, `media.ctc-research.com`, `media.lms-demo.com`, `media.vresume.structa.cloud`.
- Legacy self-signed certs remain in `proxy/certs/` for rollback purposes; they are no longer the source of truth.

## Authentication & Authorization
- All sites use `django-allauth` for authentication with `django-fusion` auth mixins.
- Auth views extend `PageHandler` from `django_fusion.site`.
- HTMX is used for modal-based login/register flows.
- Social auth adapters live in site `plugins/accounts/adapters.py`.
- MFA support: custom TOTP-based 2FA in profile settings (via `two_factor_enabled` / `two_factor_secret` on profile model).
- `allauth.mfa` is available as optional dependency for WebAuthn/passkey support.
- Auth email templates are managed as Wagtail snippets via `AuthEmailTemplate`.
- Account adapter: `plugins.accounts.adapters.RegistrationAdapter` (HTMX-aware, fragment rendering).
- Supported auth flows: login, signup, password reset, password change, email management, social signup, social connections.

## Component System (django-fusion)
- Use `{% comp "name" %}` for rendered components from `django_fusion.comp`.
- Use `{% comp_include "path" %}` as a drop-in replacement for `{% include %}` that registers paths for tracking.
- Use `{% include "path" %}` only for truly dynamic template names (e.g., `{% include template_name %}`).
- Bridge legacy includes to `comp` via `register_include_path()`.
- The `IncludePathComponent` class maps include paths to component names verbatim.
- Register include paths in `AppConfig.ready()` or via `COMPONENTS_INCLUDE_PATH_ROOTS` setting.
- Component template directories: `components/blocks/`, `components/partials/`, `tags/`.
- Component namespaces use dot notation: `{% comp "contact.sections.form" block=block / %}`.

## django-fusion Canonical Import Paths

All re-export shims have been removed. Use these canonical paths directly.

### Routing (`comp.routes`)

```python
from django_fusion.comp.routes import (
    # Base routing
    Viewset, BaseViewset, ViewsetMeta, Route, route, menu_path, IndexViewMixin,
    # Descriptor
    viewprop,
    # Model viewsets
    BaseModelViewset, ModelViewset, ReadonlyModelViewset,
    ListBulkActionsMixin, CreateViewMixin, UpdateViewMixin, DeleteViewMixin, DetailViewMixin,
    # Site/Application
    Application, AppMenuMixin, Site,
    # Routable components
    RoutableComponent, FragmentComponent,
    # Fragment detection
    FragmentDetector, FragmentDetectionMixin,
)
```

### Generic CBVs (`comp.generic`)

```python
from django_fusion.comp.generic import (
    Action, CreateModelView, DeleteBulkActionView, DeleteModelView,
    DetailModelView, ListModelView, UpdateModelView,
    BaseListModelView, BaseBulkActionView, SearchableViewMixin, TableView,
)
```

### Other canonical paths

| Module | Canonical Path |
|--------|---------------|
| Handlers | `django_fusion.core.handlers` |
| Managers | `django_fusion.core.managers` |
| Models | `django_fusion.core.models` |
| Services | `django_fusion.core.services` |
| Views (FilterMixin, SearchMixin) | `django_fusion.web.views` |
| Loaders | `django_fusion.comp.loaders` |
| Middlewares | `django_fusion.core.middlewares` |
| Cache | `django_fusion.core.cache` |

## Media & Static Files
- Shared static files: `applications/assets/static/`.
- Site-specific staticfiles: `applications/<site>/assets/staticfiles/`.
- Site-specific media: `applications/<site>/assets/media/`.
- Nginx mounts each site's staticfiles under `/var/www/sites/<site>/static/`.
- Traefik routes `PathPrefix(/static/)` and `PathPrefix(/media/)` to `shared-media:80`.
