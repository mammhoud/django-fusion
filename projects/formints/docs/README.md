# Formints POS — Documentation

> **Canonical home for Formints POS docs** (`projects/formints/`). The
> reader-facing docs site pointers live in [`docs/pos/`](../../../docs/pos/README.md).
> Edition plans and the capability matrix are the **source of truth** for what
> each edition ships:
> [`docs/plans/editions/`](../../../docs/plans/editions/README.md).

## Editions status (21 Aug 2026)

| Edition | Directory | Status |
|---------|-----------|--------|
| **Community** | `formint-community/` | ✅ done |
| **Standard** | `formint-standard/` | ✅ done |
| **Pro** | `formint-pro/` | ✅ done |
| **Cloud** | `formint-cloud/` | 🟡 staging |
| **pos-client** | `formint-client/` | 🔵 dev |

See the [finish board](../../../docs/plans/editions/README.md#finish-board-status-per-edition--21-aug-2026)
for what remains per edition.

## Index

| Document | Description |
|----------|-------------|
| [`GETTING_STARTED.md`](GETTING_STARTED.md) | **Setup & build guide** — step-by-step startup/build for every edition |
| [`architecture/editions.md`](architecture/editions.md) | Per-edition components & features (Community → Pro → Cloud → pos-client) |
| [`architecture/pos-architecture.md`](architecture/pos-architecture.md) | Cross-edition POS architecture |
| [`architecture/pro-cloud-sync-contract.md`](architecture/pro-cloud-sync-contract.md) | Pro ↔ Cloud sync contract |
| [`architecture/server-migration-guide.md`](architecture/server-migration-guide.md) | Server migration guide (legacy → Django) |
| [`architecture/table-column-comparison.md`](architecture/table-column-comparison.md) | Table & column comparison across editions |
| [`FORMINT_ARCHITECTURE.md`](FORMINT_ARCHITECTURE.md) | Formint POS Professional architecture (merged package) |
| [`COMMANDS.md`](COMMANDS.md) | CLI / Makefile commands reference |
| [`ROLE_SYSTEM.md`](ROLE_SYSTEM.md) | Roles & permissions design |
| [`THEME_SYSTEM.md`](THEME_SYSTEM.md) | Theme variant system |
| [`TEMPLATES.md`](TEMPLATES.md) | Template architecture (Django + django-fusion) |
| [`adr/`](adr/) | Architecture Decision Records |
| [`seed-data/`](seed-data/) | Seed data reference (presets, JSON) |
| [`screenshots/`](screenshots/) | Admin + frontend screenshots |
| [`legacy/`](legacy/README.md) | **Archived** pre-merge / Robyn-era docs (history only) |

## Canonical plans & comparison

- **Edition plans (canonical):** [`docs/plans/editions/`](../../../docs/plans/editions/README.md)
  — Community (`01`), Standard (`02`), Pro (`03`), Cloud (`04`), pos-client
  (`05`), JS/TS SDK (`06`), Community version (`07`), tenant schemas (`08`).
- **Feature/buyer matrix:** [`docs/plans/editions/comparison.md`](../../../docs/plans/editions/comparison.md).
- **Product home README:** [`projects/formints/README.md`](../README.md).
- **Strategy (private):** [`docs/startup/formints.md`](../../../docs/startup/formints.md).
