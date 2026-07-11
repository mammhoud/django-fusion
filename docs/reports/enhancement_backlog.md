# Enhancement Backlog From Retired Plans

The `.plans/` directory was retired after consolidating its active requirements into tracked documentation and stability fixes. This file preserves the important unfinished work so the repository can remove planning artifacts without losing scope.

## Not done yet

| Priority | Enhancement | Source plan context | Acceptance criteria |
|---|---|---|---|
| High | Confirm `django-fusion`, `django-fusion`, and `ceptor-ai` imports in every active environment. | Generic branch execution plan was blocked by missing `django_fusion` during URL import checks. | `uv sync` completes, `python -c "import django_fusion, django_fusion, ceptor_ai"` succeeds, and both site URL modules import without errors. |
| High | Run targeted site test suites after dependencies are available. | Alliance targeted pytest was blocked by missing/unavailable pytest dependencies in the active environment. | `uv run pytest tests/websites tests/unit` completes or has documented, reproducible failures. |
| High | Add CI smoke checks for Docker build and compose configuration. | Docker deployment plans required stable deployment verification. | CI runs `docker compose ... config`, builds `compose/Dockerfile`, and fails on missing workspace paths. |
| Medium | Integrate notification/SSE JavaScript modules into the real asset tree. | JS asset plan kept prototype modules in `.plans/.js.plans`. | Notification modules live under the tracked frontend source tree, are included in webpack entries, and `npm run build` emits bundles. |
| Medium | Add HTMX notification smoke tests. | JS asset plan described `HX-Trigger` and browser console checks but did not implement automated coverage. | A small browser or static test verifies notification globals and HTMX trigger handling. |
| Medium | Normalize site names in legacy docs and scripts. | Plans and old docs referenced `ctc-research.com`, `structa.cloud`, and `VResume` paths that do not match this checkout. | Root docs, scripts, and Docker defaults consistently use `ctc-research` and `lms-demo`, with aliases only where needed. |
| Low | Decide whether the docs are product docs or workspace docs. | Existing docs still include VResume/ThemeForest material. | Docs navigation clearly separates workspace/deployment docs from legacy product guide material, or legacy material is archived. |
| Low | Add production backup/restore runbooks. | Docker deployment checklist referenced persistence concerns. | Backup and restore commands for PostgreSQL volumes and media are documented and tested. |

## Requirements now represented in tracked files

- Unique multi-site thin-layer architecture is documented in `docs/architecture/unique_architecture.md`.
- Docker deployment flow and stability gates are documented in `docs/deployment_flow.md` and `docs/deployment.md`.
- Actual workspace member names are enforced in `pyproject.toml`, `manage.py`, and `compose/Dockerfile`.
- Remaining plan items are tracked in this backlog instead of `.plans/`.
