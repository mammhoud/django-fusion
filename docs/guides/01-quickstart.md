---
title: Quickstart
description: First-time setup — clone the monorepo, install dependencies, configure environment, deploy, and verify.
navigation:
  title: Quickstart
  icon: i-lucide-zap
object:
  type: "guide"
  id: "guide.quickstart"
attributes:
  source_path: "guides/01-quickstart.md"
  canonical_route: "/docs/en/guides/01-quickstart"
  source_of_truth: "repository-markdown"
  audience: "newcomers, CI bootstrap, first-time deploy"
  status: "maintained"
  owner: "workspace"
tags:
  - structa-cloud
  - onboarding
  - quickstart
  - setup
  - deploy
links:
  - label: "Project Awareness"
    to: "/guides/00-project-awareness"
    icon: "i-lucide-compass"
  - label: "Setup & Build"
    to: "/guides/02-setup"
    icon: "i-lucide-wrench"
  - label: "Commands Reference"
    to: "/COMMANDS"
    icon: "i-lucide-terminal"
---

# ⚡ Quickstart — First Hour

> Get from zero to running Structa Cloud sites in one sitting. This guide covers the absolute minimum: clone, install, configure, deploy, verify.

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| **Git** | ≥ 2.40 | `apt install git` / `brew install git` |
| **Docker + Compose** | ≥ 24 / ≥ 2.20 | [Docker Desktop](https://docker.com) or `apt install docker.io docker-compose-plugin` |
| **Python** | ≥ 3.11 | [uv](https://docs.astral.sh/uv/) recommended: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Node** | 18–22 | `nvm` / `fnm` / [Volta](https://volta.sh) |
| **Make** | any | usually preinstalled |

> 💡 **uv** manages the Python workspace (`uv sync`). If you don't have it, `pip install uv` works too.

---

## 1. Clone & Initialize Submodules

```bash
git clone https://github.com/mammhoud/structa.cloud.git
cd structa.cloud
git submodule update --init --recursive
```

> The `libs/django-fusion/` directory is a Git submodule and **must** be initialized before any Django site can boot.

---

## 2. Install Workspace Dependencies

```bash
# Python deps (workspace-level, via uv)
uv sync

# Or without uv: pip install -e libs/django-fusion/ -r projects/pyproject.toml
```

```bash
# JavaScript frontends (runs npm install in each frontend)
npm run install:projects

# Formints editions (Rust/Tauri + POS SDKs)
cd projects/formints && make install-all
```

> ⏱️ First run takes 3–8 min depending on cache. Subsequent runs are seconds.

---

## 3. Environment Configuration

Copy the example env files and edit as needed:

```bash
cp .env.example .env
# Optional: cp .env.local.example .env.local
# Optional: cp application/proxy/.env.example application/proxy/.env
```

**Minimum required edits in `.env`:**

```bash
POSTGRES_USER=admin
POSTGRES_PASSWORD=postgres
DB_NAME_PRECIS_LMS=db_precis_lms
DB_NAME_PRECIS_DEV=db_precis_dev
DB_NAME_PRECIS_CTC=db_precis_ctc
DB_NAME_VRESUME=db_vresume
DB_NAME_LOOP_CRM=db_loop_crm
BLINKO_DB_PASSWORD=Blinko2024SecurePass!
CODER_DB_PASSWORD=Coder2024SecurePass!
```

> See `.env.example` for the full list. For local-only dev you can keep most defaults.

---

## 4. Start Infrastructure (PostgreSQL + Redis + Traefik)

```bash
# Creates networks, starts postgres & redis
make -C application/databases up

# Starts Traefik reverse proxy
make -C application/proxy up
```

Verify they're healthy:
```bash
docker ps --format '{{.Names}}\t{{.Status}}' | grep -E 'postgres|redis|proxy'
# Should show "healthy" for all three
```

---

## 5. Deploy the Stack (Postgres-First Order)

```bash
# Full deploy: databases → media → apps → proxy
make deploy
```

This runs the dependency-ordered deployment:
1. Databases (Postgres, Redis)
2. Self-hosted tools (Blinko, Docus, Affine, Mailpit, Monitoring, Ollama)
3. Application sites (Precis Main, Precis Dev, Precis CTC, Syntara, Loop-CRM)
4. Shared workers (Dramatiq + APScheduler)
5. Proxy (Traefik reload)

> ⚡ **Shortcut:** `just deploy` does the same via the Justfile.

---

## 6. Verify Sites Are Up

```bash
# Probe every site's health endpoint via the common network
make probe-health
```

Expected output shows each site responding with its health JSON. You can also hit the URLs directly:

| Site | URL | Health Endpoint |
|------|-----|-----------------|
| Precis Main (unified LMS + landing) | https://structa.cloud | `/health` |
| Precis Dev | https://dev.structa.cloud | `/health` |
| Precis CTC Research | https://ctc-research.com | `/health` |
| Syntara (Cypercloud) | https://syntara.structa.cloud | `/health` |
| Loop-CRM | https://crm.structa.cloud | `/health` |
| Blinko Notes | https://tools.structa.cloud/notes/ | `/api/health` |
| Docus Docs | https://docs.structa.cloud | `/health` |

---

## 7. Run Checks & Tests (Optional)

```bash
# All workspace checks (Python ruff, Django check, Astro check, etc.)
just check

# All workspace tests
just test
```

---

## 🎉 You're Live!

The Structa Cloud stack is now running. Next steps:

| Want to… | Go To |
|----------|-------|
| Understand the repo layout | [Project Awareness](00-project-awareness.md) |
| Set up a specific project | [Setup & Build](02-setup.md) |
| Configure authentication | [Auth](03-auth.md) |
| Start daily development | [Dev](04-dev.md) |
| Deploy to production | [Deploy](05-deploy.md) |
| Customize safely | [Customize](06-customize.md) |

---

## ## Remarks & Notes

- **First run** pulls ~2 GB of Docker images; subsequent `make deploy` is incremental.
- **Port conflicts:** If 80/443 are busy, Traefik won't start. Stop other services or use `make -C application/proxy up` with custom ports via `.env`.
- **Database migrations** run automatically on first deploy via `make deploy`. For manual control: `cd projects/precis/precis-main/backend && make migrate`.
- **Submodule updates:** When `libs/django-fusion/` changes, run `git submodule update --remote libs/django-fusion` then `uv sync`.
- **Cleanup:** `make clean` removes generated files (caches, dist, logs) + root compose teardown; `make clean-unused` also prunes unused Docker resources (both keep volumes). `make clean-all` is the destructive full teardown. `make cleanup` is the legacy docker-only prune.

<!-- AI-generated: review needed -->