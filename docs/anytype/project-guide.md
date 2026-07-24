---
# yaml-language-server: $schema=schemas/workspace.schema.json
Object type:
    - Workspace
Backlinks:
    - development-workflow-this-page-describes-how-a.md
Creation date: "2024-07-12T10:00:00Z"
Created by:
    - mammhoud
Links:
    - bafyreiashpvmxhh43xvuqgpiknrpkbivnzoeb6qo5z5ldpmvb2wvlm5q3u
    - website-and-application-descriptions.md
    - tasks-and-backlog.md
    - architecture-overview.md
    - development-workflow-this-page-describes-how-a.md
Emoji: "\U0001F5FE"
id: bafyreigoele4rxistm3zkzu7varofbvz3uep4sjtaka3dp4rolctugo3a4
---
# Project Guide   
This guide maps the concepts in our Anytype workspace to the actual files and directories in the Structa Cloud repository.   
## Key repo directories   
### core/   
The heart of the project. Contains Django sites, shared assets, local libraries, and build tooling.   
- `core/ctc-research/` – CTC Research site   
- `core/lms-demo/` – LMS demo site   
- `core/VResume/` – VResume site   
- `core/tinker/` – Template customizer   
- `core/configs/` – Shared Django settings   
- `core/assets/` – Shared templates, static files, frontend scripts   
- `core/libs/` – Local reusable libraries   
- `core/Makefile` – Main dispatcher for Django/test/Docker commands   
   
### applications/   
Infrastructure and supporting applications.   
- `applications/proxy/` – Traefik and Nginx   
- `applications/databases/` – PostgreSQL and Redis   
- `applications/anytype/` – This workspace   
   
### docs/   
Canonical documentation.   
- `docs/README.md` – Documentation entrypoint   
- `docs/websites/` – Site-specific docs   
- `docs/deployment/` – Deployment guides   
- `docs/guides/` – Integration and customization guides   
   
### tests/   
Shared and per-site tests.   
- `tests/core/` – Core shared tests   
- `tests/websites/` – Per-site website tests   
- `tests/scripts/` – Test and utility scripts   
   
## How to navigate   
1. Start with the   
    [Vision and Mission](bafyreiashpvmxhh43xvuqgpiknrpkbivnzoeb6qo5z5ld.md) for the big picture.   
2. Use [Website Descriptions](website-and-application-descriptions.md) to understand each product.   
3. Open [Tasks](tasks-and-backlog.md) to see what is being worked on.   
4. Dive into [Architecture Overview](architecture-overview.md) for technical details.   
5. Follow [Development Workflow](development-workflow-this-page-describes-how-a.md) when moving from idea to code.   
   
   
