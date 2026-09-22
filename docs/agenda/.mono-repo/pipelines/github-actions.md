---
Object type: Pipeline
Tags: pipeline, ci, cd, github-actions, automation
Status: Active
Related Features: component-framework
Related Releases: formint-editions-2026-08
---

# GitHub Actions — Workspace Checks & Tests

> **Description:** The CI/CD workflow set in `.github/` — `make check` / `make test` across projects, docs validation, and composite actions for reusable steps.

## Method

- Workflows delegate to `projects/Makefile` targets (e.g. `make check WEBSITE=structa.cloud`)
- Composite actions encapsulate repeated setup (Python, Node, Rust)
- Docs validation via `prepare-content` + `validate-content`

## Boundary

- Never run destructive/effectful steps (migrations, volume pruning, production deploys) in CI without explicit workflow intent

## Use case

Every push runs the narrowest relevant checks per project; failures block merge before deployment.

## Related

- → `docs-pipeline.md` — Docs automation
- → `../objects/pipeline.md` — Pipeline object type