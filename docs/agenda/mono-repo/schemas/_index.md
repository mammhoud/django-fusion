# Schemas — JSON Schema Definitions

> JSON schema files for AnyType object type validation.
> Used by the `# yaml-language-server` directive in frontmatter.

---

## Available Schemas

| Schema | Type | File |
|--------|------|------|
| Page | `page.schema.json` | General page type |
| Bookmark | `bookmark.schema.json` | External link/bookmark |
| Workspace | `workspace.schema.json` | Workspace/portfolio hub |
| Feature | `feature.schema.json` | Feature entity |
| Task | `task.schema.json` | Implementation task |
| Note | `note.schema.json` | Quick note |
| Milestone | `milestone.schema.json` | Milestone/phase |
| People | `people.schema.json` | Person/stakeholder |
| Configuration | — | Config entity (uses page schema) |
| Edition | — | Edition entity (uses page schema) |
| Goal | — | Goal entity (uses page schema) |

---

## Usage

Reference schemas in frontmatter:

Reference schemas in a document's frontmatter via the schema directive, for example pointing to `page.schema.json` for a page type.

---

## Related

- → `../objects/_object-types.md` — Object types that use these schemas
- → `../README.md` — Master index
