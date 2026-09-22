---
name: structa-doc-authoring
description: "Structa Cloud documentation authoring — the powerful, repo-tuned writing skill for docs/ (Docus pipeline). Enforces emoji headers, ## Remarks & Notes, AI-generated review markers, language-hinted code guides, mermaid architecture diagrams, mermaid ERDs, real preview-image pointers, Affine graph frontmatter (object/attributes/tags/links), canonical paths + aliases, and EN/AR parity via docs/docus/ar-content. Use for any documentation work in this monorepo: new pages, rewrites, package guides, startup/strategy docs, product docs, and bilingual translations. Companion to the structa-docs conventions skill."
tags: [documentation, docs, docus, mermaid, bilingual, arabic, structa-cloud]
argument-hint: "<what to document and which product>"
---

# Structa Doc Authoring — Powerful Documentation Skill

## 1. Skill Meta

**Name:** structa-doc-authoring
**Triggers:** "write docs for", "document X", "rewrite this doc", "add diagrams", "translate to Arabic", "enhance the documentation", "create a package guide".
**Companion skills:** `structa-docs` (conventions + doc types) · `content-production` (marketing/SEO content) · `documentation-writer` (Diátaxis structure).

## 2. The Non-Negotiables

Every generated document **must** include:

1. **🎯 Emoji headers** — H1 + H2 with an emoji (🎓 🏥 🤝 🤖 💳 🧩 🚀 📚 ⚙️ 🔒 …). One per major section; never decorative spam.
2. **`## Remarks & Notes`** — mandatory closing section with operational caveats ("watch out for X", "tested with Y", "middleware order matters").
3. **`<!-- AI-generated: review needed -->`** — marker on AI-written content.
4. **Language-hinted code blocks** — `bash`, `python`, `django`, `yaml`, `nginx`, `astro`, `typescript`. Use **real repo paths and make commands** (`cd projects && make check WEBSITE=precis-main`), never invented ones.
5. **Diagrams** — one mermaid diagram per architecture-heavy page:
   - `graph LR` / `graph TB` for architecture and "where used" maps.
   - `erDiagram` for models/schema pages.
6. **Preview pointers** — reference real images under `docs/assets/previews/` or `docs/assets/screenshots/` when they exist; never invent paths.
7. **Affine/Docus frontmatter** — every page:
   ```yaml
   ---
   title: ...
   description: ...
   navigation:
     title: ...
     icon: i-lucide-<name>
   object:
     type: "guide" | "reference" | "product" | "private-strategy" | "package-guide"
     id: "docs.<route>"
   attributes:
     source_path: "<path>"
     canonical_route: "/docs/en/<route>"
     source_of_truth: "repository-markdown"
     owner: "<product>"
     status: "maintained"
   tags:
     - structa-cloud
     - <section>
   links:
     - label: "Documentation home"
       to: "/docs/en/"
       icon: "i-lucide-house"
   ---
   ```
   Use Docus `to` for links — never `href`.

## 3. Canonical Paths & Aliases (never stale)

| Entity | Canonical | Aliases (internal only) |
|--------|-----------|--------------------------|
| Precis | `projects/structa.cloud/` · `docs/precis/` | `precis-lms`, `precis-landing`, Precis Landing |
| CTC | `projects/precis/precis-ctc/` · `docs/precis-ctc/` | `ctc`, `ctc-research.com` |
| Loop-CRM | `projects/loop-crm/` · `docs/loop-crm/` | `crm` |
| Syntara | `projects/syntara/` · `docs/syntara/` | `cypercloud` (legacy) |
| Formint POS | `projects/formints/` · `docs/pos/` | `pos`, edition names |
| django-fusion | `libs/django-fusion/` (repo root) · `docs/libs/` | — |
| Infra | `application/` · `docs/dev/infrastructure/` | `services/` (legacy) |

## 4. Where Things Live

- **How-to guides** → `docs/guides/` (numbered 00–09, subfolders like `auth/`)
- **Product docs** → `docs/<product>/` (precis, precis-ctc, loop-crm, syntara, pos)
- **Library docs** → `docs/libs/` (django-fusion.md + package docs at `libs/django-fusion/docs/DF-0NN`)
- **Strategy (private)** → `docs/startup/` 🔒 (MVP canvas, TAM/SAM/SOM, ideal clients)
- **Plans & ADRs** → `docs/plans/` (legacy archive under `docs/plans/legacy-archive/`)
- **AI/agents** → `docs/ai/`
- **Arabic** → `docs/docus/ar-content/<same-route>.md`

## 5. Bilingual Rule (EN/AR)

For user-facing pages, also write the Arabic mirror at
`docs/docus/ar-content/<route>.md`: natural RTL Arabic, same H2 structure,
`## Remarks & Notes` → `## ملاحظات وإرشادات`, same frontmatter minus the
generated graph block. Link to `/docs/en/<route>` for the full English source.

## 6. Workflow

1. **Search first** — `rg` docs/ for existing coverage; link, don't duplicate.
2. **Plan the structure** — outline H2s before writing prose.
3. **Write** with the non-negotiables above.
4. **Consolidate** — if the page duplicates another, merge and delete the loser.
5. **Validate**:
   ```bash
   cd docs/docus && npm run prepare-content && npm run validate-content
   ```
   Fix any frontmatter failures.
6. **Review the diff** for stale paths, secrets, and scope leakage.

## 7. Quality Gates

- [ ] Frontmatter present with `object/attributes/tags/links` (no `href`).
- [ ] `## Remarks & Notes` at the end.
- [ ] `<!-- AI-generated: review needed -->` on AI sections.
- [ ] Mermaid diagram(s) for architecture/data pages.
- [ ] Real paths + make commands (no invented paths).
- [ ] Preview image links exist under `docs/assets/previews|screenshots/`.
- [ ] Arabic mirror added for user-facing pages.
- [ ] `npm run validate-content` passes.
- [ ] No secrets, no duplicated content, canonical paths used.
