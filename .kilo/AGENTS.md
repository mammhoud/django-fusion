# MCP Server — Agent Instructions

Path: `.kilo/mcp_server.py`

## Purpose

FastAPI-based MCP (Model Context Protocol) server for Structa Cloud.
Provides project-local introspection and status endpoints for AI agents
and tooling without triggering heavy initialization (Django config, AI model
loading) at import time.

## Running

```bash
# From project root, run the MCP server:
uvicorn --app-dir .kilo mcp_server:app --host 0.0.0.0 --port 8100
```

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Overall service health: Django status, optional dependencies, Traefik, Docker, auth, websites |
| `GET /viewsets` | Available `django-osoul` viewsets |
| `GET /migrations/status` | Django `showmigrations` output (503 if Django not configured) |
| `GET /crafts-ai/info` | `crafts_ai` package metadata |
| `GET /crafts-ai/agents` | Known `crafts_ai` agents listing |
| `GET /django-osoul/info` | `django-osoul` package metadata and module inventory |
| `GET /django-osoul/viewsets` | `django-osoul` viewsets availability |
| `GET /traefik/status` | Traefik dynamic config, certs, and site router existence |
| `GET /docker/status` | Docker container status for the project |
| `GET /auth/features` | Auth feature availability (allauth, MFA, social auth, oauth2) |
| `GET /websites/endpoints` | Configured website host/port/service mappings |
| `GET /openrouter/status` | OpenRouter readiness (API key + openai package check) |

## Design Notes

- **Import-safe**: Does not configure Django or call external AI APIs at module level
- **Optional dependencies**: Gracefully handles missing `fastapi`, `django`, `crafts_ai`, `openai`
- **Lightweight**: Returns JSON responses for all endpoints
- **Modular**: Each endpoint is self-contained, easy to add new helpers
- **Project path**: Uses `/home/structa.cloud/proxy/traefik` for config detection
