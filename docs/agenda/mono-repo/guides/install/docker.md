---
Object type: Guide
Tags: install, deploy, docker, pos
Status: Published
Platform: Docker
---

# Docker Setup Guide

> Description-oriented guide for containerized deployment in development and production environments. Tasks are described by action and outcome; exact commands live in the repository docs.

## Prerequisites

| Tool | Minimum Version | Purpose |
|------|-----------------|---------|
| Docker Engine | 24+ | Container runtime |
| Docker Compose | v2.20+ | Service orchestration |

## Setup steps

1. **Install Docker** on your platform:
   - **macOS** — use Docker Desktop or a lightweight alternative like OrbStack
   - **Linux (Ubuntu/Debian)** — install the Docker engine and Compose plugin, enable the service, and add your user to the Docker group
   - **Windows** — use Docker Desktop with the WSL2 backend, or install WSL2 directly and follow the Linux instructions inside it
2. **Clone the repository** — clone the monorepo so it is ready for deployment.
3. **Deploy the stack** — run a full-stack deployment (databases → applications → proxy), or deploy each layer step-by-step.
4. **Manage services** — view running services, inspect logs, check health, start, stop, and reset as needed. Note that a full reset destroys data.
5. **Develop in Docker** — run a single site in development mode, run tests, and build assets for that site.

## Compose structure

| File | Purpose |
|------|---------|
| docker-compose.yml | Root orchestration |
| applications/databases/docker-compose.yml | PostgreSQL + Redis |
| applications/proxy/docker-compose.yml | Traefik + Nginx |
| applications/compose/docker-compose.applications.yml | Django applications |
| applications/compose/docker-compose.tasks.yml | Background workers |

## Configuration variables

| Variable | Purpose | Required |
|----------|---------|----------|
| Cloudflare DNS token | Certificate issuance | Yes (SSL) |
| PostgreSQL user | Database username | Yes |
| PostgreSQL password | Database password | Yes |
| Django secret key | Application security | Yes |
| Let's Encrypt email | Certificate notifications | Yes (SSL) |

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Docker permission denied | Add the user to the Docker group and re-login |
| Port 80/443 already in use | Stop other web servers or change proxy ports |
| SSL certificate error | Re-run the certificate bootstrap script |
| Database connection refused | Ensure the database services are running |

## Related

- → `macos.md` — macOS setup (for local desktop dev)
- → `linux.md` — Linux setup (for local desktop dev)
- → `windows.md` — Windows setup (for local desktop dev)
- → `../deployment.md` — Deployment guide
- → `../configuration.md` — System configuration
- → `../../README.md` — Anytype hub
