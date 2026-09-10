---
Object type: Plan
Tags: legacy, cleanup, docs
Status: Historical
---

# Code Removal & Content Cleanup Plan

> **Status:** Complete
> **Updated:** 2026-08-28
> **Goal:** Keep the documentation business-readable and safe — no surrounding code fences, no command examples, no raw developers. Replace them with tables, arrow (→) flows, and plain prose.

---

## Principle

Any block wrapped in triple backticks (``` ) is treated as "code-related." It is removed and replaced with:

- **Flow/relationships** → indented arrow lists (`A → B → C`)
- **Structured/multi-column info** → markdown tables
- **Lists / hierarchies** → bullet lists or tables

No functional content is lost; only the code-fence wrapper and any command/implementation detail is rewritten into safe prose.

---

## Files to clean

### 1. Content and index documents

| File | What is removed |
|------|-----------------|
| `products/_index.md` | product-graph text diagram |
| `goals/_index.md` | goal-lifecycle flow code block |
| `brand/_index.md` | color-palette tree block |
| `features/pos-system.md` | organization text diagram |
| `decisions/_index.md` | ADR-lifecycle flow block |
| `changelogs/_index.md` | changelog markdown template block |
| `architecture/editions.md` | edition-flow text diagram |
| `architecture/overview.md` | monorepo-layout tree + dangling image link |
| `architecture/website-descriptions.md` | multiple text/flow blocks |

### 2. Guide and reference documents

| File | What is removed |
|------|-----------------|
| `guides/install/_index.md` | install command examples |
| `guides/install/docker.md` | docker run/build commands |
| `guides/install/linux.md` | linux install commands |
| `guides/install/macos.md` | brew install commands |
| `guides/install/windows.md` | powershell install commands |
| `guides/deployment.md` | deploy command blocks |
| `guides/configuration.md` | config/env command examples |
| `guides/object-linking.md` | relation/link code examples |
| `guides/development-workflow.md` | workflow command blocks |
| `_prompts.md` | AI-prompt template blocks |

### 3. Object type definition files

| File | What is removed |
|------|-----------------|
| `objects/api.md`, `bookmark.md`, `blog-post.md`, `component.md`, `configuration.md`, `decision.md`, `feature.md`, `goal.md`, `integration.md`, `milestone.md`, `note.md`, `page.md`, `pipeline.md`, `release.md`, `sprint.md`, `style.md`, `task.md`, `workspace.md` | property/template code blocks |
| `objects/_templates.md` | kept — copy-paste templates for Anytype, not code (user decision) |
| `objects/_relations.md` | relation-model flow block |

---

## Implementation order

1. Content and index documents (lowest risk, purely presentational)
2. Architecture documents
3. Guide and reference documents
4. Object type definition files

## Verification

After each batch, confirm no `py- ``` ` fences remain in the targeted file (the `plans/` and top-level docs are already clean).
