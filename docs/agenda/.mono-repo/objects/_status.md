# Anytype Documentation Status

> **Purpose:** Single status view for the focused Anytype knowledge graph. Detailed deletion and rollback policy lives in `../../plans/document-lifecycle.md`.
> **Last reviewed:** 2026-09-03

## Status legend

| Status | Meaning |
|---|---|
| ✅ Current | Authoritative and linked from an active index |
| 🔄 Update needed | Valuable but stale, incomplete, or inconsistent |
| 🗄️ Historical | Preserved for migration, audit, or design history |
| 🗑️ Deletion candidate | Duplicate or empty; never delete before the manifest gate |

## Focused current set

| Area | Files | Status | Notes |
|---|---|---|---|
| Hub | `README.md` | ✅ Current | Focused Anytype import entry point (Channel Home page) |
| Channel model | `guides/channel-structure.md` | ✅ Current | Vault → Channel container, Home types, roles, Content Model |
| Edition architecture | `architecture/editions.md` | ✅ Current | Community, Formint Professional, POS Cloud |
| Formint product | `plans/formint-pos-professional-plan.md` | ✅ Current | Product/use-case summary |

| Cloud | `plans/cloud.md` | ✅ Current | Cloud-only transport boundary |
| Market research | `plans/pos-market-research.md` | ✅ Current | Working hypotheses and validation questions |
| Team plan | `plans/team.md` | ✅ Current | Team ownership, members, periodic tasks |
| People | `objects/people/` | ✅ Current | me, dariia, yahia, asmaa, mahmoud, moustafa |
| Object schema | `objects/_object-types.md`, `_relations.md`, `_tags.md`, `_templates.md` | ✅ Current | Channel-scoped Content Model, complete-document anatomy, periodic-task model |
| Import method | `guides/pos-documentation-system.md` | ✅ Current | Channel import method + complete-document writing rules |

## Update-needed set

| File or group | Reason | Action |
|---|---|---|
| `plans/market-research.md` | Broad Structa Cloud research, separate from POS edition research | Mark as general research or link to the POS research object |
| Old indexes and pages with malformed frontmatter | Import and navigation reliability | Normalize only after link/reference scan |

## Historical set

- `plans/_legacy/networking-detailed.md`, `marketing-strategy-expanded.md`, `operational-plan-expanded.md`, `risk-management-detailed.md`, `start-up.md`, `projects-list.md`, `free-version.md`, `full-version.md`, `solo-version.md` — Legacy duplicate stubs redirecting to canonical files
## No-delete rule

No file is permanently deleted merely because it is old or marked complete. A deletion candidate must have a unique manifest ID, replacement, archive, hash, hold decision, and tested rollback in `docs/plans/deletion-manifest.md`.

## Cleanup phases

1. **Normalize:** current frontmatter, canonical names, indexes, and links
2. **Classify:** current, update, historical, or deletion candidate
3. **Archive:** preserve superseded content with a replacement header
4. **Validate:** links, frontmatter, Anytype import, and relevant project tests
5. **Delete selectively:** only approved manifest rows, in small batches
6. **Review:** update this file and the root plan index after each batch

## Related

- → `../README.md` — Anytype hub
- → `../architecture/editions.md` — Current editions
- → `../plans/formint-pos-professional-plan.md` — Formint summary
- → `../../../plans/document-lifecycle.md` — Lifecycle policy
- → `../../../plans/deletion-manifest.md` — Rollback-first deletion register
