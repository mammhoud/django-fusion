# Shared Templates — Agent Instructions

See [README.md](README.md) for the full template organization guide and directory structure.

See [../../docs/templates.md](../../docs/templates.md) for template usage and best practices.

See [../../docs/INDEX.md](../../docs/INDEX.md) for the master documentation index.

## Quick Rules
- `plugins/` is canonical for emails, errors, newsletter, privacy, mfa, pagination
- Layout variants (apps, landing, learning, profile) are kept as-is — they may diverge
- Use BEM classes: `card`, `card__title`, `card--featured`
- Use `fragment_name` for HTMX fragment identifiers
- Preserve existing context variables, filters, and block tags
