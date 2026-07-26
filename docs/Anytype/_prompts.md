# AnyType Documentation — AI Agent Prompts

> Prompts and instructions for AI agents working with the AnyType documentation system.

---

## Document Generation

### Creating a New Object Type

```
Create an AnyType object type definition for [TYPE NAME] at `docs/Anytype/objects/[name].md`.

Include:
1. Frontmatter with `object type: [Type Name]`, `tags`, `status`
2. Description of the type's purpose
3. Properties table with Name, Type, Options, Description
4. Usage in knowledge graph (ASCII diagram)
5. Example with YAML frontmatter
6. Related links at bottom
```

### Writing a Platform Install Guide

```
Create a platform installation guide at `docs/Anytype/guides/install/[platform].md`.

Include:
1. Frontmatter with Object type: Guide, platform tag, Status: Published
2. Prerequisites section
3. Step-by-step install instructions (package managers, tools, deps)
4. Clone & setup repository instructions
5. Verification commands
6. Troubleshooting table
7. Related links
```

### Adding a Feature Document

```
Create a new feature description at `docs/Anytype/features/[name].md`.

Include:
1. Frontmatter with Object type: Feature, edition tags, status
2. Feature overview and purpose
3. Key capabilities with bullet points
4. Technical implementation details
5. Edition compatibility matrix
6. Related docs links
```

---

## Knowledge Graph Operations

### Checking Graph Integrity

```
Review the AnyType documentation at `docs/Anytype/` for consistency:

1. Check that every document has correct frontmatter (Object type, Tags)
2. Verify that all cross-references (→ links) point to existing files
3. Check for orphaned files (no backlinks from other docs)
4. Report any duplicate or deprecated content
```

### Updating Relations

```
Update the relations in `docs/Anytype/objects/_relations.md` to include
the new [TYPE NAME] entity.

1. Add the relation entry to the relations table
2. Update the Graph View Connections ASCII diagram
3. Add any new relation properties to affected object types
```

---

## Quality Checklist

When reviewing AnyType documentation:

- [ ] Frontmatter has correct `Object type`
- [ ] Tags match `_tags.md` definitions
- [ ] Cross-references use `→` arrow format
- [ ] Related Docs section at bottom of each file
- [ ] Properties defined in `_object-types.md` are used correctly
- [ ] Diagrams use consistent ASCII box-drawing characters
- [ ] Tables use compact format (no unnecessary line breaks in cells)
- [ ] File is in correct subdirectory per `README.md` structure

---

## Related

- → `README.md` — Master index
- → `objects/_object-types.md` — Object type definitions
- → `../../AGENTS.md` — Project-wide AI agent instructions
