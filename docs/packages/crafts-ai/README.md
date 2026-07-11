# ceptor-ai Documentation

`ceptor-ai` is vendored as a local monorepo library at `core/libs/ceptor-ai/`.
It is intentionally a pure Python package with no Django imports, so Django projects can
use it for AI, CLI, and MCP integration without introducing framework coupling.

## Import and package layout

- Distribution/package directory: `core/libs/ceptor-ai/`
- Python source root: `core/libs/ceptor-ai/src/`
- Import package: `ceptor_ai`
- CLI entry point: `ceptor-ai`
- Optional MCP app: `ceptor_ai.mcp_server:app`

## Installation

Install the package in editable mode from the repository root:

```bash
uv pip install -e core/libs/ceptor-ai/
```

For optional FastAPI MCP endpoints, install with the `mcp` extra:

```bash
uv pip install -e 'core/libs/ceptor-ai/[mcp]'
```

## Usage

```python
from ceptor_ai import package_info

info = package_info()
assert info["import_package"] == "ceptor_ai"
```

Run local checks through the module or console script:

```bash
python -m ceptor_ai info
python -m ceptor_ai health
ceptor-ai health
```

## Kilo integration

Kilo exposes a `ceptor-ai` MCP server in `.kilo/config.json` and a
`ceptor-ai-toolsmith` agent plus `/ceptor-ai` command in `.kilo/kilo.jsonc` and
`.kilo/commands/ceptor-ai.md`. The MCP app is launched with:

```bash
uvicorn ceptor_ai.mcp_server:app --host 127.0.0.1 --port 8002
```

## Boundary rules

`ceptor-ai` remains standalone:

- Do not import Django or Wagtail from `ceptor_ai`.
- Keep Django adapters in Django apps or in a separate integration layer.
- Use `docs/shared/scripts/check_boundaries.sh` or
  `docs/shared/scripts/libs/check_boundaries.sh` to verify boundaries.
