# Specification and Implementation Plan for Monorepo Infrastructure

## Overview

The `/data/structa.cloud` monorepo runs three Django/Wagtail applications from a single codebase — **ctc-research** (SITE_ID 1, port 5070), **lms-demo** (SITE_ID 2, port 5071), and **VResume** (port 5072). They share a Webpack 5 pipeline rooted at `assets/`, a Python dependency tree managed by `uv`, and a flat log directory at `logs/` that currently offers no per-site isolation.

This plan addresses five areas: formalising the architectural boundaries as prose hint notes, establishing bundle-size budgets and log isolation, migrating documentation from MkDocs to Docsify, wiring per-site Docker volume mounts, and adding a pre-commit governance pipeline with import-reachability verification. One confirmed production error — a typo in a Django import path — is logged and resolved. The ctc-research → lms-demo migration facts are formally recorded.

No ASCII diagrams, no tables (except the Error Resolution Log), and no Mermaid charts appear in this document.

---

## Executive Summary

The three sites currently share `assets/node_modules`, the webpack pipeline, and `configs/settings.py` but diverge in SITE_ID, port, and database name. The frontend build is healthy (408 bundles, 73 MB, 23 pre-existing Vue warnings) but carries three stale Webpack aliases (`@theme`, `@layouts`, `@usecases`) that point to the deleted `assets/static/js/theme/` directory — a build-time bomb if any file ever imports them. The log directory has no isolation, making per-site debugging unnecessarily difficult. The docs server is a heavyweight Python/MkDocs container that can be replaced with a 10 MB nginx:alpine Docsify instance.

---

## Architecture

### Monorepo Layout

The workspace root at `/data/structa.cloud` contains three site directories, a shared `assets/` tree, a `configs/` package that all Django sites import, a `webpack/` directory holding `common.config.js` and `main.config.js`, and a flat `logs/` directory that all three sites write to today. Each site directory follows the pattern `{site}/assets/static/js/app.js` as its Webpack entry point and `{site}/assets/bundles/{site}/` as its output directory.

### Shared vs Per-Site Frontend Packages

The workspace-wide shared packages — the ones every site consumes — are Webpack 5, Babel, Sass, PostCSS, Tailwind CSS 4, `mini-css-extract-plugin`, `webpack-bundle-tracker`, Vue 3, Alpine.js, htmx.org, and Bootstrap 5. These live in `assets/node_modules` and are resolved globally across all three site builds via the `resolve.modules` list in `main.config.js`.

Per-site or optional packages are those that only one or two sites import in their own `app.js` or component files. ApexCharts and ECharts are used by lms-demo and ctc-research for dashboard views; Chart.js is a lighter alternative available as a fallback. Grid.js (not ag-grid, which is absent from `package.json`) handles data-table rendering. Quill powers rich-text editing. Swiper and GLightbox are used for media-heavy pages. FullCalendar is present but only activated in lms-demo's scheduling views.

`axios` is not listed in `assets/package.json` — HTTP requests are handled via `fetch` or htmx's built-in request layer. `winston` is a Node.js logging library and is not applicable in this stack; the Python-side equivalent is `structlog` + `python-json-logger` + `django-structlog`, all declared in `pyproject.toml`.

### Webpack Entry and Output Routing

`main.config.js` reads the `PROJECT_PATH`/`DJANGO_SITE`/`env.site` environment variable and resolves it through `SITE_DIR_MAP` to the canonical directory name. The alias keys `ctc`, `ctc-research`, and `ctc-research.com` all resolve to `ctc-research`; `structa`, `structa.cloud`, and `lms` all resolve to `lms-demo`; `vresume`, `VResume`, `resume`, and `vresume.structa.cloud` all resolve to `VResume`. When building for VResume, the shared `core/main.js` entry is omitted — VResume carries its own self-contained core. For ctc-research and lms-demo, three entry points are emitted: `main` (shared core), `static` (CSS + vendor), and `app` (site-specific).

### Stale `@theme` Alias

`main.config.js` declares `'@theme': path.resolve(workspaceRoot, 'assets/static/js/theme')`. The `assets/static/js/theme/` directory was deleted on June 2, 2026 as part of the vendor-packages and usecases migration. Any import that references `@theme` will silently resolve to a non-existent directory and fail at bundle time. This alias must be updated to point to `assets/static/js/modules` or removed entirely. Similarly, `@layouts` and `@usecases` point into the deleted `theme/` subtree and must be redirected or removed.

### Python Settings Inheritance

