---
Object type: Guide
Tags: development, workflow, django
Status: Published
---

# Development Workflow

> This page describes how an idea moves from planning in Anytype to working software in the Structa Cloud repo.

## 1. Capture in Anytype

When a new feature, fix, or improvement is identified, it is first captured in this workspace.

- Add it to [Tasks](../tasks/tasks-and-backlog.md).
- Link it to the relevant planning page (vision, product development, etc.).
- If it affects a specific website, note the site in the task.

## 2. Map to repo path

Use the [Project Guide](../plans/project-guide.md) to find the correct repo location.

| Type of work | Repo location |
|--------------|---------------|
| Site-specific feature | core/<site>/ |
| Shared template/component | core/assets/templates/ or core/assets/static/ |
| Shared setting | core/configs/ |
| Reusable library code | core/libs/<library>/ |
| Infrastructure | applications/proxy/, applications/databases/, docker-compose.yml |
| Documentation | docs/ |
| Tests | tests/ |

## 3. Implement

Follow the existing conventions:

- Use the site-specific build flow for site-specific work.
- Prefer class-based views and keep business logic out of views.
- Use django-fusion components and fragments.
- Add tests for new functionality.

## 4. Validate

Run the narrowest relevant checks first, in this order:

1. Run Django checks for the site.
2. Run the local test suite.
3. Validate the compose configuration.

## 5. Review

- Open a pull request.
- Ensure CI passes (lint, tests, compose config).
- Request review from a teammate.

## 6. Deploy

Use the root deployment flow, which runs the full chain: databases → media → applications → tasks → docs → proxy.

## Branching convention

| Branch prefix | Purpose |
|---------------|---------|
| feature/<short-description> | New features |
| fix/<short-description> | Bug fixes |
| refactor/<short-description> | Refactoring |
| docs/<short-description> | Documentation changes |

## Common operations

| Operation | Description |
|-----------|-------------|
| Start a site locally | Run the site's development server |
| Build assets for a site | Produce static assets for the site |
| Run migrations | Apply database migrations |
| Deploy everything | Run the full deployment chain |

## Related Docs

- → `../architecture/overview.md` — Architecture context
- → `../guides/_index.md` — Quick start guide
- → `../tasks/tasks-and-backlog.md` — Implementation tasks
- → `../plans/product-development.md` — Development lifecycle
