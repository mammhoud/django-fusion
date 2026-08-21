---
title: Project awareness and computation guide
description: How to locate, run, validate, extend, and document the Structa Cloud monorepo.
navigation:
  title: Project awareness
  icon: i-lucide-compass
object:
  type: "guide"
  id: "guide.project-awareness"
attributes:
  source_path: "guides/00-project-awareness.md"
  canonical_route: "/docs/en/guides/00-project-awareness"
  source_of_truth: "repository-markdown"
  audience: "engineers, operators, and coding agents"
  status: "maintained"
  owner: "workspace"
tags:
  - structa-cloud
  - onboarding
  - architecture
  - commands
  - docus
  - project-awareness
links:
  - label: "Architecture reference"
    to: "/docs/en/architecture"
    icon: "i-lucide-landmark"
  - label: "Canonical project structure"
    to: "/docs/en/project-structure"
    icon: "i-lucide-folder-tree"
  - label: "Documentation build"
    to: "/docs/en/guides/09-docus"
    icon: "i-lucide-book-open"
---

# Project awareness and computation guide

<!-- AI-generated: review needed -->

This is the shortest reliable route from “I need to change something” to “I
know which product owns it, how it runs, and how to verify it.” Structa Cloud
is a monorepo, but the products are isolated applications. Start by identifying
the owner; do not infer ownership from a stale historical path.

## 1. Read the repository as a graph

The repository is organized as linked objects rather than one flat application:

```text
workspace
├── projects/                 product objects and shared project configuration
│   ├── precis/               Precis LMS, Precis Landing, CTC Research
│   ├── formints/             POS editions and shared POS tests
│   ├── syntara/              AI chat/customizer runtime
│   └── loop-crm/             CRM and social scheduling monolith
├── libs/django-fusion/       shared framework object (git submodule)
├── application/             infrastructure and proxy objects
├── tests/                    cross-project verification object
└── docs/                     canonical documentation source + Docus app
```

Each object has attributes that must agree across code and documentation:

| Object | Important attributes | Canonical links |
|---|---|---|
| Product | filesystem path, runtime/site identity, stack, owner, port/domain | product `README.md`, nearest `AGENTS.md`, `projects/Makefile` |
| Backend | settings module, URL root, database, media/static roots, worker | product `backend/`, Compose file, environment guide |
| Frontend | package manager, API origin, build target, static/public assets | product `frontend/`, `package.json`, project guide |
| Shared library | submodule commit, public imports, tests, consuming products | `libs/django-fusion/AGENTS.md`, library docs |
| Infrastructure service | Compose service, network, router, health path, volume | `application/`, routing guide, deployment runbook |
| Document | source path, Docus route, owner, status, tags, links | this Markdown tree; generated Docus content is not authored |

The Docus build adds these attributes to generated English documents as
frontmatter: `object`, `attributes`, `tags`, and `links`. The authoritative
content remains the Markdown file under `docs/`; `docs/content/` is an
ignored build product and must never become a second authoring tree.

## 2. First commands: orient before editing

Run these read-only commands from the repository root:

```bash
pwd
find . -name AGENTS.md -print
git status --short --untracked-files=all
cd projects && make show-config WEBSITE=precis-ctc
```

Then read, in order:

1. `AGENTS.md` at the repository root;
2. `projects/AGENTS.md`;
3. the nearest product `AGENTS.md`;
4. the product README and Makefile;
5. the relevant docs page and current callers/tests.

The current canonical product identities are:

| Runtime identity | Canonical path | Compatibility aliases |
|---|---|---|
| `precis-main` | `projects/precis/precis-main/` | `precis-lms`, `precis-landing` dispatcher aliases where documented |
| `precis-landing` | `projects/precis/precis-landing/` | legacy Precis Landing runtime copy |
| `precis-ctc` | `projects/precis/precis-ctc/` | `ctc`, `ctc-website`, `ctc-research.com` |
| `syntara` | `projects/syntara/` | `cypercloud` runtime alias where required |
| Formint editions | `projects/formints/<edition>/` | historical Formint/POS names only as documented aliases |

## 3. The computation path

For a web request, compute the owner and route before changing code:

```text
browser / Astro / HTMX / API client
        ↓ Host + path
Traefik or local server
        ↓ router/service
Django ASGI/WSGI or Astro server
        ↓ middleware
URL resolver
        ↓
Wagtail page | django-fusion component | API | HTMX fragment
        ↓
model/service/query + template or JSON serializer
        ↓
HTML | fragment | JSON | stream
```

For a background operation:

```text
request or scheduler
        ↓
Django service / task actor
        ↓
Redis broker (production) or in-process backend (development/tests)
        ↓
Dramatiq worker
        ↓
PostgreSQL record, email, media operation, or cache update
```

For a frontend build:

```text
source Astro/TypeScript + CSS
        ↓
package-local check and build
        ↓
static output / server bundle
        ↓
Compose image or host-mounted static root
        ↓
Traefik + Nginx/static proxy
```

## 4. Canonical commands

### Workspace and documentation

```bash
# From the repository root
uv sync
uv run pytest

# Docus source validation and generation
cd docs
make check
make -C docus prepare-content
make build             # Nuxt/Docus server build
make build-static      # optional static export
make serve             # local server at /docs/
```

`make -C docs check` is the safe first documentation gate. `make -C docs clean`
removes generated Docus output only; it does not remove source Markdown.

