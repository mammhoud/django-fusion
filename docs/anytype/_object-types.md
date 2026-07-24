# AnyType Object Types — Structured Documentation System

> **Import Instruction:** Create these custom Types in AnyType (Settings → Content Model → Add Type).
> Assign each doc to its type, then use Properties + Relations to link them.

---

## Type: Architecture 🏗️
**Description:** System architecture, data flow, and high-level design documents
**Layout:** Page
**Properties:**
- `Status` (Select) → Draft | Review | Published | Archived
- `Edition` (Relation → Edition)
- `Version` (Text)
- `Related Features` (Relation → Feature)
- `Related Guides` (Relation → Guide)
- `Related Goals` (Relation → Goal)
- `Tags` (Multi-select)

**Files:** `architecture/*.md`

---

## Type: Feature ✨
**Description:** Feature descriptions, capabilities, and edition-specific implementations
**Layout:** Page
**Properties:**
- `Status` (Select) → Planned | In Development | Complete | Deprecated
- `Edition` (Relation → Edition)
- `Priority` (Select) → Low | Medium | High | Critical
- `Tags` (Multi-select)
- `Depends On` (Relation → Feature)
- `Implementation` (Relation → Guide)
- `Related Goals` (Relation → Goal)
- `Related Milestones` (Relation → Milestone)

**Files:** `features/*.md`

---

## Type: Guide 📘
**Description:** Step-by-step guides for setup, development, deployment, customization
**Layout:** Page
**Properties:**
- `Status` (Select) → Draft | Review | Published
- `Category` (Select) → Setup | Development | Deployment | Theming | Testing | Migration | Troubleshooting
- `Target Audience` (Select) → Developer | Admin | End User | Designer
- `Prerequisites` (Relation → Guide)
- `Related Architecture` (Relation → Architecture)
- `Related Features` (Relation → Feature)
- `Part Of` (Relation → Plan)

**Files:** `guides/*.md`

---

## Type: Reference 📚
**Description:** API endpoints, command references, configuration schemas
**Layout:** Page
**Properties:**
- `Category` (Select) → API | CLI | Database | Config | i18n | Schema | SDK
- `Edition` (Relation → Edition)
- `Version` (Text)
- `Related Architecture` (Relation → Architecture)

**Files:** `references/*.md`

---

## Type: Changelog 📋
**Description:** Version history, migration notes, breaking changes
**Layout:** Page
**Properties:**
- `Version` (Text, required)
- `Date` (Date)
- `Edition` (Relation → Edition)
- `Type` (Select) → Major | Minor | Patch | Breaking | Security
- `Related Features` (Relation → Feature)
- `Related Goals` (Relation → Goal)
- `Related Milestones` (Relation → Milestone)

**Files:** `changelogs/*.md`

---

## Type: Diagram 📊
**Description:** ASCII / Mermaid diagrams for visual understanding
**Layout:** Page
**Properties:**
- `Type` (Select) → Flow | Architecture | Sequence | Data Model | Timeline
- `Edition` (Relation → Edition)
- `Related Docs` (Relation → Architecture | Reference | Guide)

**Files:** Embedded within other types or standalone in `diagrams/`

---

## Type: Task ✅
**Description:** Implementation tasks, TODOs, enhancement plans
**Layout:** Task
**Properties:**
- `Status` (Select) → Backlog | In Progress | Done | Blocked | Cancelled
- `Priority` (Select) → Low | Medium | High | Critical
- `Edition` (Relation → Edition)
- `Assignee` (Relation → Person)
- `Depends On` (Relation → Task)
- `Related Goal` (Relation → Goal)
- `Related Milestone` (Relation → Milestone)
- `Related Feature` (Relation → Feature)
- `Tags` (Multi-select)
- `Estimated Hours` (Number)
- `Actual Hours` (Number)

**Files:** `tasks/*.md`

---

## [NEW] Type: Goal 🎯
**Description:** Strategic goals, objectives, and key results for product development
**Layout:** Page
**Properties:**
- `Status` (Select) → Active | Achieved | At Risk | Deprioritized
- `Category` (Select) → Product | Business | Technical | Design | Growth
- `Priority` (Select) → Low | Medium | High | Critical
- `Target Date` (Date)
- `Key Results` (Text — multi-line)
- `Edition` (Relation → Edition)
- `Related Features` (Relation → Feature)
- `Related Tasks` (Relation → Task)
- `Related Milestones` (Relation → Milestone)
- `Related Plans` (Relation → Plan)
- `Tags` (Multi-select)

**Files:** `goals/*.md`

---

