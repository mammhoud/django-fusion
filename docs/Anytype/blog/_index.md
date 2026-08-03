---
Object type: Workspace
Tags: blog---

# Blog — Articles, Tutorials & Announcements

> Published content from the Structa Cloud team — tutorials, case studies, product updates, and technical deep-dives.

---

## Blog Post Index

| Date | Title | Author | Category | Edition |
|------|-------|--------|----------|---------|
| 2026-07-24 | POS Theme System Launch | mammhoud | Announcement | pos-solo, pos-full |
| 2026-07-20 | Building a Multi-Branch POS with Django | mammhoud | Technical | pos-full |
| 2026-07-15 | Wagtail CMS for Multi-Site Django | mammhoud | Tutorial | ctc-research, lms |
| 2026-07-10 | Tauri v2 Desktop Apps with React | mammhoud | Technical | pos-mini, pos-solo |
| 2026-07-05 | From Monolith to Modular Django | mammhoud | Case Study | all |

---

## Sample Blog Posts

### POS Theme System Launch

> **Excerpt:** Five production-ready themes for the POS desktop app — Default, Corporate, Luxury, Pastel, and Perplexity.

- **Published:** 2026-07-24
- **Author:** → `people/mammhoud.md`
- **Category:** Announcement
- **Tags:** `#pos-solo` `#pos-full` `#theme-default` `#theme-corporate` `#theme-luxury` `#theme-pastel` `#theme-perplexity`

The POS suite now ships with five theme variants, each supporting light and dark mode. The theme system uses CSS custom properties that map to Tailwind v4 tokens, making it easy to create new variants or customize existing ones.

**Key highlights:**
- 5 theme variants with light/dark support
- CSS variable overrides for Tailwind v4 tokens
- Runtime switching via Settings → Appearance
- RTL support for Arabic and Hebrew layouts

**Related Docs:**
- → `features/pos-theme-system.md` — Theme feature details
- → `guides/theming.md` — Theme customization guide
- → `architecture/theme-system.md` — Architecture deep-dive
- → `editions/pos-solo.md` — POS Solo edition

---

### Building a Multi-Branch POS with Django

> **Excerpt:** How we built a cloud-synced POS system for restaurant chains using Django, Robyn sidecar, and SQLite.

- **Published:** 2026-07-20
- **Author:** → `people/mammhoud.md`
- **Category:** Technical
- **Tags:** `#pos-full` `#django` `#backend` `#sync`

The POS Full edition handles multi-branch restaurant operations with a unique architecture: each terminal runs a local SQLite database for offline reliability, while a Django + Robyn sidecar handles cloud synchronization across branches.

**Related Docs:**
- → `architecture/sync-architecture.md` — Sync architecture
- → `features/pos-full-cloud.md` — Cloud sync feature
- → `api/sync-endpoints.md` — Sync API
- → `decisions/002-sqlite-over-postgres.md` — SQLite ADR

---

### Wagtail CMS for Multi-Site Django

> **Excerpt:** Using Wagtail to power multiple branded websites from a single Django deployment.

- **Published:** 2026-07-15
- **Author:** → `people/mammhoud.md`
- **Category:** Tutorial
- **Tags:** `#wagtail` `#cms` `#ctc-research` `#lms`

Wagtail's page-based CMS model makes it natural to power multiple branded websites from one Django codebase. Each site gets its own page tree, media library, and theme — all sharing the same models, views, and authentication system.

**Related Docs:**
- → `architecture/multi-site-cms.md` — Multi-site architecture
- → `guides/setup.md` — Setup guide
- → `features/intro-pages-cms.md` — CMS pages feature

---

## Related

- → `_index.md` — Blog directory overview
- → `../people/mammhoud.md` — Author profile
- → `../objects/blog-post.md` — Blog/Post object type definition
