---
Object type: Release
Tags: release, formint, editions, version
Status: Released
Related Features: pos-system, pos-offline, pos-integration
Related Milestones: formint-editions-chain
---

# Formint Editions 2026-08 — Edition Chain Release

> **Description:** Community, Standard, and Pro editions completed with the canonical per-edition plans; Cloud on staging.

## What shipped

- Community ✅ done — refunds & returns, offline-first (Rust/Diesel/SQLite)
- Standard ✅ done — multi-currency, tax profiles, custom roles, export, sync queue
- Pro ✅ done — merged `pos-full` + `pos-solo`, required Django backend
- Cloud 🟡 staging — schema-per-tenant master, backups, monitoring
- Umbrella plan `finish-community-standard` archived (superseded by the per-edition chain — see the ✅ Shipped milestone in `../../feature-tracking.md` § Formint POS)

## Evidence

- Per-edition `make check`/`make test` green
- Chain status recorded in `../../../plans/editions/README.md`

## Related

- → `../editions/_index.md` — Edition objects
- → `../../feature-tracking.md` § Formint POS — ✅ Shipped milestone
- → `../objects/release.md` — Release object type