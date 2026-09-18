# Formint — Color Palette & Theme Reference

> **Applies to:** formintA (site slug formint-pos) · **Source:** `assets/styles/index.css` + `src/contexts/ThemeContext.tsx`
>
> **Canonical design language:** [`../../../docs/THEME_SYSTEM.md`](../../../docs/THEME_SYSTEM.md) — shared palette/tokens/motion sourced from formint-pro.

---

## Overview

Formint themes are built on **FlyonUI v2.4.1** using OKLCH color tokens. Each theme variant defines the semantic tokens (`--color-primary`, `--color-base-100`, …) via `@plugin "flyonui/theme"` blocks in `assets/styles/index.css`. Switching a variant changes every component at once because the whole BEM component library references these tokens (see `assets/styles/base/_variables.css`).

```
ThemeContext (variant + mode)
    ↓  THEME_MAP[variant][mode]
data-theme attribute on <html>
    ↓  FlyonUI CSS resolves OKLCH tokens
BEM components + Tailwind utilities adapt automatically
```

---

## Theme Variants & Data-theme Mapping

The picker offers 6 variants; each maps to a FlyonUI theme per mode.

| Variant | Light `data-theme` | Dark `data-theme` | Mood |
|---------|-------------------|-------------------|------|
| **Default** | `light` | `dark` | Clean slate & indigo |
| **Corporate** | `corporate-light` | `corporate-dark` | Professional blue tones |
| **Luxury** | `luxury-light` | `luxury-dark` | Rich gold & warm hues |
| **Pastel** | `perplexity`¹ | `pastel-dark` | Soft candy colors |
| **Perplexity** | `perplexity` | `perplexity` | Minimal & intelligent |

¹ Pastel light intentionally reuses the built-in Perplexity theme (both are rounded, pastel-forward).
The **default launch themes** are `perplexity --default` (light) and `pastel-dark --prefersdark` (dark) — declared in the `@plugin "flyonui"` block.

> `src/contexts/ThemeContext.tsx` owns `THEME_VARIANTS` (picker entries) and `THEME_MAP` (the table above).

---

## OKLCH Token Reference

Each theme block defines the same token set. Values are **per theme**; the two tables below show the Light variants and Dark variants.

| Token | Role |
|-------|------|
| `--color-base-100` | Main surface background (page) |
| `--color-base-200` | Slightly darker surface (cards, dropdowns) |
| `--color-base-300` | Deepest surface (borders, hover fills) |
| `--color-base-content` | Text/icon color on base surfaces |
| `--color-primary` / `-content` | Brand/action color + its text |
| `--color-secondary` / `-content` | Complementary accent |
| `--color-accent` / `-content` | Highlight color |
| `--color-neutral` / `-content` | Neutral gray surface |
| `--color-info / success / warning / error` | Semantic state colors (+ content variants) |
| `--radius-selector / field / box` | Border-radius scale |
| `--border` | Default border width |
| `--depth` / `--noise` | Dynamic shadows / background noise |

### Light themes — key values

| Theme | Primary | Base-100 | Base-content | Radius (box) |
|-------|---------|----------|--------------|:---:|
| `light` (built-in) | Indigo | Near-white | Dark slate | default |
| `corporate-light` | `oklch(54.61% 0.2152 262.88)` | `98.42%` | `27.95%` | `0.5rem` |
| `luxury-light` | `oklch(68.06% 0.1423 75.83)` gold | `98.48%` | `26.85%` | `0.5625rem` |
| `pastel-light`² | `oklch(59.16% 0.2180 0.58)` | `97.14%` | `29.32%` | `2rem` (pill) |

### Dark themes — key values

| Theme | Primary | Base-100 | Base-content | Radius (box) |
|-------|---------|----------|--------------|:---:|
| `dark` (built-in) | Indigo | Dark slate | Light | default |
| `corporate-dark` | `oklch(62.31% 0.1880 259.81)` | `20.77%` | `92.88%` | `0.5rem` |
| `luxury-dark` | `oklch(79.52% 0.1617 86.05)` | `21.61%` | `98.48%` | `0.5625rem` |
| `pastel-dark` | `oklch(72.53% 0.1752 349.76)` | `25.39%` | `94.82%` | `2rem` (pill) |

