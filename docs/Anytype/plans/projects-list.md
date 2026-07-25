---
# yaml-language-server: $schema=schemas/page.schema.json
Object type:
    - Page
Tags:
    - projects
    - sites
    - reference
Status: Published
---

# Projects — Detailed Site & Application Index

> **Type:** Page 📄
> **Description:** Expanded project references with descriptions, tech stacks, and current status for every active site and application.

---

## Web Applications

### CTC Research — `projects/ctc-research/` → ctc-research.com:5070
Research and training platform with Wagtail-powered content management. Publishes academic research, delivers courses, and provides training materials.

- **Color:** Sky Blue (#0ea5e9) — represents professional research and academic trust
- **Stack:** Django 4.2 + Wagtail 5.x + PostgreSQL
- **Status:** ✅ Complete

### LMS Demo — `projects/lms/` → structa.cloud:5071
Learning Management System demonstration showcasing course creation, enrolment, progress tracking, and student dashboards.

- **Color:** Emerald (#10b981) — represents growth and learning progression
- **Stack:** Django 4.2 + Wagtail 5.x + PostgreSQL
- **Status:** ✅ Complete

### VResume — `projects/portfolio/` → vresume.structa.cloud:5072
Professional portfolio and resume builder with customizable templates, AI-assisted content, and PDF export.

- **Color:** Violet (#8b5cf6) — represents creative expression and professional identity
- **Stack:** Django 4.2 + Wagtail 5.x + PostgreSQL
- **Status:** ✅ Complete

### CyperCloud — `projects/cypercloud/` → localhost:5073
AI Chat Customizer platform — customize AI chat behavior, manage prompts, configure models, brand the interface.

- **Color:** Cyan (#06b6d4) — represents AI intelligence and cloud technology
- **Stack:** Django 4.2 + ceptor-ai + PostgreSQL
- **Status:** 🚧 In Development

---

## POS Editions

### pos-mini — `projects/pos/pos-mini/`
Lightweight Rust/Tauri desktop app with SQLite. Air-gapped, offline-first design for food trucks, kiosks, and pop-ups.

- **Color:** Rust Red (#f7524a) — represents speed, performance, minimal overhead
- **Stack:** Rust (Tauri) → React (TypeScript) → SQLite
- **Status:** ✅ Complete

### pos-solo — `projects/pos/pos-solo/`
Standalone single-branch POS with Django ORM + Robyn sidecar. LAN sync between branch devices.

- **Color:** Teal (#0d9488) — represents balance between standalone power and connectivity
- **Stack:** Rust (Tauri) → TypeScript (React) → Python (Django + Robyn) → SQLite
- **Status:** 🚧 In Development

### pos-full — `projects/pos/pos-full/`
Enterprise multi-branch POS with cloud sync, CRM integration, and advanced analytics.

- **Color:** Gold (#eab308) — represents premium enterprise value
- **Stack:** Same as solo + PostgreSQL + Cloud API
- **Status:** 📋 Planned

---

## Shared Libraries

### django-fusion — `libs/django-fusion/`
Component-based Django framework providing routing, generic CBVs, routable components, and fragment rendering across all sites.

### ceptor-ai — `libs/ceptor-ai/`
AI integration helpers — content generation, smart customization, text analysis, and personalization across all applications.

---

## Infrastructure

| Component | Path | Purpose |
|-----------|------|---------|
| **Traefik Proxy** | `applications/proxy/` | SSL termination, SNI routing, Let's Encrypt |
| **Nginx Media** | `applications/proxy/Dockerfile` | Static/media file serving |
| **PostgreSQL** | `applications/databases/` | Primary data store (15+) |
| **Redis** | `applications/databases/` | Cache, sessions, task queues |

---

## Related Docs

- → `projects.md` — Project hub
- → `../../architecture/website-descriptions.md` — Full descriptions
- → `../../features/comparison-matrix.md` — Feature comparison
- → `../../README.md` — Master index
