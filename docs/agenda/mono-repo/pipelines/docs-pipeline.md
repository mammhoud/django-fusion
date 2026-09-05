---
Object type: Pipeline
Tags: pipeline, docs, validation, automation
Status: Active
Related Features: documentation-system
Related Releases: docs-pipeline-2026-09
---

# Docs Pipeline — Prepare + Validate + Render

> **Description:** The docs automation chain: prepare content, validate frontmatter + AR parity, and render mermaid diagrams to SVG.

## Method

1. `node docs/scripts/prepare-content.mjs` — build `docs/content/` from authored tree
2. `node docs/scripts/validate-content.mjs` — frontmatter keys + AR mirror check
3. `node docs/scripts/render-agenda-diagrams.mjs` — render mermaid blocks to SVGs under `docs/public/agenda/diagrams/`

## Boundary

- `content/` is generated — never edit it directly
- Diagram SVGs are derived assets; re-render after editing mermaid sources

## Use case

Contributors edit markdown; the pipeline validates and the site renders EN + AR with images.

## Related

- → `github-actions.md` — CI wrapper
- → `../tools/docus-docs.md` — Docs engine
- → `../objects/pipeline.md` — Pipeline object type