# Coder Templates

Terraform templates for [Coder](https://coder.com) workspaces. Each template
provisions a development environment with the monorepo mounted, Docker socket
access, and a Coder agent for IDE/port-forwarding.

## Templates

| Template | What it provisions | Traefik? | Workspace constraint |
|---|---|---|---|
| [**dev-stack**](./dev-stack/README.md) | code-server IDE + Blinko AI notes | Yes | Must be named `dev` |
| [**website**](./website/README.md) | Django/Wagtail (landing-fusion backend) | No | None (any name works) |

### dev-stack

Multi-service dev workspace. Spins up a code-server IDE with Node.js/npm and a
Blinko note-taking instance, both routed through the shared Traefik reverse
proxy at `code.structa.cloud` and `blinko.structa.cloud`.

→ [dev-stack README](./dev-stack/README.md) · [main.tf](./dev-stack/main.tf)

### website

Single-container Django/Wagtail workspace. Builds from the landing-fusion
Dockerfile, creates an isolated PostgreSQL database, runs migrations, and starts
the Django dev server. Accessed through Coder's built-in port forwarding.

→ [website README](./website/README.md) · [main.tf](./website/main.tf)

## Shared infrastructure

Both templates depend on infrastructure defined outside the templates
directory:

| Component | Defined in |
|---|---|
| PostgreSQL + Redis + Coder | `applications/databases/docker-compose.yml` |
| Traefik reverse proxy | `applications/proxy/docker-compose.yml` |
| Traefik dynamic routes | `applications/proxy/traefik/dynamic/*.yml` |
| Docker network (`common`) | Created externally |

The databases docker-compose must be running before any workspace is created.

## Quick start

```bash
# 1. Start infrastructure
cd applications/databases
docker compose up -d

# 2. Push templates to Coder (or use the Coder UI)
coder templates push dev-stack  --directory applications/templates/dev-stack
coder templates push website    --directory applications/templates/website

# 3. Create a workspace from the Coder dashboard
#    - dev-stack: name it "dev" (required!)
#    - website:   name it anything
```

## File layout

```
applications/templates/
├── README.md              ← you are here
├── dev-stack/
│   ├── main.tf            ← code-server + Blinko
│   └── README.md          ← full docs
└── website/
    ├── main.tf            ← Django/Wagtail
    └── README.md          ← full docs
```
