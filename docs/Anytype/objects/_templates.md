# Template Generation Guide

> **Purpose:** Standard templates for creating new documentation objects.
> Copy the template, fill in the fields, import into AnyType.
> See `_object-types.md` for full property definitions per type.

---

## Full Example Template (Feature ✨)

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
1. [ ] Criterion 1
2. [ ] Criterion 2

## Related Docs
- → `architecture/` — Architecture context
- → `guides/` — Implementation guide
- → `goals/` — Strategic goal alignment
- → `api/` — API endpoints
- → `milestones/` — Delivery milestone
```

---

## Compact Frontmatter Reference

| Object Type | Required Frontmatter | Select Options |
|-------------|---------------------|----------------|
| Architecture 🏗️ | Status, Edition, Version | Status: Draft / Review / Published / Archived |
| Feature ✨ | Status, Edition, Priority | Status: Planned / In Development / Complete / Deprecated |
| Guide 📘 | Status, Category, Audience | Category: Setup / Dev / Deploy / Theming / Testing / Migration / Troubleshooting |
| Reference 📚 | Category, Edition, Version | Category: API / CLI / Database / Config / i18n / Schema / SDK |
| Changelog 📋 | Version, Date, Edition, Type | Type: Major / Minor / Patch / Breaking / Security |
| Diagram 📊 | Type, Edition | Type: Flow / Architecture / Sequence / Data Model / Timeline |
| Task ✅ | Status, Priority, Edition | Status: Backlog / In Progress / Done / Blocked / Cancelled |
| Goal 🎯 | Status, Category, Priority, Target Date | Category: Product / Business / Technical / Design / Growth |
| Edition 📦 | Status, Version, Audience, Pricing | Audience: Individual / Small Business / Enterprise |
| Blog/Post 📝 | Status, Author, Date, Category | Category: Announcement / Tutorial / Case Study / Update / Technical |
| Plan 📋 | Status, Type, Start Date, End Date, Owner | Type: Roadmap / Sprint / Release / Milestone / Quarterly / Annual |
| Milestone 🏁 | Status, Due Date | Status: Planned / In Progress / Reached / Delayed / Cancelled |
| Person 👤 | Role | Role: Developer / Designer / Manager / Contributor / Stakeholder |
| Project 📁 | Status, Start Date, End Date, Owner | Status: Active / On Hold / Completed / Cancelled |
| Component 🔧 | Status, Category, Framework, Edition | Category: UI / Form / Navigation / Data / Layout / Widget |
| API 📡 | Status, Method, Endpoint, Version | Method: GET / POST / PUT / PATCH / DELETE |
| Release 🚀 | Status, Version, Release Date, Edition | Status: Planned / In Progress / Released / Rolled Back |
| Decision ⚡ | Status, Category, Date, Decision Maker | Category: Architecture / Technology / Process / Security / Performance |
| Pipeline 🔄 | Status, Type, Provider | Type: CI / CD / Test / Deploy / Lint / Security |
| Style 🎨 | Category, Token, Value | Category: Color / Typography / Spacing / Shadow / Animation / Icon |
| Sprint 🏃 | Status, Sprint Number, Start Date, End Date | Status: Planning / Active / Completed / Cancelled |
| Integration 🔗 | Status, Category, Provider, Auth Type | Category: Payment / CRM / Email / SMS / Analytics / Auth / Storage |
| Page 📄 | Status | Status: Draft / Review / Published |
| Note 📝 | — (optional Tags) | — |
| Bookmark 🔖 | URL, Category | Category: Development / Documentation / Publishing / Staging / Done |
| Workspace 🏢 | — (optional Tags) | — |
| Configuration ⚙️ | Category, Platform, Required | Category: Environment / Build / Database / Proxy / Auth / Deployment |

---

## Common Sections by Object Type

| Object Type | Recommended Sections |
|-------------|---------------------|
| Guide 📘 | Prerequisites, Step 1...N, Verification, Troubleshooting |
| Decision ⚡ | Context, Options Considered, Decision, Consequences |
| Release 🚀 | Overview, Features, Bug Fixes, Deployment Notes |
| Project 📁 | Overview, Timeline, Success Criteria |
| Sprint 🏃 | Goals, Tasks, Retrospective (What went well / To improve / Action items) |
| Integration 🔗 | Overview, Setup, API Endpoints Used, Rate Limits |
| Style 🎨 | Value (table), Usage, Related Components |
| Blog/Post 📝 | Excerpt, Introduction, Content, Conclusion |
| Milestone 🏁 | Description, Deliverables |
| Plan 📋 | Scope, Milestones (table), Timeline |

---

## File Naming Conventions

| Object Type | Convention | Example |
|-------------|-----------|---------|
| Architecture | `kebab-case.md` | `sync-architecture.md` |
| Feature | `feature-short-name.md` | `pos-offline.md` |
| Guide | `guide-topic-name.md` | `setup.md` |
| Reference | `reference-category-name.md` | `database-schema.md` |
| Blog/Post | `YYYY-MM-DD-post-slug.md` | `2026-07-01-solo-beta.md` |
| Decision | `NNN-title-kebab.md` | `001-use-django-orm.md` |
| Sprint | `sprint-N.md` | `sprint-12.md` |
| Release | `v-major-minor-patch.md` | `v1-2-0.md` |
| Other | `kebab-case-descriptive.md` | `tasks-and-backlog.md` |

---

## Template Usage Tips

| Field | Format | Notes |
|-------|--------|-------|
| Links | `(link to Type)` | Replace with actual AnyType relation link |
| Tags | `tag1, tag2` | Comma-separated, no `#` prefix in frontmatter |
| Dates | `YYYY-MM-DD` | ISO 8601 |
| Booleans | `true` / `false` | Lowercase in YAML |
| Arrays | `[item1, item2]` | Square brackets for YAML arrays |
