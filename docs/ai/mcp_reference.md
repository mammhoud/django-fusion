# MCP reference and setup prompt

This page is the source of truth for the local Model Context Protocol (MCP)
workflow used by Structa Cloud AI tools. The current server is a small HTTP
metadata app owned by `ceptor-ai`; it is intended for local, trusted clients and
must not be exposed publicly without authentication and network controls.

## Canonical server

- **Application:** `ceptor_ai.mcp_server:app`
- **Source:** `core/libs/ceptor-ai/src/ceptor_ai/mcp_server.py`
- **Optional dependency:** `fastapi` and `uvicorn` from the `mcp` extra
- **Bind address:** `127.0.0.1` (local-only by default)
- **Port:** `8002`
- **Kilo entry:** `applications/kilo/config.json`

Install and start it from the repository root:

```bash
uv pip install -e core/libs/ceptor-ai/
uv pip install -e 'core/libs/ceptor-ai/[mcp]'
PYTHONPATH=core/libs/ceptor-ai/src \
  uvicorn ceptor_ai.mcp_server:app --host 127.0.0.1 --port 8002
```

The same setup as a copy/paste prompt for an AI assistant:

> Configure the local Structa Cloud `ceptor-ai` MCP server. First read
> `AGENTS.md`, `docs/ai/START_HERE.md`, `docs/ai/latest_features.md`, and
> `core/libs/ceptor-ai/AGENTS.md`. From the repository root, install the
> editable package and its `mcp` extra. Launch
> `ceptor_ai.mcp_server:app` with `PYTHONPATH=core/libs/ceptor-ai/src`, bound to
> `127.0.0.1:8002`. Verify `/health`, `/info`, `/features`, and
> `/file-structure` with curl. Do not bind to `0.0.0.0`, expose the port through
> a proxy, send secrets in prompts, or add Django/Wagtail imports to the
> standalone `ceptor_ai` MCP module. Report the exact command, endpoint results,
> and any missing optional packages before editing configuration.

## Kilo configuration

`applications/kilo/config.json` contains the HTTP MCP entry used by Kilo:

```json
{
  "ceptor-ai": {
    "command": "uvicorn",
    "args": [
      "ceptor_ai.mcp_server:app",
      "--host", "127.0.0.1",
      "--port", "8002"
    ],
    "env": {
      "PYTHONPATH": "core/libs/ceptor-ai/src"
    }
  }
}
```

Run a smoke test before opening Kilo:

```bash
curl --fail http://127.0.0.1:8002/health
curl --fail http://127.0.0.1:8002/info
curl --fail http://127.0.0.1:8002/features
curl --fail http://127.0.0.1:8002/file-structure
```

## Endpoint contract

| Endpoint | Use | Safe behavior |
|---|---|---|
| `GET /health` | Readiness check | Does not require Django settings. |
| `GET /info` | Package/import metadata | Mirrors the CLI metadata function. |
| `GET /features` | Current MCP feature inventory | Use to discover capabilities before a task. |
| `GET /file-structure` | Canonical package/docs/Kilo paths | Prefer these paths over guessed paths. |
| `GET /auth/features` | Optional auth package detection | Reports availability, not credentials. |
| `GET /django-fusion/info` | Optional library metadata | May return unavailable when the package is absent. |
| `GET /django-fusion/components` | Component registry summary | Read-only introspection. |
| `GET /django-fusion/viewsets` | Viewset availability | Read-only introspection. |
| `GET /websites/endpoints` | Site host/port map | Configuration metadata only. |
| `GET /ssl/status` | Certificate presence/expiry summary | Never returns private keys. |
| `GET /proxy/status` | Proxy configuration presence | Does not mutate proxy files. |

## Safety and maintenance rules

1. Keep the server importable without Django settings. Optional integrations must
   use `importlib.util.find_spec` and `importlib.import_module`.
2. Treat every endpoint as read-only metadata. Do not add file writes, shell
   execution, database mutations, or secret/config values to responses.
3. Update `MCP_FEATURES`, this page, and `docs/ai/latest_features.md` together
   whenever an endpoint or public capability changes.
4. Keep paths rooted at the current monorepo layout: `core/libs/`,
   `applications/kilo/`, and `docs/ai/`.
5. Run `core/libs/ceptor-ai` metadata tests after changes.

## Troubleshooting

- **`ModuleNotFoundError: ceptor_ai`:** run from the repository root and set
  `PYTHONPATH=core/libs/ceptor-ai/src`, or install the editable package.
- **`Error loading ASGI app`:** install the MCP extra and confirm the target is
  `ceptor_ai.mcp_server:app`, not the old `.kilo` or `mcp_server:app` path.
- **Connection refused:** start uvicorn first and confirm port `8002` is free.
- **Optional package unavailable:** this is expected for integrations that are
  not installed; `/health`, `/info`, `/features`, and `/file-structure` should
  still work.
- **Kilo sees stale data:** restart the local MCP process and re-run `/features`.
