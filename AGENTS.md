# Structa Cloud – AI Agent Instructions

## Project Overview

Structa Cloud is a Django monorepo with multiple site projects, shared configuration, shared frontend assets, and local reusable Django libraries. It also includes a **desktop POS application** (Tauri 2 + Rust + React) and an **AI platform** (Cypercloud + CeptorAI).

---

## Repository Layout

### Directory Structure

```
structa.cloud/
├── projects/              # All Django + desktop projects
│   ├── Makefile           # Canonical dispatcher (WEBSITE= selection)
│   ├── configs/           # Shared Django configuration
│   ├── assets/            # Shared frontend assets, templates, static, locale
│   ├── www/               # Shared/core Django code + workers
│   ├── lms/               # LMS Demo site (structa.cloud)
│   ├── portfolio/         # Portfolio/VResume site (vresume.structa.cloud)
│   ├── cypercloud/        # AI Chat Customizer platform
│   ├── ctc-research/      # CTC Research site (ctc-research.com)
│   └── pos/               # Desktop POS app (Tauri 2 + Rust + React)
├── libs/                  # Reusable Python packages (git submodules)
│   ├── django-fusion/     # Component system + routing framework
│   └── ceptor-ai/         # AI chat client + MCP server
├── applications/          # Infrastructure + tooling
│   ├── proxy/             # Traefik reverse proxy + SSL
│   ├── databases/         # Postgres + Redis compose
│   ├── compose/           # Docker Compose orchestration
│   └── scripts/           # Build + automation scripts
├── docs/                  # Documentation (mkdocs)
├── tests/                 # Workspace-level test suite
├── .venv/                 # Unified Python venv (git-ignored)
├── Makefile               # Root dispatcher
└── pyproject.toml         # Workspace config
```

## Canonical Site Paths

Use these canonical paths when working on site-specific code:

| Site | Path | Domain | Port |
|------|------|--------|:----:|
| CTC Research | `projects/ctc-research/` | ctc-research.com | 5070 |
| LMS Demo | `projects/lms/` | structa.cloud | 5071 |
| Portfolio | `projects/portfolio/` | vresume.structa.cloud | 5072 |
| Cypercloud | `projects/cypercloud/` | localhost | 5073 |

Each site can contain its own `assets/`, `plugins/`, `templates/`, `tests/`, `www/`, and site-level `Makefile` as applicable.

### POS Editions

The POS app has three editions:

| Edition | Directory | Description |
|---------|-----------|-------------|
| **Minimal** | `projects/pos/pos-mini/` | Bare-bones Tauri + Rust + SQLite |
| **Solo** | `projects/pos/pos-solo/` | Standalone with embedded Python sidecar |
| **Full** | `projects/pos/pos-full/` | Multi-terminal with external sidecar + Cloud CRM |

---

## Shared Settings

Shared settings live under `projects/configs/`:
- `projects/configs/base/` for base configuration modules
- `projects/configs/settings/` for environment/site settings
- `tests/projects/configs/` for test settings and test configuration helpers

Prefer adding common settings in `projects/configs/` rather than duplicating them inside individual sites. Keep site-specific overrides in the relevant site path.

---

## Shared Frontend Assets

Shared frontend assets live under `projects/assets/`:
- `projects/assets/templates/` — templates shared across sites
- `projects/assets/static/` — shared static files
- `projects/assets/scripts/` — shared frontend/build scripts
- `projects/assets/locale/` — shared localization assets

When adding shared styles, scripts, images, or templates, place them in `projects/assets/` unless they are truly site-specific.

---

## Local Libraries

Local reusable libraries live under `libs/`:

| Library | Description | Key Docs |
|---------|-------------|----------|
| `libs/django-fusion/` | Component system, routing, forms/tables, auth, Wagtail blocks | [`django-fusion/AGENTS.md`](libs/django-fusion/AGENTS.md) |
| `libs/ceptor-ai/` | AI chat client, MCP server, BEM converter, agent generation | [`ceptor-ai/AGENTS.md`](libs/ceptor-ai/AGENTS.md) |

Treat these as first-class local packages. Make reusable framework-level changes in the appropriate library instead of copying logic into site projects.

---

## Makefile Delegation

- The root `Makefile` is a thin entrypoint that delegates application and site work to `projects/Makefile`.
- `projects/Makefile` is the canonical dispatcher for Django checks, tests, migrations, asset builds, Docker/site commands, and `WEBSITE=...` selection.
- Site Makefiles live in each `projects/<site>/` directory.
- Prefer invoking site work through `projects/Makefile` unless a site Makefile target is explicitly needed.
- Preserve existing website aliases in `projects/Makefile`; do not invent new canonical site names without updating the dispatcher.

### Common Makefile Targets

```bash
# Development
cd projects && make dev WEBSITE=lms
cd projects && make check WEBSITE=lms
cd projects && make test WEBSITE=lms

# Deployment
make deploy              # Full stack
make deploy-databases    # Postgres + Redis
make deploy-app          # Django sites
make deploy-proxy        # Traefik

# POS
make pos                 # POS dev targets
make pos-build           # Build POS editions

# Git
make push                # Push repo + lib submodules
make push-lib LIB=django-fusion  # Push single lib
```

---

## Template Conventions

### Template Location Hierarchy

Template locations are intentionally layered. Check all relevant paths before adding or moving templates:

1. Shared templates: `projects/assets/templates/`
2. Site root templates: `projects/<site>/templates/`
3. Site asset templates: `projects/<site>/assets/templates/`
4. Site Django app templates: `projects/<site>/www/**/templates/`
5. Plugin templates: `projects/<site>/plugins/**/templates/`

### Component Template Naming

