# Documentation Deletion Manifest

> **Status:** Active register — no deletion is approved by this file alone.
> **Policy:** [`document-lifecycle.md`](document-lifecycle.md)
> **Last reviewed:** 2026-08-14

## Purpose

Every deletion must have a recorded replacement, archive, evidence scan, hold decision, and tested rollback. Empty cells mean **not approved**.

## Lifecycle actions

| Action | Meaning |
|---|---|
| `keep` | Current source of truth; maintain and index |
| `update` | Useful but stale; update before reuse |
| `archive` | Preserve read-only with a replacement and retention reason |
| `quarantine` | Remove from active navigation while validating references |
| `delete` | Permanent removal after all gates and approval |

## Required record

| ID | Path | Action | Reason | Replacement | Archive path | Hash | Hold | Restore test | Change ID | Owner |
|---|---|---|---|---|---|---|---|---|---|---|
| DOC-0001 | `docs/plans/pos/formint-pos-professional-plan.md` | keep | Canonical Professional plan | — | — | — | none | n/a | — | Product |
| DOC-0002 | `docs/plans/pos/forge-pos-plan.md` | keep | Formint migration source | Formint plan | `docs/plans/legacy/pos/` after retirement | pending | migration hold | pending | — | POS |
| DOC-0003 | `docs/plans/pos/tauri-plugins-enhancement-plan.md` | keep | Current desktop migration | Formint plan | — | pending | migration hold | pending | — | POS |
| DOC-0004 | `docs/plans/pos/cloud-plan.md` | keep | Cloud architecture | Anytype cloud summary | — | pending | none | pending | — | Cloud |
| DOC-0005 | `docs/plans/pos/pos-solo-enhancement.md` | archive | Working file is absent; no recreation approved | Formint and Forge plans | none; preserve this record | unavailable | migration hold | not applicable | — | POS |
| DOC-0006 | `docs/plans/legacy/pos/forge-pos-ui-enhancement-master.md` | archive | Completed Forge design evidence | Formint design contract | same path | pending | rollback/design hold | pending | — | POS |
| DOC-0007 | `docs/plans/legacy/pos/forge-pos-tasks-status.md` | archive | Completed Forge status snapshot | Formint parity gates | same path | pending | rollback/design hold | pending | — | POS |
| DOC-0008 | `docs/plans/legacy/pos/forge-pos-enhancement.md` | archive | Completed Forge implementation source | Formint migration | same path | pending | rollback/design hold | pending | — | POS |
| DOC-0009 | `docs/Anytype/plans/market-research.md` | update | Broad Structa Cloud research; not POS-specific | `docs/Anytype/plans/pos-market-research.md` | pending | pending | evidence hold | pending | — | Product |
| DOC-0010 | `docs/Anytype/objects/_status.md` | update | Stale tracker with nonexistent names | This lifecycle plan | — | pending | none | n/a | — | Docs |
| DOC-0011 | `docs/plans/repository/worker-consolidation.md` | archive | Celery/LMS-inclusive worker design is superseded | `docs/plans/repository/active-monorepo-consolidation-2026-08-14.md` | `docs/plans/repository/worker-consolidation.md` | pending | migration hold | pending | 2026-08-14 | Infrastructure |
| DOC-0012 | `applications/templates/dev-stack/` | delete | Renamed to the canonical Coder template path | `applications/templates/workspace/` | Git history | pending | deployment hold | pending | 2026-08-14 | Infrastructure |
| DOC-0016 | `applications/templates/dev-workspace/` | update | Template renamed to `workspace` (containers no longer depend on the Coder workspace name) | `applications/templates/workspace/` | Git history | completed in working tree | none | pending review | 2026-08-14 | Infrastructure |
| DOC-0013 | `applications/proxy/traefik/dynamic/blinko.yml` | keep as redirect | Blinko was replaced by AFFiNE (affine.pro); the router now serves a 301 redirect for legacy bookmarks | `applications/templates/workspace/main.tf` AFFiNE resources | same path (redirect router) | completed in working tree | none | pending review | 2026-08-14 | Infrastructure |
| DOC-0014 | `applications/proxy/traefik/dynamic/code-server.yml` | delete | code-server is now an authenticated Coder app without a public subdomain | Coder app in `applications/templates/workspace/main.tf` | Git history | completed in working tree | none | pending review | 2026-08-14 | Infrastructure |
| DOC-0015 | AppFlowy workspace stack (`appflowy-*` containers, `space.structa.cloud` full-stack routes) | replace | AppFlowy Cloud was replaced by AFFiNE (single origin, affine.pro); the space host is now a redirect | `applications/templates/workspace/main.tf` AFFiNE resources | `applications/proxy/traefik/dynamic/affine.yml` + `space.yml` redirect | completed in working tree | none | pending review | 2026-08-14 | Infrastructure |
| DOC-0017 | Service containers in `applications/templates/workspace/main.tf` (code-server/filegator/affine images + containers) | replace | All workspace services moved into the repo's compose devcontainer (`.devcontainer/docker-compose.yml`); the template now only provisions an agent-host container that runs the devcontainer | `.devcontainer/docker-compose.yml` + `coder_devcontainer` | Git history | completed in working tree | none | pending review | 2026-08-14 | Infrastructure |
| DOC-0018 | Public `affine.pro` host (Traefik router + cert + nginx server_name) | delete | All workspace services consolidated under `space.structa.cloud` (root = AFFiNE); affine.pro removed entirely | `applications/proxy/traefik/dynamic/space.yml` + nginx template | Git history | completed in working tree | none | pending review | 2026-08-14 | Infrastructure |
| DOC-0019 | Workspace code-server + FileGator services (containers, Coder apps, `filegator.structa.cloud` route, `applications/proxy/filegator/`) | delete | Bundled services removed from the devcontainer; the IDE runs inside the devcontainer and no file manager is shipped | `.devcontainer/docker-compose.yml` (AFFiNE only) + nginx `space.structa.cloud` root | Git history | completed in working tree | none | pending review | 2026-08-14 | Infrastructure |
| DOC-0020 | `applications/templates/devcontainer/` (Docker-in-Docker template) | merge | Templates merged into ONE: the `devcontainer` template's features (devcontainer auto-start, VS Code Web, display_apps) folded into `workspace`; the merged template binds the host checkout instead of cloning | `applications/templates/workspace/` | Git history | completed in working tree | none | pending review | 2026-08-14 | Infrastructure |
| DOC-0021 | `docs/plans/CODEBASE_AUDIT_AND_MIGRATION_PLAN.md` | delete | Audited `projects/precis-lms/` + `projects/cms-fusion/` apps no longer exist; superseded by Precis/Landing-Fusion | `docs/plans/README.md` | Git history | completed | none | pending review | 2026-08-16 | Docs |
| DOC-0022 | `docs/plans/FUSION_LMS_CMS_DESIGN.md` | delete | Design doc for retired `precis-lms`/`cms-fusion` product lines | `docs/plans/README.md` | Git history | completed | none | pending review | 2026-08-16 | Docs |
| DOC-0023 | `docs/plans/ASSETS_MIGRATION_INVENTORY.md` | delete | Inventory for retired `precis-lms`/`cms-fusion` backends | `docs/plans/README.md` | Git history | completed | none | pending review | 2026-08-16 | Docs |

