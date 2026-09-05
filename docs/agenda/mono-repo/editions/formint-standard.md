---
Object type: Edition
Tags: edition, formint, standard, pos, rust, django
Status: Completed
Related Features: pos-system, pos-offline
Related Plans: formint-pos-professional-plan
---

# Formint Standard — Community + Business Tier

> **Description:** Community capabilities plus multi-currency, tax profiles, custom roles & permissions, CSV/JSON export, and an offline sync queue. Rust/Diesel + SQLite primary with an optional Django sidecar for sync/cloud.

## Scope

- Everything in Community
- Multi-currency, tax profiles, custom roles & permission enforcement
- CSV/JSON data export
- Offline sync queue
- Optional Django sidecar (`sync/cloud`)

## Boundaries

- Standard is **Rust/Diesel-first with an optional Django sidecar**; Pro is the first edition with a *required* Django backend.

## Evidence

- ✅ Done (per `docs/plans/editions/` chain status)
- `cargo test` + sidecar `make test` green
- Plan: `../../../plans/editions/02-standard.md`

## Related

- → `formint-community.md` — Base tier
- → `formint-pro.md` — Next tier in the chain
- → `../objects/edition.md` — Edition object type