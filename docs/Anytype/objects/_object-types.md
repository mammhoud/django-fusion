# Object Types — Knowledge Graph Schema

> **Import Instruction:** Create these custom Types in your AnyType space (Settings → Content Model → Add Type).
> Assign each doc to its type, then use Properties + Relations to build the knowledge graph.

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
- `Related Decisions` (Relation → Decision)
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
- `Related API` (Relation → API)

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
- `Related Release` (Relation → Release)

**Files:** `changelogs/*.md`

---

## Type: Diagram 📊
**Description:** ASCII / Mermaid diagrams for visual understanding
**Layout:** Page
**Properties:**
- `Type` (Select) → Flow | Architecture | Sequence | Data Model | Timeline
- `Edition` (Relation → Edition)
- `Related Docs` (Relation → Architecture | Reference | Guide)

**Files:** `diagrams/*.md`

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
- `Related Sprint` (Relation → Sprint)
- `Tags` (Multi-select)
- `Estimated Hours` (Number)
- `Actual Hours` (Number)

**Files:** `tasks/*.md`

---

## Type: Goal 🎯
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

## Type: Edition 📦
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

## Type: Blog / Post 📝
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
- `Related Release` (Relation → Release)

**Files:** `blog/*.md`

---

## Type: Plan 📋
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

## Type: Milestone 🏁
**Description:** Key milestones, checkpoints, and release markers
**Layout:** Page
**Properties:**
- `Status` (Select) → Planned | In Progress | Reached | Delayed | Cancelled
- `Due Date` (Date)
- `Completed Date` (Date)
- `Related Plan` (Relation → Plan)
- `Related Release` (Relation → Release)
- `Related Goals` (Relation → Goal)
- `Related Tasks` (Relation → Task)
- `Related Features` (Relation → Feature)
- `Tags` (Multi-select)

**Files:** `milestones/*.md`

---

## Type: Person 👤
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

## Type: Project 📁
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
- `Related Releases` (Relation → Release)
- `Tags` (Multi-select)

**Files:** `projects/*.md`

---

## Type: Component 🔧
**Description:** Reusable UI/backend components from django-fusion and POS frontend
**Layout:** Page
**Properties:**
- `Status` (Select) → Stable | Beta | Deprecated | Experimental
- `Category` (Select) → UI | Form | Navigation | Data | Layout | Widget
- `Framework` (Select) → React | Django | Rust | Tailwind
- `Edition` (Relation → Edition)
- `Depends On` (Relation → Component)
- `Related API` (Relation → API)
- `Related Style` (Relation → Style)
- `Related Features` (Relation → Feature)
- `Tags` (Multi-select)

**Files:** `components/*.md`

---

## Type: API 📡
**Description:** API endpoint definitions, request/response schemas, authentication
**Layout:** Page
**Properties:**
- `Status` (Select) → Stable | Beta | Deprecated | Experimental
- `Method` (Select) → GET | POST | PUT | PATCH | DELETE
- `Endpoint` (Text)
- `Auth Required` (Boolean)
- `Rate Limited` (Boolean)
- `Version` (Text)
- `Edition` (Relation → Edition)
- `Related Feature` (Relation → Feature)
- `Related Component` (Relation → Component)
- `Related Integration` (Relation → Integration)
- `Tags` (Multi-select)

**Files:** `api/*.md`

---

## Type: Release 🚀
**Description:** Version releases with features, fixes, and deployment notes
**Layout:** Page
**Properties:**
- `Status` (Select) → Planned | In Progress | Released | Rolled Back
- `Version` (Text, required)
- `Release Date` (Date)
- `Edition` (Relation → Edition)
- `Milestone` (Relation → Milestone)
- `Related Features` (Relation → Feature)
- `Related Changelog` (Relation → Changelog)
- `Related Pipeline` (Relation → Pipeline)
- `Tags` (Multi-select)

**Files:** `releases/*.md`

---

## Type: Decision ⚡
**Description:** Architectural Decision Records (ADRs) — rationale for key technical decisions
**Layout:** Page
**Properties:**
- `Status` (Select) → Proposed | Accepted | Deprecated | Superseded
- `Category` (Select) → Architecture | Technology | Process | Security | Performance
- `Date` (Date)
- `Decision Maker` (Relation → Person)
- `Supersedes` (Relation → Decision)
- `Related Architecture` (Relation → Architecture)
- `Related Features` (Relation → Feature)
- `Tags` (Multi-select)

**Files:** `decisions/*.md`

---

## Type: Pipeline 🔄
**Description:** CI/CD pipeline definitions, build steps, deployment workflows
**Layout:** Page
**Properties:**
- `Status` (Select) → Active | Inactive | Failed
- `Type` (Select) → CI | CD | Test | Deploy | Lint | Security
- `Provider` (Select) → GitHub Actions | Docker | Custom
- `Triggers` (Multi-select) → Push | PR | Schedule | Manual
- `Related Release` (Relation → Release)
- `Related Reference` (Relation → Reference)
- `Tags` (Multi-select)

