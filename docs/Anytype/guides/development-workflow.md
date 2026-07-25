---
# yaml-language-server: $schema=schemas/note.schema.json
Object type:
    - Note
Backlinks:
    - product-development.md
    - startup-planner.md
    - project-guide.md
Creation date: "2024-07-12T10:00:00Z"
Created by:
    - mammhoud
Links:
    - tasks-and-backlog.md
    - project-guide.md
Emoji: "\U0001F504"
id: bafyreibwtwdpkxrbqodnjuzlxhgx23gnwmcoimkurarffpxl7u2qk2tmk4
---
Development Workflow   
This page describes how an idea moves from planning in Anytype to working code in the Structa Cloud repo.   
## 1. Capture in Anytype   
When a new feature, fix, or improvement is identified, it is first captured in this workspace.   
- Add it to [Tasks](tasks-and-backlog.md).   
- Link it to the relevant planning page (vision, product development, etc.).   
- If it affects a specific website, note the site in the task.   
   
## 2. Map to repo path   
Use the [Project Guide](project-guide.md) to find the correct repo location.   
|              Type of work   <br> |                                                          Repo location   <br> |
|:---------------------------------|:------------------------------------------------------------------------------|
|     Site-specific feature   <br> |                                                         `core/<site>/`   <br> |
| Shared template/component   <br> |                      `core/assets/templates/` or `core/assets/static/`   <br> |
|            Shared setting   <br> |                                                        `core/configs/`   <br> |
|     Reusable library code   <br> |                                                 `core/libs/<library>/`   <br> |
|            Infrastructure   <br> | `applications/proxy/`, `applications/databases/`, `docker-compose.yml`   <br> |
|             Documentation   <br> |                                                                `docs/`   <br> |
|                     Tests   <br> |                                                               `tests/`   <br> |

## 3. Implement   
Follow the existing conventions:   
- Use `WEBSITE=<site>` with `core/Makefile` for site-specific work.   
- Prefer class-based views and keep business logic out of views.   
- Use `django-fusion` components and fragments.   
- Add tests for new functionality.   
   
## 4. Validate   
Run the narrowest relevant checks first.   
```
# Django checks for a site
make -C core check WEBSITE=ctc-research

# Tests
make -C core test-local

# Docker compose config
make deploy-preflight

```
## 5. Review   
- Open a pull request.   
- Ensure CI passes (lint, tests, compose config).   
- Request review from a teammate.   
   
## 6. Deploy   
Use the root Makefile for deployment.   
```
make deploy

```
This runs the full chain: databases → media → apps → tasks → docs → proxy.   
## Branching convention   
- `feature/<short-description>` – new features   
- `fix/<short-description>` – bug fixes   
- `refactor/<short-description>` – refactoring   
- `docs/<short-description>` – documentation changes   
   
## Useful commands   
```
# Start a site locally
make -C core run-dev WEBSITE=ctc-research

# Build assets for a site
make -C core build-assets WEBSITE=ctc-research

# Run migrations
make -C core migrate WEBSITE=ctc-research

# Deploy everything
make deploy

```
   