### Project dispatcher

```bash
cd projects
make show-config WEBSITE=precis-main
make check WEBSITE=precis-main
make test WEBSITE=precis-main
make run-dev WEBSITE=precis-ctc
make check WEBSITE=precis-ctc
make test WEBSITE=precis-ctc
```

Use the dispatcher for site selection because it owns compatibility aliases and
maps runtime identities to current filesystem paths.

### Precis CTC

```bash
cd projects/precis/precis-ctc
make check
make test
make validate-config
make build

cd backend
python manage.py check
python manage.py test
python manage.py prepare_ctc_media --dry-run
```

Do not run migrations, fixture loads, `load_data --replace`, or deployment
commands against shared/production data without explicit approval.

### Precis frontends and POS projects

```bash
cd projects/precis/precis-main/backend && make check && make test
cd projects/precis/precis-landing && make check && make backend-test
cd projects/formints/formint-pro && make check && make test
cd projects/formints/formint-cloud && make check && make test
cd projects/formints/formint-community && npm run check && npm test
cd projects/formints/formint-client && npm run lint
cd libs/django-fusion && uv run pytest
```

Always confirm the local project package manager before installing or running a
script. Do not copy a command from a historical document if the current
project Makefile or `package.json` disagrees.

## 5. How to extend the graph safely

### New backend behavior

1. Find the owning app boundary: `models`, `services`, `handlers`, `api`,
   `components`, or `management`.
2. Search for existing routes, callers, serializers, and tests.
3. Keep URL orchestration thin; put business rules in a service/manager.
4. Use canonical `django_fusion.*` imports and stable fragment names.
5. Update the product API/architecture doc and add a focused test.

### New frontend behavior

1. Confirm whether the page is Astro, React/Vue, or a native Tauri surface.
2. Preserve the render-first/data-API/HTMX contract that the product already
   exposes.
3. Keep source assets separate from generated bundles and collected static files.
4. Run the package `check`, targeted test, and build when practical.
5. Link the feature to its backend endpoint and product documentation.

### New infrastructure behavior

1. Identify the Compose service, network, volume, health check, and router.
2. Update the owning `application/` config, routing guide, and deployment
   runbook together.
3. Validate Compose/YAML without bringing down or recreating shared services.
4. Treat volume pruning, production migration, certificate operations, and
   deploys as effectful actions requiring explicit user direction.

## 6. Documentation as an Affine-style knowledge graph

Use Markdown as the single source and Docus as the presentation/index layer.
Every new document should describe:

```yaml
object:
  type: guide | architecture | runbook | api | decision | reference
  id: stable.document.identifier
attributes:
  source_of_truth: repository-markdown
  owner: product-or-team
  status: maintained | proposed | deprecated
  audience: reader description
tags:
  - architecture
  - product-or-system
links:
  - label: Related document
    to: "/docs/en/path/to/document"
    icon: "i-lucide-link"
```

These are document objects and attributes, not a second database. Use stable
IDs when a document is referenced by plans, agents, or Docus links. Prefer links
to duplicating explanations. A page can link to its source code, owner project,
architecture decision, commands, tests, and deployment/runbook neighbors.

The generator in `docs/scripts/prepare-content.mjs` adds the shared graph
metadata to legacy Markdown that lacks it. If a document already owns an
`object` block, that source metadata is preserved. This allows gradual
normalization without rewriting every historical page in one risky change.

## 7. Docus source and deployment model

```text
docs/**/*.md or *.mdx       canonical authored content
        ↓ prepare-content.mjs
 docs/content/en/           ignored generated English tree + metadata
 docs/ar-content/           authored Arabic source
        ↓ Nuxt/Docus build
 .output/server/index.mjs  SSR documentation service
        ↓ shared-proxy + Traefik
 docs.structa.cloud/       root-host documentation
 media.structa.cloud/docs/ prefixed documentation host
```

Do not edit `docs/content/`, `.nuxt/`, `.output/`, `dist/`, or
`node_modules/`. If generated content is wrong, fix the source Markdown or the
preparation script. The root `docs/index.html` is only a compatibility redirect;
it is not a second documentation application.

## 8. Working with an agent

Give an agent the object graph coordinates, not only a feature sentence:

```text
Owner: projects/precis/precis-ctc/
Surface: backend API + Astro frontend
Contract: /apis/content/media/ and /fragment/pages/<slug>/
Data: Wagtail dump + shared media root
Docs: docs/precis-ctc/ and docs/guides/00-project-awareness.md
Checks: cd projects/precis/precis-ctc/frontend && npm run check
Safety: do not load/replace shared fixtures or deploy without approval
```

This reduces stale-path edits, keeps project boundaries intact, and makes the
validation command explicit before implementation begins.

## Remarks & Notes

- The repository root `AGENTS.md` is the safety authority; this guide is an orientation layer, not a replacement for scoped instructions.
- `docs/` Markdown is canonical. Docus generated content is intentionally ignored and disposable; deleting it is safe, authoring in it is not.
- “Compute on it” means trace the object through its request/build/task pipeline, then run the narrowest owner-specific check before broad workspace validation.
- Product paths and aliases are synchronized from the current repository map; verify `projects/Makefile` if a path appears inconsistent.
- Human review is recommended for architecture, operations, medical, legal, and public product documentation before publication.
