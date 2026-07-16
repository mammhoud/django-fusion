# Requirements Document

## Introduction

The `/data/structa.cloud` monorepo hosts three Django/Wagtail applications — **ctc-research**, **lms-demo**, and **VResume** — sharing a single Webpack 5 build pipeline, a Python dependency tree managed by `uv`, and a flat log directory. This document defines requirements for formalising the architecture as prose hint notes, establishing bundle-size governance and log isolation, migrating documentation from MkDocs to Docsify, defining Docker-Compose orchestration overlays, and adding a pre-commit governance pipeline with import-reachability verification.

---

## Requirements

### 1. Architectural Documentation

**1.1** The spec MUST document, in prose hint-note form, how the monorepo separates per-site concerns from shared concerns. Specifically: the three site entry points (`ctc-research/assets/static/js/app.js`, `lms-demo/assets/static/js/app.js`, `VResume/assets/static/js/app.js`) are per-site; the shared core lives in `assets/static/js/core/main.js` (used by ctc-research and lms-demo; VResume carries its own core).

**1.2** The spec MUST note that `main.config.js` retains a `@theme` alias pointing to the now-deleted `assets/static/js/theme/` directory. This stale alias MUST be flagged as a risk and its removal or replacement (pointing to `assets/static/js/modules`) MUST be listed as a required task.

**1.3** The spec MUST document the SITE_DIR_MAP resolution logic used by Webpack (`ctc`/`ctc-research.com` → `ctc-research`; `structa`/`structa.cloud`/`lms` → `lms-demo`; `vresume`/`VResume`/`resume` → `VResume`) as hint notes — no tables or diagrams.

**1.4** The spec MUST distinguish frontend packages that are workspace-wide shared (webpack, babel, sass, postcss, tailwindcss 4, mini-css-extract-plugin, webpack-bundle-tracker, vue 3, alpinejs, htmx.org, bootstrap 5) from those that are per-site or optional (apexcharts, echarts, chart.js, gridjs, quill, swiper, glightbox, fullcalendar). Note: ag-grid is absent from `package.json` — gridjs is the correct data-table package.

**1.5** The spec MUST note that `axios` is not in `assets/package.json` (fetch/htmx handles HTTP) and that `winston` is not applicable on the Python side — the equivalent logging stack is `structlog` + `python-json-logger` + `django-structlog` as declared in `pyproject.toml`.

### 2. Package Enhancement Plans

**2.1** The spec MUST define three bundle-budget targets enforced via a separate `size-limit` configuration at `assets/.size-limit.json`:
- `client` bundle: 25 kB gzip maximum
- `admin` bundle: 120 kB gzip maximum
- `marketing` bundle: 15 kB gzip maximum

**2.2** The current `performance` block in `common.config.js` sets `maxEntrypointSize: 1 MB` with `hints: 'warning'`. The spec MUST require that per-bundle budgets be enforced by `size-limit` and NOT by modifying the shared Webpack config, so existing large-vendor tolerances are preserved.

**2.3** The spec MUST require log directory isolation. Target layout:
```
logs/
  ctc-research/
    application.log  debug.log  error.log
  lms-demo/
    application.log  debug.log  error.log
  vresume/
    application.log  debug.log  error.log
```

**2.4** Log isolation MUST be implemented via `structlog`/`python-json-logger` file handler configuration in `configs/settings.py`, keyed on the `WEBSITE_IDENTIFIER` environment variable. `LOG_DIR` is derived as `BASE_DIR / "logs" / WEBSITE_IDENTIFIER`.

**2.5** Each per-site log directory MUST be created at container start if absent. Docker volume mounts for `logs/` subtrees MUST use writable named volumes.

### 3. Docsify Documentation Structure

**3.1** The existing docs server uses MkDocs Material. The spec MUST plan migration to Docsify (client-side rendering, no build step, served as static files via `nginx:alpine`).

