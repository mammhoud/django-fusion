# AnyType Relations — Object Linking Guide

> **Import Instruction:** Use these Relations in AnyType to link related documentation objects.
> Apply the "Object" property type with the specified relation name.

---

## Relation Definitions

| Name | Type | Source → Target | Description |
|------|------|-----------------|-------------|
| `Related Architecture` | Object → Architecture | Any → Architecture | Links features/guides to architectural docs |
| `Related Feature` | Object → Feature | Any → Feature | Links architectures/guides to feature docs |
| `Related Guide` | Object → Guide | Any → Guide | Links features/architectures to guides |
| `Related Reference` | Object → Reference | Any → Reference | Links features/guides to API/command refs |
| `Related Goal` | Object → Goal | Any → Goal | Links tasks/features/plans to their strategic goals |
| `Related Plan` | Object → Plan | Any → Plan | Links milestones/tasks/goals to parent plans |
| `Related Milestone` | Object → Milestone | Any → Milestone | Links features/tasks to delivery milestones |
| `Related Edition` | Object → Edition | Any → Edition | Links features/docs/guides to product editions |
| `Related Person` | Object → Person | Any → Person | Links tasks/posts to team members |
| `Related Project` | Object → Project | Any → Project | Links plans/goals to high-level projects |
| `Related Blog Post` | Object → Blog/Post | Any → Blog/Post | Links features/guides to announcement posts |
| `Depends On` | Object → Task/Feature | Task → Task/Feature | Dependency chain for implementation |
| `Implements` | Object → Architecture | Guide → Architecture | A guide that implements an architecture |
| `Part Of` | Object → Plan | Guide → Plan | A guide that belongs to a specific plan |
| `Prerequisites` | Object → Guide | Guide → Guide | Prerequisite guides needed before starting |
| `See Also` | Object → Any | Any → Any | General cross-reference |

---

## Graph View Connections

```
                          Project 📁
                        /    |     \
                       ▼     ▼      \
                   Plan 📋  Goal 🎯  \
                  /    \      |       \
                 ▼      ▼     ▼        ▼
           Milestone 🏁  Tasks ✅  Edition 📦
                |           |         |
                ▼           ▼         ▼
           Feature ✨ ←──────┘         |
              |                        |
       ┌──────┼──────┐                |
       ▼      ▼      ▼                ▼
   Guide 📘  Blog📝  Reference📚  Architecture 🏗️

   Changelog 📋 ← connects to Features, Goals, Milestones
   Diagram 📊 ← connects to Architecture
   Person 👤 ← connects to Tasks, Posts, Plans
```

---

## Backlink Strategy

In AnyType, backlinks are created automatically when two objects are related.
Use backlinks to navigate:

```
Open Architecture → see "Related Features" → see all Feature docs
Open Goal → see "Related Tasks" → see all implementation tasks
Open Edition → see "Features Included" → see all feature docs in that edition
```

---

## Usage in Files

Each markdown file ends with a `Related Docs` section using → arrows:

```markdown
## Related Docs
- → `architecture/editions-overview.md` — Edition comparison
- → `features/pos-mini.md` — pos-mini features
- → `guides/setup.md` — Setup guide
- → `goals/v1-release.md` — V1 release goals
```

In AnyType, convert these → links to Object Relations by:
1. Opening the target document
2. Adding the appropriate Relation property (e.g., "Related Architecture", "Related Goal")
3. Linking it back to the source document

---

## Quick Reference Template

Copy this into any document's Related Docs section:

```markdown
## Related Docs
- → `architecture/` —
- → `features/` —
- → `guides/` —
- → `goals/` —
- → `plans/` —
- → `changelogs/` —
- → `blog/` —
- → `editions/` —
```
