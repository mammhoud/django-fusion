# Schemas — JSON Schema Definitions

> JSON schema files for AnyType object type validation.
> Used by the `# yaml-language-server` directive in frontmatter.

---

## Available Schemas

| Schema | Type | File |
|--------|------|------|
| Page | `page.schema.json` | General page type |
| Bookmark | `bookmark.schema.json` | External link/bookmark |
| Milestone | `milestone.schema.json` | Milestone/phase |
| Note | `note.schema.json` | Quick note |
| People | `people.schema.json` | Person/stakeholder |
| Task | `task.schema.json` | Implementation task |
| Feature | — | Feature entity (uses page schema) |
| Goal | — | Goal entity (uses page schema) |
| Edition | — | Edition entity (uses page schema) |
| Configuration | — | Config entity (uses page schema) |

---

## Usage

Reference schemas in frontmatter:

```yaml
# yaml-language-server: $schema=schemas/page.schema.json
```

---

## Related

- → `../objects/_object-types.md` — Object types that use these schemas
- → `../README.md` — Master index
