---
# yaml-language-server: $schema=schemas/workspace.schema.json
Object type:
    - Workspace
Backlinks:
    - product-development.md
    - project-guide.md
Creation date: "2024-07-12T10:00:00Z"
Created by:
    - mammhoud
Links:
    - files/arcade-pc-office.jpg
Emoji: "\U0001FAC6"
id: bafyreidnsve2j4l6qs3hxh734hualo2bf5xlvtdlqw5vrtubqdxmrlokem
---
# Architecture Overview   
[arcade-pc-office](../files/arcade-pc-office.jpg)    
This page describes the high-level architecture of Structa Cloud.   
## Monorepo layout   
```
structa.cloud/
├── core/                          # Django sites and shared code
│   ├── ctc-research/              # CTC Research site
│   ├── lms-demo/                  # LMS demo site
│   ├── VResume/                   # VResume site
│   ├── tinker/                    # Template customizer
│   ├── configs/                   # Shared Django settings
│   ├── assets/                    # Shared templates, static files, scripts
│   ├── libs/                      # Local reusable libraries
│   ├── www/                       # Shared/core Django code
│   └── compose/                   # Dockerfile and entrypoint
├── applications/                  # Infrastructure and supporting apps
│   ├── proxy/                     # Traefik + Nginx
│   ├── databases/                 # PostgreSQL + Redis
├── tests/                         # Shared and per-site tests
├── docs/                          # Documentation
└── docker-compose.yml             # Root orchestration file

```
## Technology stack   
|        Layer   <br> |               Technology   <br> |
|:--------------------|:--------------------------------|
|      Backend   <br> |          Django, Wagtail   <br> |
|     Frontend   <br> |      SCSS, Webpack, HTMX   <br> |
|    Libraries   <br> | django-fusion, ceptor-ai   <br> |
|         Auth   <br> |           django-allauth   <br> |
|   Task queue   <br> |           Celery + Redis   <br> |
|     Database   <br> |               PostgreSQL   <br> |
|        Cache   <br> |                    Redis   <br> |
|        Proxy   <br> |                  Traefik   <br> |
| Static/media   <br> |                    Nginx   <br> |
|    Container   <br> |   Docker, Docker Compose   <br> |

## Shared components   
All sites share:   
- **Templates** in `core/assets/templates/`   
- **Static files** in `core/assets/static/`   
- **Settings** in `core/configs/`   
- **Libraries** in `core/libs/`   
   
Per-site code lives in `core/<site>/` and can override shared templates and styles.   
## Request flow   
1. User request hits Traefik (`applications/proxy/`).   
2. Traefik routes to the correct site container based on host.   
3. Site container runs Django/Wagtail code from `core/<site>/`.   
4. Static and media files are served by Nginx (`shared-media`).   
5. Background tasks are processed by Celery workers.   
   
## Data flow   
- PostgreSQL stores application data.   
- Redis stores cache and Celery broker/result backend.   
- Site media is stored in per-site volumes and served by Nginx.   
   
## Scalability   
- New sites can be added under `core/<new-site>/`.   
- Shared components reduce duplication.   
- Background tasks are centralized in shared workers.   
- Multi-domain or single-domain deployment is supported.   

## Related Docs — (intentionally omitted: AnyType export with native backlink navigation; cross-references are maintained through the AnyType graph.)