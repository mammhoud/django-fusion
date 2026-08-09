# POS Theme System

> **Version:** 1.0.0  
> **Last Updated:** 24 July 2026  
> **Applies to:** pos-mini, pos-solo, pos-full  
> **Files:** `src/styles/themes.css`, `src/styles/theme-overrides.css`, `src/contexts/ThemeContext.tsx`

---

## 1. Architecture Overview

```
User selects variant       localStorage           <html> element
   in Settings             ──────────►           ──────────────►
      │                    theme-variant          data-theme="corporate"
      │                    theme-mode             class="dark"
      │                    theme-follow-system    class="light"
      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ThemeContext.tsx                                                     │
│                                                                      │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────────────────────┐  │
│  │  mode     │  │  variant     │  │  followSystem               │  │
│  │  light    │  │  default     │  │  true/false                 │  │
│  │  dark     │  │  corporate   │  │  watches prefers-color-    │  │
│  │           │  │  luxury      │  │  scheme media query         │  │
│  │           │  │  pastel      │  │                             │  │
│  │           │  │  cyberpunk   │  │                             │  │
│  └─────┬─────┘  └──────┬──────┘  └────────────┬────────────────┘  │
│        │               │                      │                    │
│        ▼               ▼                      ▼                    │
│  Apply: <html> → class="dark|light" + data-theme="default|..."    │
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│  Tailwind v4 CSS Custom Properties                                  │
│                                                                     │
│  themes.css — Defines --theme-* CSS vars per variant               │
│  theme-overrides.css — Maps --color-* tokens to variant values     │
│                      (teal, slate, gray, indigo, amber, etc.)      │
│                                                                     │
│  tailwind.config.js — theme.extend.colors.theme → --theme-* vars   │
└────────────────────────────────────────────────────────────────────┘
```

---

## 2. Theme Variants

| Variant | Icon | Light Description | Dark Description | Mood |
|---------|:----:|-------------------|------------------|------|
| **Default** | 🎨 | Clean slate & indigo | Deep slate & indigo | Professional |
| **Corporate** | 💼 | Blue-toned, professional | Dark blue, serious | Trustworthy |
| **Luxury** | 👑 | Gold & warm hues | Rich gold on dark | Premium |
| **Pastel** | 🌸 | Soft candy colors | Muted pastel on dark | Playful |
| **Cyberpunk** | ⚡ | Neon on light | Neon on black | Futuristic |

### Default Theme
No CSS variable overrides — uses base Tailwind color tokens (slate, teal, indigo).

### Corporate Theme
Replaces teal → blue tones. Replaces slate → clean gray scale. All interactive elements shift from green-teal to blue.

### Luxury Theme  
Replaces teal → gold/amber. Replaces slate → warm stone. Accent colors shift to rich golds and warm oranges.

### Pastel Theme
Replaces teal → pink/magenta. Replaces slate → purple tones. Soft, playful palette with reduced contrast.

### Cyberpunk Theme
Replaces teal → magenta/neon pink. Replaces slate → dark grays with light text. High-contrast futuristic look with neon accents.

---

## 3. File Structure

```
src/
├── contexts/
│   └── ThemeContext.tsx        # React context: mode, variant, followSystem
├── components/
│   └── ThemeToggle.tsx         # Light/dark toggle button (nav bar)
├── styles/
│   ├── themes.css              # --theme-* CSS variables per variant
│   ├── theme-overrides.css     # --color-* token overrides per variant
│   └── base/
│       └── _variables.css      # Global CSS custom properties
├── pages/
│   └── Settings.tsx            # Appearance tab: Light/Dark/Auto + variants
└── index.css                   # Import chain
```

### Import Order (index.css)

```css
@import "tailwindcss";                    # Base Tailwind (defines --color-*)
@import "./styles/themes.css";            # Theme CSS variables (--theme-*)
@import "./styles/theme-overrides.css";   # Override --color-* per variant
@import "../../assets/css/base/_variables.css";
@import "../../assets/css/base/_reset.css";
@import "../../assets/css/components/_card.css";
...
```

The order is critical: `theme-overrides.css` must come AFTER `tailwindcss` so it can redefine `--color-teal-500`, `--color-slate-900`, etc. per variant.

---

## 4. ThemeContext API

### Exported Values

```typescript
interface ThemeContextType {
  /** Resolved visual mode: 'light' | 'dark' */
  mode: Mode;
  /** Active variant: 'default' | 'corporate' | 'luxury' | 'pastel' | 'cyberpunk' */
  variant: ThemeVariant;
  /** Whether mode follows OS preference */
  followSystem: boolean;
  /** Toggle light/dark (disables followSystem) */
  toggleMode: () => void;
  /** Set specific mode, disables followSystem */
  setMode: (mode: Mode) => void;
  /** Set variant */
  setVariant: (variant: ThemeVariant) => void;
  /** Enable/disable OS preference following */
  setFollowSystem: (follow: boolean) => void;
}
```

### localStorage Keys

| Key | Values | Purpose |
|-----|--------|---------|
| `theme-mode` | `"light"` \| `"dark"` | Persisted mode selection |
| `theme-variant` | `"default"` \| `"corporate"` \| ... | Persisted variant selection |
| `theme-follow-system` | `"true"` \| `"false"` | Whether to follow OS preference |

