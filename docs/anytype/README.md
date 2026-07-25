# AnyType Documentation — Structa Cloud

> **Canonical entry point** for the Anytype documentation system.
> 22 object types powering the knowledge graph across dedicated content directories.

---

## Directory Structure

```
Anytype/
├── README.md                     ← You are here
├── _prompts.md                   ← AI agent prompts for these docs
│
├── objects/                      ← AnyType object type & entity definitions
│   ├── _index.md                 ← Object types overview
│   ├── _object-types.md          ← All 22 custom type definitions
│   ├── _relations.md             ← 25+ relation definitions
│   ├── _tags.md                  ← 80+ multi-select tag definitions
│   ├── page.md, workspace.md, feature.md, milestone.md
│   ├── task.md, bookmark.md, note.md, people.md
│   ├── blog-post.md, goal.md, edition.md, configuration.md
│   └── component.md, api.md, release.md, decision.md
│       pipeline.md, style.md, sprint.md, integration.md
│
├── architecture/                 ← System architecture & design docs
├── features/                     ← Product feature descriptions
├── guides/                       ← Step-by-step guides (with install/)
│
├── components/                   ← UI & business component docs (NEW)
├── api/                          ← API endpoint definitions (NEW)
├── releases/                     ← Version release tracking (NEW)
├── decisions/                    ← ADRs (Architectural Decision Records) (NEW)
├── pipelines/                    ← CI/CD pipeline definitions (NEW)
├── style/                        ← Design tokens & theme docs (NEW)
├── sprints/                      ← Sprint cycle tracking (NEW)
├── integrations/                 ← Third-party connector docs (NEW)
│
├── references/                   ← API & config references
├── plans/                        ← Business & project plans
├── changelogs/                   ← Version history
├── tasks/                        ← Implementation tasks
├── goals/                        ← Strategic goals & OKRs
├── milestones/                   ← Key milestones & checkpoints
├── editions/                     ← Product edition definitions
├── projects/                     ← High-level project tracking
├── blog/                         ← Blog posts & announcements
├── people/                       ← Team members & authors
│
├── schemas/                      ← JSON schema definitions
│   ├── page.schema.json
│   ├── bookmark.schema.json
│   ├── milestone.schema.json
│   ├── note.schema.json
│   ├── people.schema.json
│   └── task.schema.json
│
├── diagrams/                     ← ASCII/Mermaid diagrams
└── files/                        ← Images & assets
```

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
| Component | 🔧 | `components/` | Reusable UI & business logic |
| API | 📡 | `api/` | Endpoint definitions |
| Release | 🚀 | `releases/` | Version releases |
| Decision | ⚡ | `decisions/` | ADRs & design rationale |
| Pipeline | 🔄 | `pipelines/` | CI/CD workflow definitions |
| Style | 🎨 | `style/` | Design tokens & brand |
| Sprint | 🏃 | `sprints/` | Sprint cycles & retrospectives |
| Integration | 🔗 | `integrations/` | Third-party connectors |

---

## Object Type Organization

The types are organized in layers:

```
Strategic Layer:     Project 📁 → Plan 📋 → Goal 🎯 → Milestone 🏁
Delivery Layer:      Sprint 🏃 → Task ✅ → Feature ✨ → Release 🚀
Implementation Layer: Guide 📘 → Component 🔧 → API 📡 → Integration 🔗
Foundation Layer:    Architecture 🏗️ → Decision ⚡ → Style 🎨 → Reference 📚
Tracking Layer:      Changelog 📋 → Pipeline 🔄 → Diagram 📊
People Layer:        Person 👤 → Blog/Post 📝
Product Layer:       Edition 📦 → features/*.md
```

---

## Navigation

| Section | Files | Start Here |
|---------|-------|-----------|
| **Objects** | 22 type definitions | `objects/_object-types.md` |
| **Architecture** | System design | `architecture/_index.md` |
| **Features** | Product capabilities | `features/_index.md` |
| **Guides** | How-to & workflows | `guides/_index.md` |
| **Components** | UI library | `components/_index.md` |
| **API** | Endpoints | `api/_index.md` |
| **References** | Schemas & commands | `references/_index.md` |
| **Plans** | Strategy & operations | `plans/_index.md` |
| **Tasks** | Implementation backlog | `tasks/_index.md` |
| **Changelogs** | Version history | `changelogs/_index.md` |

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

- → `../ai/prompts.md` — AI agent prompts
- → `../../AGENTS.md` — Project-wide AI agent instructions
- → `../../libs/ceptor-ai/AGENTS.md` — Ceptor AI agent instructions
- → `object/_object-types.md` — All 22 object type definitions
- → `objects/_relations.md` — Relation linking guide
- → `objects/_tags.md` — Tag definitions
