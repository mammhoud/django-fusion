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
├── affine/          AFFiNE workspace (was in proxy/nginx compose)
├── ollama/          Ollama + Open WebUI (LLM inference)
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
| `tools.structa.cloud/adminer/` | Adminer | `adminer` | 8080 |
| `tools.structa.cloud/mailpit/` | Mailpit | `mailpit` | 8025 |
| `tools.structa.cloud/ai/` | Open WebUI | `open-webui` | 8080 |
| `tools.structa.cloud/grafana/` | Grafana | `grafana` | 3000 |
| `tools.structa.cloud/docs/` | Docus | `docus` | 3000 (deployed from `docs/docker-compose.yml`) |
| `tools.structa.cloud/space/` | AFFiNE | `proxy-affine` | 3010 |

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
make deploy-ollama      # Ollama + Open WebUI
make deploy-adminer     # Adminer
make deploy-mailpit     # Mailpit
make deploy-affine      # AFFiNE workspace (tools.structa.cloud/space/)
```

### Networks

Every tool joins the external `common` and `traefik-net` networks. Ollama also
joins `ollama-net` (dedicated inference network). Create them once:

```bash
make create-networks
```

### Environment

Every variable referenced by the tool compose files lives in
**`application/tools/.env.example`** (versions, ports, designs, and generated
RANDOM defaults for secrets) — covering all tools, including the ones
commented out of the aggregate file (`adminer/`, `monitoring/`, `ollama/`):
`OLLAMA_VERSION`, `OPEN_WEBUI_SECRET_KEY`, `ADMINER_DESIGN`, `MAILPIT_VERSION`,
`GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD`, `AFFINE_DB_PASSWORD`, …

```bash
cd application/tools/<tool>
make setup     # creates ../.env from ../.env.example (only if missing)
make up        # compose --env-file ../.env
```

Each tool Makefile resolves `ENV_FILE ?= $(if $(wildcard ../.env),../.env,../../../.env)`
— the tools env (`application/tools/.env`) wins when present, otherwise the
repo-root `.env` keeps existing deployments working untouched. The aggregate
file (`application/tools/docker-compose.yml`) interpolates from
`application/tools/.env` when run from this directory.

> **AFFiNE note:** `AFFINE_DB_PASSWORD` / `REDIS_PASSWORD` are shared with the
> database cluster — they must match `application/databases/.env`. The
> generated defaults in `.env.example` only work against a fresh cluster;
> rotate/align them before pointing AFFiNE at a live one.

## Per-tool notes

- **ollama/** — backs the existing MCP agent configs (`.agents/mcp/*`) and
  Syntara/CeptorAI, which already point at `ollama:11434`. Models are pulled on
  demand into `./data` (gitignored).
- **adminer/** — connects to `postgres:5432` on the `common` network; no host
  port published (routed internally).
- **mailpit/** — SMTP listener on `:1025`; point Django `EMAIL_HOST=mailpit`
  port `1025` to capture outbound mail.
- **monitoring/** — Prometheus scrapes product targets; Grafana is the operator
  UI with `SERVE_FROM_SUB_PATH=/grafana/`.
- **affine/** — migrated out of `application/proxy/` so the proxy directory
  owns only Traefik/Nginx/certs.
- **docus/** — migrated out of `application/proxy/` and then out of
  `application/tools/` entirely; the app now lives at the root of `docs/`.
