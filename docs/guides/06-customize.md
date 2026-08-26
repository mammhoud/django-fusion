---
title: Customize
description: What you can safely customize across all Structa Cloud projects — tag system, overrides, extensions, config, templates.
navigation:
  title: Customize
  icon: i-lucide-palette
object:
  type: "guide"
  id: "guide.customize"
attributes:
  source_path: "guides/06-customize.md"
  canonical_route: "/docs/en/guides/06-customize"
  source_of_truth: "repository-markdown"
  audience: "engineers, operators, and coding agents"
  status: "maintained"
  owner: "workspace"
tags:
  - structa-cloud
  - onboarding
  - customize
  - override
  - extend
  - config
  - templates
links:
  - label: "Deploy"
    to: "/guides/05-deploy"
    icon: "i-lucide-rocket"
  - label: "Clone Site"
    to: "/guides/07-clone-site"
    icon: "i-lucide-package"
  - label: "Customization Methods"
    to: "/dev/customization/customization-methods"
    icon: "i-lucide-wrench"
---

# 🎨 Customize — Customization Guide

> **Related:** All platform docs — see per-platform customization sections
> **Tags:** #customization #override #extend #config #templates

What you can safely customize across all Structa Cloud projects, and what you shouldn't touch.

---

## Customization Tag System

Every customizable element across the platform carries a tag indicating its safety level:

| Tag | Meaning | Examples |
|-----|---------|----------|
| 🟢 **Safe** | Change freely, no upgrade risk | SCSS variables, template overrides, config values, i18n strings |
| 🟡 **Extend** | Add via hooks/extension points | Django signals, Tauri commands, API clients, sidecar endpoints |
| 🔵 **Template** | Override template files | `templates/` overrides, component templates, email templates |
| ⚪ **Config** | Environment/config only | Feature flags, env vars, settings.yaml, `.env` |
| 🔴 **Core** | Do not modify — fork if needed | Framework internals, migration logic, security code, DB schema core |

> 💡 **Tip:** The tag appears in doc headers, code comments, and PR checklists. If it's not tagged, assume 🔴.

---

## Decision Matrix

| Layer | What to do | Tag |
|-------|------------|-----|
| **SCSS/CSS** | Override variables in `assets/scss/_custom.scss` | 🟢 |
| **Django Templates** | Override in `templates/` (fusion respects load order) | 🟢 |
| **Django Settings** | Use `configs/` cascade + env overrides | ⚪ |
| **Django Models** | Extend via `AbstractBase` or signals | 🟡 |
| **React/Tauri Components** | Wrap or extend, don't modify core | 🟡 |
| **Rust Operations** | Add new operations, don't change signatures | 🟡 |
| **Sidecar APIs** | Add endpoints in `server.py` | 🟡 |
| **Database Migrations** | Never edit generated — add new migration | 🔴 |
| **django-fusion Core** | Use `{% comp %}`, fragments, routing APIs | 🔴 |
| **Tauri Core** | Config only via `tauri.conf.json` | 🔴 |

---

## Per-Project Customization Points

### Precis (Django + Astro)
- **Templates:** `templates/` overrides Wagtail blocks, fusion fragments
- **CSS:** `assets/scss/_custom.scss` → compiled to `fusion.css`
- **Config:** `configs/*.yml` + `Env/` overrides
- **Astro:** Override pages in `frontend/src/pages/`, components in `src/components/`

### POS (Tauri + React + Rust)
- **UI:** Override components in `src/components/`, styles in `src/styles/`
- **Config:** `tauri.conf.json`, `capabilities/`, env vars
- **Rust:** Add operations in `src-tauri/src/operations/`
- **Sidecar:** Add endpoints in `sidecar/server.py`

### Syntara (Django + HTMX)
- **Templates:** `templates/` + fusion fragments
- **CSS:** Same fusion CSS pipeline
- **Config:** `configs/` cascade

### Loop-CRM (Django + Astro)
- Similar to Precis pattern

---

## Adding a New Customization Point

1. **Identify the layer** (CSS, template, config, code, core)
2. **Tag it** in code comments: `// 🟢 Safe: override via X`
3. **Document it** in the project's customization section
4. **Test** that upstream updates don't break it

---

## Common Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Edit `libs/django-fusion/` directly | Extend via `{% comp %}` or fragments |
| Modify generated `schema.rs` | Add new migration |
| Hardcode env values in code | Use `configs/` cascade + env |
| Fork `django-fusion` for small changes | Use fragments/components/hooks |

---

## ## Remarks & Notes

- The tag system is enforced in code review — untagged changes default to 🔴.
- Per-project customization guides live in each project's docs (e.g., `precis/`, `pos/`).
- Upstream updates (`git submodule update --remote libs/django-fusion`) should never break 🟢/🟡 changes.
- When in doubt, open a PR discussion — customization boundaries evolve.

---

→ [Back to Guides](README.md) | [Deploy](05-deploy.md) | [Clone Site](07-clone-site.md) | [Customization Methods](/docs/en/dev/customization/customization-methods)

<!-- AI-generated: review needed -->