## Deletion gate

A row may change to `delete` only when all are true:

- [ ] replacement is current and linked from an index;
- [ ] repository-wide references and dynamic references are clean;
- [ ] no code, CI, deployment, legal, audit, or migration hold exists;
- [ ] archive is created outside the active working path;
- [ ] SHA-256 hash is recorded;
- [ ] restore has been tested and recorded;
- [ ] owner approves the change;
- [ ] a small deletion change ID/commit is recorded;
- [ ] focused tests and Markdown/frontmatter/link validation pass.

## Rollback procedure

```bash
# Example only: use the exact archive path recorded in the row.
mkdir -p /tmp/formint-doc-rollback
sha256sum archives/<archive-name>.tar.gz
 tar -xzf archives/<archive-name>.tar.gz -C /tmp/formint-doc-rollback
# Compare restored content, then copy back only after review.
```

For Git-backed recovery, record the deletion change ID and restore the specific path from the parent revision. Never force-reset a shared branch to recover one document.

## Current decision

The 2026-08-14 monorepo consolidation records completed, deprecated, and
renamed items in the active repository plan. The `dev-stack` directory is
replaced by `workspace` (via the intermediate `dev-workspace` path, DOC-0012 /
DOC-0016); the old paths are not second source trees. The historical worker
plan remains archived evidence, and the former Blinko, AppFlowy (space) and
code-server public routes are replaced by AFFiNE (affine.pro) and internal
Coder apps. No production database, Docker volume, or unrelated product
source is deleted by this pass.

## 2026-08-14 deletion (owner-approved)

The retired plan directories `docs/plans/pos/`, `docs/plans/migrated/`,
`docs/plans/cms-fusion/`, and `docs/plans/precis-lms/` were permanently removed
(47 files). Each had a verified replacement — the Formints `editions/` chain
(`03-pro.md` → `formint-pro`, `04-cloud.md` → `formint-cloud`) for the retired
`projects/pos/` scope, and Precis/Landing-Fusion for the CMS/LMS migration
plans. The pre-migration originals under `migrated/` were duplicates of the
superseded copies and are recoverable from git history. Indexes
(`README.md`, `document-lifecycle.md`, `editions/README.md`, `mkdocs.yml`,
`docs/_sidebar.md`, `docs/recommendations.md`) were updated in the same pass.

## 2026-08-16 deletion (owner-approved)

The entire `docs/plans/legacy/` directory was permanently removed — completed
phase reports, retired `pos/` plans, and the retired `precis-lms`/`cms-fusion`
migration/design/inventory docs (DOC-0021, DOC-0022, DOC-0023). Every file is
recoverable from git history, and the deletion gate's replacement test is
satisfied by the canonical `docs/plans/README.md` index. This supersedes the
`docs/plans/legacy/pos/*` rows (DOC-0006, DOC-0007, DOC-0008), the earlier
`docs/plans/pos/*` rows (DOC-0001 … DOC-0005, removed 2026-08-14), and the
`docs/Anytype/*` rows (DOC-0009, DOC-0010). `DJANGO_BOLT_FUSION_CASE_STUDY.md`
is retained as the historical case study.
