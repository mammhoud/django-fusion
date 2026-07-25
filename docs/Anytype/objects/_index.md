# Objects — AnyType Type Definitions

> Define the object types that power the Structa Cloud knowledge graph.

---

## Core Object Types

| Type | Description | Layout | Schema File |
|------|-------------|--------|-------------|
| **Page** | General-purpose knowledge page | Page | `page.schema.json` |
| **Workspace** | High-level workspace/meta page | Page | — |
| **Bookmark** | External link or reference | Bookmark | `bookmark.schema.json` |
| **Feature** | Product feature or capability | Page | — |
| **Milestone** | Key milestone or phase | Milestone | `milestone.schema.json` |
| **Task** | Implementation task or TODO | Task | `task.schema.json` |
| **Goal** | Strategic objective or target | Page | — |
| **Edition** | Product edition variant | Page | — |
| **Configuration** | System/environment config | Page | — |
| **Blog/Post** | Published content or article | Page | — |
| **People** | Team member or stakeholder | Page | `people.schema.json` |
| **Note** | Quick note or learning | Note | `note.schema.json` |

---

## Import Workflow

1. Open AnyType → **Settings → Content Model → Add Type**
2. Create each type with its properties
3. Create shared **Tags** Multi-select property from `_tags.md`
4. Create **Relations** from `_relations.md`
5. Import markdown files → assign correct type
6. Link related objects in Graph View

---

## Related

- → `_object-types.md` — Full type definitions with all properties
- → `_relations.md` — Relation/linking guide
- → `_tags.md` — Tag definitions
- → `../README.md` — Back to master index
