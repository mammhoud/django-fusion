# Kilo MCP Server — AI Agent Instructions

Path: `applications/kilo/`

## Purpose

FastAPI-based MCP (Model Context Protocol) server for the Structa Cloud monorepo. Provides project-local introspection and status endpoints for AI agents and tooling without triggering heavy initialization (Django config, AI model loading) at import time.

---

## Running

```bash
# From project root, run the MCP server:
uvicorn --app-dir applications/kilo mcp_server:app --host 0.0.0.0 --port 8100

# Or use the Makefile target:
make kilo-server
```

---

## Endpoints

### Health & Status

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /health` | GET | Overall service health: Django status, optional depedencies, Traefik, Docker, auth, websites |
| `GET /readyz` | GET | Readiness probe (lightweight, no dependency checks) |
| `GET /livez` | GET | Liveness probe (always returns 200 if server is running) |

### django-fusion

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /viewsets` | GET | Available `django-fusion` viewsets |
| `GET /django-fusion/info` | GET | `django-fusion` package metadata and module inventory |
| `GET /django-fusion/viewsets` | GET | `django-fusion` viewsets availability |

### Ceptor-AI

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /ceptor-ai/info` | GET | `ceptor_ai` package metadata |
| `GET /ceptor-ai/agents` | GET | Known `ceptor_ai` agents listing |

### Migrations

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /migrations/status` | GET | Django `showmigrations` output (503 if Django not configured) |

### Infrastructure

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /traefik/status` | GET | Traefik dynamic config, certs, and site router existence |
| `GET /docker/status` | GET | Docker container status for the project |
| `GET /auth/features` | GET | Auth feature availability (allauth, MFA, social auth, OAuth2) |
| `GET /websites/endpoints` | GET | Configured website host/port/service mappings |
| `GET /openrouter/status` | GET | OpenRouter readiness (API key + openai package check) |

---

## Skills

| Skill | Path | Purpose |
|-------|------|---------|
| MCP Deploy Verifier | `skills/mcp-deploy-verifier/SKILL.md` | Verifies deployment readiness of MCP endpoints |
| Wagtail Field Customizer | `skills/wagtail-field-customizer/SKILL.md` | Customizes Wagtail page fields via AI |
| SCSS BEM Converter | `skills/scss-bem-converter/SKILL.md` | Converts CSS classes to strict BEM naming |

---

## Commands

| Command | Path | Purpose |
|---------|------|---------|
| `apply-design` | `commands/apply-design.md` | Apply design system changes |
| `find-component` | `commands/find-component.md` | Locate component source files |
| `add-field` | `commands/add-field.md` | Add fields to Django models |
| `deploy` | `commands/deploy.md` | Deploy commands |
| `ceptor-ai` | `commands/ceptor-ai.md` | Ceptor-AI integration commands |

---

## Design Notes

- **Import-safe**: Does not configure Django or call external AI APIs at module level
- **Optional dependencies**: Gracefully handles missing `fastapi`, `django`, `ceptor_ai`, `openai`
- **Lightweight**: Returns JSON responses for all endpoints
- **Modular**: Each endpoint is self-contained, easy to add new helpers
- **Project path**: Uses `/home/structa.cloud/applications/proxy/traefik` for config detection

---

## Development

```bash
# Run with hot reload
uvicorn --app-dir applications/kilo mcp_server:app --host 127.0.0.1 --port 8100 --reload

# Test all endpoints
curl http://127.0.0.1:8100/health
curl http://127.0.0.1:8100/django-fusion/info
curl http://127.0.0.1:8100/traefik/status
```

---

## Related Docs

| Resource | Path |
|----------|------|
| MCP Integration | `docs/ai/mcp-integration.md` |
| AI Agents | `docs/ai/agents.md` |
| Ceptor-AI | `libs/ceptor-ai/AGENTS.md` |
| django-fusion | `libs/django-fusion/AGENTS.md` |
