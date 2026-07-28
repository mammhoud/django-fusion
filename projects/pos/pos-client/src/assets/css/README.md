# 📁 POS Styles (`src/styles/`)

> **Related Names:** `styles`, `CSS`, `BEM`, `design tokens`, `variables`, `dark mode`, `RTL`, `animations`, `scrollbar`
> **Tags:** #css #bem #design #theme #styles

Modular BEM-inspired CSS architecture with design tokens, resets, component blocks, and utilities.

```
styles/
├── base/                    # 🔴 Design tokens + resets
│   ├── _variables.css       #    CSS custom properties (colors, sizing, shadows)
│   └── _reset.css           #    Base reset, safe-area, theme backgrounds
├── components/              # 🟢 Component blocks
│   ├── _card.css            #    Glass-morphism + hover cards
│   └── _receipt.css         #    Receipt layout styles
└── utilities/               # 🟢 Utility classes
    ├── _rtl.css             #    RTL flip + direction-aware styles
    ├── _animations.css      #    Transition + keyframe animations
    └── _scrollbar.css       #    Thin custom scrollbar
```

## Customization Tags

| File | Tag | How to customize |
|------|-----|-----------------|
| `_variables.css` | 🟢 `customizable` | Change colors, fonts, sizing, spacing |
| `_reset.css` | 🔴 `not-customizable` | Safe-area and base reset must remain |
| `_card.css` | 🟢 `customizable` | Change card styles, glass effect intensity |
| `_receipt.css` | 🟢 `customizable` | Change receipt layout |
| `_rtl.css` | 🔴 `not-customizable` | RTL logic must work with Arabic |
| `_animations.css` | 🟢 `customizable` | Add/change animations |
| `_scrollbar.css` | 🟢 `customizable` | Change scrollbar width/color |

## Design Tokens (`_variables.css`)

```css
:root {
  --color-bg-body: #f8fafc;
  --color-text-body: #0f172a;
  --color-primary: #667eea;
  --card-glass-bg: rgba(255, 255, 255, 0.7);
  /* ... 50+ tokens */
}

html.dark {
  --color-bg-body: #0f172a;
  --color-text-body: #f8fafc;
  --card-glass-bg: rgba(255, 255, 255, 0.1);
  /* ... inverse tokens */
}
```

## BEM Conventions

```css
/* Block */
.card--glass { }

/* Block + Modifier */
.card--hover { }

/* Utility */
.u-scrollbar-thin { }
.u-rtl-flip { }
```

> 💡 **Tip:** Combine BEM classes with Tailwind utilities: `className="card--glass card--hover rounded-xl p-4"`

## Reference

- [Design & Layout Guide →](../../docs/design-layout.md)
- [Customization Guide →](../../docs/customization-react.md)
