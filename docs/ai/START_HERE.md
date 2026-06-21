# Structa Cloud AI Start Here

Use this guide as the first stop for AI-assisted work in this repository. It
connects repository-specific agent rules, Kilo Code setup, local AI tooling,
template customization workflow, and optional integration plans.

## 1. Kilo Code setup for this repository

Kilo project configuration lives in the repository-level `.kilo/` directory:

- `.kilo/kilo.jsonc` defines Kilo permissions, indexing, named agents, and slash
  commands.
- `.kilo/config.json` defines MCP servers available to Kilo.
- `.kilo/commands/` stores project slash-command prompts, including component
  and crafts-ai helpers.
- `.kilo/skills/` stores repository skills for deployment verification,
  SCSS/BEM conversion, and Wagtail field customization.

Recommended setup flow:

1. Open the repository root in Kilo Code: `/workspace/structa.cloud`.
2. Confirm Kilo is reading `.kilo/kilo.jsonc` from this repository, not a global
   default.
3. Keep repository indexing enabled. The configured indexing provider is Ollama
   with the `nomic-embed-text:latest` embedding model and Qdrant vector store.
4. Use the project agents that match the task scope:
   - `django-architect` for structure and design decisions.
   - `django-coder` for Django models, views, templates, forms, APIs, and HTMX.
   - `frontend-developer` for HTML/CSS/JavaScript work.
   - `test-engineer` for test coverage.
   - `documentation-writer` for docs.
   - `crafts-ai-toolsmith` for the standalone `crafts-ai` package.
5. Use slash commands when they fit the task, for example `/crafts-ai` and the
   component-finding command in `.kilo/commands/find-component.md`.

Do not replace repository settings with generic Django defaults. This is a
monorepo under `applications/`, and site work should use the canonical site
paths listed in `AGENTS.md`.

## 2. How AI tools should read `AGENTS.md`

AI tools must treat `AGENTS.md` files as scoped repository instructions:

1. Start at the repository root and read `AGENTS.md` before planning changes.
2. Search for more deeply nested `AGENTS.md` files before editing files in a
   subtree. A nested file applies to the directory tree rooted where it appears.
3. Apply the most specific applicable instruction when instructions conflict.
4. Treat direct user instructions and higher-level system/developer instructions
   as higher priority than `AGENTS.md`.
5. For this repository, preserve the actual monorepo layout:
   - shared settings in `applications/configs/`,
   - shared assets and templates in `applications/assets/`,
   - local reusable packages in `applications/libs/`,
   - site code in `applications/ctc-research/`, `applications/lms-demo/`, and
     `applications/VResume/`.
6. Use `rg`, not recursive `grep`, for repository searches.
7. Prefer `applications/Makefile` for site checks and orchestration unless a
   site-level Makefile target is specifically required.

## 3. How to customize templates safely

Template changes should be narrow, traceable, and validated against rendered
pages. Use this workflow before replacing markup.

### Find the page template

1. Identify the site and page route first. Use canonical site names and paths:
   - CTC Research: `applications/ctc-research/`
   - LMS Demo: `applications/lms-demo/`
   - VResume: `applications/VResume/`
2. Search layered template locations in this order:
   - shared templates: `applications/assets/templates/`
   - site root templates: `applications/<site>/templates/`
   - site asset templates: `applications/<site>/assets/templates/`
   - site app templates: `applications/<site>/www/**/templates/`
   - plugin templates: `applications/<site>/plugins/**/templates/`
3. Use targeted commands such as:

   ```bash
   rg -n "template_name|extends|include|block content" applications/<site> applications/assets/templates
   rg -n "class .*Page|template =|serve\(" applications/<site>/www applications/<site>/plugins
   ```

### Find the component include

1. Inspect `{% include %}`, `{% extends %}`, `{% block %}`, and custom template
   tags around the markup being changed.
2. Search for the component's class names, block names, include paths, and
   fragment identifiers.
3. Keep `fragment_name` as the canonical name for fragment identifiers and
   context keys. Do not introduce alternate names such as `fragment`, `name`,
   `fragment_slug`, or `fragment_key` unless preserving existing compatibility.

### Preserve context data

1. Read the view, page model, context processor, template tag, or include caller
   that provides the current context.
2. Keep variable names stable unless the call chain is updated end-to-end.
3. When adding an include, pass only the required context using Django template
   `with` syntax where practical.
4. Avoid moving business logic into templates. Put reusable logic in the
   existing service/module structure or the appropriate local library.

### Replace with a shared component

1. Use `applications/assets/templates/` for cross-site components.
2. Use site-specific template directories only when presentation is unique to one
   site.
3. Preserve accessible names, ARIA attributes, translation tags, and data
   attributes used by JavaScript or tests.
4. Preserve BEM-style class names for reusable components, or introduce new
   BEM-style names that match nearby conventions.
5. Do not use IDs for styling.

### Validate the rendered page

1. Run the narrowest relevant template, Django, or site check first.
2. Prefer delegated Makefile commands from `applications/Makefile`, for example:

   ```bash
   make -C applications check WEBSITE=ctc
   make -C applications check WEBSITE=structa
   make -C applications check WEBSITE=vresume
   ```

3. If a runnable web page changed, render the page locally and inspect it in a
   browser. Take a screenshot when the change is perceptible.
4. Verify that JavaScript selectors, HTMX attributes, analytics hooks, and tests
   still target the expected elements.

## 4. django-osoul MCP setup and configuration

`django-osoul` is documented under `docs/packages/django-osoul/`. In this
repository it is treated as local reusable infrastructure and should stay out of
production application logic unless the existing docs explicitly call for it.

