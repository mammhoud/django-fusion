---
Object type: Changelog
Tags: changelog, release, version, migration, breaking-change
Status: Active
---

# Changelog — Version History & Migration Notes

> **Description:** Version history, migration notes, breaking changes, and security updates. Maintains a clear record of product evolution.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Draft, Published |
| `Version` | Text | Version this changelog covers |
| `Date` | Date | Release date |
| `Related Editions` | Relation → Edition | Editions affected |
| `Type` | Select | Feature, Fix, Security, Migration, Breaking Change, Maintenance |
| `Related Features` | Relation → Feature | Features in this version |
| `Related Goals` | Relation → Goal | Strategic alignment |
| `Related Milestones` | Relation → Milestone | Delivery checkpoints |
| `Related Releases` | Relation → Release | Releases this changelog documents |
| `Tags` | Multi-select | Cross-cutting labels |

## Use

Log each version with dated entries: added, changed, fixed, security, migration notes. Link to features for context and releases for deployment history.

## Graph

Changelog → Related Releases → Release → Related Features → Feature · Changelog → Related Milestones → Milestone.

## Related

- → `_object-types.md` — Type registry
- → `_relations.md` — Relation guide
- → `../changelogs/_index.md` — Changelogs directory
- → `release.md` — Release object type