# AnyType Template Generation Guide

> **Purpose:** Standard templates for creating new AnyType documentation objects.
> Copy the appropriate template, fill in the fields, and import into AnyType.
> Templates cover all 27 object types with proper frontmatter and relation links.

---

## Reference: Common Frontmatter Fields

| Field | Type | Description |
|-------|------|-------------|
| `Object type` | Text | The AnyType object type name |
| `Status` | Select | Lifecycle state (varies by type) |
| `Tags` | Multi-select | Cross-cutting labels from `_tags.md` |
| `Edition` | Relation → Edition | Product edition this belongs to |

---

## Template: Architecture 🏗️

```markdown
---
Object type: Architecture
Status: Draft
Edition: (link to Edition)
Version: 0.1.0
Tags:
---

# [Architecture Name]

## Overview
Brief description of the architecture component, its purpose, and scope.

## Components
- **Component 1:** Description of component and its responsibilities
- **Component 2:** Description of component and its responsibilities

## Data Flow
```
[ASCII or Mermaid diagram showing data/service flow]
```

## Related Decisions
- (link to Decision) — Design rationale for this architecture

## Related Docs
- → `features/` — Features this architecture supports
- → `guides/` — Implementation guides
- → `goals/` — Strategic goals this serves
```

---

## Template: Feature ✨

```markdown
---
Object type: Feature
Status: Planned
Edition: (link to Edition)
Priority: Medium
Tags:
---

# [Feature Name]

## Description
What does this feature do? Why is it needed?

## User Story
As a [type of user], I want to [action] so that [benefit].

## Acceptance Criteria
1. [ ] Criterion 1 — describes expected behavior
2. [ ] Criterion 2 — describes edge case
3. [ ] Criterion 3 — describes error handling

## Dependencies
- Depends on: (link to Feature)

## Related Docs
- → `architecture/` — Architecture context
- → `guides/` — Implementation guide
- → `goals/` — Strategic goal alignment
- → `api/` — API endpoints
- → `milestones/` — Delivery milestone
```

---

## Template: Guide 📘

```markdown
---
Object type: Guide
Status: Draft
Category: [Setup | Development | Deployment | Theming | Testing | Migration | Troubleshooting]
Target Audience: [Developer | Admin | End User | Designer]
Tags:
---

# [Guide Title]

## Prerequisites
- (link to prerequisite Guide)
- Required tools and versions

## Step 1: [Title]
Step-by-step description and instructions.

## Step 2: [Title]
Step-by-step description and instructions.

## Verification
Commands or checks to confirm success.

## Troubleshooting
| Issue | Solution |
|-------|----------|
| Common error | How to resolve |

## Related Docs
- → `architecture/` — Architecture reference
- → `references/` — Command/config reference
- → `features/` — Related features
```

---

## Template: Reference 📚

```markdown
---
Object type: Reference
Category: [API | CLI | Database | Config | i18n | Schema | SDK]
Edition: (link to Edition)
Version: 1.0.0
Tags:
---

# [Reference Name]

## Overview
What this reference covers.

## Details
Organized reference content — tables, code blocks, lists.

## Related Docs
- → `architecture/` — Architecture context
- → `guides/` — Usage guides
```

---

## Template: Changelog 📋

```markdown
---
Object type: Changelog
Version: 1.0.0
Date: YYYY-MM-DD
Edition: (link to Edition)
Type: [Major | Minor | Patch | Breaking | Security]
Tags:
---

# Changelog — v[Version]

### Added
- New features and capabilities (link to Feature)

### Fixed
- Bug fixes and corrections (link to Task)

### Changed
- Modifications to existing functionality

### Deprecated
- Features scheduled for removal

### Removed
- Features removed in this version

## Related Docs
- → `releases/` — Release notes
- → `milestones/` — Related milestones
```

---

## Template: Diagram 📊

```markdown
---
Object type: Diagram
Type: [Flow | Architecture | Sequence | Data Model | Timeline]
Edition: (link to Edition)
Tags:
---

# [Diagram Title]

```
[ASCII or Mermaid diagram content]
```

## Explanation
Description of what the diagram shows.

## Related Docs
- → `architecture/` — Architecture context
- → `references/` — Supporting references
- → `guides/` — Related guides
```