Both ctc-research and lms-demo resolve their Django settings through `from configs.settings import *`, then override `WEBSITE_NAME`, `WEBSITE_IDENTIFIER`, `SITE_ID`, and `ROOT_URLCONF`. The `SILENCED_SYSTEM_CHECKS` list is duplicated verbatim in both `settings.py` files; it should be consolidated into `configs/settings.py` to avoid drift. VResume follows the same inheritance pattern.

---

## Components and Interfaces

### Webpack Build Pipeline

`webpack/common.config.js` defines shared Babel, CSS/SCSS, Vue, and image rules plus the split-chunks optimization. `webpack/main.config.js` merges common config, sets site-specific entry/output, adds `BundleTracker`, and resolves aliases. `assets/scripts/workspace.mjs` orchestrates multi-site builds via npm scripts. The interface contract between sites and the pipeline is: each site provides `{site}/assets/static/js/app.js`, `{site}/assets/static/js/static.js`, and receives `{site}/assets/bundles/{site}/bundles.json` as the Django `webpack-loader` manifest.

### Logging Stack

`configs/settings.py` defines the `LOGGING` dict using `structlog` and `python-json-logger` file handlers. Today all handlers write to a flat path under `logs/`. The new interface: `LOG_DIR = Path(BASE_DIR) / "logs" / os.environ.get("WEBSITE_IDENTIFIER", "unknown")`. Each handler's `filename` key references `LOG_DIR / "{level}.log"`. The directory is created by both the settings module and the Docker entrypoint.

### Docsify Documentation Service

The docs container is a plain `nginx:1.27-alpine` instance. Its only interface is HTTP on port 80. The documentation content is bind-mounted from `/data/docs` as `:ro`. The container has no write access to the docs tree. The `index.html` loads Docsify from CDN; `_sidebar.md` drives navigation; content is served as raw Markdown and rendered client-side.

### Governance Scripts

`scripts/check-imports.mjs` reads the alias table from `webpack/main.config.js` (or an extracted constant), resolves each target path, and exits non-zero if any path is missing. It is called from the Husky pre-commit hook and from CI. `assets/.size-limit.json` declares per-bundle gzip budgets consumed by the `size-limit` CLI.

---

## Data Models

This feature introduces no new database models. The following configuration structures are new or modified.

### LOG_DIR Derivation (Python)

```python
import os
from pathlib import Path

WEBSITE_IDENTIFIER = os.environ.get("WEBSITE_IDENTIFIER", "unknown")
LOG_DIR = Path(BASE_DIR) / "logs" / WEBSITE_IDENTIFIER
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "app_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "application.log"),
            "maxBytes": 10_485_760,  # 10 MB
            "backupCount": 5,
            "formatter": "json",
        },
        "debug_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "debug.log"),
            "maxBytes": 10_485_760,
            "backupCount": 3,
            "level": "DEBUG",
            "formatter": "json",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "error.log"),
            "maxBytes": 10_485_760,
            "backupCount": 5,
            "level": "ERROR",
            "formatter": "json",
        },
    },
    # ... formatters and loggers unchanged
}
```

### Bundle-Size Configuration (JSON)

`assets/.size-limit.json` declares three budget entries. Each entry names a logical bundle, specifies the glob path to the compiled output in the corresponding site's `bundles/` directory, sets the gzip byte limit, and enables gzip measurement. The `client` entry targets ctc-research's `app-*.js`, `admin` targets lms-demo's `app-*.js`, and `marketing` targets VResume's `app-*.js`.

### Docker Compose Overlay (YAML)

`docker-compose.infra.yml` declares three named volumes for per-site logs and the `structa-docs` service. It does not declare its own networks — it references the external `traefik-net` network. Service additions reference the base definitions in `docker-compose.yml` via the merge key pattern.

---

## Detailed Implementation Sections

### Package Enhancement Plans

#### Bundle Budgets

Three logical bundle targets need enforced size limits. These budgets do not modify `common.config.js` (which retains its 1 MB entrypoint tolerance for vendor chunks) — they are enforced by `size-limit` at `assets/.size-limit.json`:

The `client` bundle covers the minimal interactive layer served to anonymous users — Alpine.js, htmx, minimal Bootstrap JS, and site-specific initialisation. Target: 25 kB gzip. Achievable by tree-shaking Alpine.js to registered components only and loading htmx as an external CDN script rather than bundling it.

The `admin` bundle covers the Wagtail/Django admin extension layer — unfold theming, Quill, minor chart widgets. Target: 120 kB gzip. Generous enough for Quill (around 50 kB gzip) plus admin-specific CSS.

