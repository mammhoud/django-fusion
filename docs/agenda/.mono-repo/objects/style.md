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
| `Related Components` | Relation → Component | — | Components using this token |
| `Depends On` | Relation → Style | — | Token dependencies |
| `Tags` | Multi-select | — | Cross-cutting labels |

---

## Usage

Component uses a Style, which is defined by the Theme System.

---

## Related

- → `_object-types.md` — All type definitions
- → `component.md` — Component entity
- → `../brand/_index.md` — Theme architecture
- → `../brand/logos-icons.md` — Theme guide
