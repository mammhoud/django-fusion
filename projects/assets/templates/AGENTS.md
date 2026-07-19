# Shared Templates — Agent Instructions

## Documentation Index

- **[components/AGENTS.md](components/AGENTS.md)** — Shared component inventory (chat, cookies, forms, modals, pagination) with templates, context variables, and usage
- **[../ctc-research/AGENTS.md](../ctc-research/AGENTS.md)** — CTC Research site template path tree and plugin structure
- **[../lms/AGENTS.md](../lms/AGENTS.md)** — LMS Demo site template path tree and plugin structure
- **[../VResume/AGENTS.md](../VResume/AGENTS.md)** — VResume site template path tree and page models
- **[../../docs/templates.md](../../docs/templates.md)** — Template usage and best practices
- **[../../docs/INDEX.md](../../docs/INDEX.md)** — Master documentation index

## Quick Rules
- `plugins/` is canonical for emails, errors, newsletter, privacy, mfa, pagination
- Layout variants (apps, landing, learning, profile) are kept as-is — they may diverge
- Use BEM classes: `card`, `card__title`, `card--featured`
- Use `fragment_name` for HTMX fragment identifiers
- Preserve existing context variables, filters, and block tags