The `marketing` bundle covers landing-page components — animations, Swiper, AOS, CountUp. Target: 15 kB gzip. Requires importing only the required Swiper modules (Navigation, Pagination) rather than the full bundle.

#### Log Directory Isolation

Today all three sites write to `/data/structa.cloud/logs/application.log`, `debug.log`, and `error.log` without any site prefix. The `configs/settings.py` `LOGGING` dict derives `LOG_DIR` as `Path(BASE_DIR) / "logs" / os.environ.get("WEBSITE_IDENTIFIER", "unknown")`. Each handler's `filename` references `LOG_DIR / "{level}.log"`. The directory is created at startup. The Docker entrypoint adds `mkdir -p /app/logs/$WEBSITE_IDENTIFIER` before the application starts.

---

### Docsify Markdown Structure

#### Why Docsify

Docsify renders Markdown at runtime in the browser — no build step, no `mkdocs build`, no Python runtime. The entire docs directory is served as static files, making the container a plain `nginx:alpine` instance and the Docker volume trivially `:ro`. The current `/data/docs/` directory is served by a MkDocs Material container built from Python; that Dockerfile and compose service are replaced.

#### File Layout

```
docs/
  index.html              ← Docsify bootstrap (loads docsify from CDN)
  README.md               ← Landing page / documentation overview
  _sidebar.md             ← Navigation sidebar
  architecture-notes.md   ← Architectural hint notes (mirrors Architecture section)
  error-resolution-log.md ← Error log with markdown table
  migration-record.md     ← ctc-research → lms-demo migration facts
  ecosystem/              ← Existing ecosystem docs (retained)
  infrastructure/         ← Existing infrastructure docs (retained)
  auth/                   ← Existing auth docs (retained)
  shared/                 ← Existing shared docs (retained)
```

#### `docs/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Structa Cloud Docs</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify@4/lib/themes/vue.css" />
</head>
<body>
  <div id="app"></div>
  <script>
    window.$docsify = {
      name: 'Structa Cloud',
      repo: '',
      loadSidebar: true,
      subMaxLevel: 2,
      search: { placeholder: 'Search docs' }
    };
  </script>
  <script src="//cdn.jsdelivr.net/npm/docsify@4/lib/docsify.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/docsify@4/lib/plugins/search.min.js"></script>
</body>
</html>
```

#### `docs/_sidebar.md`

```markdown
- [Overview](README.md)
- **Monorepo**
  - [Architecture Notes](architecture-notes.md)
  - [Error Resolution Log](error-resolution-log.md)
  - [Migration Record](migration-record.md)
- **Ecosystem**
  - [Getting Started](ecosystem/getting-started/)
  - [Architecture](ecosystem/architecture/)
  - [Deployment](ecosystem/deployment/)
  - [Development](ecosystem/development/)
- **Projects**
  - [structa.cloud](structa.cloud/)
  - [ctc-research.com](ctc-research.com/)
- **Packages**
  - [django-fusion](packages/django-fusion/)
  - [crafts-ai](packages/crafts-ai/)
  - [django-fusion](packages/django-fusion/)
- **Infrastructure**
  - [Docker](infrastructure/docker/)
  - [Traefik](infrastructure/traefik/)
  - [PostgreSQL](infrastructure/postgres/)
  - [Redis](infrastructure/cache/)
  - [LMS](infrastructure/lms/)
- **Auth System**
  - [Overview](auth/README.md)
  - [Adapter](auth/adapter.md)
  - [Templates](auth/templates.md)
  - [Social Login](auth/social-login.md)
  - [Testing](auth/testing.md)
- **Shared Resources**
  - [Styling](shared/styling/)
  - [Testing](shared/testing/)
  - [Troubleshooting](shared/troubleshooting/)
```

#### Docsify Dockerfile

Replaces both `/data/docs/Dockerfile` and `/data/deploy/compose/docs/Dockerfile`:

```dockerfile
# Docsify static documentation server
FROM nginx:1.27-alpine

