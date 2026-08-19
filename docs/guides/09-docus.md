---
title: Docus implementation guide
description: How Structa Cloud documentation is authored, enriched, validated, built, and deployed.
navigation:
  title: Docus implementation
  icon: i-lucide-book-marked
object:
  type: "guide"
  id: "guide.docus"
attributes:
  source_path: "guides/09-docus.md"
  canonical_route: "/docs/en/guides/09-docus"
  source_of_truth: "repository-markdown"
  owner: "documentation"
  status: "maintained"
tags:
  - structa-cloud
  - documentation
  - docus
  - nuxt
  - deployment
links:
  - label: "Project awareness"
    to: "/docs/en/guides/00-project-awareness"
    icon: "i-lucide-compass"
  - label: "Documentation home"
    to: "/docs/en/"
    icon: "i-lucide-house"
---

# Docus implementation guide

<!-- AI-generated: review needed -->

This guide is the canonical operational reference for the Docus application.
The authored pages live under `docs/**/*.md` and `docs/**/*.mdx`; the Docus
application at `docs/docus/` generates and serves them. Do not create a second
published copy inside `docs/docus/content/`.

## Source and generated boundaries

```text
docs/**/*.md or *.mdx
        │ authored source
        ▼
docs/docus/scripts/prepare-content.mjs
        │ adds metadata and copies Arabic sources
        ▼
docs/docus/content/en/ and docs/docus/content/ar/
        │ ignored generated content
        ▼
Nuxt/Docus SSR server
        │
shared-proxy + Traefik
        ├── /docs/ on the shared documentation host
        └── docs.structa.cloud/
```

`docs/docus/content/`, `.nuxt/`, `.output/`, `dist/`, and `node_modules/` are
build products. If their content is wrong, fix the authored Markdown or the
preparation script. The root `docs/index.html` is only a compatibility redirect.

## Document object metadata

New authored pages should use this frontmatter shape:

```yaml
object:
  type: guide | architecture | runbook | api | decision | reference
  id: stable.document.identifier
attributes:
  source_path: guides/example.md
  canonical_route: /docs/en/guides/example
  source_of_truth: repository-markdown
  owner: product-or-team
  status: maintained | proposed | deprecated
tags:
  - architecture
  - product-or-system
links:
  - label: Related document
    to: /docs/en/guides/00-project-awareness
    icon: i-lucide-link
```

`links` follows Docus' header-link contract: use `label`, `to`, `icon`, and an
optional `target`. The preparation script adds equivalent metadata to legacy
pages without frontmatter. Existing source frontmatter remains authoritative,
so a page with an `object` block is copied without a duplicate metadata block.

## Local commands

From the repository root:

```bash
cd docs
make check
make -C docus prepare-content
make -C docus validate-content
make build
make build-static
make serve
make preview
```

Or from the Docus application directory:

```bash
cd docs/docus
npm install
npm run prepare-content
npm run validate-content
npm run dev
npm run build
npm run build:static
npm run preview
```

Use `make check` before a build. It validates the Nuxt configuration, locale
sources, generated document metadata, and Docus-native links. A production build
is an SSR server build; static export is optional and may be slower because it
renders every requested route.

## Local routes and locales

- English: `http://localhost:3000/docs/en/`
- Arabic RTL: `http://localhost:3000/docs/ar/`
- Root compatibility redirect: `docs/index.html`

The application uses `NUXT_APP_BASE_URL=/docs/` so links remain correct when
shared-proxy serves the site below `/docs/`. The root-host deployment preserves
the same generated route contract behind its proxy configuration.

## Deployment contract

```text
Dockerfile: docs/Dockerfile
Application: docs/docus/
Container: docus:3000
Proxy: applications/proxy/configs/traefik/dynamic/docs.yml
Nginx: applications/proxy/configs/nginx/default.conf.template
```

The image copies the full `docs/` tree because the preparation script walks the
sibling authored Markdown tree. It then runs `npm run build` and starts
`.output/server/index.mjs`. Validate the Docker/Compose configuration without
recreating shared services; deployment commands require explicit approval.

## Linking and deduplication rules

1. Add or edit the canonical Markdown page under `docs/`.
2. Add frontmatter metadata and a final `## Remarks & Notes` section.
3. Link to an existing page or source path instead of repeating its content.
4. Run `make -C docs check` to regenerate the ignored presentation tree.
5. Never commit or manually edit generated Docus content.

## Remarks & Notes

- The Docus app README at `docs/docus/README.md` is an application-maintainer note; this page is the published documentation guide.
- Docus route slugs are lowercase even when a source filename uses uppercase characters such as `ARCHITECTURE.md`.
- A successful documentation build validates the documentation service, not the health of product backends or production proxy routes.
- Human review is recommended before publishing architecture, operations, medical, legal, or public product documentation.
