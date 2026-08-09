# Recommendations first

> **Purpose:** the shortest path from the current repository state to the next safe, valuable work.
>
> **Updated:** 2026-08-09

This page is the decision layer for Structa Cloud documentation. Read it before opening detailed plans. The plan files below are implementation contracts; this page keeps priorities, ownership, and sequencing visible.

## Recommended order

### 1. Keep `docs/plans/` as the only active plan registry

All engineering plans now belong under [`docs/plans/`](plans/README.md), organized by scope:

- `plans/repository/` — cross-repository architecture, cleanup, and delivery work;
- `plans/pos/` — Formint/POS product and edition plans;
- `plans/cms-fusion/`, `plans/lms-fusion/`, and `plans/landing-fusion/` — site-specific work;
- `plans/django-fusion/` — shared framework work;
- `plans/legacy/` — read-only historical evidence only.

Do not create new plans under `docs/dev/plans/`, `projects/*/docs/superpowers/plans/`, or `docs/plans/migrated/`.

### 2. Finish the current product vertical slices before starting broad cleanup

Prioritize work that produces a tested user-visible path:

1. **Formint POS Professional Edition** — continue from the canonical [Professional plan](plans/pos/formint-pos-professional-plan.md), starting with branch → order → KDS → sync → reporting.
2. **Landing Fusion** — keep the content and blog rendering contract covered by focused backend/frontend tests before adding new page blocks.
3. **CMS/LMS Fusion** — close the remaining frontend and deployment tasks only when the relevant plan has an owner and a verification command.

### 3. Treat migration and legacy material as evidence, not scope

Completed phase reports, Forge parity notes, deployment records, and migration audits can be useful for rollback and investigation. They are now archived under `plans/legacy/` and must not be presented as active work. Delete an archived file only after the lifecycle and deletion-manifest gates pass.

### 4. Use evidence-based status labels

A plan is **Complete** only when implementation, tests, documentation, and release evidence exist. Use **Active**, **Planned**, **Superseded**, or **Archived** when any part is missing. Avoid copying status claims from historical snapshots into current indexes.

### 5. Keep product knowledge separate from engineering execution

- Engineering plans, migrations, tests, and deployment procedures: [`docs/plans/`](plans/README.md)
- Product decisions, market hypotheses, and edition boundaries: `docs/Anytype/` (separate knowledge graph when present)
- Current architecture and operational guides: the relevant topic/project section in [`docs/README.md`](README.md)

Link between these sources; do not maintain competing copies of the same implementation plan.

## Current next actions

| Priority | Action | Source of truth | Verification |
|:--:|---|---|---|
| P0 | Maintain the Formint edition extension chain and select the next executable task | [`plans/editions/README.md`](plans/editions/README.md) | Edition-specific Rust/Python/frontend tests |
| P0 | Keep active Landing Fusion content work aligned with its post-only rendering contract | [`plans/landing-fusion/`](plans/landing-fusion/) | Backend tests + frontend `npm run check` |
| P1 | Close the remaining CMS/LMS Fusion frontend and deployment gates | [`plans/cms-fusion/`](plans/cms-fusion/), [`plans/lms-fusion/`](plans/lms-fusion/) | Site checks, tests, and frontend builds |
| P1 | Consolidate repository cleanup decisions without deleting compatibility sources prematurely | [`plans/repository/migration-cleanup-master.md`](plans/repository/migration-cleanup-master.md) | Reference scan + focused project checks |
| P2 | Improve docs navigation and link validation as part of every documentation change | [`plans/document-lifecycle.md`](plans/document-lifecycle.md) | `python3 applications/scripts/check_markdown_links.py` |

## Rules for adding a plan

1. Start with a status, owner, date, scope, dependencies, and verification commands.
2. Put the file in the appropriate `docs/plans/<scope>/` directory.
3. Add it to [`docs/plans/README.md`](plans/README.md) and the relevant project subsection.
4. Link to source code and existing plans instead of duplicating them.
5. Mark superseded plans and move historical evidence to `plans/legacy/`.

## Related

- [`docs/README.md`](README.md) — main documentation hub
- [`docs/plans/README.md`](plans/README.md) — canonical plan registry
- [`docs/plans/document-lifecycle.md`](plans/document-lifecycle.md) — archive and deletion policy
- [`docs/plans/deletion-manifest.md`](plans/deletion-manifest.md) — deletion approval register
