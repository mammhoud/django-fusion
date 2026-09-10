---
Object type: Workspace
Tags: references, api, configuration, workspace
Status: Active
Related Products: formint-pos
Related Editions: Community, Formint Professional, POS Cloud
---

# References — API, Configuration & Operational Facts

> API endpoints, command references, database boundaries, configuration facts, and internationalization references.

## Contents

| Document | Category | Description |
|---|---|---|
| `learnings.md` | Knowledge | Industry trends, best practices, and research notes |

## Planned

| Document | Category | Description |
|---|---|---|
| `sidecar-api.md` | API | Local application service boundary |
| `database-schema.md` | Database | Local and hosted persistence schemas |
| `tauri-commands.md` | CLI | Native desktop command reference |
| `i18n-keys.md` | i18n | Translation and RTL key reference |

## Product boundary

- Community and Formint Professional may use local application boundaries appropriate to their released features.
- POS Cloud owns hosted tenant, branch, billing, analytics, backup, and managed integration references.
- Legacy `pos-solo` and `pos-full` references are migration context; do not use them as current edition labels.

## Related

- → `../architecture/editions.md` — Edition scope
- → `../architecture/sync-data.md` — Synchronization boundaries
- → `../plans/cloud.md` — Cloud operating model
- → `../plans/tauri-desktop.md` — Desktop tools
- → `../objects/api.md` — API object type
- → `../objects/configuration.md` — Configuration object type
- → `../README.md` — Anytype hub
