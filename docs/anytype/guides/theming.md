---
# yaml-language-server: $schema=schemas/page.schema.json
Object type: Guide
Tags: frontend, pos-mini, pos-solo, pos-full, theming
Status: Published
Category: Theming
---

# Guide — Theme Customization

> **Type:** Guide 📘
> **Theme variant system — customize colors to match brand identity.**

---

## How Themes Work

```css
[data-theme="variant"] {
  --color-teal-500: #3b82f6;   /* Overrides primary accent */
  --color-slate-900: #f8fafc;  /* Overrides dark mode text */
}
```

Tailwind v4 utility classes use CSS custom properties. Theme variants redefine these properties at the `[data-theme]` level for instant restyling.

---

## Project Color Palettes

Each project has an associated color identity that can be expressed through the theme system:

### CTC Research — Research & Training
| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#0ea5e9` (Sky-500) | Research highlights, course CTAs |
| Surface | `#f0f9ff` / `#0c4a6e` | Page backgrounds |
| **Vibe** | Professional, academic, trustworthy |

### LMS Demo — Learning & Education
| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#10b981` (Emerald-500) | Progress bars, completion badges |
| Surface | `#ecfdf5` / `#064e3b` | Course cards, lesson panels |
| **Vibe** | Growth-oriented, fresh, encouraging |

### VResume — Portfolio & Identity
| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#8b5cf6` (Violet-500) | Portfolio accents, skill badges |
| Surface | `#f5f3ff` / `#1e1b4b` | Portfolio cards |
| **Vibe** | Creative, expressive, professional |

### CyperCloud — AI & Cloud
| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#06b6d4` (Cyan-500) | Chat bubbles, AI responses |
| Surface | `#ecfeff` / `#164e63` | Chat panels |
| **Vibe** | Intelligent, futuristic, connected |

---

## Existing Theme Variants

| Variant | Primary (Teal →) | Surface (Slate →) | Best For | Mood |
|---------|-------------------|-------------------|----------|------|
| `default` | Indigo/teal `#6366f1`→`#14b8a6` | Cool gray `#0f172a`→`#f8fafc` | General use | Clean, modern, versatile |
| `corporate` | Blue `#3b82f6` | Neutral slate `#1e293b`→`#f1f5f9` | Offices | Professional, trustworthy, calm |
| `luxury` | Gold/amber `#eab308`→`#f59e0b` | Warm stone `#292524`→`#fafaf9` | Fine dining | Premium, elegant, warm |
| `pastel` | Pink/purple `#ec4899`→`#a855f7` | Soft lavender `#2e1065`→`#faf5ff` | Cafes, bakeries | Playful, soft, inviting |
| `cyberpunk` | Magenta/neon `#cc00cc`→`#06b6d4` | Dark gray `#111827`→`#e5e7eb` | Gaming centers | Energetic, futuristic, bold |

---

## Adding a New Variant

### 1. CSS Overrides → theme-overrides.css

```css
[data-theme="ocean"] {
  --color-teal-50:  #ecfeff;
  --color-teal-500: #06b6d4;
  --color-teal-600: #0891b2;
  /* ... full spectrum ... */
  --color-slate-50:  #f0f9ff;
  --color-slate-900: #0c4a6e;
  /* Also override: gray, indigo, amber, red, green, purple, cyan, sky, orange */
}

/* Dark mode inversion */
.dark[data-theme="ocean"] {
  --color-teal-50:  #164e63;
  --color-teal-500: #06b6d4;
  --color-slate-50:  #0c4a6e;
  --color-slate-900: #f0f9ff;
}
```

### 2. Register Variant → ThemeContext.tsx

```typescript
{ id: 'ocean', label: 'Ocean', icon: '🌊', description: 'Deep blue waters — calm and professional' }
```

### 3. Add Translations → i18n/en.json

```json
"appearanceTab": {
  "themeOcean": "Ocean",
  "oceanDesc": "Deep blue waters — calm and professional"
}
```

### 4. Settings UI → Settings.tsx

```tsx
<THEME_VARIANTS.map(v => (
  <button onClick={() => setVariant(v.id)}>
    {v.icon} {t(`appearanceTab.theme${...}`)}
  </button>
))}
```

---

## Light / Dark Mode

```typescript
ThemeContext followSystem=true  → @media (prefers-color-scheme)
ThemeContext setMode('light')   → html.classList.add('light')
ThemeContext setMode('dark')    → html.classList.add('dark')
```

---

## Required Override Colors

| Group | Used For | Example Classes |
|-------|----------|-----------------|
| `--color-teal-*` | Primary accent | `bg-teal-500`, `text-teal-400` |
| `--color-slate-*` | Background/text | `bg-slate-100`, `text-slate-900` |
| `--color-gray-*` | Borders | `dark:border-gray-600` |
| `--color-indigo-*` | Secondary accent | `bg-indigo-500` |
| `--color-amber-*` | Warning/dining | `bg-amber-400` |
| `--color-emerald-*` | Success | `text-emerald-500` |
| `--color-red-*` | Danger | `bg-red-500` |
| `--color-purple-*` | Analytics | `text-purple-600` |
| `--color-cyan-*` | Light accent | `bg-cyan-500` |
| `--color-sky-*` | Info/delivery | `text-sky-500` |
| `--color-orange-*` | Accent alternate | `bg-orange-400` |

---

## Related Docs

- → `../architecture/theme-system.md` — Theme architecture & design
- → `development.md` — Development workflow
- → `../references/i18n-keys.md` — Appearance tab translations
- → `../README.md` — Master index