## [NEW] Type: Edition 📦
**Description:** Product edition/version definitions (mini, solo, full, cloud) with scope and constraints
**Layout:** Page
**Properties:**
- `Status` (Select) → Active | Deprecated | Planned
- `Version` (Text)
- `Release Date` (Date)
- `FeaturesIncluded` (Relation → Feature)
- `FeaturesExcluded` (Relation → Feature)
- `Target Audience` (Select) → Individual | Small Business | Enterprise
- `Pricing Tier` (Select) → Free | Starter | Professional | Enterprise
- `Compatibility` (Relation → Reference)
- `Related Goals` (Relation → Goal)
- `Tags` (Multi-select)

**Files:** `editions/*.md`

---

## [NEW] Type: Blog / Post 📝
**Description:** Blog posts, articles, announcements, and changelog entries
**Layout:** Page
**Properties:**
- `Status` (Select) → Draft | Published | Scheduled | Archived
- `Author` (Relation → Person)
- `Published Date` (Date)
- `Category` (Select) → Announcement | Tutorial | Case Study | Update | Technical
- `Tags` (Multi-select)
- `Featured Image` (Media)
- `Excerpt` (Text)
- `Related Features` (Relation → Feature)
- `Related Guides` (Relation → Guide)
- `Related Goals` (Relation → Goal)

**Files:** `blog/*.md`

---

## [NEW] Type: Plan 📋
**Description:** Development plans, roadmaps, release plans, and project plans
**Layout:** Page
**Properties:**
- `Status` (Select) → Draft | Active | Completed | Cancelled
- `Type` (Select) → Roadmap | Sprint | Release | Milestone | Quarterly | Annual
- `Start Date` (Date)
- `End Date` (Date)
- `Owner` (Relation → Person)
- `Related Goals` (Relation → Goal)
- `Related Milestones` (Relation → Milestone)
- `Related Tasks` (Relation → Task)
- `Related Editions` (Relation → Edition)
- `Tags` (Multi-select)
- `Progress` (Number — percentage)

**Files:** `plans/*.md`

---

## [NEW] Type: Milestone 🏁
**Description:** Key milestones, checkpoints, and release markers
**Layout:** Page
**Properties:**
- `Status` (Select) → Planned | In Progress | Reached | Delayed | Cancelled
- `Due Date` (Date)
- `Completed Date` (Date)
- `Related Plan` (Relation → Plan)
- `Related Goals` (Relation → Goal)
- `Related Tasks` (Relation → Task)
- `Related Features` (Relation → Feature)
- `Tags` (Multi-select)

**Files:** `milestones/*.md`

---

## [NEW] Type: Person 👤
**Description:** Team members, contributors, stakeholders, and authors
**Layout:** Profile
**Properties:**
- `Role` (Select) → Developer | Designer | Manager | Contributor | Stakeholder
- `Email` (Email)
- `Tags` (Multi-select)
- `Assigned Tasks` (Relation → Task)
- `Authored Posts` (Relation → Blog/Post)
- `Owned Plans` (Relation → Plan)

**Files:** `people/*.md`

---

## [NEW] Type: Project 📁
**Description:** High-level projects that group multiple plans, goals, and features
**Layout:** Page
**Properties:**
- `Status` (Select) → Active | On Hold | Completed | Cancelled
- `Start Date` (Date)
- `End Date` (Date)
- `Owner` (Relation → Person)
- `Related Plans` (Relation → Plan)
- `Related Goals` (Relation → Goal)
- `Related Milestones` (Relation → Milestone)
- `Related Features` (Relation → Feature)
- `Tags` (Multi-select)

**Files:** `projects/*.md`

---

## Import Checklist
1. Create all Types above in AnyType Content Model
2. Create the Tags from `_tags.md` as Multi-select property options
3. Create the Relations from `_relations.md`
4. Import markdown files using AnyType's Markdown import
5. Assign each file to its Type
6. Link related objects using Relations
7. Use Graph View to visualize connections

---

## Object Type Map

```
                    Project 📁
                   /    |     \
                  ▼     ▼      ▼
              Plan 📋  Goal 🎯  Edition 📦
               |       /    \      |
               ▼      ▼      ▼     ▼
           Milestone🏁 Tasks ✅  Feature ✨
                                    |
                          ┌─────────┼─────────┐
                          ▼         ▼         ▼
                      Guide 📘  Blog/Post📝  Reference📚

              Architecture 🏗️ ← supports everything
              Changelog 📋 ← tracks releases
              Diagram 📊 ← visual context
              Person 👤 ← links to tasks & posts
```
