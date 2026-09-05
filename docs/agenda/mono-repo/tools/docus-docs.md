---
Object type: Tool
Tags: tool, docus, docs, nuxt, documentation
Status: Active
Category: Operations
Related Features: documentation-system
Related Plans: project-workspace
---

# Docus — Docs Engine

> **Description:** The Nuxt-based Docus engine powering the docs site (`docs/`) — markdown-first content with graph metadata, EN/AR parity, and LLM-ready output.

## Method

- `docs/scripts/prepare-content.mjs` copies authored markdown into `docs/content/en/` with graph metadata
- `docs/scripts/validate-content.mjs` checks frontmatter (object/attributes/tags/links) + AR mirror parity
- Rendered diagram SVGs served from `docs/public/agenda/diagrams/`
- Deployment: Nuxt server; prerender crawling disabled (repo-sized tree)

## Boundary

- The authored tree IS the docs root (flattened from `docs/docus/`)
- Keep source files in `docs/` — `content/` is generated output

## Use case

Team authors markdown; the pipeline validates it, generates graph metadata, and the site serves EN + AR with LLM-ready output at `docs.structa.cloud`.

## Related

- → `../documentation/_index.md` — Documentation objects
- → `../../../guides/09-docus.md` — Docus pipeline guide
- → `../objects/tool.md` — Tool object type