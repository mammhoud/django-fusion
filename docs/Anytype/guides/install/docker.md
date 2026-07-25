---
# yaml-language-server: $schema=../../schemas/page.schema.json
Object type: Guide
Tags: install, deploy, pos-mini, pos-solo, pos-full, pos-cloud
Status: Published
Platform: Docker
---

# Docker Installation Guide

> Containerized deployment guide for production and development environments.

---

## Prerequisites

```bash
# Docker Engine (any platform)
docker --version          # ≥ 24
docker compose version    # ≥ v2.20

# For Tauri desktop builds (macOS/Linux only)
# Tauri development requires native system dependencies
```

---

## Step 1: Install Docker

### macOS

```bash
# Docker Desktop for Mac
brew install --cask docker

# Or use OrbStack (lighter alternative)
brew install --cask orbstack
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and back in for group changes
```

### Windows

```powershell
# Docker Desktop with WSL2 backend
winget install Docker.DockerDesktop

# Or use WSL2 directly with Docker CLI
wsl --install -d Ubuntu
# Then follow Linux instructions in WSL2
```

---

## Step 2: Clone Repository

```bash
git clone https://github.com/mammhoud/structa.cloud.git
cd structa.cloud
```

---

## Step 3: Full Stack Deployment

```bash
# Deploy everything (databases → apps → proxy)
make deploy

# Or deploy step-by-step:
make deploy-databases   # PostgreSQL + Redis
make deploy-app         # Django applications
make deploy-proxy       # Traefik + Nginx
```

---

## Step 4: Service Management

```bash
# View all running services
docker compose ps

# View logs
make logs
# Or specific services:
docker compose logs app

# Check health
make status

# Stop everything
make stop

# Full reset (destroys data!)
make clean
```

---

## Development in Docker

```bash
# Run a single site in development mode
cd projects && make dev WEBSITE=lms

# Run tests
cd projects && make test WEBSITE=lms

# Build assets
cd projects && make build WEBSITE=lms
```

---

## Docker Compose Structure

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Root orchestration |
| `applications/databases/docker-compose.yml` | PostgreSQL + Redis |
| `applications/proxy/docker-compose.yml` | Traefik + Nginx |
| `applications/compose/docker-compose.applications.yml` | Django apps |
| `applications/compose/docker-compose.tasks.yml` | Celery workers |

---

## Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `CF_DNS_API_TOKEN` | Cloudflare DNS API token | Yes (SSL) |
| `POSTGRES_USER` | Database username | Yes |
| `POSTGRES_PASSWORD` | Database password | Yes |
| `SECRET_KEY` | Django secret key | Yes |
| `ACME_EMAIL` | Let's Encrypt notification email | Yes (SSL) |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `docker: permission denied` | Add user to docker group: `sudo usermod -aG docker $USER` |
| `port 80/443 already in use` | Stop other web servers or change proxy ports |
| `SSL certificate error` | Run `./applications/proxy/scripts/manage-certs.sh bootstrap-acme` |
| `Database connection refused` | Ensure databases are running: `docker compose ps` |

---

## Related

- → `macos.md` — macOS setup (for local Tauri dev)
- → `linux.md` — Linux setup (for local Tauri dev)
- → `windows.md` — Windows setup (for local Tauri dev)
- → `../deployment.md` — Deployment guide
- → `../configuration.md` — System configuration
- → `../../objects/configuration.md` — Configuration object type
- → `../../README.md` — Master index
