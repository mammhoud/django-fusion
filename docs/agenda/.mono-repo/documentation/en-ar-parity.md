---
Object type: Documentation
Tags: documentation, i18n, arabic, parity
Status: Active
Type: Guide
Audience: Team
Related Repositories: structa-cloud-monorepo
Related Guides: _index
---

# EN/AR Parity — Bilingual Documentation

> **Description:** The English/Arabic parity method — `docs/ar-content/` mirrors the English tree so key docs exist in both languages.

## Method

- English authored in `docs/` is the source of truth
- Arabic mirrors live in `docs/ar-content/` with the same relative structure
- `validate-content` checks the AR mirror for required docs (parity failures block the pipeline)
- Agenda docs are English-only by decision (case studies, task boards) — the *definition* and READMEs get AR rows

## Scope

- Required mirrors: guides, plans indexes, agenda README/index rows, product docs
- Not mirrored: working trackers (feature-tracking, task-tracking), case studies

## Related

- → `docs-tree.md` — Docs set
- → `../../CONTENT_MODEL.md` § packages — Where parity applies
- → `../objects/documentation.md` — Documentation object type