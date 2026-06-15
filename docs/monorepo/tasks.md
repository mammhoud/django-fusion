# Implementation Plan: Monorepo Frontend Infrastructure

## Overview

Six task groups implement the specification in dependency order: architectural cleanup must precede the governance pipeline (which checks for the stale aliases), log isolation must precede the Docker compose overlay (which declares the log volumes), and Docsify content creation must precede the Dockerfile replacement. All groups can proceed in parallel except where noted.

## Tasks

### Group 1: Architectural Cleanup

- [ ] 1.1 Remove stale `@theme`, `@layouts`, `@usecases` aliases from `webpack/main.config.js`; update `@theme` → `@modules` pointing to `assets/static/js/modules` if any existing code references it
- [ ] 1.2 Consolidate duplicated `SILENCED_SYSTEM_CHECKS` list from `ctc-research/settings.py` and `lms-demo/settings.py` into `configs/settings.py`
- [ ] 1.3 Run `npm run build:ctc && npm run build:structa && npm run build:vresume` and confirm all three builds pass with no new errors

### Group 2: Log Directory Isolation

- [ ] 2.1 Add `WEBSITE_IDENTIFIER`-keyed `LOG_DIR` derivation to `configs/settings.py` LOGGING configuration (depends on: none)
- [ ] 2.2 Add `LOG_DIR.mkdir(parents=True, exist_ok=True)` guard immediately before the `LOGGING` dict
- [ ] 2.3 Update all `FileHandler` `filename` values to reference `LOG_DIR / "application.log"`, `LOG_DIR / "debug.log"`, `LOG_DIR / "error.log"`
- [ ] 2.4 Add `mkdir -p /app/logs/$WEBSITE_IDENTIFIER` to `deploy/applications/django/entrypoint` before the final `exec` call
- [ ] 2.5 Verify isolation locally: start each Django server with its `WEBSITE_IDENTIFIER` set and confirm log files appear in the correct subdirectory

### Group 3: Docsify Migration

- [ ] 3.1 Create `docs/index.html` with the Docsify CDN bootstrap page (content specified in design.md)
- [ ] 3.2 Create `docs/architecture-notes.md` with the architectural hint notes from design.md §Architecture
- [ ] 3.3 Create `docs/error-resolution-log.md` with the error resolution table (single entry: `mnagement` typo in lessons.py line 12)
- [ ] 3.4 Create `docs/migration-record.md` with the ctc-research → lms-demo structural diff and theme migration facts from design.md §Migration Log
- [ ] 3.5 Update `docs/_sidebar.md` to add the Monorepo section (Architecture Notes, Error Resolution Log, Migration Record) at the top, retaining all existing sections
- [ ] 3.6 Replace `/data/docs/Dockerfile` with the Docsify `nginx:1.27-alpine` Dockerfile from design.md §Docsify Dockerfile
- [ ] 3.7 Replace `/data/deploy/compose/docs/Dockerfile` with the same Docsify Dockerfile
- [ ] 3.8 Update `/data/deploy/applications/docker-compose.docs.yml`: use the new image, remove `mkdocs.yml` and `README.md` volume mounts, change docs bind mount to `/data/docs:/usr/share/nginx/html:ro`, update healthcheck to use `wget`

### Group 4: Docker-Compose Overlay

- [ ] 4.1 Create `deploy/applications/docker-compose.infra.yml` with: named volume declarations (`ctc-research-logs`, `lms-demo-logs`, `vresume-logs`), `structa-docs` Docsify service with `:ro` bind mount, `lms-demo-website` log volume addition (depends on: 2.5, 3.8)
- [ ] 4.2 Add `- ctc-research-logs:/app/logs/ctc-research` to the `ctc-research-website` volumes list in `docker-compose.yml`
- [ ] 4.3 Add `- vresume-logs:/app/logs/vresume` to the `vresume-website` volumes list in `docker-compose.yml`

### Group 5: Governance Pipeline

