# crafts-ai

`crafts-ai` is the standalone AI/MCP toolkit vendored into the structa.cloud monorepo.
It exposes the import package `crafts_ai` and the console command `crafts-ai`.

The package is also the migration home for framework-agnostic AI, MCP, prompt,
and orchestration code that used to be planned under `crafts-ai`. Django,
Wagtail, middleware, model, snippet, and queue-dispatch runtime code must remain
in `crafts-ai` until it is extracted behind non-Django adapters.

## Install

```bash
uv pip install -e applications/libs/crafts-ai/
```

## Quick check

```bash
python -m crafts_ai info
crafts-ai health
crafts-ai projects
crafts-ai rseal-plan applications
```

## crafts-ai migration boundary

Use `crafts-ai rseal-plan <root>` before changing website imports. It classifies
`crafts_ai.rseal` imports as one of:

- `move-to-crafts-ai` for framework-agnostic AI, MCP, or orchestrator code.
- `keep-in-crafts-ai` for Django/Wagtail models, blocks, middleware, snippets,
  pipelines, and job dispatchers.
- `needs-review` for import families that do not yet have an explicit rule.

This keeps CTC Research, LMS Demo, and VResume imports stable while the AI parts
are organized under `crafts_ai`.
