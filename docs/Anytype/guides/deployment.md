---
# yaml-language-server: $schema=schemas/workspace.schema.json
Object type:
    - Workspace
Backlinks:
    - product-development.md
Creation date: "2024-07-12T10:00:00Z"
Created by:
    - mammhoud
Emoji: "\U0001F680"
id: bafyreihcvz6bc62qrn4eoplhbhdmftxbzmlzlg4zccf7xxulyca3dutfim
---
# Deployment Guide   
This page summarizes how Structa Cloud is deployed.   
## Overview   
Deployment is orchestrated through Docker Compose. The root `docker-compose.yml` includes the database, proxy, and application compose files.   
## Quick start   
```
# Validate configuration
make deploy-preflight

# Deploy everything
make deploy

```
## Deployment order   
The default `postgres-first` order is:   
1. **Databases** – PostgreSQL and Redis   
2. **Coder** – depends on PostgreSQL   
3. **Media server** – Nginx shared media server   
4. **Applications** – CTC Research, LMS Demo, VResume   
5. **Tasks** – Celery workers and beat   
6. **Docs** – documentation service   
7. **Proxy** – Traefik reverse proxy   
   
## Key compose files   
|                                                   File   <br> |              Purpose   <br> |
|:--------------------------------------------------------------|:----------------------------|
|                                   `docker-compose.yml`   <br> |   Root orchestration   <br> |
|            `applications/databases/docker-compose.yml`   <br> |   PostgreSQL + Redis   <br> |
|                `applications/proxy/docker-compose.yml`   <br> |      Traefik + Nginx   <br> |
| `applications/compose/docker-compose.applications.yml`   <br> | Application services   <br> |
|        `applications/compose/docker-compose.tasks.yml`   <br> |       Celery workers   <br> |
|         `applications/compose/docker-compose.docs.yml`   <br> |         Docs service   <br> |

## Environment   
Copy and fill the environment files:   
```
cp applications/proxy/.env.example applications/proxy/.env

```
Set at minimum:   
- `CF\_DNS\_API\_TOKEN` – Cloudflare DNS API token   
- `POSTGRES\_USER`, `POSTGRES\_PASSWORD` – database credentials   
- `SECRET\_KEY` – Django secret key   
   
## SSL certificates   
Traefik obtains certificates via Let's Encrypt DNS-01 (Cloudflare).   
```
# Bootstrap ACME storage
./applications/proxy/scripts/manage-certs.sh bootstrap-acme

# Check certificate status
./applications/proxy/scripts/manage-certs.sh status

```
## Useful commands   
```
# Deploy only databases
make deploy-databases

# Deploy only applications
make deploy-app

# Restart proxy
make deploy-proxy

# View status
make status

# View logs
make logs

```
## Rollback   
If a deployment fails, stop and restart services:   
```
make stop
make deploy

```
For a full reset (destroys data):   
```
make clean

```

## Related Docs
- → `../architecture/overview.md` — Architecture context
- → `../references/database-schema.md` — Database schemas
- → `../../applications/proxy/README.md` — Proxy configuration
- → `../tasks/tasks-and-backlog.md` — Deployment tasks