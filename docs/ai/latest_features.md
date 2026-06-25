# Latest AI, MCP, and crafts-ai Feature Inventory

This file is the current attachment-style summary for AI agents working in this
repository. Keep it aligned with `crafts_ai.mcp_server` so local MCP clients and
human documentation describe the same capabilities.

## Current MCP endpoints

| Endpoint | Purpose |
| --- | --- |
| `/health` | Readiness check for Kilo/MCP clients. |
| `/info` | Package metadata shared with the `crafts-ai` CLI. |
| `/features` | Full AI/MCP feature inventory and canonical file structure. |
| `/file-structure` | Compact package, docs, and Kilo path map. |

## Agent-facing features

- **Repository-aware Kilo setup**: `.kilo/config.json`, `.kilo/kilo.jsonc`,
  `.kilo/commands/`, and `.kilo/skills/` define the local agent entrypoints.
- **crafts-ai MCP bridge**: `applications/libs/crafts-ai/src/crafts_ai/mcp_server.py`
  exposes metadata that can be read by local MCP clients without importing
  Django, Wagtail, Celery, or site modules.
- **AI customizer docs**: `docs/ai/START_HERE.md`, `docs/ai/customizer.md`, and
  `applications/libs/crafts-ai/docs/agents.md` describe safe template/component
  discovery and BEM conversion workflows.
- **Monorepo structure awareness**: agents must treat `applications/` as the
  application root and use the canonical site paths from `AGENTS.md`.

## Canonical file structure for latest AI docs

```text
docs/ai/
├── README.md
├── START_HERE.md
├── latest_features.md
├── mcp_reference.md
├── customizer.md
├── setup.md
├── config.md
├── troubleshooting.md
└── tasks/

applications/libs/crafts-ai/
├── AGENTS.md
├── docs/agents.md
├── pyproject.toml
└── src/crafts_ai/
    ├── cli.py
    ├── customizer/
    └── mcp_server.py
```

## Maintenance checklist

1. Update `crafts_ai.mcp_server.MCP_FEATURES` when an endpoint or MCP-facing
   capability changes.
2. Update this file and `docs/ai/mcp_reference.md` in the same change.
3. Keep `crafts_ai` framework-agnostic; use `importlib.util.find_spec` and
   `importlib.import_module` for optional dependencies.
4. Run the lightweight crafts-ai metadata tests after changes.