² `pastel-light` block exists in `index.css` but the Pastel variant maps light mode to `perplexity`.

---

## Custom Actions & Choices at Color Themes

### 1. Variant picker (Settings → Appearance)

`THEME_VARIANTS` drives the cards in `Settings.tsx` Appearance tab. Each entry has an **id, label, icon and description** — add a new card and it appears in the picker automatically.

```ts
// src/contexts/ThemeContext.tsx
export const THEME_VARIANTS = [
  { id: 'default',    label: 'Default',    icon: 'tabler--palette',  description: 'Clean slate & indigo' },
  { id: 'corporate',  label: 'Corporate',  icon: 'tabler--briefcase', description: 'Professional blue tones' },
  { id: 'luxury',     label: 'Luxury',     icon: 'tabler--crown',     description: 'Rich gold & warm hues' },
  { id: 'pastel',     label: 'Pastel',     icon: 'tabler--flower',    description: 'Soft candy colors' },
  { id: 'perplexity', label: 'Perplexity', icon: 'tabler--sparkles',  description: 'Minimal & intelligent' },
];
```

### 2. Theme preview modal (live switcher)

`ThemePreviewModal.tsx` (Settings → Appearance → **Preview Theme Components**) is the app's complete component preview. It renders buttons, forms, alerts, badges, tabs, stats, cards, tables and progress bars, and its **Light / Dark / System switcher + variant chooser are bound live to `ThemeContext`** — every click instantly applies to the whole app, so you can compare choices before committing.

### 3. Adding a permanent variant

To register a brand-new theme, paste a `@plugin "flyonui/theme"` block into `index.css`:

```css
@plugin "flyonui/theme" {
  name: "ocean-light";
  color-scheme: light;
  --color-primary: oklch(55% 0.15 220);
  /* … */
}
```

Then add the variant to `THEME_MAP` + `THEME_VARIANTS` in `ThemeContext.tsx`.

### 4. Per-page color choices

| Area | Where | What you choose |
|------|-------|-----------------|
| Category colors | ProductManager → Manage categories | One of `CATEGORY_COLOR_PALETTE` (10 swatches) or any custom hex |
| Product card accents | Fixed — `PRODUCT_CARD_COLORS[0]` | Every card shares one uniform accent color (per-product accents removed) |
| Product card palette | `ProductCard.tsx` (`PRODUCT_CARD_COLORS`) | 7 rotating bg/border/initial/badge/icon sets |

---

## Semantic App Tokens (theme-aware)

`assets/styles/base/_variables.css` maps FlyonUI tokens onto app-level BEM names used by the component library:

| Token | Maps to |
|-------|---------|
| `--color__surface--page / card / raised` | `base-100 / 200 / 300` |
| `--color__text--primary / secondary / disabled` | `base-content` mixes |
| `--color__semantic--primary / info / success / warning / error` | FlyonUI semantic tokens |
| `--color__border--subtle / default / emphasis` | `base-300` mixes |
| `--shadow--sm … --colored` | Depth scale (theme-agnostic) |

> 💡 **Rule of thumb:** new components should use the `--color__*` / `oklch(var(--color-primary))` tokens — never hard-coded hex — so they keep working under every variant and both modes.

---

## References

- [`docs/styling.md`](styling.md) — styling stack, FlyonUI integration, bundle analysis
- [`docs/customization.md`](customization.md) — end-user theming guide (settings paths)
- `assets/styles/index.css` — the custom `@plugin "flyonui/theme"` blocks (corporate/luxury/pastel light+dark; source of truth)
- `src/contexts/ThemeContext.tsx` — `THEME_VARIANTS`, `THEME_MAP`, `useTheme()`
- `src/components/display/ThemePreviewModal.tsx` — live cross-variant preview modal
- [FlyonUI docs](https://flyonui.com) — theme token reference