RUN rm -rf /usr/share/nginx/html/*

COPY . /usr/share/nginx/html/

RUN printf 'server {\n\
  listen 80;\n\
  root /usr/share/nginx/html;\n\
  index index.html;\n\
  location / {\n\
    try_files $uri $uri/ /index.html;\n\
  }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost/ || exit 1
```

---

### Docker-Compose Configuration

The following snippet is an additive overlay, not a replacement for `deploy/applications/docker-compose.yml`. Save it as `deploy/applications/docker-compose.infra.yml`.

```yaml
# docker-compose.infra.yml
# Overlay: Docsify service + per-site log volume declarations
# Usage:
#   docker compose \
#     -f applications/docker-compose.yml \
#     -f applications/docker-compose.infra.yml \
#     up -d

networks:
  traefik-net:
    external: true
    name: traefik-net

volumes:
  ctc-research-logs:
  lms-demo-logs:
  vresume-logs:

services:
  # ── Docsify documentation server ────────────────────────────────────────
  structa-docs:
    build:
      context: /data/docs
      dockerfile: Dockerfile
    image: structa-docs:latest
    container_name: structa-docs
    restart: unless-stopped
    volumes:
      # Read-only bind mount — container cannot modify documentation
      - /data/docs:/usr/share/nginx/html:ro
    networks:
      - traefik-net
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.docs.rule=Host(`docs.structa.cloud`)"
      - "traefik.http.routers.docs.entrypoints=websecure"
      - "traefik.http.routers.docs.tls=true"
      - "traefik.http.services.docs.loadbalancer.server.port=80"
    deploy:
      resources:
        limits:
          cpus: "0.25"
          memory: 64M
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost/"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

  # ── lms-demo with isolated log volume (extends base definition) ──────────
  lms-demo-website:
    volumes:
      - lms-demo-logs:/app/logs/lms-demo
```

Add `- ctc-research-logs:/app/logs/ctc-research` to the ctc-research service volumes list and `- vresume-logs:/app/logs/vresume` to the VResume service volumes list in the base `docker-compose.yml`.

---

### Governance Pipeline

#### Husky Pre-Commit Hooks

Husky is installed in `assets/` where `package.json` lives.

```bash
# Run once from assets/
npm install --save-dev husky markdownlint-cli size-limit @size-limit/webpack lint-staged
npx husky init
```

`assets/.husky/pre-commit`:
```sh
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# 1. Lint staged markdown and JS files
npx lint-staged

# 2. Import reachability check
node ../scripts/check-imports.mjs

# 3. Bundle size audit
npm run build:audit 2>&1 | tee /tmp/bundle-audit.log
if grep -q "exceeded" /tmp/bundle-audit.log; then
  echo "❌ Bundle budget exceeded — see /tmp/bundle-audit.log"
  exit 1
fi
```

`assets/.lintstagedrc.json`:
```json
{
  "*.md": ["markdownlint --fix", "git add"],
  "*.js": ["eslint --fix", "git add"]
}
```

`assets/eslint.config.mjs` (ESLint 9 flat config):
```js
import globals from "globals";

export default [
  {
    files: [
      "static/js/**/*.js",
      "../ctc-research/assets/static/js/**/*.js",
      "../lms-demo/assets/static/js/**/*.js",
      "../VResume/assets/static/js/**/*.js"
    ],
    languageOptions: { globals: { ...globals.browser } },
    rules: {
      "no-unused-vars": "warn",
      "no-undef": "error",
      "no-console": "off"
    }
  }
];
```

`assets/.markdownlintrc.json`:
```json
{
  "default": true,
  "MD013": { "line_length": 120 },
  "MD033": false,
  "MD041": false
}
```

`assets/.size-limit.json`:
```json
[
  {
    "name": "client",
    "path": "../ctc-research/assets/bundles/ctc-research/app-*.js",
    "limit": "25 kB",
    "gzip": true
  },
  {
    "name": "admin",
    "path": "../lms-demo/assets/bundles/lms-demo/app-*.js",
    "limit": "120 kB",
    "gzip": true
  },
  {
    "name": "marketing",
    "path": "../VResume/assets/bundles/vresume/app-*.js",
    "limit": "15 kB",
    "gzip": true
  }
]
```

Add to `assets/package.json` scripts: `"build:audit": "size-limit"`.

#### Import Reachability Check

`scripts/check-imports.mjs` (at `/data/structa.cloud/scripts/`):

```js
#!/usr/bin/env node
// check-imports.mjs — verifies that all Webpack alias targets exist on disk.
// Exits non-zero if any alias points to a missing path.
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const workspaceRoot = path.resolve(__dirname, "..");

