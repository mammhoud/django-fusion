---
title: Documentation Authoring Prompt
description: The powerful, repo-tuned prompt for generating Structa Cloud documentation — emoji, remarks & notes, code guides, mermaid diagrams, ERD, preview images, Affine metadata, bilingual EN/AR.
navigation:
  title: Doc authoring prompt ✍️
  icon: i-lucide-pen-tool
object:
  type: "prompt-guide"
  id: "docs.ai.doc-authoring"
attributes:
  source_path: "ai/documentation-authoring.md"
  canonical_route: "/docs/en/ai/documentation-authoring"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "maintained"
tags:
  - structa-cloud
  - ai
  - documentation
  - prompt
  - docus
links:
  - label: "AI & Agents home"
    to: "/docs/en/ai"
    icon: "i-lucide-bot"
  - label: "Docus implementation"
    to: "/docs/en/guides/09-docus"
    icon: "i-lucide-book-marked"
  - label: "Skill: structa-doc-authoring"
    to: "https://github.com/mammhoud/structa.cloud/tree/generic/.agents/skills/structa-doc-authoring"
    icon: "i-lucide-wrench"
    target: "_blank"
---

# ✍️ Documentation Authoring Prompt

> Copy-paste prompt for generating powerful, organized Structa Cloud documentation.
> It enforces the repo conventions: **emoji headers, `## Remarks & Notes`,
> `<!-- AI-generated: review needed -->`, language-hinted code guides, mermaid
> diagrams + ERD, preview-image pointers, Affine graph metadata, and EN/AR
> parity.**

<!-- AI-generated: review needed -->

## The Prompt

```text
You are the Structa Cloud documentation author. Write or rewrite documentation
for the repository at docs/ (authoritative Markdown) that is published through
the Docus pipeline (docs/). Follow these rules strictly:

1. STYLE — Affine-grade, engaging technical writing:
   - Use emoji in H1/H2 headers and navigation titles (🎓 🏥 🤝 🤖 💳 🧩 🚀 📚).
   - Every document ends with a "## Remarks & Notes" section with operational
     caveats.
   - Add "<!-- AI-generated: review needed -->" for any AI-written content.
   - Lead with the most useful information; show, don't tell.

2. STRUCTURE — always include, when applicable:
   - "## Where & How It's Used" (for shared libraries) with a per-project table.
   - "## Architecture" with a mermaid diagram (graph LR / graph TB).
   - "## Data Model / ERD" with a mermaid erDiagram for database-heavy topics.
   - "## Quick Start" code guide with language-hinted blocks (bash, python,
     django, yaml, nginx, astro) using real repo paths and make commands.
   - "## Preview" section pointing to real preview images under
     docs/assets/previews/ or docs/assets/screenshots/ when they exist.

3. METADATA — every page carries Docus/Affine frontmatter:
   title, description, navigation (title + icon), object (type + id),
   attributes (source_path, canonical_route, owner, status), tags, links.
   Never use "href" in links — use Docus "to".

4. PATHS — always use canonical paths + compatibility aliases (root AGENTS.md):
   precis-main (aliases precis-lms/precis-landing), syntara (legacy cypercloud),
   libs/django-fusion at the repo root, formints editions. No stale paths.

5. BILINGUAL — when a page is user-facing, also provide an Arabic translation
   under docs/ar-content/<same-route>.md (RTL, natural Arabic, same
   structure, "Remarks & Notes" translated as "ملاحظات وإرشادات").

6. DEDUP — never create a second copy of existing content: search docs/ first,
   link instead of duplicating, and prefer editing existing files.

7. VALIDATE — after writing, run:  cd docs && npm run prepare-content &&
   npm run validate-content   (and fix any frontmatter failures).
```

## What Makes Output Powerful

| Element | Why it matters | Rule |
|---------|----------------|------|
| 🎯 Emoji headers | Scanability in Docus nav & TOC | 1 per major section, not decorative spam |
| 📋 Remarks & Notes | Captures the operational truth docs usually miss | Mandatory closing section |
| 🧭 Mermaid diagrams | Architecture at a glance | One diagram per architecture-heavy page |
| 🗄️ ERD (mermaid) | Data model clarity | For models/schema pages |
| ⌨️ Code guides | Real commands that work | Language hints + canonical paths |
| 🖼️ Previews | Proof over prose | Link real `docs/assets/previews/` images |
| 🏷️ Graph metadata | Affine object linking + Docus LLM output | Frontmatter on every page |
| 🌐 EN/AR parity | Bilingual product reach | Same-route `ar-content/` mirror |

## Usage

- **Human:** paste into any coding agent when requesting docs work.
- **Agent:** this prompt is encoded as the `structa-doc-authoring` skill
  (`.agents/skills/structa-doc-authoring/SKILL.md`) — load it by name instead
  of pasting.
- **Catalog:** see [`skills-catalog.md`](skills-catalog.md) for all skills.

## Remarks & Notes

- The Docus pipeline auto-adds graph metadata to legacy pages, but authoring it
  explicitly is always better — see [Docus guide](../guides/09-docus.md).
- Generated files under `docs/content/` are disposable; never edit them.
- Preview images live in `docs/assets/previews/`; if a referenced image is
  missing, say so instead of inventing a path.
