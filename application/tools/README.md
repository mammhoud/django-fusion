# Self-Hosted Tools

**Location:** `application/tools/`
**Purpose:** Auxiliary self-hosted services that back the platform (inference,
database admin, mail capture, monitoring, docs, workspace, automation).

Each tool lives in its own directory with a `docker-compose.yml` + `Makefile`,
and is reachable through a single Traefik entry point at
`tools.structa.cloud/<tool>/` (path-based split performed by the tools-proxy
Nginx — see `application/tools/nginx/default.conf.template`).

```
application/tools/
├── README.md          (this file)
├── .env.example       (shared env template)
├── .gitignore
├── docker-compose.yml     (aggregate include for all tools)
├── docker-compose.nginx.yml (tools-proxy Nginx)
├── xyops/             Job scheduling, workflows, monitoring, alerts
├── blinko/            Personal AI note tool
├── adminer/           Database administration UI
├── mailpit/           Email catcher (SMTP :1025, UI :8025)
├── affine/            Permanent shared workspace (AFFiNE)
├── coder/             Cloud dev environment (Space)
├── monitoring/        Prometheus + Grafana
└── nginx/             Shared-proxy Dockerfile + config + www/
```

> The Docus documentation service moved out of `application/tools/` — it now
> lives at the root of `docs/` (`docs/docker-compose.yml` + `docs/Makefile`).
> Route it with `make -C docs up` / `make deploy-docs` (root).

## Entry point

| Path | Tool | Container | Port | Default Sign‑In |
|---|---|---|---|---|
| `tools.structa.cloud/` | navigation page | tools-proxy | 80 | — |
| `space.structa.cloud/` | Space (Coder) | `coder` | 7080 | Configured at setup |
| `tools.structa.cloud/` | AFFiNE | `proxy-affine` | 3010 | First visitor signs up |
| `tools.structa.cloud/notes/` | Blinko | `blinko` | 1111 | First visitor signs up |
| `ops.structa.cloud/` | xyOps | `xyops` | 5522 | `admin` / `admin` |
| `tools.structa.cloud/adminer/` | Adminer | `adminer` | 8080 | PostgreSQL credentials |
| `tools.structa.cloud/mailpit/` | Mailpit | `mailpit` | 8025 | — (no auth) |
| `tools.structa.cloud/grafana/` | Grafana | `grafana` | 3000 | `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD` |
| `tools.structa.cloud/docs/` | Docus | `docus` | 3000 (deployed from `docs/docker-compose.yml`) | — |

TLS is handled by Traefik (`certResolver: letsencrypt-http`) — no manual
certificate generation is required; see
`application/proxy/configs/traefik/dynamic/tools.yml`.

### Sign-in notes

- **Blinko** has **no** hardcoded default admin credentials. The first visitor
  creates an account via the sign-up page on the Blinko login screen. The
  live-demo `blinko/blinko` pair is a special demo-only setup.
- **xyOps** ships with `admin` / `admin` — change immediately after first
  login.
- **AFFiNE** creates the first account through its onboarding flow; no
  pre-seeded user exists.

## Deploy

Each tool has its own Makefile (`make up` / `down` / `logs` / `status`), and
the root Makefile aggregates them:

```bash
# All tools
make deploy-tools

# Individual tools
make deploy-utilities   # monitoring (Prometheus + Grafana)
make deploy-adminer     # Adminer
make deploy-mailpit     # Mailpit
make deploy-blinko      # Blinko notes (tools.structa.cloud/notes/)
make deploy-xyops       # xyOps automation (ops.structa.cloud)
make deploy-affine      # AFFiNE workspace
```

### Networks

The shared proxy joins `common` and `traefik-net`. Create the external
networks once:

```bash
make create-networks
```

### Environment

Every variable referenced by the tool compose files lives in
**`application/tools/.env.example`** (versions, ports, designs, and generated
RANDOM defaults for secrets) — covering all tools, including the ones
commented out of the aggregate file (`adminer/`, `monitoring/`):
`ADMINER_DESIGN`, `MAILPIT_VERSION`, `GRAFANA_ADMIN_USER`,
`GRAFANA_ADMIN_PASSWORD`, `BLINKO_DB_PASSWORD`, `XYOPS_HOSTNAME`, …

```bash
cd application/tools/<tool>
make setup     # creates the tool's local .env from its example if missing
make up        # uses the tool-local env, then shared tools/root fallback
```

Each tool Makefile resolves its env according to that tool's contract. The
aggregate file (`application/tools/docker-compose.yml`) uses the env file
supplied by the caller.

> **Blinko note:** `BLINKO_DB_PASSWORD` belongs to the shared PostgreSQL
> cluster. The generated defaults in `.env.example` are for fresh local
> deployments only.

## Per-tool notes

- **xyops/** — self-hosted operations automation platform. Job scheduling,
  visual workflows, server monitoring, alerting, tickets, and incident
  management. Served at `ops.structa.cloud/` via Traefik (dedicated
  subdomain — no native sub-path support). Ports 5522 (HTTP) and 5523
  (HTTPS). `XYOPS_xysat_local=true` starts a local worker in the same
  container. Bind the Docker socket only when xyOps needs to launch
  containers.
- **space (coder)** — cloud development environment at `space.structa.cloud/`.
  Provides VS Code Web, terminals, and AI agent workspaces. Managed by
  `application/docker-compose.yml`.
- **blinko/** — self-hosted personal AI note tool. Connects to the shared
  PostgreSQL cluster (`postgres:5432` on `common`). Served at
  `tools.structa.cloud/notes/`.
- **affine/** — permanent shared workspace (AFFiNE). Real-time docs,
  whiteboards, and databases. Served at `tools.structa.cloud/`. Uses
  `warehouse-net` for PostgreSQL and `common` for Redis.
- **adminer/** — connects to `postgres:5432` on the `common` network; no host
  port published (routed internally).
- **mailpit/** — SMTP listener on `:1025`; point Django `EMAIL_HOST=mailpit`
  port `1025` to capture outbound mail.
- **monitoring/** — Prometheus scrapes product targets; Grafana is the operator
  UI with `SERVE_FROM_SUB_PATH=/grafana/`.
- **docus/** — migrated out of `application/proxy/` and then out of
  `application/tools/` entirely; the app now lives at the root of `docs/`.

## Projects

| Project | Description | Status |
|---|---|---|
| Precis Main | Unified LMS + Landing product | Active |
| Precis CTC | Medical research center site | Active |
| Precis Dev | Multi-tenant SaaS platform | Planned |
| Formints | POS editions (Community, Standard, Cloud) | Active |
| Syntara | AI chat and customization | Active |
| Loop CRM | Customer relationship management | Active |

## Tools that could be added

| Tool | Description | Category |
|---|---|---|
| n8n | Workflow automation | Automation |
| Uptime Kuma | Uptime monitoring | Monitoring |
| Trigrium | Personal note-taking (alternative to Blinko) | Notes |
| Plausible | Privacy-focused analytics | Analytics |
| MinIO | S3-compatible object storage | Storage |
| Keycloak | Identity and access management | Auth |
| Gitea | Self-hosted Git service | DevOps |
| Portainer | Docker management UI | DevOps |