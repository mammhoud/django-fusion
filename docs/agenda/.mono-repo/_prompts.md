---
Object type: Guide
Tags: prompts, ai, agents
Status: Published
---

> Prompts and instructions for AI agents working with the AnyType documentation system.
> **Container:** the docs import as one Anytype **Channel** — see `guides/channel-structure.md` before creating or moving types.
>
> **Status: all prompts completed (2026-09-05).** Every type below has a
> definition file in `objects/`, every type has a home directory with content,
> and the graph integrity check passes (see `objects/_index.md` per-type table).

---

## Channel operations

### Setting up the Structa Cloud Channel

> ✅ Completed — see `objects/_object-types.md` (registry), `objects/_relations.md` (relations), `objects/_tags.md` (tags), `objects/_templates.md` (templates), `objects/_index.md` (per-type files).

Create the Anytype Channel (Vault → + → Personal/Group), choose a Page Home, then build its Content Model:

1. Types and properties from `objects/_object-types.md`
2. Relations from `objects/_relations.md`
3. Tags from `objects/_tags.md`
4. Templates from `objects/_templates.md`

Set `README.md` as the Homepage, invite members per `objects/team.md`, and pin `objects/_index.md` + `guides/_index.md` to the Sidebar.

### Checking complete-document compliance

When reviewing a content object file, verify it is a **complete document**:

1. Frontmatter has `Object type`, `Tags`, `Status`, and required properties
2. H1 title exists with an object-type label
3. One-line description under the H1
4. Body sections match the type's template
5. `## Related` links exist at the bottom
6. Status is accurate (Active objects are linked from an active index)

---

## Document generation

### Creating a new object type

> ✅ Completed — every type defined in `_object-types.md` now has a definition
> file (`objects/<type>.md`). Missing types added 2026-09-05: architecture,
> guide, reference, changelog, diagram, project, report, dashboard,
> data-pipeline, methodology, insight, recommendation, repository, module,
> documentation.

Create an AnyType object type definition for the given type name at `docs/agenda/mono-repo/objects/<name>.md`, including:

1. Frontmatter with object type, tags, and status
2. Description of the type's purpose
3. Properties table (Name, Type, Options, Description)
4. Usage in the knowledge graph
5. Example with frontmatter
6. Related links at the bottom

### Writing a platform install guide

> ✅ Completed — `guides/install/` covers docker, linux, macos, windows.

Create a platform installation guide at `docs/agenda/mono-repo/guides/install/<platform>.md`, including:

1. Frontmatter with Object type: Guide, platform tag, Status: Published
2. Prerequisites section
3. Step-by-step install instructions
4. Clone and setup repository instructions
5. Verification steps
6. Troubleshooting table
7. Related links

### Adding a feature document

> ✅ Completed — `features/` holds 14 feature objects (POS, CMS, AI, portfolio…).

Create a new feature description at `docs/agenda/mono-repo/features/<name>.md`, including:

1. Frontmatter with Object type: Feature, edition tags, status
2. Feature overview and purpose
3. Key capabilities
4. Edition compatibility matrix
5. Related docs links

---

## Knowledge graph operations

### Checking graph integrity

> ✅ Completed 2026-09-05 — all new directories (`projects/`, `editions/`,
> `sprints/`, `releases/`, `integrations/`, `apis/`, `components/`, `tools/`,
> `pipelines/`, `styles/`, `diagrams/`, `reports/`, `dashboards/`,
> `data-pipelines/`, `methodologies/`, `insights/`, `recommendations/`,
> `repositories/`, `modules/`, `documentation/`) verified: every `→ link`
> resolves to an existing file, no orphaned content objects.

Review the AnyType documentation for consistency:

1. Check that every document has correct frontmatter (Object type, Tags)
2. Verify that all cross-references (→ links) point to existing files
3. Check for orphaned files (no backlinks from other docs)
4. Report any duplicate or deprecated content

### Filling role ↔ project relations

> Runs offline; writes only inside `<!-- agenda-relations:… -->` blocks, so it is
> safe to re-run after any edit to the fact tables.

Fill the roles named in the agenda fact tables back into the graph
the same way the Anytype client attaches relation properties to objects:

1. `node agenda/scripts/link-agenda-relations.mjs` (from `docs/`) — scans
   `task-tracking.md`, `sales-pipeline.md`, the plans family,
   `case-studies/` and `feature-tracking/` (one file per product), then fills `## Assigned Objects (generated)` on
   Person objects and `## Related Roles / Related Documents / Related Features`
   on Project objects, plus a missing `Owner:` from the explicit owner map.
   `--check` (CI) fails on drift; `--dry-run` reports only; `--emit-anytype`
   writes the payload in `anytype-client` shape for a later push.
2. Resolve anything it reports: unknown `@handles` (create the Person object or
   add a `HANDLE_ALIASES` entry) and non-person owners (teams, `TBD`) — the
   script never invents a Person or an accountable `Owner`.
3. Re-run `--check` after hand-editing an object so the generated block and the
   authored relations stay consistent.

### Updating relations

> ✅ Completed — `objects/_relations.md` now includes the data-analysis and
> monorepo-structure relation groups added with the new types.

Update the relations in `docs/agenda/mono-repo/objects/_relations.md` to include the new type entity:

1. Add the relation entry to the relations table
2. Update the Graph View Connections diagram
3. Add any new relation properties to affected object types

---

## Quality checklist

When reviewing AnyType documentation:

- Frontmatter has the correct Object type
- Tags match `_tags.md` definitions
- Cross-references use the → arrow format
- Related Docs section at the bottom of each file
- Properties defined in `_object-types.md` are used correctly
- Diagrams use consistent box-drawing characters
- Tables use compact format (no unnecessary line breaks in cells)
- File is in the correct subdirectory per `README.md` structure

---

## Related

- → `README.md` — Master index
- → `objects/_object-types.md` — Object type definitions
- → `../../../AGENTS.md` — Project-wide AI agent instructions
