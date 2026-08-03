# Landing-Fusion — Plan

> **Status:** 🟢 Phase 0 + 1 complete; backend added
> **Tags:** #landing #astro #django #wagtail #aha-stack

Plan documents for the landing-only slice of the CMS-Fusion → AHA-stack migration.

| Doc | Purpose |
|-----|---------|
| [`LANDING_FUSION_PLAN.md`](./LANDING_FUSION_PLAN.md) | The landing-fusion build plan: structure, phases, backend fields, frontend blocks |
| [`SHADCNBLOCKS_THEME.md`](./SHADCNBLOCKS_THEME.md) | Theme styles extracted from the cloned `mainline-astro-template` (oklch tokens, DM Sans, dark variant) |
| [`../../cms-fusion/plan/ASTRO_MIGRATION_PLAN.md`](../../cms-fusion/plan/ASTRO_MIGRATION_PLAN.md) | Source migration plan (upstream, referenced for phases) |

## Status summary

- **Frontend** (`frontend/`) — Astro 5 + Tailwind 4 + HTMX + Alpine. Phase 0 ✅, Phase 1 ✅, dark mode §5.1 ✅.
- **Backend** (`backend/`) — Django 5.2 + Wagtail 7.4, landing-only page models + templates. New ✅.
- **Theme** — shadcnblocks styles extracted from the clone → documented in [`SHADCNBLOCKS_THEME.md`](./SHADCNBLOCKS_THEME.md).
