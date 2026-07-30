# POS Solo — Changelog

> All notable changes to the POS Solo edition (standalone Tauri 2 + embedded Python sidecar).
> See also: [`../CHANGELOG.md`](../CHANGELOG.md) for POS-wide changes.

---

## [Unreleased] — July 30, 2026

### Planned
- **Django Fusion enhancements** — Frontend component and page integration per [`docs/plans/pos/django-fusion-enhancements.md`](../../docs/plans/pos/django-fusion-enhancements.md)
- **Enhancement plan** — Per [`docs/plans/pos/pos-solo-enhancement.md`](../../docs/plans/pos/pos-solo-enhancement.md): inventory/recipes page, FlyonUI theme migration, Makefile aliases, dev API commands
- **Shared frontend** — Shares React/TypeScript/Tailwind frontend architecture with forge-pos edition

---

## v1.2.0 — July 2026

### Changed
- **Sidecar migration** — Sanic → Robyn async Python server with Django ORM
- **Edition rename** — Extended → Solo; replaced Sanic with Robyn, unified models, approval workflow, product sync
- **Build cleanup** — Removed build artifacts, node_modules, logs, and target directories

---

## v1.0.0 — June 2026

See [`../CHANGELOG.md`](../CHANGELOG.md) for the full initial release notes.

### Added
- **Initial POS Solo release** — Standalone POS with embedded Python sidecar (Robyn + Django ORM)
- Core POS features shared with forge-pos edition
