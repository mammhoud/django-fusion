# Structa Cloud prompt catalog

The repository now has a canonical, machine-readable prompt catalog:

```text
application/agents/prompts/catalog.json
```

It turns the existing `.agents/skills`, `application/agents/agent/*.json`, and
project `AGENTS.md` guidance into reusable prompts that an AI agent can load,
combine, and execute as a planning or coding workflow.

## What is included

| Group | Meaning | Catalog prefix |
|---|---|---|
| Skill prompts | Reusable task instructions mapped to specialist agents and skills | `skill.` |
| Project prompts | Complete project descriptions, boundaries, agent sequences, and checks | `project.` |
| Workflows | Multi-agent orchestration recipes | `workflow.` |

Every skill/project prompt includes:

- a stable ID, title, and complete description;
- the primary agent and supporting agents;
- related installed skills;
- expected inputs and outputs;
- an explicit safety contract;
- project paths and validation commands where applicable.

## Prompt composition

A prompt is assembled from four layers, in this order:

1. **Repository rules:** root `AGENTS.md`, then all nearer `AGENTS.md` files;
2. **Project pack:** the `project.*` description for the owning product;
3. **Skill pack:** one or more `skill.*` task prompts;
4. **Task context:** the user's request, exact files, constraints, and desired output.

Example composition for a Landing-Fusion Wagtail block:

```text
project.precis-landing
+ skill.wagtail-content-model
+ skill.django-fusion-component
+ user task: add a featured-course block to the home page
```

The agent must read the actual files named by the project instructions before
editing. Catalog text is guidance, not a substitute for source inspection.

## Available project packs

### Landing-Fusion
Astro 5 + Tailwind 4 + HTMX/Alpine frontend paired with Django 5.2/Wagtail 7.4.
The prompt preserves both the Astro/data-API road and Django/Fusion/HTMX road,
with project-owned content, assets, translations, SEO, and route ordering.

### Precis
Django 5.2/Wagtail 7.4 learning platform with an Astro shell. The prompt keeps
course discovery, detail, syllabus, enrollment, wishlist, progress,
certificates, auth, localization, API, and fragment contracts synchronized.

### Formint
A separated family of Community, Standard, Professional, Cloud, and Client
editions. The prompt requires the edition to be named first, prevents Python
sidecars in native editions, prevents Robyn reintroduction into Cloud, and
preserves typed API/sync/transaction contracts.

### Syntara
Django + HTMX + SSE + Webpack/SCSS AI chat/customizer. The prompt uses
`projects/syntara/` as canonical, keeps providers behind the chat boundary, and
makes template discovery reviewable and path-limited.

### django-fusion
Reusable Python/Django/Wagtail framework behavior. The prompt prevents product
branding, models, credentials, deployment behavior, and arbitrary MCP execution
from leaking into the shared library.

## Available skill packs

The initial catalog includes prompts for:

- website redesign and accessibility audit;
- django-fusion components and `{% comp %}` usage;
- Wagtail fields and StreamField blocks;
- safe read-only MCP tools and prompt workflows;
- template/static/logo/preloader health;
- Dramatiq background-job architecture and staged migration.

The installed full skill documents remain the detailed source material under
`.agents/skills/` and `application/agents/skills/`. The catalog provides a
stable task-oriented entry point and agent mapping; it does not replace those
skill files.

## Agent mapping

The catalog uses the role definitions in `application/agents/agent/`:

- `django-architect` — boundaries, services, schemas, workers;
- `django-coder` — Django/Wagtail/templates/forms/APIs;
- `frontend-developer` — Astro/React/Vue/TypeScript/CSS/accessibility;
- `template-tinker` — template discovery and customization;
- `ceptor-ai-toolsmith` — standalone AI/MCP boundaries;
- `security-auditor` — threat modeling and security review;
- `test-engineer` — unit, contract, integration, and browser validation;
- `code-reviewer` — final quality and compatibility review;
- `product-manager` — user journeys, acceptance criteria, prioritization;
- `devops-engineer` — CI, Compose, infrastructure, and operations;
- `documentation-writer` — maintainable technical documentation.

The prompt catalog does not change agent permissions. Existing permissions in
`application/agents/agent/*.json` and `kilo.jsonc` remain authoritative.

## MCP access

The lightweight Kilo service exposes repository-specific, read-only REST catalog endpoints (these are not standard MCP `prompts/list` or `prompts/get` methods):

```bash
curl http://127.0.0.1:8100/prompts
curl http://127.0.0.1:8100/prompts/project.precis-landing
curl http://127.0.0.1:8100/prompts/skill.website-redesign-audit
```

The list response contains concise metadata. The detail response contains the
complete prompt definition. Prompt IDs are path-safe stable identifiers, and
unknown IDs return a structured 404.

The MCP service does **not**:

- execute a prompt;
- interpolate user-controlled values;
- call an LLM provider;
- read arbitrary source files;
- write files or run shell commands;
- run migrations, purge queues, or deploy services.

A coding assistant may use the returned prompt as context, then follow its own
approved edit/test workflow. Any future mutation endpoint must be separate,
short-lived, authenticated, diff-based, auditable, and reversible.

## Adding or changing a prompt

1. Choose the correct stable prefix and ID.
2. Read the owning `AGENTS.md` and relevant project README/Makefile.
3. Include complete description, agent mapping, inputs, expected output, and
   safety boundaries.
4. Update `catalog.json` and this documentation when the public workflow changes.
5. Run the prompt catalog contract tests.
6. Review for stale paths, secrets, deployment claims, and contradictory rules.

Validation:

```bash
cd /home/structa.cloud
uv run pytest application/agents/test_prompts.py -q
python3 -m json.tool application/agents/prompts/catalog.json >/dev/null
```

## Related references

- [`docs/ai/prompts.md`](prompts.md) — human prompt library and skill inventory;
- [`docs/ai/agents.md`](agents.md) — AGENTS hierarchy and role inventory;
- [`docs/ai/mcp-integration.md`](mcp-integration.md) — MCP architecture;
- [`application/agents/AGENTS.md`](../../application/agents/AGENTS.md) — Kilo rules;
- [`libs/django-fusion/docs/WEBSITE_MCP.md`](../../libs/django-fusion/docs/WEBSITE_MCP.md) — website audit MCP tools.
