---
Object type: Guide
Tags: configuration, reference, install
Status: Published
Category: Config
---

# Configuration — System Setup Reference

> System configuration variables, environment settings, and their default values across platforms and editions.

## Environment variables

### Core variables

| Variable | Required | Default | Description | Platform |
|----------|----------|---------|-------------|----------|
| SECRET_KEY | Yes | — | Django secret key | All |
| DEBUG | No | off | Django debug mode (on for development) | All |
| DATABASE_URL | Yes | sqlite local | Database connection string | All |
| ALLOWED_HOSTS | Yes | all | Allowed hostnames | All |

### Database configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| POSTGRES_USER | PostgreSQL | structa | Database username |
| POSTGRES_PASSWORD | PostgreSQL | — | Database password |
| POSTGRES_DB | PostgreSQL | structa | Database name |
| POSTGRES_HOST | PostgreSQL | localhost | Database host |
| POSTGRES_PORT | PostgreSQL | 5432 | Database port |
| REDIS_URL | Redis | local Redis | Redis connection string |

### Deployment & proxy

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| CF_DNS_API_TOKEN | SSL (Traefik) | — | Cloudflare DNS token for Let's Encrypt |
| ACME_EMAIL | SSL | — | Email for certificate notifications |
| TRAEFIK_DOMAIN | No | localhost | Primary domain for routing |
| MEDIA_URL | No | /media/ | Media files URL prefix |
| STATIC_URL | No | /static/ | Static files URL prefix |

### POS sidecar

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| SIDECAR_PORT | No | 8766 | Sidecar HTTP server port |
| SIDECAR_HOST | No | 127.0.0.1 | Sidecar bind address |
| TAURI_DEV_HOST | No | localhost | Tauri dev server host |
| TAURI_DEV_PORT | No | 1420 | Tauri dev server port |

## Configuration files

| File | Purpose | Edition |
|------|---------|---------|
| pyproject.toml | Python project and dependency config | Solo, Full |
| Cargo.toml | Rust project and dependency config | Mini |
| package.json | Node.js project and config | All |
| tailwind.config | Tailwind CSS customization | All |
| vite.config | Vite build configuration | All |
| tsconfig.json | TypeScript compiler options | All |
| docker-compose.yml | Docker service orchestration | Cloud |
| .env | Environment variables | All |

## Platform-specific settings

### macOS

Development profile: debug mode on, local SQLite database, sidecar on the local port.

### Linux

Production profile: debug mode off, PostgreSQL database, production secret key.

### Windows (PowerShell)

Development profile: debug mode on, local SQLite database, sidecar on the local port.

### Docker

Production profile via the environment file: debug off, PostgreSQL database, production secret key, and Cloudflare DNS token for SSL.

## Common operations

| Operation | Description | Target |
|-----------|-------------|--------|
| Run development servers | Start all dev servers | projects/ |
| Deploy full stack | Deploy the whole platform | Root |
| Run tests | Execute test suites | projects/ |
| Run Django checks | Validate installation | projects/ |
| Run migrations | Apply database migrations | projects/ |

## Related

- → `install/macos.md` — macOS install
- → `install/linux.md` — Linux install
- → `install/windows.md` — Windows install
- → `install/docker.md` — Docker install
- → `deployment.md` — Deployment guide
- → `../../README.md` — Anytype hub
