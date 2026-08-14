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
| DOC-0012 | `applications/templates/dev-stack/` | delete | Renamed to the canonical Coder template path | `applications/templates/dev-workspace/` | Git history | pending | deployment hold | pending | 2026-08-14 | Infrastructure |
| DOC-0013 | `applications/proxy/traefik/dynamic/blinko.yml` | delete | Blinko was replaced by the internal AppFlowy workspace stack; no public Blinko host remains | `applications/templates/dev-workspace/main.tf` AppFlowy resources | Git history | completed in working tree | none | pending review | 2026-08-14 | Infrastructure |
| DOC-0014 | `applications/proxy/traefik/dynamic/code-server.yml` | delete | code-server is now an authenticated Coder app without a public subdomain | Coder app in `applications/templates/dev-workspace/main.tf` | Git history | completed in working tree | none | pending review | 2026-08-14 | Infrastructure |

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
replaced by `dev-workspace`; the old path is not a second source tree. The
historical worker plan remains archived evidence, and the former Blinko and
code-server public routes are replaced by internal Coder apps. No production
database, Docker volume, or unrelated product source is deleted by this pass.

No POS or Anytype document is approved for permanent deletion in this pass. The safe action is to update indexes, label historical sources, create verified archives, and delete only after the manifest rows are completed.
