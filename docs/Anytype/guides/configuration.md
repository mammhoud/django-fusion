---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Guide
Tags: configuration, reference, install
Status: Published
Category: Config
---

# Configuration — System Setup Reference

> All system configuration variables, environment settings, and their default values across platforms and editions.

---

## Environment Variables

### Core Variables

| Variable | Required | Default | Description | Platform |
|----------|----------|---------|-------------|----------|
| `SECRET_KEY` | ✅ | — | Django secret key (generate with `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`) | All |
| `DEBUG` | — | `False` | Django debug mode (`True` for development) | All |
| `DATABASE_URL` | ✅ | `sqlite:///restaurant.db` | Database connection string | All |
| `ALLOWED_HOSTS` | ✅ | `*` | Comma-separated allowed hostnames | All |

### Database Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `POSTGRES_USER` | PostgreSQL | `structa` | Database username |
| `POSTGRES_PASSWORD` | PostgreSQL | — | Database password |
| `POSTGRES_DB` | PostgreSQL | `structa` | Database name |
| `POSTGRES_HOST` | PostgreSQL | `localhost` | Database host |
| `POSTGRES_PORT` | PostgreSQL | `5432` | Database port |
| `REDIS_URL` | Redis | `redis://localhost:6379/0` | Redis connection string |

### Deployment & Proxy

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CF_DNS_API_TOKEN` | SSL (Traefik) | — | Cloudflare DNS API token for Let's Encrypt |
| `ACME_EMAIL` | SSL | — | Email for Let's Encrypt notifications |
| `TRAEFIK_DOMAIN` | — | `localhost` | Primary domain for routing |
| `MEDIA_URL` | — | `/media/` | Media files URL prefix |
| `STATIC_URL` | — | `/static/` | Static files URL prefix |

### POS Sidecar

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SIDECAR_PORT` | — | `8766` | Sidecar HTTP server port |
| `SIDECAR_HOST` | — | `127.0.0.1` | Sidecar bind address |
| `TAURI_DEV_HOST` | — | `localhost` | Tauri dev server host |
| `TAURI_DEV_PORT` | — | `1420` | Tauri dev server port |

---

## Configuration Files

| File | Purpose | Edition |
|------|---------|---------|
| `pyproject.toml` | Python project/dependency config | Solo, Full |
| `Cargo.toml` | Rust project/dependency config | Mini |
| `package.json` | Node.js project/config | All |
| `tailwind.config.ts` | Tailwind CSS customization | All |
| `vite.config.ts` | Vite build configuration | All |
| `tsconfig.json` | TypeScript compiler options | All |
| `docker-compose.yml` | Docker service orchestration | Cloud |
| `.env` | Environment variables | All |

---

## Platform-Specific Settings

### macOS

```bash
# Development profile
export DEBUG=True
export DATABASE_URL=sqlite:///restaurant.db
export SIDECAR_PORT=8766
```

### Linux

```bash
# Production profile
export DEBUG=False
export DATABASE_URL=postgres://user:pass@localhost:5432/structa
export SECRET_KEY=your-production-key
```

### Windows (PowerShell)

```powershell
$env:DEBUG = "True"
$env:DATABASE_URL = "sqlite:///restaurant.db"
$env:SIDECAR_PORT = "8766"
```

### Docker

```bash
# .env file
DEBUG=False
DATABASE_URL=postgres://structa:password@db:5432/structa
SECRET_KEY=production-secret-key
CF_DNS_API_TOKEN=cloudflare-token
```

---

## Makefile Targets

| Command | Description | Target Directory |
|---------|-------------|-----------------|
| `make dev` | Run development servers | `projects/` |
| `make deploy` | Deploy full stack | Root |
| `make test` | Run tests | `projects/` |
| `make check` | Django checks | `projects/` |
| `make migrate` | Run migrations | `projects/` |

---

## Related

- → `install/macos.md` — macOS install
- → `install/linux.md` — Linux install
- → `install/windows.md` — Windows install
- → `install/docker.md` — Docker install
- → `../deployment.md` — Deployment guide
- → `../../objects/configuration.md` — Configuration object type
- → `../../README.md` — Master index
