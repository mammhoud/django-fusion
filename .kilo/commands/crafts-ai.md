---
description: Work with the local crafts-ai package and MCP endpoints
agent: crafts-ai-toolsmith
---
# crafts-ai Workflow

Use this workflow when adding or validating standalone AI/MCP utilities.

1. Confirm the local package is installed: `uv pip install -e applications/libs/crafts-ai/`.
2. Verify the import package: `python -m crafts_ai info`.
3. Run the health check: `python -m crafts_ai health`.
4. Keep all package code under `applications/libs/crafts-ai/src/crafts_ai`.
5. Do not import Django or Wagtail from `crafts_ai`.
6. If MCP endpoints are needed, run `uvicorn crafts_ai.mcp_server:app --host 127.0.0.1 --port 8002`.