### Behavior

1. **On load**: Reads localStorage for all three keys. Falls back to `prefers-color-scheme` for mode if no saved mode.
2. **System mode**: When `followSystem=true`, listens to `matchMedia('(prefers-color-scheme: dark)')` and updates mode in real-time.
3. **Manual toggle**: Clicking Light/Dark in Settings or the ThemeToggle in the nav bar disables `followSystem`.
4. **Persistence**: All three settings are saved to localStorage on every change.

---

## 5. How Theme Overrides Work (Tailwind v4)

### The Problem

All components in the codebase use hardcoded Tailwind utility classes like:

```tsx
className="bg-teal-500 hover:bg-teal-600 text-slate-900 dark:text-white"
```

In Tailwind v3, these compiled to hardcoded hex values at build time — impossible to override at runtime. **Switching theme variants had no visible effect.**

### The Solution (Tailwind v4)

In Tailwind v4 (used by this project via `@tailwindcss/postcss`), utility classes are generated from CSS custom properties:

```css
/* Tailwind v4 internally defines: */
:root {
  --color-teal-500: #14b8a6;
  --color-slate-900: #0f172a;
}

/* bg-teal-500 compiles to: */
.bg-teal-500 { background-color: var(--color-teal-500); }
```

By overriding `--color-teal-500` (and all other color tokens) per `[data-theme]`, every utility class that uses those tokens automatically picks up the new values:

```css
[data-theme="corporate"] {
  --color-teal-500: #3b82f6;  /* Blue instead of teal */
  --color-teal-600: #2563eb;
  --color-slate-900: #0f172a;
  /* ... */
}
```

This means **zero component changes** — every `bg-teal-500` instantly becomes blue when Corporate is selected.

### Why This Works

Tailwind v4 changed from Sass-generated classes to CSS-custom-property-based classes. This is the key architectural difference:

```
Tailwind v3:  .bg-teal-500 { background-color: #14b8a6; }   ← Fixed at build
Tailwind v4:  .bg-teal-500 { background-color: var(--color-teal-500); }  ← Dynamic at runtime
```

---

## 6. Color Scales Overridden

The `theme-overrides.css` file overrides these color scales per variant:

| Scale | Used For | Components |
|-------|----------|------------|
| **teal** | Primary actions, accents | Buttons, active states, focus rings, badges |
| **slate** | Backgrounds, text | Page backgrounds, cards, text colors |
| **gray** | Dark mode borders | `dark:border-gray-600`, `dark:border-gray-700` |
| **indigo** | Secondary accents | Badges, secondary buttons, hover states |
| **amber** | Warnings, dining | Warning alerts, dining tab accents |
| **cyan** | Light accent alternate | Info cards, accent highlights |
| **purple** | Analytics, charts | Chart colors, analytics section, database tab |
| **emerald** | Success indicators | Stock status, success badges, active indicators |
| **red** | Danger, errors | Error messages, delete buttons, validation |
| **sky** | Delivery, info | Delivery tab, info cards |
| **orange** | Accent alternate | Alternate highlights, warning variants |

---

## 7. Adding a New Theme Variant

1. Add the variant ID to `ThemeContext.tsx`:

```typescript
export type ThemeVariant = 'default' | 'corporate' | 'luxury' | 'pastel' | 'cyberpunk' | 'ocean';
```

2. Add the variant entry in `THEME_VARIANTS` array:

```typescript
{ id: 'ocean', label: 'Ocean', icon: '🌊', description: 'Deep blues & seafoam' },
```

3. Add CSS variable overrides in `theme-overrides.css`:

```css
[data-theme="ocean"] {
  --color-teal-500: #0891b2;
  --color-teal-600: #0e7490;
  /* ... more overrides ... */
}
.dark[data-theme="ocean"] {
  /* Dark mode overrides */
}
```

4. (Optional) If you also want `theme.*` CSS classes (`bg-theme-primary`, `text-theme-text`, etc.) to work, add corresponding `--theme-*` variable overrides in `themes.css`. These classes are wired in `tailwind.config.js` via `var(--theme-primary, #6366f1)` but most components use Tailwind utility classes (now overridden via `--color-*` tokens in step 3). Adding `--theme-*` overrides enables both systems.

---

## 8. Troubleshooting

### Theme switch has no visible effect
- **Check**: Is `theme-overrides.css` imported in `index.css` AFTER `tailwindcss`?
- **Check**: Is `data-theme` set on `<html>`? Use DevTools to inspect `<html>` element.
- **Check**: Is the variant saved in localStorage? Look for `theme-variant` key.
- **Check**: Is Tailwind v4 being used? Verify `@tailwindcss/postcss` in postcss config.

### Dark mode not working
- **Check**: Is `class="dark"` on `<html>`? The `dark:` variant requires the `.dark` class.
- **Check**: Does the `@custom-variant dark` rule exist in `index.css`?
- **Check**: Is `followSystem` enabled? The OS preference might differ from the UI state.

### Theme flickers on page load
- This is expected — React hydrates and applies the theme after initial render.
- To eliminate flicker, add a `<script>` in `index.html` that reads localStorage and sets `data-theme` and class on `<html>` synchronously before React loads.
