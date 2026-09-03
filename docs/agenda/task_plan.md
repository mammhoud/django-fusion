---
Object type: Task
Tags: docs, anytype, organization, frontmatter
Status: Completed
---

# Task Plan: Complete Anytype Organization Enhancement

## Goal
Enhance all markdown files in the docs/agenda/mono-repo with proper Anytype frontmatter (Object type, Tags, Status), fix malformed tags, remove extraneous properties, and ensure every content file follows the established pattern matching `page.md` and other object files.

## Phases

### Phase 1: Audit — Identify all files needing enhancement
- Scan all .md files for missing/incorrect frontmatter
- Categorize: missing Status, missing Tags, malformed tags, extra properties, missing Object type

### Phase 2: Fix malformed frontmatter
- Fix `changelogs/_index.md` (tags: `changelogs---`)
- Fix `brand/_index.md` (tags: `logos, icons---`)
- Remove extraneous properties from `deployment.md` (Backlinks, Creation date, Created by, Links, Emoji, id)
- Remove extraneous properties from `development-workflow.md` (Backlinks, Creation date, Created by, Links, Emoji, id)

### Phase 3: Add missing frontmatter
- Add Tags/Status to `object-linking.md`
- Add Status to `logos-icons.md`
- Add Object type/Tags/Status to any other files missing them

### Phase 4: Verify all files
- Re-scan to confirm all files have proper frontmatter
- Cross-reference with `_object-types.md` for valid Object type values

## Next Step
Completed — all content files in docs/agenda/mono-repo now carry valid Object type, Tags, and Status frontmatter.
