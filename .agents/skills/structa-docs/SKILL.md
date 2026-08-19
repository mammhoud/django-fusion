---
name: structa-docs
description: "Structa Cloud documentation conventions — the monorepo-personalized documentation skill. Use for any documentation work in this repo: writing or updating docs/ pages, ADRs, runbooks, API specs, product guides, and the docs/ai/ agent-integration docs. Encodes the repo's actual docs layout, ADR format, Remarks & Notes rule, AI-generated review markers, and the requirement to keep documentation paths synchronized with the real tree and Makefile aliases."
argument-hint: "<what to document and which product>"
---

# Structa Docs — Documentation Conventions for Structa Cloud

## 1. Skill Meta

**Name:** Structa Docs
**Description:** The repo's canonical documentation standards. Documentation is
a first-class deliverable here: every architecture decision, route change, or
feature must be reflected in `docs/`. This skill encodes the repo's actual
layout, format rules, and sync obligations so docs stay truthful.

## 2. The docs/ Landscape (real layout)

```text
docs/
├── ARCHITECTURE.md            # high-level monorepo architecture
├── README.md / _sidebar.md    # MkDocs site entry + sidebar
├── ai/                        # agent integration docs (mcp-integration.md, prompts, agents.md)
├── assets/  auth/  design/  dev/  features/  guides/
├── plans/                     # ADR-style decisions, migration plans, case studies
├── precis/  landing-fusion/   # product docs (backend-api.md, deployment.md, frontend.md)
├── formints/  pos/  cypercloud/  libs/  shared/
├── project-structure.md  overview.md  recent-changes.md  recommendations.md
└── changelogs/
```

Before writing: **scan `docs/` first** — the answer may already exist (link to
it instead of duplicating). Check `docs/_sidebar.md` when adding a page to the
MkDocs site.

## 3. Document Types (repo-flavored)

### ADR / Decision (`docs/plans/` or `docs/decisions/`)
- Every ADR needs a **date** and a **status**: `Proposed` / `Accepted` / `Superseded`.
- Structure: Context → Options considered → Decision → Consequences → `## Remarks & Notes`.
- Reference the actual file paths and Makefile aliases involved (canonical path + compatibility alias).

### Architecture Doc
- Follow `docs/ARCHITECTURE.md` style: context/goals, diagrams, key decisions and trade-offs, data flow and integration points.
- Cite local paths (`projects/precis/precis-main/backend/`, `libs/django-fusion/`) — the repo map in the root `AGENTS.md` is the source of truth.

### Runbook (`docs/operations/playbooks/` if created, or `docs/guides/`)
- When to use → prerequisites/access → step-by-step → rollback → escalation.
- Include the actual commands from the Makefile dispatcher (`cd projects && make check WEBSITE=precis-main`, `make run-dev WEBSITE=precis-landing`, etc.).

### API Docs (per product, e.g. `docs/landing-fusion/backend-api.md`)
- Endpoint reference with request/response examples, auth, error codes, rate limits, pagination.
- Document the render-first/data-API contract where it exists (server-rendered HTML vs HTMX fragment vs JSON for Astro) — preserve explicit endpoint contracts and headers.

### Product Guide (e.g. `docs/landing-fusion/frontend.md`)
- Setup, key systems and how they connect, common tasks with walkthroughs, who to ask for what.

## 4. Format Rules (mandatory)

1. **`## Remarks & Notes` at the end of EVERY generated document.** Put operational caveats here: "Watch out for X", "This config was tested with Y; later versions may deprecate Z", "Middleware order matters".
2. **`<!-- AI-generated: review needed -->`** marker on AI-written sections that need human verification.
3. **Code blocks with language hints** for all snippets (`yaml`, `python`, `astro`, `nginx`, `bash`).
4. **Link, don't duplicate.** Reference other docs instead of copying content; keep `docs/_sidebar.md` in sync.
5. **Keep docs paths synchronized with the real tree and Makefile aliases.** If a product is renamed or migrated, document BOTH the canonical path and the compatibility alias (e.g. `precis/precis-main` canonical vs `WEBSITE=precis-main` alias). Do not document stale legacy paths as current.
6. **No secrets.** Never print tokens, passwords, or full `.env` files — use `.env.example` names without values.

## 5. Writing Principles

1. **Write for the reader** — who is reading this and what do they need?
2. **Start with the most useful information** — don't bury the lede.
3. **Show, don't tell** — code examples, commands, configs.
4. **Keep it current** — outdated docs are worse than no docs; when you change code, update the doc in the same change.
5. **Precise path hygiene** — always name the owning product and canonical path (per root `AGENTS.md` ownership rules).

## 6. Sync Obligations

When you change code in this repo, also update docs that reference it:
- A route/handler change → product `frontend.md` / `backend-api.md` and the site's Traefik dynamic file comment header (`application/proxy/configs/traefik/dynamic/<site>.yml` documents routes).
- A new field/model → `docs/backend/api-models.md` or the product API doc.
- A new pattern/architecture decision → ADR in `docs/plans/` (date + status + Remarks).
- An MCP/agent capability → `docs/ai/mcp-integration.md` (Kilo server lives in `application/agents/`).
- A proxy/scaling change → `docs/nginx/traefik-routing-rules.md` (mirror `application/proxy/configs/traefik/dynamic/*.yml`) per the container-arch-scaling skill.

## 7. Pre-Flight Checklist

1. Scanned `docs/` and `docs/_sidebar.md` for existing coverage? (Link, don't duplicate.)
2. Picked the right doc type and location (product doc vs ADR vs runbook)?
3. Included `## Remarks & Notes`?
4. Added `<!-- AI-generated: review needed -->` where applicable?
5. Used language-hinted code blocks and real commands/paths?
6. Documented canonical path + compatibility alias for any renamed entity?
7. No secrets, no stale paths, docs tree + Makefile aliases in sync?
