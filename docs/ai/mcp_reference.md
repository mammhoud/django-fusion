# MCP Reference for Structa Cloud AI Tools

This reference documents the current local MCP-facing files and endpoints used
by AI tooling in Structa Cloud.

## crafts-ai MCP app

- Import path: `crafts_ai.mcp_server:app`
- Source file: `applications/libs/crafts-ai/src/crafts_ai/mcp_server.py`
- Optional dependency: `fastapi` via `applications/libs/crafts-ai/[mcp]`
- Recommended local command:

```bash
PYTHONPATH=applications/libs/crafts-ai/src \
  uvicorn crafts_ai.mcp_server:app --host 127.0.0.1 --port 8002
```

## Available endpoints

- `GET /health` returns readiness metadata.
- `GET /info` returns package metadata from the shared CLI metadata function.
- `GET /features` returns the latest feature inventory plus canonical files.
- `GET /file-structure` returns the package/docs/Kilo path map only.

## Documentation attachments for agents

When an AI client asks for the latest repository feature files, attach or cite
these files together:

1. `docs/ai/START_HERE.md`
2. `docs/ai/latest_features.md`
3. `docs/ai/mcp_reference.md`
4. `applications/libs/crafts-ai/docs/agents.md`
5. `applications/libs/crafts-ai/src/crafts_ai/mcp_server.py`

## Safety boundaries

The MCP metadata module must remain safe to import without Django settings. Do
not add Django, Wagtail, Celery, database, or website imports to
`crafts_ai.mcp_server`. Keep optional runtime integrations behind
`importlib.util.find_spec` and `importlib.import_module`.
