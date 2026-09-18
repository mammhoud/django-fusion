# Syntara / Cypercloud — AI Agent Instructions

**Path:** `projects/syntara/`  
**Compatibility name:** Cypercloud  
**Stack:** Django + HTMX + Webpack/SCSS + Monaco-style code editing + local AI/Ceptor integration

Read the root and `projects/AGENTS.md` before working here. New filesystem
references should use `projects/syntara/`; preserve `cypercloud` only in
runtime aliases, URLs, environment names, and external documentation where it
is part of the contract.

## Layout

```text
syntara/
├── chat/
│   ├── models.py             # Conversation/message persistence
│   ├── views.py              # Chat and template-discovery views
│   ├── views_stream.py       # SSE/streaming response endpoints
│   ├── services.py           # Conversation and AI business logic
│   ├── site_data.py          # Configured-site/template discovery
│   ├── customizer.py         # Template catalog/customization helpers
│   ├── ceptor.py             # Ceptor/provider integration boundary
│   ├── forms.py, constants.py, exceptions.py
│   └── migrations/
├── templates/
│   ├── base.html             # Site shell
│   ├── chat.html             # Main chat UI
│   ├── components/           # Chat/editor/navigation components
│   └── fragments/            # HTMX response fragments
├── assets/
│   ├── static/               # Source JS/CSS and generated bundles
│   └── webpack.config.js
├── configs/                  # YAML model/provider settings
├── settings.py               # Django settings and site catalog
├── urls.py                   # Chat, API, fragments, streaming routes
├── server.py                 # Container/server entry point
├── docker-compose.yml
├── Dockerfile
└── Makefile
```

The template catalog is intentionally a bridge into other products. It may
inspect templates from Precis, Precis Landing, and legacy site paths, but it
must not mutate those products implicitly. Generated suggestions should be
reviewable and written only through explicit user actions.

## Request and streaming contracts

- Standard HTML pages and HTMX fragments are rendered from `templates/`.
- Chat completion endpoints may return normal JSON or Server-Sent Events.
- Provider-specific behavior belongs behind `chat/ceptor.py`/`services.py`, not
  in templates or URL wiring.
- Keep conversation persistence and streaming failure behavior testable without
  requiring a live external AI provider.
- Treat Ollama/OpenAI/Anthropic credentials and model configuration as runtime
  environment/config values. Never hard-code secrets or provider tokens.

Important surfaces include:

| Surface | Typical purpose |
|---|---|
| `/` | Chat home and recent conversations |
| `/chat/<id>/` | Conversation view and message submission |
| `/chat/<id>/stream/` | Streaming AI response |
| `/api/websites/` and `/api/pages/...` | Template discovery |
| `/fragments/...` | HTMX navigation/cards/sidebar fragments |
| `/api/ceptor/...` | Provider/MCP health, config, and completion surfaces |

Confirm exact paths in `urls.py` before adding endpoints.

## Template and frontend rules

- Keep AI-generated content dynamic; do not replace model/template data with
  placeholder markup.
- Use `{% comp %}` where a registered django-fusion component exists.
- Use `fragment_name` for HTMX fragment identifiers and context keys.
- Preserve editor-safe escaping and markdown/code rendering boundaries.
- Keep SCSS BEM-style and edit source files under `assets/static/styles/`; run
  the Webpack build rather than editing generated bundle output.
- A template discovery change must be checked against the configured catalog and
  path permissions; do not broaden filesystem scanning casually.

## Commands

Use the product's Makefile and README as the authority; the historical command
names below are representative:

```bash
cd projects/syntara
python manage.py check
python manage.py migrate
make runserver
make build
make build-collect
make test
```

For a container validation without starting it, use:

```bash
docker compose -f projects/syntara/docker-compose.yml config -q
```

## Tests

Update tests for:

- Conversation/message model changes
- JSON and SSE response shapes
- Template discovery and path filtering
- HTMX fragment rendering
- Provider fallback/error handling

Prefer Django test clients and deterministic provider stubs over live AI calls.
