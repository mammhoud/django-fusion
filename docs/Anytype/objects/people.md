---
# yaml-language-server: $schema=../schemas/people.schema.json
Object type: People
Tags: people, person, team
Status: Published
---

# People — Team Members & Contributors

> **Type:** Person 👤
> **Layout:** Profile
> **Description:** Team members, contributors, stakeholders, and authors — linked to tasks, posts, decisions, and owned plans.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Role` | Select | Developer, Designer, Manager, Contributor, Stakeholder | Team role |
| `Email` | Email | — | Contact email |
| `Tags` | Multi-select | — | Cross-cutting labels |
| `Assigned Tasks` | Relation → Task | — | Tasks assigned to this person |
| `Authored Posts` | Relation → Blog/Post | — | Blog posts written by this person |
| `Owned Plans` | Relation → Plan | — | Plans owned by this person |
| `Owned Goals` | Relation → Goal | — | Goals owned by this person |

---

## Usage in Knowledge Graph

```
Person 👤
    ├── Assigned Tasks ──→ Task ✅
    ├── Authored Posts ──→ Blog/Post 📝
    ├── Owned Plans ─────→ Plan 📋
    └── Owned Goals ─────→ Goal 🎯
```

---

## Related

- → `_object-types.md` — All type definitions
- → `_relations.md` — Relations guide
- → `../people/_index.md` — People directory
