---
# yaml-language-server: $schema=schemas/task.schema.json
Object type:
    - Task
Backlinks:
    - development-workflow-this-page-describes-how-a.md
    - product-development.md
    - startup-planner.md
    - project-guide.md
Creation date: "2024-07-12T10:00:00Z"
Created by:
    - mammhoud
Emoji: ✅
id: bafyreicu32jskfanu42qqsi5g2iiw3i6gwbohr2t2epcmipotxb53bqfsq
---
# Tasks & Backlog   
This page tracks current tasks, upcoming work, and completed milestones for Structa Cloud.   
## Proposed / backlog   
- [ ] **Reorganize compose files** – move orchestration closer to core and verify Docker paths.   
- [ ] **Enhance Anytype workspace** – connect startup planning pages to actual repo structure.   
- [ ] **Worker consolidation** – finalize `core/www/worker/` layout and Celery routing.   
- [ ] **AI integration** – wire `ceptor-ai` into content generation workflows.   
- [ ] **Multi-domain media serving** – verify `media.\*` subdomains routing.   
- [ ] **Auth flows** – review allauth MFA and social login adapters across sites.   
- [ ] **Component library** – document shared components in `core/assets/templates/`.   
## Completed   
- [x] Initial Django/Wagtail multi-site setup   
- [x] Shared templates and static assets   
- [x] Traefik + Nginx proxy infrastructure   
- [x] Local Anytype container for planning   
## Task details   
### Reorganize compose files   
**Goal:** Ensure Docker Compose orchestration files point to the correct `core/` paths and that build contexts/volume mounts are valid.   
**Related files:**   
- `docker-compose.yml`   
- `applications/compose/docker-compose.\*.yml`   
- `core/compose/Dockerfile`   
- `core/compose/entrypoint`   
   
### Enhance Anytype workspace   
**Goal:** Make the Anytype pages useful references that map business goals to repo paths.   
**Related files:**   
- `applications/anytype/\*.md`   
- `AGENTS.md`   
- `docs/README.md`   
   
### Worker consolidation   
**Goal:** Move shared Celery tasks from `core/tasks/` to `core/www/worker/` while keeping task names stable.   
**Related files:**   
- `core/tasks/`   
- `core/www/`   
- `applications/compose/docker-compose.tasks.yml`   
   
## How tasks become code   
1. A task is captured here in Anytype.   
2. It is broken down into repo issues or Makefile targets.   
3. Code is written in the matching `core/<site>/` or shared location.   
4. Changes are validated with `make deploy-preflight` and tests.   
