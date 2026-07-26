# Relations — Object Linking Guide

> **Import Instruction:** Create these Relations in your AnyType space to link documentation objects.
> Apply the "Object" property type with the specified relation name.

---

## Relation Definitions

| Name | Type | Source → Target | Description |
|------|------|-----------------|-------------|
| `Related Architecture` | Object → Architecture | Any → Architecture | Links features/guides to architectural docs |
| `Related Feature` | Object → Feature | Any → Feature | Links architectures/guides to feature docs |
| `Related Guide` | Object → Guide | Any → Guide | Links features/architectures to guides |
| `Related Reference` | Object → Reference | Any → Reference | Links features/guides to API/command refs |
| `Related Goal` | Object → Goal | Any → Goal | Links tasks/features/plans to strategic goals |
| `Related Plan` | Object → Plan | Any → Plan | Links milestones/tasks/goals to parent plans |
| `Related Milestone` | Object → Milestone | Any → Milestone | Links features/tasks to delivery milestones |
| `Related Edition` | Object → Edition | Any → Edition | Links features/docs/guides to product editions |
| `Related Person` | Object → Person | Any → Person | Links tasks/posts to team members |
| `Related Project` | Object → Project | Any → Project | Links plans/goals to high-level projects |
| `Related Blog Post` | Object → Blog/Post | Any → Blog/Post | Links features/guides to announcement posts |
| `Related Component` | Object → Component | Any → Component | Links features/guides to UI/business components |
| `Related API` | Object → API | Any → API | Links features/components to API definitions |
| `Related Release` | Object → Release | Any → Release | Links changes/features to version releases |
| `Related Decision` | Object → Decision | Any → Decision | Links architecture to ADRs |
| `Related Pipeline` | Object → Pipeline | Any → Pipeline | Links releases to CI/CD pipelines |
| `Related Style` | Object → Style | Any → Style | Links components to design tokens |
| `Related Sprint` | Object → Sprint | Any → Sprint | Links tasks to sprint cycles |
| `Related Integration` | Object → Integration | Any → Integration | Links features/API to external connectors |
| `Depends On` | Object → Task/Feature/Component | Any → Dep | Dependency chain |
| `Implements` | Object → Architecture/Feature | Guide → Arch/Feat | A guide that implements an architecture/feature |
| `Part Of` | Object → Plan/Project | Guide → Plan | A guide that belongs to a plan |
| `Prerequisites` | Object → Guide | Guide → Guide | Prerequisite guides |
| `Supersedes` | Object → Decision | Decision → Decision | Replaces a previous decision |
| `See Also` | Object → Any | Any → Any | General cross-reference |
| `Assignee` | Object → Person | Task → Person | Assigns a task to a person |
| `Author` | Object → Person | Blog/Post → Person | Links a blog post to its author |
| `Owner` | Object → Person | Plan/Sprint → Person | Designates the owner of a plan or sprint |
| `Decision Maker` | Object → Person | Decision → Person | Records who made an architectural decision |
| `Theme` | Object → Edition | Style → Edition | Associates a style token with an edition theme |
| `Implementation` | Object → Guide | Feature → Guide | The guide that implements a feature |
| `Related Docs` | Object → Any | Diagram → Any | Connects diagram to its related documents |
| `Related Changelog` | Object → Changelog | Release → Changelog | Links a release to its changelog entry |
| `FeaturesIncluded` | Object → Feature | Edition → Feature | Features included in an edition |
| `FeaturesExcluded` | Object → Feature | Edition → Feature | Features excluded from an edition |
| `Compatibility` | Object → Reference | Edition → Reference | Technical compatibility references |

---

## Graph View Connections

```
                    Project 📁
                   /    |     \
                  ▼     ▼      \
              Plan 📋  Goal 🎯   \
             /    \      |        \
            ▼      ▼     ▼         ▼
      Milestone🏁  Tasks ✅  Edition 📦
           |          |          |
           ▼          ▼          ▼
       Sprint 🏃  Feature ✨──────┘
                       |
              ┌────────┼────────┐
              ▼        ▼        ▼
           Guide 📘  API 📡  Component 🔧
              |        |        |
              ▼        ▼        ▼
           Blog📝   Integration🔗  Style 🎨
                       |
                       ▼
                   Pipeline 🔄

       Release 🚀 ← joins Milestone + Pipeline + Changelog
       Decision ⚡ ← joins Architecture + Person
       Architecture 🏗️ ← supports everything
       Changelog 📋 ← tracks release versions
       Person 👤 ← links to tasks, posts, decisions, sprints
       Diagram 📊 ← visual context for architecture/features
       Reference 📚 ← API & config docs
```

---

## Backlink Strategy

In AnyType, backlinks are created automatically when two objects are related.
Use backlinks to navigate the knowledge graph:

```yaml
Open Architecture → "Related Decisions" → see all ADRs
Open Feature → "Related API" → see all API endpoints
Open Component → "Related Style" → see design tokens
Open Release → "Related Pipeline" → see CI/CD status
Open Sprint → "Related Tasks" → see all sprint work
Open Goal → "Related Tasks" → see implementation progress
```

---

## Usage in Files

Each markdown file ends with a `Related Docs` section using → arrows:

```markdown
## Related Docs
- → `architecture/editions.md` — Edition comparison
- → `features/pos-mini.md` — pos-mini features
- → `guides/setup.md` — Setup guide
- → `goals/v1-release.md` — V1 release goals
- → `components/navbar.md` — Navbar component
- → `api/order-endpoints.md` — Order API
```

In AnyType, convert these → links to Object Relations by:
1. Opening the target document
2. Adding the appropriate Relation property
3. Linking it back to the source document

---

## Usage in Practice

For a step-by-step walkthrough of creating AnyType relations and linking objects, see the [`object-linking.md`](../guides/object-linking.md) guide.

---

## Quick Reference Template

Copy this into any document's Related Docs section:

```markdown
## Related Docs
- → `architecture/` —
- → `features/` —
- → `guides/` —
- → `components/` —
- → `api/` —
- → `goals/` —
- → `plans/` —
- → `releases/` —
- → `style/` —
- → `editions/` —
```

---

## Relation Cardinality Reference

| Relation | Cardinality | Example |
|----------|-------------|---------|
| `Related Architecture` | One Architecture → Many Docs | One architecture doc can be linked from many features |
| `Related Feature` | Many Features → Many Docs | Cross-cutting feature relationships |
| `Depends On` | One Task → One Task (optional chain) | Linear dependency chains |
| `Related Sprint` | One Sprint → Many Tasks | Sprint groups multiple tasks |
| `Assignee` | One Person → Many Tasks | One person assigned multiple tasks |
| `Supersedes` | One Decision → One Decision | Linear decision history |
