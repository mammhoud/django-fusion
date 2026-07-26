---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Style
Tags: style, design, token, theme
Status: Published
---

# Style — Design Tokens & Brand Guidelines

> **Type:** Style 🎨
> **Layout:** Page
> **Description:** Design tokens, color palettes, typography scales, spacing, shadows, animations, and brand guidelines.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Category` | Select | Color, Typography, Spacing, Shadow, Animation, Icon | Token category |
| `Token` | Text | — | CSS variable name |
| `Value` | Text | — | Token value (hex, rem, etc.) |
| `Theme` | Relation → Edition | — | Theme/edition this belongs to |
| `Related Component` | Relation → Component | — | Components using this token |
| `Depends On` | Relation → Style | — | Token dependencies |
| `Tags` | Multi-select | — | Cross-cutting labels |

---

## Usage

```
Component 🔧 ── uses ──→ Style 🎨 ── defined by ──→ Theme System
```

---

## Related

- → `_object-types.md` — All type definitions
- → `../style/` — Style directory
- → `component.md` — Component entity
- → `../architecture/theme-system.md` — Theme architecture
- → `../guides/theming.md` — Theme guide