Component template categories should not repeat the same folder name twice. For example, use `components/blocks/contact/contact_profile.html` instead of `components/blocks/contact/contact/contact_profile.html`.

Use `{% include %}` for reusable components and pass only the required context. Prefer shared templates for cross-site UI and site templates for site-specific presentation.

### Template Tags

| Tag | Usage |
|-----|-------|
| `{% comp "name" /%}` | Rendered components from `django_fusion.comp` |
| `{% comp_include "path" %}` | Drop-in replacement for `{% include %}` that registers paths for tracking |
| `{% include "path" %}` | Only for truly dynamic template names (e.g., `{% include template_name %}`) |

---

## Fragment Naming Convention

Use `fragment_name` only for fragment identifiers and context keys. Do not introduce alternate names such as `fragment`, `name`, `fragment_slug`, or `fragment_key` for the same concept unless maintaining backwards compatibility with existing code.

---

## Code Style & Standards

- **Python**: Follow PEP 8. Use type hints for new or modified functions where practical. Keep formatting compatible with Black's 88-character default.
- **Django**: Prefer class-based views where appropriate. Keep business logic out of views and in services/modules that match the existing local structure.
- **Wagtail/Django templates**: Follow the existing panel, model, and template patterns in the relevant site or library.
- **SCSS/CSS**: Follow existing project conventions and use BEM-style names for reusable component classes. Do not use IDs for styling.
- **Imports**: Never wrap imports in `try`/`except` blocks.
- **TypeScript/React**: Use strict TypeScript, functional components with hooks, React 19 patterns.

---

## Testing & Validation

- Use `rg` instead of recursive `grep` for code searches.
- Run the narrowest relevant checks first, then broader tests when practical.
- For Django site work, prefer commands delegated through `projects/Makefile` with the appropriate `WEBSITE=...` value.
- For shared library work, run tests or checks that cover both the library and affected sites when practical.

### Test Commands

```bash
uv run pytest                          # All workspace tests
cd projects && make test WEBSITE=lms  # Django site tests
cd projects/pos && cargo test         # Rust tests
cd projects/pos && npx vitest run     # React/Vite tests
```

---

## Infrastructure & Proxy

### Traefik Proxy

- Traefik proxy (`default-proxy`) serves SSL on port 443.
- Certs are obtained via Let's Encrypt DNS-01 (Cloudflare) using Traefik's native `certificatesResolvers` block in `applications/proxy/traefik/dynamic.yml`.
- Nginx media server (`shared-media`) serves static/media files for all sites.
- ACME store lives at `applications/proxy/acme/acme.json` (mode 0600), bind-mounted into the proxy at `/etc/traefik/acme/`.

### Let's Encrypt Rollout (Staged)

1. **Stage 1** — Enable LE for `vresume.structa.cloud` on Let's Encrypt **staging** CA
2. **Stage 2** — Flip to production CA; enable LE for ctc-research, structa-cloud, media, dashboard
3. **Stage 3** — Delete `applications/proxy/traefik/dynamic/certs.yml` (self-signed fallback)

### Media Subdomains

- `media.structa.cloud`
- `media.ctc-research.com`
- `media.lms.com`
- `media.vresume.structa.cloud`

---

## Authentication & Authorization

- All sites use `django-allauth` for authentication with `django-fusion` auth mixins.
- Auth views extend `PageHandler` from `django_fusion.site.interface.page_handler`.
- HTMX is used for modal-based login/register flows.
- Social auth adapters live in site `plugins/accounts/adapters.py`.
- MFA support: custom TOTP-based 2FA in profile settings (via `two_factor_enabled` / `two_factor_secret` on profile model).
- `allauth.mfa` is available as optional dependency for WebAuthn/passkey support.
- Auth email templates are managed as Wagtail snippets via `AuthEmailTemplate`.
- Account adapter: `plugins.accounts.adapters.RegistrationAdapter` (HTMX-aware, fragment rendering).
- Supported auth flows: login, signup, password reset, password change, email management, social signup, social connections.

---

## Component System (django-fusion)

- Use `{% comp "name" %}` for rendered components from `django_fusion.comp`.
- Use `{% comp_include "path" %}` as a drop-in replacement for `{% include %}` that registers paths for tracking.
- Use `{% include "path" %}` only for truly dynamic template names (e.g., `{% include template_name %}`).
- Bridge legacy includes to `comp` via `register_include_path()`.
- The `IncludePathComponent` class maps include paths to component names verbatim.
- Register include paths in `AppConfig.ready()` or via `COMPONENTS_INCLUDE_PATH_ROOTS` setting.
- Component template directories: `components/blocks/`, `components/partials/`, `tags/`.
- Component namespaces use dot notation: `{% comp "contact.sections.form" block=block / %}`.

---

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

### Other Canonical Paths

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

---

## Media & Static Files

- Shared static files: `projects/assets/static/`
- Site-specific staticfiles: `projects/<site>/assets/staticfiles/`
- Site-specific media: `projects/<site>/assets/media/`
- Nginx mounts each site's staticfiles under `/var/www/sites/<site>/static/`
- Traefik routes `PathPrefix(/static/)` and `PathPrefix(/media/)` to `shared-media:80`

---

## AI Agent Workflow

When an AI agent starts working on this monorepo:

1. **Read this file** — Get monorepo-wide conventions
2. **Read site AGENTS.md** — Get site-specific instructions
3. **Read lib AGENTS.md** — Get library conventions (if applicable)
4. **Search codebase** — Find existing patterns before generating new code
5. **Follow import paths** — Use canonical paths listed above
6. **Use Makefile delegation** — Prefer `projects/Makefile` for site commands
7. **Verify tests** — Run tests after making changes
