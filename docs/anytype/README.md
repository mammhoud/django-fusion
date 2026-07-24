# AnyType Documentation System

**Type:** Guide 📘
**Tags:** `#documentation` `#pos-mini` `#pos-solo` `#pos-full` `#pos-cloud`
**Status:** Published

---

## Overview

This directory contains the Structured Documentation System for Structa Cloud — a comprehensive AnyType knowledge base covering product architecture, features, guides, development plans, goals, blog content, and more. The system uses 14 custom object types with interlinked relations for full graph-based navigation.

---

## Directory Structure

```
anytype/
├── README.md                  # This file — navigation and overview
├── _object-types.md           # All 14 custom type definitions
├── _relations.md              # Object relation/linking guide (15 relations)
├── _tags.md                   # Multi-select tag definitions (9 categories)
├── _templates.md              # Template generation guide for new docs
├── _status.md                 # Status tracker — what's done vs needs work
│
├── architecture/              # System architecture 🏗️
│   ├── architecture-overview.md
│   ├── editions-overview.md
│   ├── role-system.md
│   ├── sync-architecture.md
│   └── theme-system.md
│
├── features/                  # Feature descriptions ✨
│   ├── comparison-matrix.md
│   ├── pos-mini.md
│   ├── pos-solo.md
│   └── pos-full.md
│
├── guides/                    # Step-by-step guides 📘
│   ├── setup.md
│   ├── development.md
│   └── theming.md
│
├── references/                # API & config references 📚
│   ├── database-schema.md
│   ├── i18n-keys.md
│   ├── sidecar-api.md
│   └── tauri-commands.md
│
├── changelogs/                # Version history 📋
│   └── pos.md
│
├── goals/                     # ⭐ NEW — Strategic goals and OKRs 🎯
│   └── (coming soon)
│
├── editions/                  # ⭐ NEW — Edition definitions 📦
│   └── (coming soon)
│
├── blog/                      # ⭐ NEW — Blog posts and announcements 📝
│   └── (coming soon)
│
├── plans/                     # ⭐ NEW — Roadmaps and development plans 📋
│   └── (coming soon)
│
├── milestones/                # ⭐ NEW — Key milestones and checkpoints 🏁
│   └── (coming soon)
│
├── people/                    # ⭐ NEW — Team member profiles 👤
│   └── (coming soon)
│
├── projects/                  # ⭐ NEW — High-level project definitions 📁
│   └── (coming soon)
│
├── diagrams/                  # ASCII / Mermaid diagrams 📊
│   └── (future)
│
├── tasks/                     # Implementation tasks ✅
│   └── (various .md files)
│
└── schemas/                   # JSON Schema definitions
    ├── task.schema.json
    ├── feature.schema.json
    ├── milestone.schema.json
    └── ...
```

---

## Object Type System (14 Types)

| # | Type | Icon | Directory | Status |
|---|------|------|-----------|--------|
| 1 | Architecture | 🏗️ | `architecture/` | ✅ |
| 2 | Feature | ✨ | `features/` | ✅ |
| 3 | Guide | 📘 | `guides/` | ✅ |
| 4 | Reference | 📚 | `references/` | ✅ |
| 5 | Changelog | 📋 | `changelogs/` | ✅ |
| 6 | Diagram | 📊 | `diagrams/` | ✅ |
| 7 | Task | ✅ | `tasks/` | ✅ |
| 8 | **Goal** | 🎯 | `goals/` | 📝 |
| 9 | **Edition** | 📦 | `editions/` | 📝 |
| 10 | **Blog/Post** | 📝 | `blog/` | 📝 |
| 11 | **Plan** | 📋 | `plans/` | 📝 |
| 12 | **Milestone** | 🏁 | `milestones/` | 📝 |
| 13 | **Person** | 👤 | `people/` | 📝 |
| 14 | **Project** | 📁 | `projects/` | 📝 |

> **7 new types added** — see `_object-types.md` for full definitions.

---

## Object Type Graph

```
                    Project 📁
                   /    |     \
                  ▼     ▼      ▼
              Plan 📋  Goal 🎯  Edition 📦
               |       /    \      |
               ▼      ▼      ▼     ▼
           Milestone🏁  Tasks ✅  Feature ✨
                                     |
                           ┌─────────┼─────────┐
                           ▼         ▼         ▼
                       Guide 📘  Blog/Post📝  Reference📚

              Architecture 🏗️ ← supports everything
              Changelog 📋 ← tracks releases
              Diagram 📊 ← visual context
              Person 👤 ← links to tasks & posts
```

---

## Quick Start

### 1. Import Schema Files
Start by creating the object types, tags, and relations in AnyType:

1. Open AnyType → Settings → Content Model → Add Type
2. Create the 14 types from `_object-types.md`
3. Create the Tags Multi-select property from `_tags.md`
4. Create the Relations from `_relations.md`

### 2. Generate New Documents
Use `_templates.md` for quick document creation:

```markdown
# Copy the template for your type, fill in the fields
# Examples:
# - Goal template → `goals/q1-2025-release.md`
# - Edition template → `editions/pos-solo-v2.md`
# - Blog template → `blog/2024-12-01-new-feature.md`
```

### 3. Import Markdown
Use AnyType's Markdown import feature for each file.
Assign the correct Type to each document after import.

### 4. Link Objects
For the `Related Docs` sections, create Object Relations:
- Open the target document
- Add the relation property
- Link back to the source

### 5. Explore Graph View
Open Graph View to see all connections.
Use filters by Type, Tags, or Edition to focus.

---

## Status Tracking

See `_status.md` for the full status tracker including:
- ✅ What's complete
- 🔄 What needs revision
- 📝 What's planned
- 🗑️ What's deprecated
- Enhancement roadmap (Phases 1-4)

---

## Style Guide

- **Minimal code** — Show method signatures + `→` return types, not full implementations
- **ASCII diagrams** — Use box-drawing characters for flow diagrams
- **Tables** — Compact comparison tables
- **Related links** — Always end with `→` cross-references
- **Frontmatter** — Type, Tags, Status, Edition at top
- **Object mapping** — Use `_templates.md` for consistent document structure

---

## Related Docs
- → `_object-types.md` — All 14 type definitions
- → `_relations.md` — Object linking guide
- → `_tags.md` — Tag definitions
- → `_templates.md` — Template generation guide
- → `_status.md` — Status tracker
- → `architecture/architecture-overview.md` — System architecture
