# Archived — PlanInc plans that lived in django-fusion

> **ARCHIVED:** read-only. Not an active source of truth.
> **Archived:** 2026-11-19 · **Replacement:** `projects/PlanInc/docs/plans/` (canonical set)
> **Reason:** this directory duplicated PlanInc's canonical plan set and described a
> `/home/` monorepo layout that no longer exists. Its one unique section — the
> responsive radius/motion ladder — was folded into
> `projects/PlanInc/docs/13-single-frontend-platforms.md` before retirement.
> **Rollback:** `projects/docs/plans/deletion-manifest.md` DOC-0028–DOC-0036.

These nine files were written between 2026-09-20 and 2026-11-03 while PlanInc was
being folded into the monorepo. They are kept as a record of that migration, not
as instructions. No active document links to them; the canonical PlanInc plan set
is `projects/PlanInc/docs/plans/` (`full-program-plan.md`, `django-bolt/`,
`cloud_surreal/`, `workflow-and-integrations/`, `BLOCKED-externally.md`).

| File | Why it is here | Canonical replacement |
|---|---|---|
| `README.md` (this index, original) | Stale plan index: pointed at `runtime/`, `planing/` and phase-4/5 files that never existed | `projects/PlanInc/docs/plans/` |
| `phase-0-git-submodules.md` | Completed migration record (submodules established) | `.gitmodules` |
| `phase-1-tauri-rust-architecture.md` | Superseded: the Tauri v2 shell ships | `projects/PlanInc/docs/13-single-frontend-platforms.md` |
| `phase-2-surrealdb-file-migration.md` | Completed: embedded SurrealKV, no container | `projects/PlanInc/docs/02-architecture.md` |
| `phase-3-prisma-postgres-removal.md` | Completed: no `planing/` or `prisma/` remains | `projects/PlanInc/docs/02-architecture.md` |
| `phase-6-brand-identity.md` | Completed: brandkit + palette ship | `projects/PlanInc/docs/10-blinko-parity-and-design-plan.md` |
| `rust-unified-workspace-plan.md` | Proposed only, never implemented (no Cargo workspace) | `projects/PlanInc/src/src-tauri/Cargo.toml` |
| `unified-dev-organization.md` (v4.1) | Duplicate draft of a `/home/` layout; radius/motion section folded | `projects/PlanInc/docs/13-single-frontend-platforms.md` |
| `unified-development-organization.md` (v4.0) | Superseded by the v4.1 copy, itself retired | `projects/PlanInc/docs/13-single-frontend-platforms.md` |

Each file carries an `ARCHIVED` header with its own replacement, reason and
manifest entry.