---

## Template: Task ✅

```markdown
---
Object type: Task
Status: [Backlog | In Progress | Done | Blocked | Cancelled]
Priority: [Low | Medium | High | Critical]
Edition: (link to Edition)
Estimated Hours: 
Tags:
---

# [Task Title]

## Description
What needs to be done and why.

## Implementation Notes
- Technical approach
- Files to modify
- Architecture considerations

## Dependencies
- Depends on: (link to Task)
- Blocked by: (link to Task)

## Related Docs
- → `features/` — Feature this implements
- → `goals/` — Goal this serves
- → `milestones/` — Milestone this is part of
- → `sprints/` — Sprint this is assigned to
```

---

## Template: Goal 🎯

```markdown
---
Object type: Goal
Status: [Active | Achieved | At Risk | Deprioritized]
Category: [Product | Business | Technical | Design | Growth]
Priority: [Low | Medium | High | Critical]
Target Date: YYYY-MM-DD
Edition: (link to Edition)
Tags:
---

# [Goal Title]

## Description
What we want to achieve and why it matters.

## Key Results
1. [KR 1 — measurable outcome with target]
2. [KR 2 — measurable outcome with target]
3. [KR 3 — measurable outcome with target]

## Related Docs
- → `features/` — Features that serve this goal
- → `tasks/` — Implementation tasks
- → `milestones/` — Progress milestones
- → `plans/` — Parent plan
```

---

## Template: Edition 📦

```markdown
---
Object type: Edition
Status: [Active | Deprecated | Planned]
Version: 1.0.0
Release Date: YYYY-MM-DD
Target Audience: [Individual | Small Business | Enterprise]
Pricing Tier: [Free | Starter | Professional | Enterprise]
Tags:
---

# [Edition Name]

## Description
What this edition includes, its scope, and target use case.

## Features
- **Included:** (link to Feature), (link to Feature)
- **Excluded:** (link to Feature), (link to Feature)

## Compatibility
- (link to Reference) — System requirements
- (link to Reference) — Dependencies

## Related Docs
- → `goals/` — Goals this edition supports
- → `architecture/editions.md` — Edition comparison
- → `features/comparison-matrix.md` — Feature grid
```

---

## Template: Blog/Post 📝

```markdown
---
Object type: Blog/Post
Status: [Draft | Published | Scheduled | Archived]
Author: (link to Person)
Published Date: YYYY-MM-DD
Category: [Announcement | Tutorial | Case Study | Update | Technical]
Tags:
---

# [Post Title]

> **Excerpt:** Brief summary for listings and previews.

## Introduction
Context and background for the post.

## Content
Body of the post — structured with headings, lists, and code examples.

## Related Docs
- → `features/` — Featured product/capability
- → `guides/` — Related guides
- → `goals/` — Strategic goals
- → `releases/` — Related release
- → `editions/` — Product edition context
```

---

## Template: Plan 📋

```markdown
---
Object type: Plan
Status: [Draft | Active | Completed | Cancelled]
Type: [Roadmap | Sprint | Release | Milestone | Quarterly | Annual]
Start Date: YYYY-MM-DD
End Date: YYYY-MM-DD
Owner: (link to Person)
Tags:
---

# [Plan Name]

## Scope
What is included in this plan, what is excluded.

## Milestones
| Milestone | Due Date | Status |
|-----------|----------|--------|
| (link to Milestone) | YYYY-MM-DD | Status |
| (link to Milestone) | YYYY-MM-DD | Status |

## Related Docs
- → `goals/` — Goals this plan addresses
- → `tasks/` — Implementation tasks
- → `milestones/` — Plan milestones
- → `editions/` — Product editions
- → `projects/` — Parent project
```

---

## Template: Milestone 🏁

