# Enhancement Roadmap

> Consolidated from project reports and the enhancement backlog (July 2026)

## 1. Architecture

- **Component Caching** — Per-site component cache with cross-worker invalidation
  → See [Component Cache Enhancement](../libs/django-fusion/component-cache-enhancement.md)
- **Event Grid Pagination Lock** — Prevent duplicate event fetching under concurrent loads
- **Template Validation** — Automated checks for missing template includes and dead paths

## 2. Frontend & UI

- **ThemeForest Submission** — Polish templates for marketplace submission
  → See [ThemeForest Plan](../themeforest/submission.md)
- **Tinker Admin UI** — Standalone admin/configuration dashboard
  → See [Tinker Reports](../websites/tinker/reports/)
- **Unused Files Cleanup** — Remove stale SCSS, JS, and template files
  → See [Unused Files Plan](unused-files-plan.md)

## 3. Developer Experience (DX)

- **Remove Legacy Packages** — `django-grep` and `django-rseal` have been folded into `django-fusion`
- **Makefile Consolidation** — Thin root Makefile delegating to `applications/Makefile`
- **Documentation Organization** — Guides split into infrastructure / startup / development

## 4. Infrastructure

- **Let's Encrypt DNS-01** — Traefik native ACME with Cloudflare DNS challenge
- **Health Check Standardization** — Consistent `/health/` endpoints with `Host` headers
- **Static Asset Pipeline** — Bundles.json normalization for django-webpack-loader v3 compat

## 5. Site-Specific

| Site | Key Enhancement |
|------|----------------|
| CTC Research | LMS plugin parity with lms-demo, 2FA TOTP completion |
| LMS Demo | WebSocket real-time learning progress |
| VResume | Portfolio/Blog fragment components, social auth |