Current Kilo MCP configuration is in `.kilo/config.json`:

- `deployment` MCP server runs `python mcp_server.py` with
  `DJANGO_SETTINGS_MODULE=core.settings`.
- `crafts-ai` MCP server runs `uvicorn crafts_ai.mcp_server:app --host
  127.0.0.1 --port 8002` with `PYTHONPATH=applications/libs/crafts-ai/src`.

There is no separate `django-osoul` MCP server entry in `.kilo/config.json` at the
moment. If one is added later, document it beside the existing MCP entries,
include its command, environment, port, and whether it is safe for local-only or
shared deployments.

Useful references:

- `docs/packages/django-osoul/README.md`
- `docs/packages/django-osoul/usage.md`
- `docs/packages/django-osoul/django-osoul-overview.md`
- `docs/guides/LIBS_INTEGRATION.md`

## 5. `crafts-ai` package usage

The local `crafts-ai` package is available under `applications/libs/crafts-ai/`.
It exposes:

- distribution directory: `applications/libs/crafts-ai/`
- import package: `crafts_ai`
- CLI command: `crafts-ai`
- optional MCP app: `crafts_ai.mcp_server:app`

Install from the repository root:

```bash
uv pip install -e applications/libs/crafts-ai/
```

Install optional MCP dependencies when needed:

```bash
uv pip install -e 'applications/libs/crafts-ai/[mcp]'
```

Run quick checks:

```bash
python -m crafts_ai info
python -m crafts_ai health
crafts-ai health
```

Boundary rule: keep `crafts_ai` standalone and pure Python. Do not import Django
or Wagtail from `crafts_ai`; put Django integration in a site app, adapter, or
explicit service boundary.

## 6. Ollama setup using `docs/ai/setup.md`

Use `docs/ai/setup.md` as the source for local Ollama and Continue setup. The
current flow is:

1. Install Ollama for macOS, Windows, or Ubuntu.
2. Pull the recommended models:

   ```bash
   ollama pull gemma3:4b
   ollama pull llama3.2:1b
   ```

3. Install the Continue extension in VS Code.
4. Configure Continue to use the local Ollama API at `http://localhost:11434`.
5. Keep telemetry disabled for local/private workflows.

Kilo indexing may use a separate Ollama base URL from `.kilo/kilo.jsonc`; verify
that the configured host is intentional for your environment before indexing
private code.

## 7. Prompt/task workflow

Use `docs/ai/tasks.md` as the task catalog and `docs/ai/scripts/task_runner.py`
as the local task runner.

Common commands from the repository's AI workflow:

```bash
make task-list
make task-run NAME=analyze_project
make task-run NAME=comprehensive_analysis SITE=ctc-research
make task-run NAME=uniform_docs VERBOSE=1
```

Direct runner usage:

```bash
python docs/ai/scripts/task_runner.py --list
python docs/ai/scripts/task_runner.py --task analyze_project
python docs/ai/scripts/task_runner.py --task update_docs --interactive
```

When adding a task:

1. Create `docs/ai/tasks/<task_name>.md`.
2. Put the short task summary on the first line.
3. Include explicit scope, search paths, expected output, and validation steps.
4. Run the task in dry-run or analysis-only mode before allowing edits.
5. Record important findings in the relevant docs or issue tracker.

## 8. Optional Rasa NLU integration plan

Rasa is not required for the current local AI workflow. If it is added, keep the
integration explicit and isolated:

1. Place Rasa under a clearly named service or package, for example
   `services/rasa-nlu/`, `applications/libs/rasa-integration/`, or an equivalent
   documented path.
2. Define intents and entities in Rasa training data, and keep action names
   stable. Example intents might include `find_template`, `run_ai_task`,
   `summarize_page_context`, and `request_component_replacement`.
3. Define actions in a dedicated action server or service layer. Actions should
   not directly mutate repository files without an explicit approval workflow.
4. Route actions to Ollama only through explicit service boundaries. For example:
   Rasa action server → `ai_orchestration` service → Ollama client. Do not let
   templates, views, or model methods call Ollama directly.
5. Document privacy requirements before deployment:
   - what user text is collected,
   - whether prompts include source code or CMS content,
   - retention policy for conversations and model traces,
   - who can access logs,
   - whether embeddings or prompts leave the host.
6. Document deployment requirements:
   - service owner and runtime,
   - ports and network boundaries,
   - secrets and environment variables,
   - model host URL,
   - health checks,
   - rollback plan.
7. Keep Rasa optional. Core Django sites should continue to run without the Rasa
   service unless a feature explicitly depends on it and has a graceful fallback.

## 9. Site-specific docs and references

Use these links when work is scoped to a specific site:

- CTC Research:
  - `applications/ctc-research/`
  - `applications/ctc-research/Makefile`
  - `applications/ctc-research/assets/readme.md`
  - `docs/guides/COURSE_SYSTEM_IMPLEMENTATION.md`
  - `docs/guides/COURSES_SYSTEM_ARCHITECTURE.md`
- LMS Demo:
  - `applications/lms-demo/`
  - `applications/lms-demo/Makefile`
  - `docs/guides/MAKEFILE_REFERENCE.md`
  - `docs/guides/SESSION_SUMMARY.md`
- VResume:
  - `applications/VResume/`
  - `applications/VResume/Makefile`
  - `docs/development.md`
  - `docs/user_guide/index.md`
  - `docs/user_guide/portfolio.md`

For cross-site development, also review:

- `docs/architecture-notes.md`
- `docs/guides/MAKEFILE_REFERENCE.md`
- `docs/guides/LIBS_INTEGRATION.md`
- `docs/development/COMPONENT_GUIDE.md`