```markdown
---
Object type: Milestone
Status: [Planned | In Progress | Reached | Delayed | Cancelled]
Due Date: YYYY-MM-DD
Completed Date: YYYY-MM-DD
Tags:
---

# [Milestone Name]

## Description
What constitutes reaching this milestone — deliverables and criteria.

## Deliverables
1. [Deliverable 1]
2. [Deliverable 2]
3. [Deliverable 3]

## Related Docs
- → `plans/` — Parent plan
- → `releases/` — Related release
- → `goals/` — Goals this milestone serves
- → `tasks/` — Tasks needed
- → `features/` — Features delivered
```

---

## Template: Person 👤

```markdown
---
Object type: Person
Role: [Developer | Designer | Manager | Contributor | Stakeholder]
Tags:
---

# [Person Name]

## Bio
Brief background, expertise, and role on the team.

## Current Work
- **Assigned Tasks:** (link to Task), (link to Task)
- **Owned Plans:** (link to Plan)
- **Owned Goals:** (link to Goal)

## Contributions
- **Authored Posts:** (link to Blog/Post), (link to Blog/Post)
```

---

## Template: Project 📁

```markdown
---
Object type: Project
Status: [Active | On Hold | Completed | Cancelled]
Start Date: YYYY-MM-DD
End Date: YYYY-MM-DD
Owner: (link to Person)
Tags:
---

# [Project Name]

## Overview
Project scope, objectives, and success criteria.

## Timeline
| Phase | Duration | Milestone |
|-------|----------|-----------|
| Phase 1 | Q1-Q2 | (link to Milestone) |
| Phase 2 | Q3-Q4 | (link to Milestone) |

## Related Docs
- → `plans/` — Project plans
- → `goals/` — Strategic alignment
- → `milestones/` — Key checkpoints
- → `features/` — Features scope
- → `releases/` — Releases
```

---

## Template: Component 🔧

```markdown
---
Object type: Component
Status: [Stable | Beta | Deprecated | Experimental]
Category: [UI | Form | Navigation | Data | Layout | Widget]
Framework: [React | Django | Rust | Tailwind]
Edition: (link to Edition)
Tags:
---

# [Component Name]

## Description
What this component does and where it's used.

## Props / API
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| propName | string | '' | Description |

## Theme Support
| Variant | Appearance |
|---------|-----------|
| Default | Standard styling |
| Dark | Dark mode variant |

## Related Docs
- → `style/` — Design tokens
- → `api/` — Related API endpoints
- → `features/` — Features using this component
```

---

## Template: API 📡

```markdown
---
Object type: API
Status: [Stable | Beta | Deprecated | Experimental]
Method: [GET | POST | PUT | PATCH | DELETE]
Endpoint: /api/v1/resource
Auth Required: true
Rate Limited: false
Version: v1
Edition: (link to Edition)
Tags:
---

# [API Name]

## Request
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | yes | Resource identifier |

## Response
```json
{
  "status": "success",
  "data": {}
}
```

## Error Codes
| Code | Description |
|------|-------------|
| 400 | Bad request |
| 401 | Unauthorized |
| 404 | Not found |

## Related Docs
- → `features/` — Related feature
- → `components/` — UI components consuming this API
- → `integrations/` — External integrations
- → `references/` — Config references
```

---

## Template: Release 🚀

```markdown
---
Object type: Release
Status: [Planned | In Progress | Released | Rolled Back]
Version: 1.0.0
Release Date: YYYY-MM-DD
Edition: (link to Edition)
Tags:
---

# Release v[Version]

## Overview
What this release delivers and why.

## Features
- (link to Feature) — Feature description
- (link to Feature) — Feature description

## Bug Fixes
- (link to Task) — Fix description

## Deployment Notes
- Migration steps, environment changes, rollback plan

## Related Docs
- → `milestones/` — Release milestone
- → `changelogs/` — Changelog entry
- → `pipelines/` — Deployment pipeline
- → `features/` — All features in this release
```

---

## Template: Decision ⚡ (ADR)

