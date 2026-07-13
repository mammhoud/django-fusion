# Latest AI, MCP, and package feature inventory

This is the compact attachment for repository-aware AI agents. Keep it aligned
with `core/libs/ceptor-ai/src/ceptor_ai/mcp_server.py`,
`applications/kilo/config.json`, and `docs/ai/mcp_reference.md`.

## Current MCP endpoints

| Endpoint | Purpose | Mutation risk |
|---|---|---|
| `/health` | Readiness check for local clients | Read-only |
| `/info` | `ceptor-ai` package metadata | Read-only |
| `/features` | Feature inventory and canonical paths | Read-only |
| `/file-structure` | Package, docs, and Kilo path map | Read-only |
| `/auth/features` | Detect optional auth integrations | Read-only; no secrets |
| `/django-fusion/info` | Optional package metadata | Read-only |
| `/django-fusion/components` | Component registry summary | Read-only |
| `/django-fusion/viewsets` | Viewset availability | Read-only |
| `/websites/endpoints` | Configured site endpoint map | Read-only |
| `/ssl/status` | Certificate presence and expiry summary | Read-only; no private keys |
| `/proxy/status` | Proxy configuration presence | Read-only |

## Local setup

```bash
# Run from the repository root.
uv pip install -e core/libs/ceptor-ai/
uv pip install -e 'core/libs/ceptor-ai/[mcp]'
PYTHONPATH=core/libs/ceptor-ai/src \
  uvicorn ceptor_ai.mcp_server:app --host 127.0.0.1 --port 8002
```

Kilo uses the same app and environment in `applications/kilo/config.json`.
Keep the server bound to loopback for local development. A shared deployment
requires authentication, an explicit owner, and documented network controls.

## Agent operating contract

Before using MCP, an agent should:

1. Read root and nested `AGENTS.md` instructions.
2. Call `/health`, then `/features` and `/file-structure`.
3. Use canonical paths returned by the server instead of guessed legacy paths.
4. Ask for approval before editing files or changing MCP configuration.
5. Never send API keys, cookies, private keys, or full environment files to MCP.
6. Treat all current endpoints as metadata-only; do not infer write capability.

Suggested setup prompt:

> Set up the local Structa Cloud `ceptor-ai` MCP server. Read the root
> `AGENTS.md`, the applicable library instructions, `docs/ai/mcp_reference.md`,
> and this feature inventory. Install the editable package with the `mcp` extra;
> start `ceptor_ai.mcp_server:app` on `127.0.0.1:8002` with
> `PYTHONPATH=core/libs/ceptor-ai/src`; verify `/health`, `/features`, and
> `/file-structure`; then report results. Do not expose the port, reveal
> secrets, mutate files, or add Django/Wagtail imports to `ceptor_ai`.

## Canonical attachment set

```text
docs/ai/
├── README.md
├── START_HERE.md
├── latest_features.md
├── mcp_reference.md
├── customizer.md
├── setup.md
└── tasks/

applications/kilo/
├── config.json
├── kilo.jsonc
├── commands/ceptor-ai.md
└── skills/

core/libs/ceptor-ai/
├── AGENTS.md
├── PROMPTS.md
├── QUICKSTART.md
├── README.md
└── src/ceptor_ai/
    ├── cli.py
    └── mcp_server.py

core/libs/django-fusion/
├── AGENTS.md
├── PROMPTS.md
├── README.md
└── docs/
```

## Maintenance checklist

- Update `MCP_FEATURES` and this file together when the public endpoint inventory
  changes.
- Update the setup prompt and Kilo command when the launch command, port, or
  environment changes.
- Keep `ceptor_ai` importable without Django settings; optional integrations
  must remain behind `find_spec`/`import_module`.
- Run `cd core/libs/ceptor-ai && uv run pytest tests/test_mcp_metadata.py` after
  MCP metadata changes.
