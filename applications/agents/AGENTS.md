# Kilo MCP Server — AI Agent Instructions

**Path:** `applications/agents/`

Read `/AGENTS.md` and `applications/AGENTS.md` first. Kilo is a lightweight
FastAPI MCP/introspection service for this repository. It exposes read-oriented
project, framework, infrastructure, and agent metadata without eagerly loading
Django or AI models.

## Layout

```text
applications/agents/
├── mcp_server.py             # FastAPI MCP endpoints
├── config.json / kilo.jsonc  # Kilo configuration
├── agent/                    # Agent role definitions
├── commands/                 # Agent-facing command instructions
├── prompts/                  # Read-only machine-readable prompt catalog
├── prompt_catalog.py        # Lazy prompt catalog loader/accessors
├── test_prompts.py          # Prompt catalog contract tests
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
| Designer | `/designer/tools`, `/designer/component-catalog`, `/designer/wagtail-field`, `/designer/form-scaffold`, `/designer/table-scaffold`, `/designer/preview` | Read-only django-fusion component catalog, Wagtail field suggestions, form/table scaffolds, and safe component preview |

Confirm current routes in `mcp_server.py` before adding or documenting an
endpoint. Keep response schemas stable and redact credentials/secret values.
Prompt endpoints are catalog-only: they return descriptions and templates but
never execute prompts, interpolate untrusted values, read arbitrary files, or
mutate the repository. Any future apply capability must be a separate,
explicitly authorized workflow.

## Skills, prompts, and commands

- `prompts/catalog.json` — stable skill, project, and workflow prompt definitions
- `prompt_catalog.py` — read-only lazy loader used by the MCP metadata endpoints
- `/prompts` — concise prompt metadata listing (requires API-key or localhost, same auth as designer)
- `/prompts/{id}` — complete prompt definition; never executes the prompt
- `skills/mcp-deploy-verifier/SKILL.md` — deployment readiness checks
- `skills/wagtail-field-customizer/SKILL.md` — Wagtail field workflows
- `skills/scss-bem-converter/SKILL.md` — BEM conversion workflow
- `commands/find-component.md` — locate component sources
- `commands/apply-design.md` — design system changes
- `commands/add-field.md` — model/Wagtail field changes
- `commands/deploy.md` — deployment procedures
- `commands/ceptor-ai.md` — AI integration procedures

## Designer tools (django-fusion)

The `/designer/` endpoints bridge django-fusion's interactive designer to MCP clients:

- `/designer/tools` — list all 8 designer tools with MCP metadata (inputSchema, annotations)
- `/designer/component-catalog?query=&limit=50` — browse registered `{% comp %}` components
- `/designer/wagtail-field?field_type=char&name=my_field` — suggest a Wagtail/Django field
- `/designer/form-scaffold?class_name=MyForm&style_framework=bootstrap` — generate a Django form scaffold
- `/designer/table-scaffold?class_name=MyTable` — generate a django-tables2 table scaffold
- `/designer/preview?name=blocks/hero.html` — safely preview a registered component with JSON props

**Safety:** All designer tools are read-only or pure-generation. They do not write
files, modify databases, compile templates, run migrations, or execute shell
commands. Generated code must be separately reviewed before application.

**Auth:** Designer endpoints are gated by a two-tier policy (mirrors `designer/views.py._is_allowed`):

| Mode | Trigger | Behaviour |
|---|---|---|
| **API-key** | `FUSION_MCP_DESIGNER_API_KEY` env var or Django setting is set | Requires ``X-API-Key`` header matching the configured key |
| **Localhost fallback** | No API key configured | Allows requests from `127.0.0.1`, `::1`, `localhost` only; remote callers receive 403 |

Set the key via environment or Django: ``FUSION_MCP_DESIGNER_API_KEY=secret``.
Callers send ``curl -H "X-API-Key: secret" http://host:8100/designer/tools``.

**GET endpoints** (simple operations via query params): `/designer/tools`, `/designer/component-catalog`, `/designer/wagtail-field`, `/designer/form-scaffold`, `/designer/table-scaffold`, `/designer/preview`.

**POST JSON-RPC endpoint** (complex operations with full JSON payloads)::

    POST /designer/tools/call
    Content-Type: application/json

    {
      "jsonrpc": "2.0",
      "id": 1,
      "method": "tools/call",
      "params": {
        "name": "designer.website_audit",
        "arguments": {
          "project": "precis-landing",
          "sections": [{"name": "hero", "kind": "hero", "has_visual": true}]
        }
      }
    }

All 8 designer tools are available via POST: `designer.website_audit`, `designer.webapp_enhancement_plan`, `designer.validate`, `designer.form_scaffold` (with fields), `designer.table_scaffold` (with columns), `designer.wagtail_field` (with choices), `designer.component_catalog`, `designer.preview` (with props).

**Prerequisites:** Requires `django_fusion` to be importable. Tools gracefully return
503 when the designer module is unavailable.

Read the product-specific `AGENTS.md` before using a command against a product.

## Local development

```bash
uvicorn --app-dir applications/agents mcp_server:app --host 127.0.0.1 --port 8100
uvicorn --app-dir applications/agents mcp_server:app --host 127.0.0.1 --port 8100 --reload
curl http://127.0.0.1:8100/readyz
curl http://127.0.0.1:8100/health
curl http://127.0.0.1:8100/prompts
curl http://127.0.0.1:8100/prompts/project.precis-landing
```

Use a local/isolated Docker context for Docker status probes. Never expose
private environment values in responses or logs.

## Related

- [`../../AGENTS.md`](../../AGENTS.md) — repository-wide rules
- [`../AGENTS.md`](../AGENTS.md) — infrastructure boundaries and safety
- [`../../libs/django-fusion/AGENTS.md`](../../libs/django-fusion/AGENTS.md)
