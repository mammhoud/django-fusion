# crafts-ai Documentation

`crafts-ai` is vendored as a local monorepo library at `applications/libs/crafts-ai/`.
It is intentionally a pure Python package with no Django imports, so Django projects can
use it for AI, CLI, and MCP integration without introducing framework coupling.

## Import and package layout

- Distribution/package directory: `applications/libs/crafts-ai/`
- Python source root: `applications/libs/crafts-ai/src/`
- Import package: `crafts_ai`
- CLI entry point: `crafts-ai`
- Optional MCP app: `crafts_ai.mcp_server:app`

## Installation

Install the package in editable mode from the repository root:

```bash
uv pip install -e applications/libs/crafts-ai/
```

For optional FastAPI MCP endpoints, install with the `mcp` extra:

```bash
uv pip install -e 'applications/libs/crafts-ai/[mcp]'
```

## Usage

```python
from crafts_ai import package_info

info = package_info()
assert info["import_package"] == "crafts_ai"
```

Run local checks through the module or console script:

```bash
python -m crafts_ai info
python -m crafts_ai health
crafts-ai health
```

## Kilo integration

Kilo exposes a `crafts-ai` MCP server in `.kilo/config.json` and a
`crafts-ai-toolsmith` agent plus `/crafts-ai` command in `.kilo/kilo.jsonc` and
`.kilo/commands/crafts-ai.md`. The MCP app is launched with:

```bash
uvicorn crafts_ai.mcp_server:app --host 127.0.0.1 --port 8002
```

## Boundary rules

`crafts-ai` remains standalone:

- Do not import Django or Wagtail from `crafts_ai`.
- Keep Django adapters in Django apps or in a separate integration layer.
- Use `docs/shared/scripts/check_boundaries.sh` or
  `docs/shared/scripts/libs/check_boundaries.sh` to verify boundaries.
