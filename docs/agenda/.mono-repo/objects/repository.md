---
Object type: Repository
Tags: monorepo, repository, codebase, organization, version-control
Status: Active
---

# Repository — Codebase Container

> **Description:** A single repository containing multiple projects, libraries, and shared code. Organizes code for collaboration and reuse.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Active, Archived |
| `Type` | Select | Monorepo, Polyrepo, Multi-project, Shared Library |
| `Structure` | Text | Directory layout |
| `Related Projects` | Relation → Project | Projects inside the repository |
| `Related Libraries` | Relation → Module | Shared libraries |
| `Related Documentation` | Relation → Documentation | Repo documentation |
| `Tags` | Multi-select | Cross-cutting labels |

## Use

Document the repository boundary, structure, and the projects/libraries it contains. The Structa Cloud monorepo is the canonical example: `projects/` (Precis, Syntara, Formints, Loop-CRM), `libs/` (django-fusion), `application/` (infra), `docs/`, `tests/`.

## Graph

Repository → Related Projects → Project · Repository → Related Libraries → Module.

## Related

- → `_object-types.md` — Type registry
- → `_relations.md` — Relation guide
- → `../repositories/_index.md` — Repositories directory
- → `module.md` — Module object type
- → `../plans/projects.md` — Repository/project workspace directory