- [ ] 5.1 Install `husky`, `markdownlint-cli`, `size-limit`, `@size-limit/webpack`, `lint-staged` in `assets/devDependencies` (run `npm install --save-dev` in `assets/`)
- [ ] 5.2 Run `npx husky init` from `assets/` to create `assets/.husky/` directory
- [ ] 5.3 Create `assets/.husky/pre-commit` with lint-staged, import-check, and bundle-audit steps (content in design.md §Husky Pre-Commit Hooks)
- [ ] 5.4 Create `assets/.lintstagedrc.json` with markdownlint for `*.md` and eslint for `*.js`
- [ ] 5.5 Create `assets/eslint.config.mjs` (flat ESLint 9 config) covering all four JS source trees
- [ ] 5.6 Create `assets/.markdownlintrc.json` with MD013 line-length 120, MD033/MD041 disabled
- [ ] 5.7 Create `assets/.size-limit.json` with client (25 kB), admin (120 kB), marketing (15 kB) budgets pointing to `bundles/` output globs
- [ ] 5.8 Add `"build:audit": "size-limit"` to `assets/package.json` scripts
- [ ] 5.9 Create `scripts/check-imports.mjs` at `/data/structa.cloud/scripts/` (content in design.md §Import Reachability Check); verify it exits 1 before alias cleanup and 0 after (depends on: 1.1)
- [ ] 5.10 Add CI steps to `.github/workflows/` for import reachability, eslint, markdownlint, and bundle audit (content in design.md §CI Integration)

### Group 6: Verification

- [ ] 6.1 Confirm `ctc-research/plugins/lms/views/lessons.py` line 12 reads `from ..management.services.courses import CourseService` (no code change needed — verify only)
- [ ] 6.2 Run `docker compose -f applications/docker-compose.yml -f applications/docker-compose.infra.yml up structa-docs -d` and confirm `http://localhost:80/` returns 200 with Docsify HTML
- [ ] 6.3 Start ctc-research and lms-demo with `WEBSITE_IDENTIFIER` set correctly and confirm log files appear in `logs/ctc-research/` and `logs/lms-demo/` respectively, not the root `logs/` directory
- [ ] 6.4 Run `node scripts/check-imports.mjs` and confirm exit 0 (all aliases resolve)
- [ ] 6.5 Run `npm run build:audit` and review the size-limit report; document any budgets that currently exceed the target (expected: app bundles may be oversized until vendor splitting is implemented as a follow-on task)

## Task Dependency Graph

```json
{
  "waves": [
    {
      "wave": 1,
      "tasks": ["1.1", "1.2", "2.1", "2.2", "2.3", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "5.1", "5.2"]
    },
    {
      "wave": 2,
      "tasks": ["1.3", "2.4", "2.5", "3.8", "5.3", "5.4", "5.5", "5.6", "5.7", "5.8"],
      "dependsOn": ["wave1"]
    },
    {
      "wave": 3,
      "tasks": ["4.1", "4.2", "4.3", "5.9", "5.10"],
      "dependsOn": ["wave2"]
    },
    {
      "wave": 4,
      "tasks": ["6.1", "6.2", "6.3", "6.4", "6.5"],
      "dependsOn": ["wave3"]
    }
  ]
}
```

Group 1 (cleanup) → Group 5, task 5.9 (import check validates the cleanup)
Group 2 (log isolation) → Group 4 (compose overlay needs volume paths confirmed)
Group 3 (Docsify content) → Group 4, task 4.1 (compose overlay references the docs image)
Groups 1, 2, 3 → Group 6 (verification)

## Notes

The bundle-size audit (task 5.7) will likely report that the `client` and `marketing` budgets are exceeded by the current large bundles. This is expected — the budgets set a target for a follow-on vendor-split task and serve as a baseline measurement rather than a hard gate in the initial rollout. The `admin` budget at 120 kB is more likely to pass given lms-demo's admin bundle is primarily Quill plus admin CSS.

The `@theme`, `@layouts`, `@usecases` aliases are confirmed stale based on live codebase inspection. Task 1.1 is the single highest-priority item — it eliminates a latent build failure risk that could surface if any developer adds a new file importing `@theme`.
