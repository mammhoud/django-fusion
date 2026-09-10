---
Object type: Guide
Tags: deployment, infrastructure, docker
Status: Published
---

# Deployment Guide

> This page summarizes how Structa Cloud is deployed.

## Overview

Deployment is orchestrated through Docker Compose. The root compose file includes the database, proxy, and application service definitions.

## Quick start

1. Run a preflight check to validate configuration.
2. Deploy the full stack.

## Deployment order

The default order is:

1. **Databases** – PostgreSQL and Redis
2. **Coder** – depends on PostgreSQL
3. **Media server** – Nginx shared media server
4. **Applications** – CTC Research, LMS Demo, VResume
5. **Tasks** – background workers and scheduled jobs
6. **Docs** – documentation service
7. **Proxy** – Traefik reverse proxy

## Key compose files

| File | Purpose |
|------|---------|
| docker-compose.yml | Root orchestration |
| applications/databases/docker-compose.yml | PostgreSQL + Redis |
| applications/proxy/docker-compose.yml | Traefik + Nginx |
| applications/compose/docker-compose.applications.yml | Application services |
| applications/compose/docker-compose.tasks.yml | Background workers |
| applications/compose/docker-compose.docs.yml | Docs service |

## Environment

Copy and fill the environment file. Set at minimum:

- **Cloudflare DNS token** – for certificate issuance
- **PostgreSQL user** and **password** – database credentials
- **SECRET_KEY** – Django secret key

## SSL certificates

Traefik obtains certificates via Let's Encrypt DNS-01 (Cloudflare). Bootstrap the certificate storage once, then check certificate status as needed.

## Useful operations

| Operation | Purpose |
|-----------|---------|
| Deploy databases only | Bring up PostgreSQL + Redis |
| Deploy applications only | Bring up the Django applications |
| Restart proxy | Rebuild the reverse proxy |
| View status | Check running services |
| View logs | Inspect service output |

## Rollback

If a deployment fails, stop the services and redeploy. For a full reset (which destroys data), use the clean operation.

## Related Docs

- → `../architecture/overview.md` — Architecture context
- → `../references/_index.md` — Database schemas (planned)
- → `../tasks/tasks-and-backlog.md` — Deployment tasks