```markdown
---
Object type: Decision
Status: [Proposed | Accepted | Deprecated | Superseded]
Category: [Architecture | Technology | Process | Security | Performance]
Date: YYYY-MM-DD
Decision Maker: (link to Person)
Tags:
---

# ADR-[Number]: [Decision Title]

## Context
What problem are we solving? What forces are at play? What constraints exist?

## Options Considered
1. **Option A:** Description — pros and cons
2. **Option B:** Description — pros and cons
3. **Option C:** Description — pros and cons

## Decision
We chose **Option A** because [rationale].

## Consequences
- **Positive:** Outcome 1, Outcome 2
- **Negative:** Trade-off 1, Trade-off 2
- **Risks:** Risk 1 (mitigation: ...)

## Related Docs
- → `architecture/` — Affected architecture
- → `features/` — Affected features
- → Supersedes: (link to Decision) — Previous decision
```

---

## Template: Pipeline 🔄

```markdown
---
Object type: Pipeline
Status: [Active | Inactive | Failed]
Type: [CI | CD | Test | Deploy | Lint | Security]
Provider: [GitHub Actions | Docker | Custom]
Triggers: [Push | PR | Schedule | Manual]
Tags:
---

# [Pipeline Name]

## Overview
Purpose and scope of this pipeline.

## Workflow Steps
1. Step 1 — Description
2. Step 2 — Description
3. Step 3 — Description

## Environment Variables
| Variable | Source | Required |
|----------|--------|----------|
| SECRET_KEY | GitHub Secrets | Yes |

## Related Docs
- → `releases/` — Releases using this pipeline
- → `references/` — Config references
```

---

## Template: Style 🎨

```markdown
---
Object type: Style
Category: [Color | Typography | Spacing | Shadow | Animation | Icon]
Token: --color-token-name
Value: #hex-value
Theme: (link to Edition)
Tags:
---

# [Token Name]

## Value
| Category | Token | Value | Usage |
|----------|-------|-------|-------|
| Color | `--color-primary` | #6366f1 | Primary accent |

## Related Docs
- → `components/` — Components using this token
- → `architecture/theme-system.md` — Theme architecture
- → `guides/theming.md` — Theme customization
```

---

## Template: Sprint 🏃

```markdown
---
Object type: Sprint
Status: [Planning | Active | Completed | Cancelled]
Sprint Number: 1
Start Date: YYYY-MM-DD
End Date: YYYY-MM-DD
Owner: (link to Person)
Tags:
---

# Sprint [Number]: [Theme/Name]

## Goals
- Goal 1
- Goal 2
- Goal 3

## Tasks
- (link to Task) — Task description
- (link to Task) — Task description

## Retrospective
### What went well
- Item 1
### What to improve
- Item 1
### Action items
- Action 1

## Related Docs
- → `goals/` — Sprint goals
- → `milestones/` — Related milestones
```

---

## Template: Integration 🔗

```markdown
---
Object type: Integration
Status: [Active | Planned | Deprecated | Broken]
Category: [Payment | CRM | Email | SMS | Analytics | Auth | Storage]
Provider: Provider Name
Auth Type: [API Key | OAuth | JWT | Basic]
Edition: (link to Edition)
Tags:
---

# [Provider Name] Integration

## Overview
What this integration provides and how it's used.

## Setup
1. Step 1 — Create account, get credentials
2. Step 2 — Configure in settings
3. Step 3 — Verify connection

## API Endpoints Used
- (link to API) — Endpoint description
- (link to API) — Endpoint description

## Rate Limits
| Limit | Per | Scope |
|-------|-----|-------|
| 1000 | hour | Per API key |

## Related Docs
- → `features/` — Features using this integration
- → `api/` — API endpoints
- → `pipelines/` — Deployment/config pipeline
```

---

## Template: Page 📄 (General Purpose)

```markdown
---
Object type: Page
Status: [Draft | Review | Published]
Tags:
---

# [Page Title]

## Content
General content body.

## Related Docs
- → `architecture/` — Architecture context
- → `features/` — Feature references
- → `guides/` — Related guides
```

---

## Template: Note 📝 (Quick/Informal)

```markdown
---
Object type: Note
Tags:
---

# [Note Title]

Quick note content — ideas, meeting minutes, reminders.

## Related Docs
- → `architecture/` — Context
- → `features/` — Related feature
```

