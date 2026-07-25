# GitHub Actions — CI Workflows Reference

> **Directory:** `.github/`
> **Updated:** 2026-07-25

---

## Workflow Inventory

| Workflow | Name | Trigger | Jobs | Status |
|----------|------|---------|------|:------:|
| `js-test.yml` | JS Tests (vitest + Playwright E2E) | PR, push, manual | 5 | ✅ Active |
| `pytest-core.yml` | pytest-core | PR, push, manual | 1 | ✅ Active |
| `check-extras.yml` | check-extras | PR, push, manual | 1 | ✅ Active |
| `deploy-ci.yml` | deploy-ci (preflight + docs validation) | PR, push, manual | 2 | ✅ Active |

---

## `js-test.yml` — JavaScript/TypeScript Tests

**Triggers:** PR + push on `projects/lms/**`, `projects/pos/**`, and `.github/workflows/js-test.yml` changes.

### Jobs (5 total, all parallel)

| Job | Project | Runs | Timeout | Node |
|-----|---------|------|:------:|:----:|
| `lms-frontend-test` | `projects/lms/front-end` | `npm run test` (Vitest, 354 tests) | 10m | 20 |
| `lms-frontend-e2e` | `projects/lms/front-end` | `npm run test:e2e` (Playwright, port 3457) | 15m | 20 |
| `lms-test` | `projects/lms/lms` | `npm run test` (Vitest, 79 tests) | 10m | 20 |
| `lms-e2e` | `projects/lms/lms` | `npm run test:e2e` (Playwright, port 3000) | 15m | 20 |
| `pos-e2e` | `projects/pos/pos-e2e` | API-only E2E (bolt pattern, no browser) | 10m | 20 |

> **Note:** POS API tests use `test.skip(true, 'Sidecar not running')` and will
> report "0 passed, 0 failed, all skipped" in CI unless a sidecar is running.

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Parallel jobs** | No `needs` dependencies — all unit + E2E jobs run concurrently for faster CI |
| **POS: API-only** | Tauri doesn't run headless in CI — uses Playwright `request` fixture |
| **Artifacts on failure** | Uploads Playwright report + test results for debugging |
| **Concurrency** | Cancels duplicate in-progress runs on the same PR/branch |
| **Path triggers** | Only triggers on changes to relevant project directories |
| **Ports** | LMS front-end: 3457, LMS lms: 3000 (Next.js defaults) |

### E2E Port Configuration

| Project | Port | webServer Command | Config |
|---------|:----:|-------------------|--------|
| `lms/front-end` | 3457 | `npx next dev -p 3457` | `playwright.config.ts` |
| `lms/lms` | 3000 | `npx next dev -p 3000` | `playwright.config.ts` |

---

## `pytest-core.yml` — Python Tests

**Triggers:** PR + push on `tests/**`, `projects/**`, and `.github/workflows/pytest-core.yml` changes.

### Job

| Job | Working Dir | Runs | Timeout | Python |
|-----|------------|------|:------:|:------:|
| `pytest` | `projects/` | `uv run pytest` | 15m | 3.11 |

### Dependency Setup

- Uses `astral-sh/setup-uv@v2` for dependency management
- `uv sync` installs from `projects/pyproject.toml`
- Tests discover from `projects/pyproject.toml` → `tool.pytest.ini_options.testpaths`

---

## `check-extras.yml` — Extras Validation

**Triggers:** PR + push on `libs/**/*.md`, `**/pyproject.toml`, and related files.

### Job

| Job | Runs | Timeout | Python |
|-----|------|:------:|:------:|
| `check-extras` | `python3 applications/scripts/staging/check_extras_in_docs.py` | 5m | 3.11 |

---

## `deploy-ci.yml` — Deploy Preflight + Docs Validation

**Triggers:** PR + push on Docker compose files, Makefile, and related files.

### Jobs (2)

| Job | Runs | Timeout |
|-----|------|:------:|
| `preflight` | Composite Action: `make deploy-ci` (docker version + preflight gates) | 5m |
| `markdown-links` | `python3 applications/scripts/staging/check_markdown_links.py` | 5m |

### Preflight Steps

1. `docker version` — verify Docker daemon is available
2. `make deploy-ci` — runs `deploy-preflight → preflight-network → check-docker + validate-deploy-order + create-networks`

---

## Composite Action: `deploy-preflight`

**File:** `.github/actions/deploy-preflight/action.yml`

Reusable composite action that runs the project-level preflight gate. Can be called from any repo:

```yaml
- uses: ./.github/actions/deploy-preflight
  with:
    make-target: deploy-ci      # optional, default: deploy-ci
    working-directory: .        # optional, default: .
```

---

## Adding a New Workflow

1. Create `.github/workflows/<name>.yml`
2. Follow existing conventions:
   - `on:` with both `pull_request` and `push` triggers
   - `paths:` filters to only run on relevant file changes
   - `workflow_dispatch:` for manual triggering
   - `timeout-minutes:` on every job
   - `concurrency:` group if needed to prevent duplicate runs
3. Validate YAML: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/<name>.yml'))"`
4. Document in this README

---

## Test Configuration Quick Reference

### Local Testing

```bash
# YAML validation
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/js-test.yml'))"

# GitHub Actions dry-run (requires act)
act pull_request -W .github/workflows/js-test.yml -v

# GitHub Actions lint (requires actionlint)
actionlint .github/workflows/

# Run the actual tests locally
cd projects/lms/front-end && npm run test:all
cd projects/lms/lms && npm run test:all
cd projects/pos/pos-e2e && npx playwright test tests/api/ --project=pos-full
```

### CI Environment Variables

| Variable | Set By | Used In |
|----------|--------|---------|
| `NODE_VERSION` | `actions/setup-node` (20) | All JS jobs |
| `PYTHON_VERSION` | `actions/setup-python` (3.11) | All Python jobs |
| `CI` | GitHub Actions (true) | `check_markdown_links.py` |

### Common Failure Modes

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `npm ci` fails | Missing `package-lock.json` | Run `npm install` locally and commit the lock file |
| `npx playwright install` fails | System deps missing | Add `--with-deps` flag |
| Playwright finds 0 tests | Empty test directory or `test.skip()` guard | `lms-e2e` has no tests yet (will pass silently); `pos-e2e` tests skip without sidecar |
| `uv sync` fails | `pyproject.toml` misconfigured | Verify `projects/pyproject.toml` has correct dependencies |
| `docker version` fails | Docker not available on runner | Use `ubuntu-latest` (has Docker pre-installed) |
