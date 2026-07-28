# Shared Templates — AI Agent Instructions

Path: `projects/assets/templates/`

## Scope

This directory contains **shared Django/Wagtail templates** used across all Structa Cloud sites (LMS, Portfolio, Cypercloud, Fusion CMS). Templates here are cross-site; site-specific overrides live in each site's own `templates/` directory.

---

## Documentation Index

- **[components/AGENTS.md](components/AGENTS.md)** — Shared component inventory (chat, cookies, forms, modals, pagination, tables, search, breadcrumbs, navigation) with templates, context variables, and usage
- **[plugins/AGENTS.md](plugins/AGENTS.md)** — Plugin template guidance (emails, errors, newsletter, privacy, MFA)
- **[../lms/AGENTS.md](../../cms/lms-full/AGENTS.md)** — LMS Demo site template path tree and plugin structure
- **[../portfolio/AGENTS.md](../../cms/portfolio/AGENTS.md)** — Portfolio/VResume site template path tree and page models
- **[../../docs/guides/07-best-practices.md](../../docs/guides/07-best-practices.md)** — Best practices for templates and code style

---

## Template Resolution Order

```
1. <site>/templates/            — Site-specific overrides (highest)
2. <site>/www/**/templates/     — App-level page templates
3. <site>/plugins/**/templates/ — Plugin templates
4. <site>/assets/templates/     — Site asset templates
5. projects/assets/templates/   — Shared templates (lowest, but first resolved for cross-site components)
```

---

## Directory Structure

```
templates/
├── components/          # Reusable UI components (chat, cookies, forms, modals, pagination)
│   ├── AGENTS.md        # Component inventory
│   ├── chat/            # Chat bubble component
│   ├── cookies/         # Cookie consent, policy, privacy components
│   ├── form/            # Form rendering components
│   ├── modal/           # Modal dialog components
│   └── pagination/      # Pagination components
├── plugins/             # Plugin-level templates
│   ├── AGENTS.md        # Plugin template guidance
│   ├── allauth.md       # Allauth template overrides
│   └── TEMPLATE_GUIDE.md
├── layout/              # Layout variants (apps, landing, learning, profile, auth)
├── base/                # Base templates
├── sections/            # Reusable page sections
├── blocks/              # Wagtail StreamField blocks
└── errors/              # Error page templates (404, 500)
```

---

## Quick Rules

- `plugins/` is canonical for emails, errors, newsletter, privacy, MFA, pagination
- Layout variants (`apps`, `landing`, `learning`, `profile`, `auth`) are kept as-is — they may diverge per site
- Use BEM classes: `card`, `card__title`, `card--featured`
- Use `fragment_name` for HTMX fragment identifiers
- Preserve existing context variables, filters, and block tags
- Prefer `{% comp "path" /%}` over `{% include "path" %}` when using django-fusion

---

## Customization Tips

- Search nearby templates first, then shared templates, before adding a new partial
- When replacing a component, copy the equivalent data bindings from the old markup to the new include or partial
- Check related app, plugin, site, and shared templates with targeted `rg` searches for include paths, block names, context variables, and CSS classes
- Site-specific overrides belong in `projects/<site>/templates/`, not here
