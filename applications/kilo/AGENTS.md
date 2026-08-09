# Kilo MCP Server — AI Agent Instructions

**Path:** `applications/kilo/`

Read `/AGENTS.md` and `applications/AGENTS.md` first. Kilo is a lightweight
FastAPI MCP/introspection service for this repository. It exposes read-oriented
project, framework, infrastructure, and agent metadata without eagerly loading
Django or AI models.

## Layout

```text
applications/kilo/
├── mcp_server.py             # FastAPI MCP endpoints
├── config.json / kilo.jsonc  # Kilo configuration
├── agent/                    # Agent role definitions
├── commands/                 # Agent-facing command instructions
└── skills/                   # Scoped reusable operational skills
```

## Runtime behavior

- Keep module import side-effect free: do not configure Django, open databases,
  load AI models, or call external services at import time.
- Optional dependencies must fail with clear endpoint-level diagnostics rather
  than breaking lightweight health/readiness endpoints.
- Resolve repository paths from the current checkout (`Path(__file__)` or an
  explicit environment variable), never from a hard-coded machine-specific
  absolute path.
- Treat status/introspection endpoints as read-only. Do not add deployment or
  file-mutating behavior without explicit authorization and a separate safety
  review.

## Endpoint groups

| Group | Examples | Purpose |
|---|---|---|
| Health | `/health`, `/readyz`, `/livez` | Service/dependency status |
| Framework | `/django-fusion/info`, `/viewsets` | django-fusion inventory |
| AI | `/ceptor-ai/info`, `/ceptor-ai/agents` | Ceptor-AI metadata |
| Infrastructure | `/traefik/status`, `/docker/status` | Config/container status |
| Sites | `/websites/endpoints` | Product host/port/service mapping |
| Auth/config | `/auth/features`, `/migrations/status` | Availability/configuration checks |

Confirm current routes in `mcp_server.py` before adding or documenting an
endpoint. Keep response schemas stable and redact credentials/secret values.

## Skills and commands

- `skills/mcp-deploy-verifier/SKILL.md` — deployment readiness checks
- `skills/wagtail-field-customizer/SKILL.md` — Wagtail field workflows
- `skills/scss-bem-converter/SKILL.md` — BEM conversion workflow
- `commands/find-component.md` — locate component sources
- `commands/apply-design.md` — design system changes
- `commands/add-field.md` — model/Wagtail field changes
- `commands/deploy.md` — deployment procedures
- `commands/ceptor-ai.md` — AI integration procedures

Read the product-specific `AGENTS.md` before using a command against a product.

## Local development

```bash
uvicorn --app-dir applications/kilo mcp_server:app --host 127.0.0.1 --port 8100
uvicorn --app-dir applications/kilo mcp_server:app --host 127.0.0.1 --port 8100 --reload
curl http://127.0.0.1:8100/readyz
curl http://127.0.0.1:8100/health
```

Use a local/isolated Docker context for Docker status probes. Never expose
private environment values in responses or logs.

## Related

- [`../../AGENTS.md`](../../AGENTS.md) — repository-wide rules
- [`../AGENTS.md`](../AGENTS.md) — infrastructure boundaries and safety
- [`../../libs/django-fusion/AGENTS.md`](../../libs/django-fusion/AGENTS.md)
