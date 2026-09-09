---
Object type: Style
Tags: style, design-token, theme, ui
Status: Active
Related Components: django-fusion-components, formint-design-system
Related Features: pos-system
---

# Design Tokens — Shared Visual System

> **Description:** The shared token vocabulary — color palettes, typography, spacing, and theming rules used by components and products.

## Token groups

| Group | Examples |
|---|---|
| Color | Theme palettes (`#theme-default` teal/indigo, corporate blue, luxury gold, pastel, perplexity) |
| Type | Scale, weights, mono/uppercase telemetry labels where the product style requires |
| Layout | Spacing scale, grid, radius/shadow rules |
| Brand | Logos + icons (see `../brand/logos-icons.md`) |

## Rules

- Tokens are maintained centrally; components consume them — no per-component color drift
- Theme variants via token sets, not component forks

## Related

- → `loop-crm-design.md` — Product-specific token map
- → `../brand/logos-icons.md` — Brand assets
- → `../objects/style.md` — Style object type