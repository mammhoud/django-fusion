# Self-Hosted Tools

**Location:** `application/tools/`
**Purpose:** Auxiliary self-hosted services that back the platform (inference,
database admin, mail capture, monitoring, docs, workspace).

Each tool lives in its own directory with a `docker-compose.yml` + `Makefile`,
and is reachable through a single Traefik entry point at
`tools.structa.cloud/<tool>/` (path-based split performed by the shared-proxy
Nginx — see `application/tools/nginx/default.conf.template`).

```
application/tools/
├── README.md        (this file)
├── .gitignore
├── docker-compose.yml   (aggregate include for all tools)
├── blinko/          Blinko personal AI note tool
├── adminer/         Database administration UI
├── mailpit/         Email catcher (SMTP :1025, UI :8025)
└── monitoring/      Prometheus + Grafana
```

> The Docus documentation service moved out of `application/tools/` — it now
> lives at the root of `docs/` (`docs/docker-compose.yml` + `docs/Makefile`).
> Route it with `make -C docs up` / `make deploy-docs` (root).

## Entry point

| Path | Tool | Container | Port |
|---|---|---|---|
| `tools.structa.cloud/` | navigation page | shared-proxy | 80 |
| `space.structa.cloud/` | Space (Coder) | `coder` | 7080 |
| `tools.structa.cloud/notes/` | Blinko | `blinko` | 1111 |
| `tools.structa.cloud/adminer/` | Adminer | `adminer` | 8080 |
| `tools.structa.cloud/mailpit/` | Mailpit | `mailpit` | 8025 |
| `tools.structa.cloud/grafana/` | Grafana | `grafana` | 3000 |
| `tools.structa.cloud/docs/` | Docus | `docus` | 3000 (deployed from `docs/docker-compose.yml`) |

TLS is handled by Traefik (`certResolver: letsencrypt-http`) — no manual
certificate generation is required; see
`application/proxy/configs/traefik/dynamic/tools.yml`.

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
```

### Networks

The shared proxy joins `common` and `traefik-net`; Blinko and its dedicated
`blinko-db` join `common` so the proxy can resolve the app and the app can
resolve its database. Create the external networks once:

```bash
make create-networks
```

### Environment

Every variable referenced by the tool compose files lives in
**`application/tools/.env.example`** (versions, ports, designs, and generated
RANDOM defaults for secrets) — covering all tools, including the ones
commented out of the aggregate file (`adminer/`, `monitoring/`):
`ADMINER_DESIGN`, `MAILPIT_VERSION`,
`GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD`, `BLINKO_DB_PASSWORD`, …

```bash
cd application/tools/<tool>
make setup     # creates the tool's local .env from its example if missing
make up        # uses the tool-local env, then shared tools/root fallback
```

Each tool Makefile resolves its env according to that tool's contract. Blinko
prefers `application/tools/blinko/.env`, then the shared tools env, then the
repo-root `.env`. The aggregate file (`application/tools/docker-compose.yml`)
uses the env file supplied by the caller.

> **Blinko note:** `BLINKO_DB_PASSWORD` belongs to the dedicated `blinko-db`
> service and must remain stable for the `blinko-data/postgres` volume. The
> generated defaults in `.env.example` are for fresh local deployments only.

## Per-tool notes

- **space (coder)** — cloud development environment at `space.structa.cloud/`.
  Provides VS Code Web, terminals, and AI agent workspaces. Managed by
  `application/docker-compose.yml`.
- **blinko/** — self-hosted personal AI note tool. Uses its dedicated
  `blinko-db` PostgreSQL service and is routed at `tools.structa.cloud/notes/`.
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
| Formints | POS editions (Community, Standard, Cloud) | Active |
| Syntara | AI chat and customization | Active |
| Loop CRM | Customer relationship management | Active |

## Tools that could be added

| Tool | Description | Category |
|---|---|---|
| n8n | Workflow automation | Automation |
| Uptime Kuma | Uptime monitoring | Monitoring |
| Trilium | Personal note-taking (alternative to Blinko) | Notes |
| Plausible | Privacy-focused analytics | Analytics |
| MinIO | S3-compatible object storage | Storage |
| Keycloak | Identity and access management | Auth |
| Gitea | Self-hosted Git service | DevOps |
| Portainer | Docker management UI | DevOps |
