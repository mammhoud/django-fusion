# Libraries and packages

This section documents third-party dependencies used by the sites. The two
maintained internal libraries are documented separately under
[`docs/packages/`](../packages/README.md) and live at `core/libs/`.

## Third-party references

- [django-allauth](django-allauth.md) — authentication, social login, and email verification
- [Hypothesis](hypothesis.md) — property-based testing
- [HTMX](htmx.md) — progressive enhancement and fragment requests

## Internal package map

| Package | Location | Use when | Boundary |
|---|---|---|---|
| `django-fusion` | `core/libs/django-fusion/` | Django/Wagtail components, routing, forms, viewsets, health checks | Django-aware shared foundation |
| `ceptor-ai` | `core/libs/ceptor-ai/` | AI helpers, orchestration, CLI, and optional MCP metadata | Standalone Python surface; no Django/Wagtail imports |

Install either package in editable mode from the repository root:

```bash
uv pip install -e core/libs/django-fusion/
uv pip install -e core/libs/ceptor-ai/
```

For local MCP setup, add the optional extra and follow
[`docs/ai/mcp_reference.md`](../ai/mcp_reference.md):

```bash
uv pip install -e 'core/libs/ceptor-ai/[mcp]'
```

Do not use the historical `venv/libs/` paths in new documentation or prompts.
For package-specific APIs, use the package README and nested `AGENTS.md` as the
source of truth.
