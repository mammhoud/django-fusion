# Guide — Theme Customization

**Type:** Guide 📘
**Tags:** `#frontend` `#pos-mini` `#pos-solo` `#pos-full`
**Status:** Published
**Category:** Theming

---

## How Themes Work

```
[data-theme="variant"] {
  --color-teal-500: #3b82f6;  /* Overrides bg-teal-500, text-teal-500, etc. */
  --color-slate-900: #f8fafc; /* Overrides dark mode text */
}
```

Tailwind v4 utility classes (e.g. `bg-teal-500`) use CSS custom properties. Theme variants redefine these properties at the `[data-theme]` level.

---

## Existing Variants

| Variant | Teal becomes | Slate becomes | Best for |
|---------|-------------|---------------|----------|
| `default` | Indigo/teal | Cool gray | General use |
| `corporate` | Blue | Neutral slate | Offices |
| `luxury` | Gold/amber | Warm stone | Fine dining |
| `pastel` | Pink/purple | Soft lavender | Cafes, bakeries |
| `cyberpunk` | Magenta/neon | Dark gray | Gaming centers |

---

## Adding a New Variant

### 1. CSS Overrides → `theme-overrides.css`
```css
/* Define ALL color tokens the app uses */
[data-theme="ocean"] {
  /* Primary (teal replacement) */
  --color-teal-50:  #ecfeff;
  --color-teal-100: #cffafe;
  --color-teal-200: #a5f3fc;
  --color-teal-300: #67e8f9;
  --color-teal-400: #22d3ee;
  --color-teal-500: #06b6d4;
  --color-teal-600: #0891b2;
  --color-teal-700: #0e7490;
  --color-teal-800: #155e75;
  --color-teal-900: #164e63;

  /* Surface (slate replacement) */
  --color-slate-50:  #f0f9ff;
  /* ... full spectrum ... */
  --color-slate-900: #0c4a6e;

  /* Also override: gray, indigo, amber, red, green, etc. */
}

/* Dark mode inversion */
.dark[data-theme="ocean"] {
  --color-teal-50:  #164e63;
  --color-teal-500: #06b6d4;
  /* Invert slate for dark bg */
  --color-slate-50:  #0c4a6e;
  --color-slate-900: #f0f9ff;
}
```

### 2. Register Variant → `ThemeContext.tsx`
```typescript
{ id: 'ocean', label: 'Ocean', icon: '🌊', description: 'Deep blue waters' }
```

### 3. Add Translations → `i18n/en.json`
```json
"appearanceTab": {
  "themeOcean": "Ocean",
  "oceanDesc": "Deep blue waters — calm and professional"
}
```

### 4. Settings UI → `Settings.tsx`
```tsx
<THEME_VARIANTS.map(v => (
  <button onClick={() => setVariant(v.id)}>
    {v.icon} {t(`appearanceTab.theme${v.id.charAt(0).toUpperCase() + v.id.slice(1)}`)}
  </button>
))}
```

---

## Light / Dark Mode

```
ThemeContext followSystem=true → @media (prefers-color-scheme)
ThemeContext setMode('light')  → html.classList.add('light')
ThemeContext setMode('dark')   → html.classList.add('dark')
```

The `html` element's `class` drives `.light` / `.dark` CSS selectors that invert slate values.

---

## Required Override Colors

To make a variant fully work, override these token groups:

| Group | Used For | Example Classes |
|-------|----------|----------------|
| `--color-teal-*` | Primary accent | `bg-teal-500`, `text-teal-400` |
| `--color-slate-*` | Background/text | `bg-slate-100`, `text-slate-900` |
| `--color-gray-*` | Dark borders | `dark:border-gray-600` |
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
- → `architecture/theme-system.md` — Theme architecture
- → `references/i18n-keys.md` — Appearance tab translations
- → `guides/development.md` — Development workflow