**3.2** The Docsify structure MUST include:
- `docs/index.html` — Docsify bootstrap page
- `docs/_sidebar.md` — navigation sidebar
- `docs/README.md` — landing/overview
- `docs/architecture-notes.md` — architectural hint notes
- `docs/error-resolution-log.md` — error resolution log (markdown table permitted here)
- `docs/migration-record.md` — ctc-research → lms-demo migration record

**3.3** The `_sidebar.md` MUST retain existing sidebar categories and add a Monorepo section.

**3.4** The docs volume MUST be mountable as `:ro` (read-only).

**3.5** The Docsify Dockerfile MUST use `nginx:alpine` — no Python runtime required.

### 4. Docker-Compose Orchestration

**4.1** The spec MUST provide an additive `docker-compose.infra.yml` overlay demonstrating: the Docsify docs service with `:ro` volume, at least one frontend Django service with a per-site writable log volume.

**4.2** Per-site log volumes MUST be declared as named volumes: `ctc-research-logs`, `lms-demo-logs`, `vresume-logs`.

**4.3** The overlay MUST NOT duplicate full network and service definitions already in `docker-compose.yml`.

### 5. Lifecycle Governance Pipeline

**5.1** The spec MUST define Husky pre-commit hooks covering: `markdownlint` for `docs/*.md`, `eslint` for all site JS, and a bundle-size audit.

**5.2** The spec MUST define an import reachability check script (`scripts/check-imports.mjs`) that verifies Webpack alias targets exist on disk and flags the stale `@theme` alias.

**5.3** Husky hooks MUST be installed in `assets/`. The `.husky/` directory resides at `assets/.husky/`.

**5.4** The pipeline MUST be CI/CD-friendly — hooks can be skipped with `--no-verify` but CI runs the same checks unconditionally.

### 6. Error Resolution

**6.1** The typo `from ..mnagement.services.courses import CourseService` in `ctc-research/plugins/lms/views/lessons.py` line 12 MUST be tracked in the error resolution log. The corrected import is `from ..management.services.courses import CourseService`. The fix is already present on disk.

**6.2** The error resolution log MUST record: file path, line number, bad import, correct import, error message, and resolution status.

### 7. Migration Record

**7.1** The spec MUST document key structural differences: SITE_ID (1 vs 2), WEBSITE_IDENTIFIER, port (5070 vs 5071), presence of `apps.py` (lms-demo only), presence of site-level `uv.lock` (lms-demo only), absence of `.env.demo`/`.env.testing` in lms-demo.

**7.2** The migration record MUST note the duplicated `SILENCED_SYSTEM_CHECKS` list and list its consolidation as a pending task.

**7.3** The migration record MUST note the theme directory deletion (June 2, 2026) and the shift from `@theme` alias to direct imports from `../../../../assets/static/js/modules/index.js`.

### 8. Hint Notes Replacement Statement

**8.1** All architectural representation in this spec is given as prose hint notes. No ASCII diagrams, no tables (except the Error Resolution Log), and no Mermaid charts appear in the requirements or design documents for this feature.

---

## Glossary

| Term | Definition |
|------|-----------|
| SITE_DIR_MAP | Webpack alias table mapping shorthand site keys to canonical directory names |
| `@theme` | Stale Webpack alias pointing to the deleted `assets/static/js/theme/` directory |
| LOG_DIR | Per-site log directory derived as `BASE_DIR / "logs" / WEBSITE_IDENTIFIER` |
| Docsify | Client-side Markdown documentation renderer; no server-side build step required |
| size-limit | Node.js tool that checks compiled bundle sizes against declared byte budgets |
| lint-staged | Git hook helper that runs linters only on staged files |
| Husky | Git hook manager that installs and runs pre-commit scripts |
| WEBSITE_IDENTIFIER | Django setting string identifying the current site (e.g. `ctc-research`, `lms-demo`, `vresume`) |
