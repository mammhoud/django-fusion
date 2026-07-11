---
description: Work with the local ceptor-ai package and MCP endpoints
agent: ceptor-ai-toolsmith
---
# ceptor-ai Workflow

Use this workflow when adding or validating standalone AI/MCP utilities.

1. Confirm the local package is installed: `uv pip install -e core/libs/ceptor-ai/`.
2. Verify the import package: `python -m ceptor_ai info`.
3. Run the health check: `python -m ceptor_ai health`.
4. Keep all package code under `core/libs/ceptor-ai/src/ceptor_ai`.
5. Do not import Django or Wagtail from `ceptor_ai`.
6. If MCP endpoints are needed, run `PYTHONPATH=core/libs/ceptor-ai/src uvicorn mcp_server:app --app-dir .kilo --host 127.0.0.1 --port 8002`.
