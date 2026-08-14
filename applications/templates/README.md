# Coder Templates

Terraform templates for [Coder](https://coder.com) workspaces. Templates
provision the monorepo, Docker access, and a Coder agent for authenticated
workspace applications.

## Templates

| Template | What it provisions | Public routing | Workspace constraint |
|---|---|---|---|
| [**dev-workspace**](./dev-workspace/README.md) | code-server + FileGator + AppFlowy Cloud | FileGator only | Must be named `dev` |
| [**website**](./website/README.md) | Django/Wagtail landing-fusion workspace | Coder app | None |

### dev-workspace

The development workspace includes an internal code-server IDE, a
workspace-scoped FileGator, and a PostgreSQL-backed AppFlowy Cloud stack.
AppFlowy and code-server are exposed only as authenticated Coder apps; no
fixed host ports or public `blinko.structa.cloud`, `code.structa.cloud`, or
`ws.structa.cloud` routes are configured.

FileGator retains `filegator.structa.cloud` for compatibility with the shared
proxy, but its container port is internal-only as well.

→ [dev-workspace README](./dev-workspace/README.md) ·
[main.tf](./dev-workspace/main.tf)

### website

Single-container Django/Wagtail workspace. It builds from the landing-fusion
Dockerfile, creates an isolated PostgreSQL database, runs migrations, and
starts the Django development server through Coder.

→ [website README](./website/README.md) · [main.tf](./website/main.tf)

## Shared infrastructure

| Component | Defined in |
|---|---|
| PostgreSQL + Redis | `applications/databases/docker-compose.yml` |
| Coder control plane | `applications/docker-compose.yml` |
| Traefik + shared-media nginx | `applications/proxy/docker-compose.yml` |
| FileGator route | `applications/proxy/traefik/dynamic/filegator.yml` |
| Docker networks (`common`, `warehouse-net`) | Infrastructure deployment |

The database and Redis services must be running before creating a
`dev-workspace`. A new PostgreSQL volume creates the `appflowy` database and
role; existing volumes need the normal database maintenance step to add them.

## Quick start

```bash
# 1. Start shared database infrastructure
cd applications/databases
docker compose up -d postgres default-redis

# 2. Start Coder
cd ..
docker compose -f docker-compose.yml up -d coder

# 3. Push the templates
coder templates push dev-workspace --directory applications/templates/dev-workspace
coder templates push website --directory applications/templates/website

# 4. Create dev-workspace with workspace name "dev"
#    Open code-server and AppFlowy from the Coder workspace page.
```

## File layout

```text
applications/templates/
├── README.md
├── dev-workspace/
│   ├── main.tf       # Coder + FileGator + internal AppFlowy Cloud
│   └── README.md     # full workspace configuration and validation
└── website/
    ├── main.tf
    └── README.md
```