**Files:** `pipelines/*.md`

---

## Type: Style 🎨
**Description:** Design tokens, UI patterns, theme definitions, brand guidelines
**Layout:** Page
**Properties:**
- `Category` (Select) → Color | Typography | Spacing | Shadow | Animation | Icon
- `Token` (Text)
- `Value` (Text)
- `Theme` (Relation → Edition)
- `Related Component` (Relation → Component)
- `Depends On` (Relation → Style)
- `Tags` (Multi-select)

**Files:** `style/*.md`

---

## Type: Sprint 🏃
**Description:** Sprint cycles with goals, tasks, and retrospectives
**Layout:** Page
**Properties:**
- `Status` (Select) → Planning | Active | Completed | Cancelled
- `Sprint Number` (Number)
- `Start Date` (Date)
- `End Date` (Date)
- `Goals` (Text — multi-line)
- `Retrospective` (Text — multi-line)
- `Owner` (Relation → Person)
- `Related Tasks` (Relation → Task)
- `Related Goals` (Relation → Goal)
- `Related Milestones` (Relation → Milestone)
- `Tags` (Multi-select)

**Files:** `sprints/*.md`

---

## Type: Integration 🔗
**Description:** Third-party integrations, connectors, and external service connections
**Layout:** Page
**Properties:**
- `Status` (Select) → Active | Planned | Deprecated | Broken
- `Category` (Select) → Payment | CRM | Email | SMS | Analytics | Auth | Storage
- `Provider` (Text)
- `Auth Type` (Select) → API Key | OAuth | JWT | Basic
- `Edition` (Relation → Edition)
- `Related API` (Relation → API)
- `Related Feature` (Relation → Feature)
- `Related Pipeline` (Relation → Pipeline)
- `Tags` (Multi-select)

**Files:** `integrations/*.md`

---

## Type: Page 📄
**Description:** General-purpose knowledge pages — documentation, notes, and reference content
**Layout:** Page
**Properties:**
- `Status` (Select) → Draft | Review | Published
- `Tags` (Multi-select)
- `Related Architecture` (Relation → Architecture)
- `Related Features` (Relation → Feature)
- `Related Guides` (Relation → Guide)

**Files:** `ANY — foundational type for all content`

---

## Type: Note 📝
**Description:** Quick notes, ideas, meeting minutes, and informal documentation
**Layout:** Note
**Properties:**
- `Tags` (Multi-select)
- `Related Architecture` (Relation → Architecture)
- `Related Feature` (Relation → Feature)
- `Related Guide` (Relation → Guide)

**Files:** Embedded within other types or standalone

---

## Type: Bookmark 🔖
**Description:** External links and references to resources outside the knowledge graph
**Layout:** Bookmark
**Properties:**
- `URL` (Text)
- `Tags` (Multi-select)
- `Category` (Select) → Development | Documentation | Publishing | Staging | Done
- `Related Feature` (Relation → Feature)

**Files:** Embedded within other types or standalone

---

## Type: Workspace 🏢
**Description:** High-level workspace/hub pages that group and reference multiple related documents
**Layout:** Page
**Properties:**
- `Backlinks` (Text)
- `Links` (Text)
- `Emoji` (Emoji)
- `Related Plans` (Relation → Plan)
- `Related Projects` (Relation → Project)
- `Tags` (Multi-select)

**Files:** Hub/overview pages

---

## Type: Configuration ⚙️
**Description:** System configuration, environment variables, build settings, and deployment parameters
**Layout:** Page
**Properties:**
- `Category` (Select) → Environment | Build | Database | Proxy | Auth | Deployment
- `Platform` (Multi-select) → macOS | Linux | Windows | Docker
- `Required` (Boolean)
- `Default Value` (Text)
- `Related Edition` (Relation → Edition)
- `Related Guide` (Relation → Guide)
- `Tags` (Multi-select)

**Files:** `references/*.md`, `guides/configuration.md`, `guides/install/*.md`

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

## Object Type Map (27 Types)

### Primary Knowledge Graph
```
                    Project 📁
                   /    |     \
                  ▼     ▼      ▼
              Plan 📋  Goal 🎯  Edition 📦
               |       /    \      |
               ▼      ▼      ▼     ▼
           Milestone🏁 Tasks ✅  Feature ✨
               |                /    |    \
               ▼               ▼     ▼     ▼
            Sprint 🏃     Guide 📘  API 📡  Component 🔧
            Release 🚀     Blog📝    Integration🔗  Style 🎨

    Architecture 🏗️ ← supports everything (decisions⚡, diagrams📊)
    Pipeline 🔄 ← delivers releases
    Person 👤 ← links to tasks, posts, decisions, sprints
    Changelog 📋 ← tracks versions (linked to Release 🚀)
    Reference 📚 ← API & config docs
```

### Foundation Types
```
Page 📄      ← General-purpose content (most common type)
Note 📝      ← Quick/informal documentation
Bookmark 🔖  ← External resource links
Workspace 🏢 ← Hub pages grouping related content
Configuration ⚙️ ← System config & environment variables
```
