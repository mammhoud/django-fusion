---
Object type: Guide
Tags: pos, documentation, anytype, workspace, method
Status: Published
---

# POS System — Documentation Method

> **Description:** How the POS workspace is organized and imported into Anytype.

## Organization

The POS documentation space is divided into focused areas:

| Area | Purpose |
|------|---------|
| Object types | Custom type definitions for Anytype import |
| Tags | Multi-select tag definitions |
| Relations | Object relation and linking guide |
| Architecture | Edition boundaries, sync model, roles, themes |
| Features | Edition capability descriptions |
| Guides | Setup, development, and theming methods |
| References | API and configuration facts |
| Changelogs | Version history |
| Diagrams | Flow and architecture visualization |

## Import to Anytype

1. **Create object types** — open Settings → Content Model → Add Type; create the types from the object-types reference
2. **Create properties** — add the listed properties to each type; create a shared Tags multi-select property
3. **Import markdown** — use Anytype's markdown import feature for each file; assign the correct type after import
4. **Link objects** — for each Related Docs section, create an object relation between the source and target
5. **Graph view** — open Graph View to see all connections; use filters by type, tag, or edition to focus

## Style guide

- **Minimal technical detail** — describe responsibility and method, not full implementations
- **Safe flows** — use arrow (→) diagrams, never surrounding code structures
- **Tables** — compact comparison tables
- **Related links** — always end with cross-references
- **Frontmatter** — Type, Tags, Status at the top

## Related

- → `../guides/pos-documentation-system.md` — Import method
- → `../objects/_object-types.md` — Object types
- → `../architecture/editions.md` — Edition boundaries
- → `../README.md` — Anytype hub
