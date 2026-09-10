---
Object type: Documentation
Tags: documentation, docs, docus
Status: Active
Type: Architecture
Audience: Developers, Team
Related Repositories: structa-cloud-monorepo
Related Guides: _index
---

# Docs Tree — Docus Documentation Set

> **Description:** The `docs/` tree — Docus docs, agenda system, plans registry, AR content, and the diagram package — the team's canonical knowledge home.

## Structure

| Path | Contents |
|---|---|
| `docs/agenda/` | Agenda system: CONTENT_MODEL, feature tracking, tasks, team notes, case studies, diagrams |
| `docs/agenda/mono-repo/` | Anytype import set (this schema + knowledge-graph objects) |
| `docs/plans/` | Canonical engineering plans (registry in README) |
| `docs/ar-content/` | Arabic mirrors (EN/AR parity) |
| `docs/guides/` | How-to guides (quickstart, setup, Docus…) |

## Method

- Authored markdown in `docs/` is canonical; `docs/content/` is generated
- `prepare-content` + `validate-content` gate every change
- Finished plans → ✅ Shipped milestones (reference contract)

## Related

- → `en-ar-parity.md` — Parity method
- → `../../CONTENT_MODEL.md` — Agenda definition
- → `../tools/docus-docs.md` — Engine
- → `../objects/documentation.md` — Documentation object type