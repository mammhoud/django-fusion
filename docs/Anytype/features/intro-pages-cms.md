---
# yaml-language-server: $schema=schemas/workspace.schema.json
Object type:
    - Workspace
Backlinks:
    - LMS
Tags:
    - cms
    - lms
    - pages
Status: Published
---

# Intro Pages (CMS) — Landing & Welcome Pages

> **Type:** Workspace 🏢
> **Platform:** LMS Demo site (structa.cloud) — introductory content pages for the learning management system.

---

## Overview

Intro Pages form the welcoming face of the LMS Demo site. They include:
- **Home page** — Hero section, featured courses, call-to-action
- **About page** — Platform mission, team, and value proposition
- **Contact page** — Inquiry form, location, support channels
- **FAQ page** — Frequently asked questions and answers
- **Terms & Privacy** — Legal pages managed through Wagtail

---

## Project Context

| Aspect | Description |
|--------|-------------|
| **Repopath** | `projects/lms/` |
| **Site** | structa.cloud (port 5071) |
| **Color** | Emerald (#10b981) / Teal (#14b8a6) — representing learning growth and education |
| **CMS Engine** | Wagtail Page models with django-fusion components |
| **Templates** | Shared from `projects/assets/templates/` |

---

## Color Palette: LMS Emerald

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#10b981` (Emerald-500) | CTA buttons, course cards, progress bars |
| Surface | `#ecfdf5` / `#064e3b` | Page backgrounds (light/dark) |
| Accent | `#14b8a6` (Teal-500) | Links, section headers, badges |
| Highlight | `#34d399` (Emerald-400) | Success states, completion markers |

---

## Wagtail Content Models

| Page Type | Template | Purpose |
|-----------|----------|---------|
| `HomePage` | `pages/home.html` | Hero, features grid, course previews |
| `AboutPage` | `pages/about.html` | Mission, team, platform story |
| `ContactPage` | `pages/contact.html` | Contact form, map, hours |
| `FaqPage` | `pages/faq.html` | Accordion FAQ, search |
| `PrivacyPage` | `pages/privacy.html` | Legal content, data policy |

---

## Related Docs

- → `../../architecture/website-descriptions.md` — LMS site details
- → `../../references/database-schema.md` — Content models schema
- → `../tasks/quizes.md` — LMS quiz features
- → `../guides/setup.md` — Quick start
- → `../README.md` — Master index