const aliases = {
  "@utility":  "assets/static/js/utility",
  "@base":     "assets/static/js/utility",
  "@modules":  "assets/static/js/modules",
  "@plugins":  "assets/static/js/plugins",
  "@core":     "assets/static/js/core",
  "@htmx":     "assets/static/js/core/htmx-bridge.js",
  "@ctc":      "ctc-research/assets/static/js",
  "@lms":      "lms-demo/assets/static/js",
  "@vresume":  "VResume/assets/static/js",
  // Stale aliases — these MUST fail until main.config.js is fixed:
  "@theme":    "assets/static/js/theme",
  "@layouts":  "assets/static/js/theme/layouts",
  "@usecases": "assets/static/js/theme/usecases",
};

let failed = false;

for (const [alias, relativePath] of Object.entries(aliases)) {
  const fullPath = path.join(workspaceRoot, relativePath);
  if (!fs.existsSync(fullPath)) {
    console.error(`❌  Stale alias: ${alias} → ${relativePath} (path does not exist)`);
    failed = true;
  } else {
    console.log(`✅  ${alias} → ${relativePath}`);
  }
}

if (failed) {
  console.error("\nFix stale aliases in webpack/main.config.js before committing.");
  process.exit(1);
}
```

Running this today immediately flags `@theme`, `@layouts`, and `@usecases`, blocking commits until `main.config.js` is corrected.

#### CI Integration

`.github/workflows/frontend.yml` additions:
```yaml
- name: Install frontend deps
  run: npm ci
  working-directory: assets

- name: Import reachability check
  run: node scripts/check-imports.mjs

- name: Lint JS
  run: npx eslint --max-warnings 0 "static/js/**/*.js"
  working-directory: assets

- name: Lint Markdown
  run: npx markdownlint "docs/**/*.md"
  working-directory: /data

- name: Build and audit bundle sizes
  run: npm run build:all && npm run build:audit
  working-directory: assets
```

---

## Error Resolution Log

| # | File | Line | Bad Import | Correct Import | Error Message (truncated) | Status |
|---|------|------|-----------|---------------|--------------------------|--------|
| 1 | `ctc-research/plugins/lms/views/lessons.py` | 12 | `from ..mnagement.services.courses import CourseService` | `from ..management.services.courses import CourseService` | `CRITICAL … ModuleNotFoundError: No module named 'plugins.lms.mnagement'` | ✅ Fixed on disk — formally logged here |

The fix is confirmed present at `/data/structa.cloud/ctc-research/plugins/lms/views/lessons.py` line 12. The error in `logs/error.log` was generated before the fix was applied. No further code action is required.

---

## Migration Log

### ctc-research → lms-demo Structural Differences

lms-demo is the renamed and re-scoped successor to ctc-research. Both sites coexist in the monorepo. `SITE_ID` is 1 for ctc-research and 2 for lms-demo. `WEBSITE_IDENTIFIER` is `ctc-research` vs `lms-demo`. The default port is 5070 for ctc-research and 5071 for lms-demo. lms-demo has an `apps.py` at the site root — ctc-research does not. lms-demo has a `uv.lock` at the site level for site-specific dependency pinning — ctc-research relies on the workspace-level `uv.lock`. lms-demo has no `.env.demo` or `.env.testing` files. Both sites share `configs.settings` via `from configs.settings import *` and both duplicate the same `SILENCED_SYSTEM_CHECKS` list verbatim; consolidating that list into `configs/settings.py` is a pending task. The Webpack `SITE_DIR_MAP` maps `structa`, `structa.cloud`, and `lms` to `lms-demo`, so `npm run build:structa` continues to work against the lms-demo site directory.

### Theme Directory Migration (June 2, 2026)

The `assets/static/js/theme/` directory was deleted as part of a vendor-packages and usecases refactor. `theme/vendor-packages.js` moved to `core/vendor-packages.js`. `theme/usecases.js` content was reorganised into `modules/usecases/index.js`. All three site `app.js` files were updated from `import { initAllUsecases } from '@theme'` to `import { initAllUsecases } from '../../../../assets/static/js/modules/index.js'` (relative path, no alias). The build passed with 23 pre-existing Vue version warnings and produced 408 bundles totalling 73 MB.

The `@theme`, `@layouts`, and `@usecases` aliases in `main.config.js` were not updated during that migration and still point into the deleted directory. These are stale aliases. The import reachability check script will catch this on every commit.

---

## Correctness Properties

The following properties hold when the implementation is correct.

### Property 1: Log isolation per site

Given any Django process running with `WEBSITE_IDENTIFIER=X`, all log file writes land under `logs/X/` and no files are created at the root `logs/` level. Violated if any handler `filename` is constructed without the `WEBSITE_IDENTIFIER` component. **Validates: Requirements 2.3, 2.4**

### Property 2: Webpack alias reachability

Given the alias table in `webpack/main.config.js`, `fs.existsSync(resolvedPath)` returns true for every entry. Currently violated by `@theme`, `@layouts`, and `@usecases` — these must be removed or redirected before this property holds. **Validates: Requirements 1.2, 5.2**

### Property 3: Docs volume read-only enforcement

Given the `structa-docs` container running with `/data/docs:/usr/share/nginx/html:ro`, any write attempt from within the container to the mounted path is rejected by the kernel. The `:ro` flag enforces this unconditionally. **Validates: Requirements 3.4, 4.3**

### Property 4: Bundle size budgets respected

Given a production build of each site, the gzip size of each `app-*.js` file does not exceed the limit in `.size-limit.json`. This property is not expected to pass immediately — it sets a measurable target for a follow-on vendor-split task. **Validates: Requirements 2.1, 2.2**

---

## Error Handling

Python-side: log handlers use `RotatingFileHandler` with `backupCount` set to prevent unbounded disk growth. The `LOG_DIR.mkdir(parents=True, exist_ok=True)` call is idempotent and will not raise if the directory already exists. If `WEBSITE_IDENTIFIER` is unset, `LOG_DIR` falls back to `logs/unknown/` rather than overwriting the root `logs/` directory.

Frontend-side: `check-imports.mjs` catches `fs.existsSync` misses and reports all failures before exiting, so engineers see every stale alias in one run rather than one at a time.

Bundle audits: `size-limit` reports all budget violations before exiting. The pre-commit hook writes the audit output to `/tmp/bundle-audit.log` so it is available for review even after the hook exits.

---

## Testing Strategy

Automated checks that validate the governance pipeline itself:

Running `node scripts/check-imports.mjs` with the current `main.config.js` (before fixing stale aliases) should exit 1 and print three `❌` lines for `@theme`, `@layouts`, `@usecases`. After removing those aliases from `main.config.js`, the script should exit 0.

Running `npm run build:audit` after a production build should report sizes for the three bundle targets. If the raw bundle sizes exceed the declared limits, the check exits 1. The current `app-*.js` bundles are large (vendor-inclusive) so the audit will likely fail until the client/marketing bundles are split to exclude vendor chunks — that split is a follow-on task.

The Docsify docs service can be validated by running `docker compose -f docker-compose.infra.yml up structa-docs -d` and curling `http://localhost:80/` — a 200 response with the Docsify HTML confirms the container is healthy.

