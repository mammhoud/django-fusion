# Theme System

**Type:** Architecture 🏗️
**Tags:** `#frontend` `#theme-default` `#theme-corporate` `#theme-luxury` `#theme-pastel` `#theme-cyberpunk`
**Status:** Published
**Edition:** Mini, Solo, Full

---

## Architecture

```
ThemeContext (React)
    │
    ├─ mode: 'light' | 'dark'
    ├─ variant: 'default' | 'corporate' | 'luxury' | 'pastel' | 'cyberpunk'
    ├─ followSystem: boolean (OS preference)
    │
    ├──→ <html> class="light|dark" data-theme="variant"
    │
    └──→ CSS Variables (Tailwind v4 token overrides)
              │
              ├─ --color-teal-*  → Primary accent (buttons, active states)
              ├─ --color-slate-* → Surface / text
              ├─ --color-gray-*  → Borders
              ├─ --color-indigo-* → Secondary accent
              └─ --color-amber-*  → Warning / dining accents
                     │
                     ▼
              Tailwind Utility Classes
              (bg-teal-500, text-slate-900, etc.)
```

---

## Theme Variants

| Variant | Primary (teal) | Surface (slate) | Feel |
|---------|---------------|-----------------|------|
| **Default** | Indigo/Teal `#6366f1`→`#14b8a6` | Gray `#0f172a`→`#f8fafc` | Clean, modern |
| **Corporate** | Blue `#3b82f6` | Slate (neutral) | Professional |
| **Luxury** | Gold `#eab308` | Warm stone | Premium |
| **Pastel** | Pink `#ec4899` | Light purple | Playful |
| **Cyberpunk** | Magenta `#cc00cc` | Dark/Light gray | Neon futuristic |

---

## Light / Dark Inversion

Each variant supports both light and dark modes:

```
.dark[data-theme="corporate"] {
  --color-slate-50:  #0f172a;  /* inverted */
  --color-slate-100: #1e293b;
  ...
  --color-slate-900: #f8fafc;
}
```

---

## Key Files

| File | Purpose |
|------|---------|
| `src/contexts/ThemeContext.tsx` | React context + provider |
| `src/styles/theme-overrides.css` | CSS variable overrides per variant |
| `src/styles/themes.css` | Additional theme CSS variables |
| `src/pages/Settings.tsx` | Appearance tab UI |

---

## Usage: Adding a New Theme Variant

```css
/* 1. Add CSS variable overrides in theme-overrides.css */
[data-theme="ocean"] {
  --color-teal-50:  #ecfeff;
  --color-teal-500: #06b6d4;
  --color-teal-600: #0891b2;
  /* ... all scale values */
}

/* 2. Define `useTheme` -- in ThemeContext.tsx */
// Already handles any data-theme value

/* 3. Add to THEME_VARIANTS in ThemeContext.tsx */
{ id: 'ocean', label: 'Ocean', icon: '🌊', description: 'Deep blue waters' }

/* 4. Add to Settings.tsx appearance tab */
```

---

## Related Docs
- → `guides/theming.md` — Theme customization guide
- → `features/comparison-matrix.md` — Which editions support theming
- → `references/i18n-keys.md` — Appearance tab i18n keys
