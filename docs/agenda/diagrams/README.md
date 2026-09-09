---
title: Agenda Diagrams — Rendered Assets & Sources
description: All agenda diagrams — rendered SVG images plus their mermaid sources — API request flows, Django model ERDs, Rust/SQLite relations, and Blinko SurrealDB
navigation:
  title: Diagrams
  icon: i-lucide-git-branch
object:
  type: "index"
  id: "agenda.diagrams"
attributes:
  source_path: "agenda/diagrams/README.md"
  canonical_route: "/docs/en/agenda/diagrams"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "active"
tags:
  - structa-cloud
  - diagrams
  - agenda
  - api
  - erd
links:
  - label: "Agenda home"
    to: "/agenda/main"
    icon: "i-lucide-clipboard-list"
  - label: "Case studies index"
    to: "/agenda/case-studies/index"
    icon: "i-lucide-book-open"
---

# 📊 Agenda Diagrams — Rendered Assets & Sources

> **Purpose:** One home for every diagram used by the agenda system. Each diagram
> exists in two forms: a **rendered image** (SVG, viewable anywhere — GitHub,
> Docus, Anytype import) and its **mermaid source** (editable, versioned).
> **Status:** Active · **Owner:** Workspace

---

## Diagram assets

Rendered images live in `docs/public/agenda/diagrams/` and are served at
`/agenda/diagrams/<name>.svg`. The mermaid sources below are canonical — edit
the source, re-render, and replace the image.

| Diagram | Rendered image | Mermaid source | Covers |
|---------|---------------|----------------|--------|
| Loop-CRM API request flows | [![API flows](/agenda/diagrams/diagrams-api-request-flows-1.svg)](/agenda/diagrams/diagrams-api-request-flows-1.svg) | [api-request-flows.md](./api-request-flows.md) | Request/response sequences with auth + tenant headers |
| Django model ERD — Loop-CRM | [![Loop-CRM ERD](/agenda/diagrams/diagrams-django-loop-crm-er-1.svg)](/agenda/diagrams/diagrams-django-loop-crm-er-1.svg) | [django-loop-crm-er.md](./django-loop-crm-er.md) | Workspace, CRM, finance, POS, billing, attribution, marketing |
| Rust SQLite ERD — Formint Community | [![Rust SQLite ERD](/agenda/diagrams/diagrams-rust-sqlite-er-1.svg)](/agenda/diagrams/diagrams-rust-sqlite-er-1.svg) | [rust-sqlite-er.md](./rust-sqlite-er.md) | Diesel schema with relations + module map |
| Blinko SurrealDB | [![Blinko SurrealDB](/agenda/diagrams/diagrams-blinko-surrealdb-1.svg)](/agenda/diagrams/diagrams-blinko-surrealdb-1.svg) | [blinko-surrealdb.md](./blinko-surrealdb.md) | Blinko notes service topology + SurrealDB data flow |
| Case-study diagrams (existing) | Per case study | Case-study files | POS sync, offline queue, QR menu, ceptor-ai, data-token, stripe, api-token |

---

## How to re-render

```bash
# 1. Edit the mermaid block in the source doc
# 2. Encode and render (mermaid.ink):
code='...mermaid...'
b64=$(printf '%s' "$code" | base64 -w0)
curl -s "https://mermaid.ink/svg/$b64" -o docs/public/agenda/diagrams/<name>.svg
```

Or use the local render script (requires `node` + `curl`):

```bash
node docs/scripts/render-agenda-diagrams.mjs
```

---

## Related

- [Case studies index](../case-studies/INDEX.md) — per-case-study diagrams
- [Feature tracking](../feature-tracking.md) — features these diagrams document
- [Content model](../CONTENT_MODEL.md) — where diagrams live in the package split

<!-- AI-generated: review needed -->