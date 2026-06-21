# crafts-ai

`crafts-ai` is the standalone AI/MCP toolkit vendored into the structa.cloud
monorepo. It exposes the import package `crafts_ai` and the console command
`crafts-ai`.

The legacy reference checkout has been retired: the former
`crafts-ai` package content and the former `django-rseal` runtime package now
live directly in this package.

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

## Merged namespaces

- Framework-agnostic AI, MCP, chat, seeding, and orchestration helpers should be
  organized under `crafts_ai`.
- The legacy `django_rseal` top-level import path is still packaged from
  `applications/libs/crafts-ai/src/django_rseal/` so existing Django/Wagtail
  runtime imports remain available while they are adapted into stable
  `crafts_ai` APIs.
- The `crafts_ai.rseal` migration inventory records which import families can be
  moved immediately and which Django/Wagtail families require adapter work first.
- Do not restore the legacy reference checkout; add AI/MCP work and migrated rseal
  runtime support here instead.

## Local checks

```bash
python -m compileall -q applications/libs/crafts-ai/src
python -m pytest applications/libs/crafts-ai/tests
```