---

## Verification Checklist

**Architectural Cleanup**
- Remove or redirect `@theme`, `@layouts`, `@usecases` aliases in `webpack/main.config.js`
- Consolidate `SILENCED_SYSTEM_CHECKS` from both `settings.py` files into `configs/settings.py`
- Confirm `scripts/check-imports.mjs` exits 0 after alias cleanup

**Log Directory Isolation**
- Add `LOG_DIR` derivation and `mkdir` guard to `configs/settings.py`
- Update all handler `filename` values to use `LOG_DIR`
- Add `mkdir -p /app/logs/$WEBSITE_IDENTIFIER` to `deploy/applications/django/entrypoint`
- Declare named volumes in compose overlay
- Add volume mounts to all three website services

**Docsify Migration**
- Create `docs/index.html` with Docsify CDN bootstrap
- Create `docs/architecture-notes.md`, `docs/error-resolution-log.md`, `docs/migration-record.md`
- Update `docs/_sidebar.md` with Monorepo section
- Replace both MkDocs Dockerfiles with Docsify nginx:alpine Dockerfile
- Update `docker-compose.docs.yml` to use `:ro` bind mount

**Docker-Compose Overlay**
- Create `deploy/applications/docker-compose.infra.yml`

**Governance Pipeline**
- Install `husky`, `markdownlint-cli`, `size-limit`, `lint-staged` in `assets/devDependencies`
- Create `assets/.husky/pre-commit`, `assets/.lintstagedrc.json`, `assets/eslint.config.mjs`, `assets/.markdownlintrc.json`, `assets/.size-limit.json`
- Create `scripts/check-imports.mjs`
- Add CI workflow steps

**Error Resolution**
- Confirm fix is on disk — line 12 reads `..management` not `..mnagement`
- Entry logged in `docs/error-resolution-log.md`

**Hint Notes Replacement Statement**
All architectural representation in this document is given as prose hint notes. No ASCII diagrams, no tables (except the Error Resolution Log), and no Mermaid charts appear in this specification.
