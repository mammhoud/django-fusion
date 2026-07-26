---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Release
Tags: release
Status: Published
---

# Release — Version Tracking & Deployment

> **Type:** Release 🚀
> **Layout:** Page
> **Description:** Version releases with features, fixes, deployment notes, and links to changelogs, milestones, and CI/CD pipelines.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Status` | Select | Planned, In Progress, Released, Rolled Back | Lifecycle stage |
| `Version` | Text (required) | — | Semantic version |
| `Release Date` | Date | — | When released |
| `Edition` | Relation → Edition | — | Product edition |
| `Milestone` | Relation → Milestone | — | Related milestone |
| `Related Features` | Relation → Feature | — | Features in this release |
| `Related Changelog` | Relation → Changelog | — | Changelog entry |
| `Related Pipeline` | Relation → Pipeline | — | CI/CD pipeline |
| `Tags` | Multi-select | — | Cross-cutting labels |

---

## Usage

```
Pipeline 🔄 ── deploys ──→ Release 🚀 ── tracks ──→ Changelog 📋
                                 │
                                 ├── includes ──→ Feature ✨
                                 └── targets ──→ Milestone 🏁
```

---

## Related

- → `_object-types.md` — All type definitions
- → `../releases/` — Releases directory
- → `milestone.md` — Milestone entity
- → `pipeline.md` — Pipeline entity
- → `../changelogs/_index.md` — Changelogs
