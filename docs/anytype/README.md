# AnyType Documentation — Structa Cloud

> **Canonical entry point** for the Anytype documentation system.
> 27 object types powering the knowledge graph across dedicated content directories.

---

## Directory Structure

```
Anytype/
├── README.md                     ← You are here
│
├── objects/                      ← Core type definitions & entity files
│   ├── _object-types.md          ← All 27 type definitions with properties
│   ├── _relations.md             ← 36 relation definitions
│   ├── _tags.md                  ← 80+ multi-select tag definitions
│   ├── _templates.md             ← Template generation guide
│   ├── _index.md                 ← Object types overview
│   └── *.md                      ← Individual entity files (feature, task, goal, etc.)
│
├── architecture/                 ← System architecture & design docs
├── features/                     ← Product feature descriptions
├── guides/                       ← Step-by-step guides
├── references/                   ← API & config references
├── plans/                        ← Business & project plans
├── tasks/                        ← Implementation backlog
├── goals/                        ← Strategic goals & OKRs
├── milestones/                   ← Key milestones & checkpoints
├── changelogs/                   ← Version history
├── blog/                         ← Blog posts & announcements
├── editions/                     ← Product edition definitions
├── projects/                     ← High-level project tracking
├── people/                       ← Team members & authors
│
├── brand/                        ← Brand assets, logos, icons
├── schemas/                      ← JSON schema definitions
├── diagrams/                     ← ASCII/Mermaid diagrams
└── files/                        ← Images & assets
```

Content directories (`architecture/`, `features/`, `guides/`, `references/`, `plans/`, `tasks/`) contain actual documentation files. Directories without dedicated documentation files (`api/`, `components/`, `integrations/`, `pipelines/`, `releases/`, `sprints/`, `style/`) are available for expansion but currently show only in the object type definitions.

---

## Object Type Reference

| Type | Emoji | Directory | Description |
|------|-------|-----------|-------------|
| Architecture | 🏗️ | `architecture/` | System design, data flow, tech stack |
| Feature | ✨ | `features/` | Product capabilities by edition |
| Guide | 📘 | `guides/` | Setup, dev, deploy, customize |
| Reference | 📚 | `references/` | APIs, commands, configs |
| Changelog | 📋 | `changelogs/` | Version history & release notes |
| Diagram | 📊 | `diagrams/` | Visual architecture & flow diagrams |
| Task | ✅ | `tasks/` | Implementation backlog & TODOs |
| Goal | 🎯 | `goals/` | Strategic objectives & OKRs |
| Edition | 📦 | `editions/` | Product edition definitions |
| Blog/Post | 📝 | `blog/` | Articles & announcements |
| Plan | 📋 | `plans/` | Roadmaps & project plans |
| Milestone | 🏁 | `milestones/` | Release markers & checkpoints |
| Person | 👤 | `people/` | Team members & contributors |
| Project | 📁 | `projects/` | High-level project tracking |
| Component | 🔧 | `—` | Reusable UI & business logic |
| API | 📡 | `—` | Endpoint definitions |
| Release | 🚀 | `—` | Version releases |
| Decision | ⚡ | `—` | ADRs & design rationale |
| Pipeline | 🔄 | `—` | CI/CD workflow definitions |
| Style | 🎨 | `—` | Design tokens & brand |
| Sprint | 🏃 | `—` | Sprint cycles & retrospectives |
| Integration | 🔗 | `—` | Third-party connectors |
| Page | 📄 | `—` | General knowledge content |
| Note | 📝 | `—` | Quick notes & meeting minutes |
| Bookmark | 🔖 | `—` | External resource links |
| Workspace | 🏢 | `—` | Hub pages grouping content |
| Configuration | ⚙️ | `—` | System config & environment |

---

## Organization Layers

```
Strategic Layer:     Project 📁 → Plan 📋 → Goal 🎯 → Milestone 🏁
Delivery Layer:      Sprint 🏃 → Task ✅ → Feature ✨ → Release 🚀
Implementation Layer: Guide 📘 → Component 🔧 → API 📡 → Integration 🔗
Foundation Layer:    Architecture 🏗️ → Decision ⚡ → Style 🎨 → Reference 📚
Tracking Layer:      Changelog 📋 → Pipeline 🔄 → Diagram 📊
People Layer:        Person 👤 → Blog/Post 📝
Product Layer:       Edition 📦 → features/*.md
Cross-cutting:       Page 📄, Note 📝, Bookmark 🔖, Workspace 🏢, Configuration ⚙️
```

---

## AnyType Import Workflow

1. **Define** — Create object types from `objects/_object-types.md`
2. **Tag** — Create multi-select Tags from `objects/_tags.md`
3. **Relate** — Create relations from `objects/_relations.md`
4. **Import** — Import markdown files using AnyType's Markdown import
5. **Assign** — Assign each file to its object type
6. **Link** — Connect objects using relations
7. **Graph** — Explore the complete knowledge graph

---

## Style Guide

- **Minimal code** — Show method signatures + `→` return types, not full implementations
- **ASCII diagrams** — Use box-drawing characters for flow diagrams
- **Frontmatter** — `Object type`, `Tags`, `Status` at top of every file
- **Cross-references** — Use `→` arrows for related links at end of each doc
- **Color tokens** — Reference project colors with hex codes in context

---

## Related Docs

- → `objects/_object-types.md` — All 27 object type definitions
- → `objects/_relations.md` — Relation linking guide
- → `objects/_tags.md` — Tag definitions
- → `objects/_templates.md` — Template generation guide
- → `brand/logos-icons.md` — Logo & icon reference
- → `../../AGENTS.md` — Project-wide AI agent instructions
- → `../../libs/ceptor-ai/AGENTS.md` — Ceptor AI agent instructions
