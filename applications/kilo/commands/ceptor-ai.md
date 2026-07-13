---
description: Set up, inspect, or safely extend the local ceptor-ai MCP package
agent: ceptor-ai-toolsmith
---
# ceptor-ai and MCP workflow

Use this workflow for standalone AI utilities, package documentation, or the
local MCP metadata service. Keep the task reproducible and stop before making
unapproved edits.

## Required context

Read these files before planning:

- `AGENTS.md` and any nested `AGENTS.md` for the target path
- `docs/ai/START_HERE.md`
- `docs/ai/mcp_reference.md`
- `docs/ai/latest_features.md`
- `core/libs/ceptor-ai/README.md`
- `core/libs/ceptor-ai/PROMPTS.md`

Confirm that the repository uses `core/libs/`, not legacy `libs/`,
`venv/libs/`, or `.kilo` package paths.

## Package checks

Run from the repository root:

```bash
uv pip install -e core/libs/ceptor-ai/
python -m ceptor_ai info
python -m ceptor_ai health
```

For MCP work, install the optional extra and use the canonical ASGI target:

```bash
uv pip install -e 'core/libs/ceptor-ai/[mcp]'
PYTHONPATH=core/libs/ceptor-ai/src \
  uvicorn ceptor_ai.mcp_server:app --host 127.0.0.1 --port 8002
```

In a second terminal, verify:

```bash
curl --fail http://127.0.0.1:8002/health
curl --fail http://127.0.0.1:8002/info
curl --fail http://127.0.0.1:8002/features
curl --fail http://127.0.0.1:8002/file-structure
```

## Safety and boundary rules

1. Keep `ceptor_ai` importable without Django settings.
2. Do not import Django, Wagtail, Celery, database models, or site modules into
   `core/libs/ceptor-ai/src/ceptor_ai/mcp_server.py`.
3. Bind local MCP servers to `127.0.0.1`; never change to `0.0.0.0` without an
   explicit deployment review and authentication plan.
4. Treat current MCP endpoints as read-only metadata. Do not add shell
   execution, file writes, mutations, or secrets to responses.
5. Use `importlib.util.find_spec` and `importlib.import_module` for optional
   integrations such as `django-fusion` and allauth.
6. If a change affects an endpoint or package public surface, update
   `MCP_FEATURES`, `docs/ai/mcp_reference.md`, `docs/ai/latest_features.md`, and
   the relevant library prompt entry together.

## Expected task response

Before editing, report:

- the files and package boundary involved,
- the current MCP command and endpoint being changed,
- whether the change is local-only or deployment-facing,
- the narrowest validation command.

After editing, report the exact files changed, test output, endpoint smoke-test
results, and any follow-up documentation required. Never claim MCP setup is
complete without a successful `/health` response.
