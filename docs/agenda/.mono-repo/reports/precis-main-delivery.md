---
Object type: Report
Tags: report, precis, precis-main, deployment, fusion, nx, documentation
Status: Active
Type: Delivery
Owner: workspace
Related Project: precis-main
Related Plans: precis-main-render-flow
---

# Precis Main — Render Flow and Command Delivery Report

> **Description:** Evidence and operating guidance for the unified Precis Main render roads, local/production Compose commands, and Nx delegation.

## Finding

The product boundary is coherent, but the command surface needed an explicit environment split. The project Makefile had local build/check/backend tasks while the Nx metadata exposed an unsafe mixed redeploy command that implicitly loaded the local Compose override when it existed.

## Changes recorded

- Added `validate-local` and `deploy-local` for the overlay-backed developer stack.
- Added `validate-production` and `deploy-production` for the base Compose production stack with the root environment file.
- Added Nx targets for `check`, `test`, `build`, `deploy-local`, and `deploy-production`; all delegate to the project Makefile.
- Corrected the root `projects/Makefile` Precis Main asset branch so the shell `case` command has a complete line continuation.
- Added the canonical `landing-fusion-render-flow.html` reference and a project-local copy.
- Linked the command contract from the Precis product docs and agenda project graph.

## Verification plan

| Check | Command | Evidence |
|---|---|---|
| Project Makefile parsing | `make -n validate-local` | No recipe execution; validates target expansion |
| Production Makefile parsing | `make -n validate-production` | No recipe execution; validates target expansion |
| Dispatcher selection | `cd projects && make show-config WEBSITE=structa.cloud` | Confirms canonical site and Compose path |
| Nx metadata | `npx nx show project precis-main-assets` | Confirms graph targets and delegation |
| HTML document | `node` parser/check or browser preview | Valid markup and responsive layout |
| Docs hygiene | `git diff --check` | No whitespace errors |

## Follow-up opportunities

- Add a CI-only `verify-render-roads` target that probes full HTML, HTMX, and JSON responses without starting a deployment.
- Add a Playwright project workflow for local overlay startup and a separate production smoke workflow that never runs seed commands.
- Add generated command tables to the project docs only if the Makefile target names remain stable.

## Remarks & Notes

- This report documents command wiring; it does not authorize a production deployment.
- Production Compose still depends on the deployment environment and shared PostgreSQL/Redis infrastructure defined by the existing stack.
- Credentials and complete environment files must never appear in reports, HTML references, or test output.

<!-- AI-generated: review needed -->
