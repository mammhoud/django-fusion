# GitHub Workflows & CI — AI Agent Instructions

**Scope:** `.github/`

Read the repository root `AGENTS.md` first. This directory contains GitHub
Actions workflows and reusable composite actions. It must reflect the current
monorepo paths and project aliases in `projects/Makefile`.

## Current CI surfaces

| Area | Current paths | Typical validation |
|---|---|---|
| Workspace Python | `tests/`, `projects/precis/precis-main/`, `libs/django-fusion/` | `uv run pytest`, Django checks |
| Precis Products | `projects/precis/precis-main/`, `projects/precis/precis-dev/` | backend tests, Astro check/build, Playwright |
| Syntara/Cypercloud | `projects/syntara/` | Django checks/tests, asset build |
| Formints POS | `projects/formints/` | pytest, Vitest, TypeScript, Rust, Playwright |
| Infrastructure | `application/`, root Makefile | Compose/YAML/proxy/deploy preflight |

Some workflows and docs retain `precis-lms`, `cms-fusion`, `lms`, `pos`, or
`cypercloud` as compatibility names. Before changing a path filter, inspect the
actual checkout and `projects/Makefile`; update aliases and filters together.
Do not silently add a filter for a nonexistent directory.

## Workflow rules

1. Preserve or deliberately update `paths:` filters when project boundaries
   change; a new product path must be covered by the relevant workflow.
2. New workflows must support `workflow_dispatch:`.
3. Set `timeout-minutes:` on every job.
4. Use `concurrency:` for duplicate Python/JS jobs where appropriate.
5. Prefer reusable composite actions for repeated setup/preflight steps.
6. Keep secrets in GitHub secret/context references or environment variables;
   never print them.
7. Document workflow additions/renames in `.github/README.md`.
8. Read the nearest product `AGENTS.md` before changing product-specific CI.

## Python jobs

Use the checked-in Python workspace configuration and the current project path:

```yaml
- uses: actions/checkout@v4
  with:
    submodules: recursive
- uses: astral-sh/setup-uv@v2
- run: uv sync
- run: uv run pytest
```

Set `working-directory` explicitly for `projects/precis/precis-main/backend`,
`projects/precis/precis-main/backend`, or a POS sidecar/backend job. Avoid assuming
that every Django project uses the same settings module.

## JavaScript, TypeScript, and Rust jobs

- Use each package's committed lockfile and package manager.
- Astro/TypeScript jobs should run the package's `check`, `test`, and/or `build`
  scripts from the relevant product directory.
- FormintA/native jobs may need `cargo check`/`cargo test` from its
  `src-tauri/` directory.
- FormintB/frontend and the shared POS E2E suite use their own `package.json`
  and Playwright/Vitest configuration.
- Install Playwright browsers only in jobs that actually run browser tests.

## Reusable deployment action

`.github/actions/deploy-preflight/action.yml` runs the repository's deployment
preflight target. It is a validation gate, not permission to deploy from every
workflow. Keep `make-target` and `working-directory` inputs documented and
validate the action with `actionlint` when available.

## Local verification

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/<name>.yml'))"
actionlint .github/workflows/              # if installed
act pull_request -W .github/workflows/<name>.yml -v  # if installed
make deploy-ci                            # preflight only; inspect recipe
```

Do not run deployment workflows against a real environment as a substitute for
local validation. Use isolated services and explicit environment configuration.

## Related guidance

- [`../AGENTS.md`](../AGENTS.md) — repository-wide structure and safety rules
- [`../projects/AGENTS.md`](../projects/AGENTS.md) — product dispatcher/aliases
- [`../application/AGENTS.md`](../application/AGENTS.md) — infrastructure CI
- [`../tests/AGENTS.md`](../tests/AGENTS.md) — test selection and fixtures
