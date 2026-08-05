# POS Full — Changelog

> All notable changes to the POS Full edition (multi-terminal with external sidecar + Cloud CRM).
> See also: [`../CHANGELOG.md`](../CHANGELOG.md) for POS-wide changes.

---

## [Unreleased] — July 30, 2026

### Planned
- **Cloud plan** — Per [`docs/plans/pos/cloud-plan.md`](../../docs/plans/pos/cloud-plan.md): WebSocket commands, multi-terminal sync, cloud CRM architecture
- **Django Fusion enhancements** — Per [`docs/plans/pos/django-fusion-enhancements.md`](../../docs/plans/pos/django-fusion-enhancements.md): 10-12 pages awaiting FusionPage wiring (Analytics, Auth, InvoicePage, ProductManager, Recipes, Reports, Sale, Settings, SupportChat, Transactions)

---

## v1.2.0 — July 2026

### Added
- **Django Bolt API** — `bolt_api.py` sidecar module with BoltAPI integration for high-performance Rust-backed API endpoints
- **Bolt URL configuration** — `bolt_urlconf.py` test module verifying Bolt URL routing
- **Bolt API tests** — `test_bolt_api.py` with comprehensive endpoint coverage

### Changed
- **Sidecar v2** — Migrated to Robyn async Python server with Cloud Master architecture
- **Rust-backed posapp** — django-bolt integration for performance-critical paths
- **Sidecar documentation** — Comprehensive `docs/SIDECAR_V2.md` with 70+ API catalog, WebSocket streams, Django signals
- **CI/CD expansion** — Comprehensive CI/CD, E2E testing, and documentation across LMS and POS projects

### Fixed
- **Build cleanup** — Removed build artifacts, node_modules, logs, and target directories

---

## v1.0.0 — June 2026

See [`../CHANGELOG.md`](../CHANGELOG.md) for the full initial release notes.

### Added
- **Initial POS Full release** — Multi-terminal POS with external sidecar (Robyn + Django ORM + Cloud CRM)
- Core POS features shared with forge-pos edition