---

## Template: Bookmark 🔖 (External Link)

```markdown
---
Object type: Bookmark
URL: https://example.com
Category: [Development | Documentation | Publishing | Staging | Done]
Tags:
---

# [Resource Title]

Brief description of the resource and why it's relevant.

## Related Docs
- → `features/` — Related feature
```

---

## Template: Workspace 🏢 (Hub Page)

```markdown
---
Object type: Workspace
Tags:
---

# [Workspace Title]

> Hub page grouping related content.

## Sections
- **Section 1:** Description and links
- **Section 2:** Description and links

## Related Docs
- → `plans/` — Related plans
- → `projects/` — Related projects
```

---

## Template: Configuration ⚙️

```markdown
---
Object type: Configuration
Category: [Environment | Build | Database | Proxy | Auth | Deployment]
Platform: [macOS | Linux | Windows | Docker]
Required: [true | false]
Default Value: value
Tags:
---

# [Config Name]

## Description
What this configuration controls.

## Values
| Environment | Value | Notes |
|-------------|-------|-------|
| Development | dev-value | |
| Production | prod-value | |

## Related Docs
- → `editions/` — Edition this applies to
- → `guides/` — Setup guides referencing this config
```

---

## Quick Reference: File Naming Conventions

| Object Type | Directory | Naming Convention | Example |
|-------------|-----------|-------------------|---------|
| Architecture 🏗️ | `architecture/` | `kebab-case-descriptive.md` | `sync-architecture.md` |
| Feature ✨ | `features/` | `feature-short-name.md` | `pos-offline.md` |
| Guide 📘 | `guides/` | `guide-topic-name.md` | `setup.md` |
| Reference 📚 | `references/` | `reference-category-name.md` | `database-schema.md` |
| Changelog 📋 | `changelogs/` | `edition-name.md` | `pos.md` |
| Diagram 📊 | `diagrams/` | `diagram-type-name.md` | `architecture-flow.md` |
| Task ✅ | `tasks/` | `task-description.md` | `tasks-and-backlog.md` |
| Goal 🎯 | `goals/` | `goal-short-name.md` | `v1-release-goals.md` |
| Edition 📦 | `editions/` | `edition-name.md` | `pos-mini.md` |
| Blog/Post 📝 | `blog/` | `YYYY-MM-DD-post-slug.md` | `2026-07-01-solo-beta.md` |
| Plan 📋 | `plans/` | `plan-type-name.md` | `product-development.md` |
| Milestone 🏁 | `milestones/` | `milestone-name.md` | `solo-beta-release.md` |
| Person 👤 | `people/` | `firstname-lastname.md` | `mammhoud.md` |
| Project 📁 | `projects/` | `project-name.md` | `pos-desktop-suite.md` |
| Component 🔧 | `components/` | `component-name.md` | `data-table.md` |
| API 📡 | `api/` | `resource-name.md` | `order-endpoints.md` |
| Release 🚀 | `releases/` | `v-major-minor-patch.md` | `v1-2-0.md` |
| Decision ⚡ | `decisions/` | `NNN-title-kebab.md` | `001-use-django-orm.md` |
| Pipeline 🔄 | `pipelines/` | `pipeline-type-name.md` | `ci-test-workflow.md` |
| Style 🎨 | `style/` | `token-category-name.md` | `color-palette.md` |
| Sprint 🏃 | `sprints/` | `sprint-N.md` | `sprint-12.md` |
| Integration 🔗 | `integrations/` | `provider-name.md` | `stripe-payments.md` |

---

## Template Usage Quick Reference

| Field | Format | Notes |
|-------|--------|-------|
| Links | `(link to Type)` | Replace with actual AnyType relation link |
| Tags | `tag1, tag2, tag3` | Comma-separated, no `#` prefix in frontmatter |
| Dates | `YYYY-MM-DD` | ISO 8601 date format |
| Booleans | `true` / `false` | Lowercase in YAML |
| Arrays | `[item1, item2]` | Square brackets for YAML arrays |
