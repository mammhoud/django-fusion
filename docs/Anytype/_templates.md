# AnyType Template Generation Guide

> **Purpose:** Standard templates for creating new AnyType documentation objects.
> Copy the appropriate template, fill in the fields, and import into AnyType.

---

## Template: Architecture Document 🏗️

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
Brief description of the architecture component.

## Components
- **Component 1:** Description
- **Component 2:** Description

## Data Flow
```
[Diagram or flow description]
```

## Decisions
- **ADR-001:** Decision description

## Related Docs
- → `features/` —
- → `guides/` —
```

---

## Template: Feature Document ✨

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
What does this feature do?

## User Story
As a [user], I want to [action] so that [benefit].

## Acceptance Criteria
1. [ ] Criterion 1
2. [ ] Criterion 2

## Dependencies
- Depends on: (link to Feature)

## Related Docs
- → `architecture/` —
- → `guides/` —
- → `goals/` —
```

---

## Template: Guide 📘

```markdown
---
Object type: Guide
Status: Draft
Category: Setup
Target Audience: Developer
Tags:
---

# [Guide Title]

## Prerequisites
- (link to prerequisite Guide)

## Step 1: [Title]
Description and instructions.

## Step 2: [Title]
Description and instructions.

## Troubleshooting
Common issues and solutions.

## Related Docs
- → `architecture/` —
- → `references/` —
- → `features/` —
```

---

## Template: Goal 🎯

```markdown
---
Object type: Goal
Status: Active
Category: Product
Priority: High
Target Date: YYYY-MM-DD
Tags:
---

# [Goal Title]

## Description
What we want to achieve and why.

## Key Results
1. [KR 1 — measurable outcome]
2. [KR 2 — measurable outcome]
3. [KR 3 — measurable outcome]

## Related Features
- (link to Feature)

## Related Tasks
- (link to Task)

## Related Milestones
- (link to Milestone)
```

---

## Template: Blog/Post 📝

```markdown
---
Object type: Blog/Post
Status: Draft
Author: (link to Person)
Published Date: YYYY-MM-DD
Category: Announcement
Tags:
---

# [Post Title]

> Excerpt: Brief summary for listings.

## Content
Body of the post...

## Related Features
- (link to Feature)

## Related Guides
- (link to Guide)
```

---

## Template: Plan 📋

```markdown
---
Object type: Plan
Status: Draft
Type: Roadmap
Start Date: YYYY-MM-DD
End Date: YYYY-MM-DD
Owner: (link to Person)
Tags:
---

# [Plan Name]

## Scope
What is included in this plan.

## Milestones
1. (link to Milestone) — Due: YYYY-MM-DD
2. (link to Milestone) — Due: YYYY-MM-DD

## Related Goals
- (link to Goal)

## Related Tasks
- (link to Task)
```

---

## Template: Milestone 🏁

```markdown
---
Object type: Milestone
Status: Planned
Due Date: YYYY-MM-DD
Tags:
---

# [Milestone Name]

## Description
What constitutes reaching this milestone.

## Deliverables
1. [Deliverable 1]
2. [Deliverable 2]

## Related Plan
- (link to Plan)

## Related Goals
- (link to Goal)
```

---

## Template: Task ✅

```markdown
---
Object type: Task
Status: Backlog
Priority: Medium
Edition: (link to Edition)
Estimated Hours: 
Tags:
---

# [Task Title]

## Description
What needs to be done.

## Implementation Notes
- Technical approach
- Files to modify

## Dependencies
- Depends on: (link to Task)

## Related Docs
- → `features/` —
- → `goals/` —
```

---

## Template: Edition 📦

```markdown
---
Object type: Edition
Status: Planned
Version: 1.0.0
Release Date: YYYY-MM-DD
Target Audience: Individual
Pricing Tier: Free
Tags:
---

# [Edition Name]

## Description
What this edition includes.

## Features
- **Included:** (link to Feature), (link to Feature)
- **Excluded:** (link to Feature)

## Compatibility
- (link to Reference)
```

---

## File Directory Mapping

| Object Type | Directory | Naming Convention |
|-------------|-----------|-------------------|
| Architecture 🏗️ | `architecture/` | `kebab-case-architecture.md` |
| Feature ✨ | `features/` | `feature-name.md` |
| Guide 📘 | `guides/` | `guide-topic-name.md` |
| Reference 📚 | `references/` | `reference-name.md` |
| Changelog 📋 | `changelogs/` | `YYYY-MM-DD-version.md` |
| Diagram 📊 | `diagrams/` | `diagram-type-name.md` |
| Task ✅ | `tasks/` | `task-short-name.md` |
| Goal 🎯 | `goals/` | `goal-short-name.md` |
| Edition 📦 | `editions/` | `edition-name.md` |
| Blog/Post 📝 | `blog/` | `YYYY-MM-DD-post-slug.md` |
| Plan 📋 | `plans/` | `plan-name.md` |
| Milestone 🏁 | `milestones/` | `milestone-name.md` |
| Person 👤 | `people/` | `person-name.md` |
| Project 📁 | `projects/` | `project-name.md` |
