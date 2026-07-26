# GitHub Workflows & CI — AI Agent Instructions

Path: `.github/`

## Scope

This directory contains the GitHub Actions workflows, reusable composite actions, and CI configuration for the Structa Cloud monorepo. AI agents modifying anything under `.github/` or CI-related scripts should read this file first.

---

## Repository Context

Structa Cloud is a Django monorepo with multiple sites, shared assets, local libraries (`libs/django-fusion`, `libs/ceptor-ai`, `libs/django-bolt`), and a desktop POS app. CI is split across Python (pytest), JavaScript/TypeScript (Vitest + Playwright), and deployment preflight checks.

### Key monorepo docs

| Doc | Purpose |
|-----|---------|
| Root `AGENTS.md` | Monorepo-wide conventions, site paths, shared assets, testing strategy |
| `libs/django-fusion/AGENTS.md` | Component system, routing, canonical imports, template tags |
| `libs/ceptor-ai/AGENTS.md` | Orchestrator, agents, MCP server, tools registry |
| `libs/django-bolt/README.md` | High-performance Rust-backed API framework |
| `.github/README.md` | Workflow inventory and local testing commands |

---

## Workflow Inventory

| Workflow | File | Purpose | Trigger |
|----------|------|---------|---------|
| `pytest-core` | `workflows/pytest-core.yml` | Python tests via `uv run pytest` | `tests/**`, `projects/**` |
| `js-test` | `workflows/js-test.yml` | Vitest + Playwright E2E for LMS and POS | `projects/lms/**`, `projects/pos/**` |
| `fusion-ci` | `workflows/fusion-ci.yml` | Django checks, tests, and Next.js builds for fusion projects | `projects/cms-fusion/**`, `projects/lms-fusion/**`, `libs/django-fusion/**`, `libs/ceptor-ai/**`, `libs/django-bolt/**` |
| `check-extras` | `workflows/check-extras.yml` | Docs/extras validation | `libs/**/*.md`, `**/pyproject.toml` |
| `deploy-ci` | `workflows/deploy-ci.yml` | Deploy preflight + markdown link check | `Makefile`, compose files, `libs/**/*.md` |

### Reusable Composite Action

- `actions/deploy-preflight/action.yml` — runs `make deploy-ci` (Docker probe + preflight gates). Accepts `make-target` and `working-directory` inputs.

---

## Agent Rules for CI Changes

1. **Preserve path filters**: every workflow uses `paths:` filters to avoid running unrelated jobs. When adding a new project or script, update the relevant workflow's `paths:` list.
2. **Add `workflow_dispatch:`**: new workflows should support manual triggering.
3. **Set `timeout-minutes:` on every job**.
4. **Use `concurrency:` groups** for JS/Python jobs that could duplicate runs on the same PR/branch.
5. **Prefer composite actions** for reusable steps; document them in `.github/README.md`.
6. **Validate YAML** after editing:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('.github/workflows/<name>.yml'))"
   ```
7. **Document the change** in `.github/README.md` workflow inventory.

---

## Common CI Tasks

### Add a new Python test job
1. Create or extend a workflow in `.github/workflows/`.
2. Set `working-directory` if the project lives under `projects/`.
3. Use `astral-sh/setup-uv@v2` and `uv sync` / `uv run pytest`.
4. Add path filters and `workflow_dispatch:`.

### Add a new JS/TS test job
1. Use `actions/setup-node@v4` with `node-version: '20'`.
2. Set `cache-dependency-path` to the project's `package-lock.json`.
3. Run `npm ci`, then the relevant test command (`npm run test`, `npm run test:e2e`).
4. For Playwright, install browsers with `npx playwright install chromium --with-deps`.

### Add a new reusable composite action
1. Create a directory under `.github/actions/<action-name>/`.
2. Write `action.yml` with a clear `name`, `description`, and `inputs`.
3. Add a usage example to `.github/README.md`.
4. Reference it from a workflow to test integration.

---

## Local CI Verification

```bash
# Validate YAML
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/js-test.yml'))"

# Dry-run with act (if installed)
act pull_request -W .github/workflows/js-test.yml -v

# Lint workflows (if actionlint is installed)
actionlint .github/workflows/
```

---

## Submodule CI Notes

The monorepo depends on three git submodules under `libs/`:

| Submodule | Branch | CI Impact |
|-----------|--------|-----------|
| `libs/django-fusion` | `generic` | Python tests import it; `pytest-core.yml` runs its analyzer tests |
| `libs/ceptor-ai` | `generic` | Imported by some site plugins; keep on `pythonpath` |
| `libs/django-bolt` | `main` | Used by fusion projects; Rust extension not built in CI here |

- Submodules are checked out by `actions/checkout@v4` by default (recursive).
- Do not pin submodule branches in workflow files; branch mapping lives in `.gitmodules`.
- If a workflow needs a submodule-specific test, add a separate job or extend `pytest-core.yml`.

---

## CI Failure Triage

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `npm ci` fails | Missing `package-lock.json` | Run `npm install` locally and commit lock |
| Playwright finds 0 tests | Empty directory or `test.skip()` | Check test files / skip guards |
| `uv sync` fails | `pyproject.toml` misconfigured | Verify workspace deps and submodule paths |
| `docker version` fails | Runner lacks Docker | Ensure `ubuntu-latest` or self-hosted with Docker |
| Composite action input not found | Missing `inputs` or typo | Validate `action.yml` with `actionlint` |

---

## Related

- [`.github/README.md`](./README.md) — full workflow inventory and local testing guide
- [`../AGENTS.md`](../AGENTS.md) — monorepo-wide agent instructions
- [`../Makefile`](../Makefile) — root dispatcher for deploy preflight
- [`../projects/Makefile`](../projects/Makefile) — site-level command delegation
