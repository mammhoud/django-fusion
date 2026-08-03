# Shadcnblocks Theme Styles (extracted from mainline-astro-template)

> **Source:** [shadcnblocks/mainline-astro-template](https://github.com/shadcnblocks/mainline-astro-template) — cloned into `/tmp/shadcnblocks` during Phase 0.
> **Tags:** #theme #shadcnblocks #tailwind-4 #oklch #styles

This document captures the theme styles extracted from the cloned Astro template so
they can be ported into the Fusion landing system. The template ships a **Tailwind CSS 4
CSS-first** theme (`src/styles/global.css`) using **oklch** color tokens, the **DM Sans**
type family, and a `.dark` class variant — the exact base that plan §5.1 (dark mode) and
§4 (theme tokens) build on.

---

## 1. Theme structure

```css
@import "tailwindcss";
@import "tw-animate-css";
@plugin "@tailwindcss/typography";

@custom-variant dark (&:is(.dark *));   /* .dark class on <html> drives dark mode */
```

The dark-mode variant is **class-based**, not `prefers-color-scheme` — identical to the
approach wired into `frontend/src/styles/globals.css` (`@custom-variant dark (&:where(.dark, .dark *))`)
and the `ThemeToggle` (localStorage → `.dark` on `<html>`).

## 2. Fonts

| Family | Weight | Source |
|--------|:------:|--------|
| DM Sans | 400 / 500 / 600 / 700 | `/fonts/dm-sans/DMSans-*.ttf` |

```css
--font-sans: var(--font-dm-sans), var(--font-inter), ui-sans-serif, system-ui, sans-serif;
--display-family: var(--font-sans);   /* headings: weight 600 */
--text-family: var(--font-inter);     /* body: weight 400 */
```

## 3. Color tokens — Light (`:root`)

| Token | Value (oklch) | Role |
|-------|---------------|------|
| `--background` | `oklch(1 0 0)` | Page bg |
| `--foreground` | `oklch(0.145 0 0)` | Body text |
| `--card` | `oklch(1 0 0)` | Cards |
| `--card-foreground` | `oklch(0.145 0 0)` | Card text |
| `--primary` | `oklch(0.92 0.04 86.47)` | Accent |
| `--primary-foreground` | `oklch(0.31 0.02 86.64)` | Text on accent |
| `--secondary` | `oklch(0.97 0 0)` | Secondary surfaces |
| `--muted` | `oklch(0.97 0 0)` | Muted bg |
| `--muted-foreground` | `oklch(0.556 0 0)` | Muted text |
| `--accent` | `oklch(0.97 0 0)` | Hover surfaces |
| `--destructive` | `oklch(0.577 0.245 27.325)` | Errors |
| `--border` / `--input` | `oklch(0.922 0 0)` | Dividers / inputs |
| `--ring` | `oklch(0.708 0 0)` | Focus rings |
| `--radius` | `8px` | Corner radius |

## 4. Color tokens — Dark (`.dark`)

| Token | Value (oklch) | Role |
|-------|---------------|------|
| `--background` | `oklch(0.145 0 0)` | Page bg |
| `--foreground` | `oklch(0.985 0 0)` | Body text |
| `--card` | `oklch(0.205 0 0)` | Cards |
| `--primary` | `oklch(0.922 0 0)` | Accent |
| `--secondary` / `--muted` | `oklch(0.269 0 0)` | Surfaces |
| `--muted-foreground` | `oklch(0.708 0 0)` | Muted text |
| `--destructive` | `oklch(0.704 0.191 22.216)` | Errors |
| `--border` / `--input` | `oklch(1 0 0 / 10%)` / `15%` | Dividers / inputs |
| `--ring` | `oklch(0.556 0 0)` | Focus rings |

Chart tokens (`--chart-1..5`) and sidebar tokens (`--sidebar*`) ship in both variants.

## 5. Token → Tailwind mapping (`@theme inline`)

```css
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-primary: var(--primary);
  --color-secondary: var(--secondary);
  --color-muted: var(--muted);
  --color-border: var(--border);
  --color-ring: var(--ring);
  /* … plus radius, shadow, breakpoint, font and animation tokens */
  --animate-accordion-down: accordion-down 0.2s ease-out;
  --animate-accordion-up: accordion-up 0.2s ease-out;
}
```

## 6. Radii & shadows

```css
--radius-sm: calc(8px - 4px); --radius-lg: 8px; --radius-2xl: 16px;
--shadow-sm: 0 1px 3px 0 rgb(0 0 0 / .1), 0 1px 2px -1px rgb(0 0 0 / .1);
--shadow-md: 0 1px 3px 0 rgb(0 0 0 / .1), 0 2px 4px -1px rgb(0 0 0 / .1);
--shadow-lg: 0 1px 3px 0 rgb(0 0 0 / .1), 0 4px 6px -1px rgb(0 0 0 / .1);
```

## 7. Breakpoints

```css
--breakpoint-sm: 640px; --breakpoint-md: 768px; --breakpoint-lg: 1024px;
--breakpoint-xl: 1280px; --breakpoint-2xl: 1400px;  /* default is 1536px */
```

## 8. Key component utilities

```css
@utility container {
  margin-inline: auto;
  padding-inline: 1.5rem;
  @media (width >= 1400px) { max-width: 1220px; }
}
/* Typography */
h1, h2, .font-display { font-family: var(--font-display); font-weight: var(--display-weight); }
body, .font-text { font-family: var(--font-text); font-weight: var(--text-weight); }
/* Border defaulting */
* { @apply border-border; }
body { @apply bg-background text-foreground; }
```

## 9. How the Fusion landing port maps this theme

| shadcnblocks token | Fusion landing token (frontend + backend) |
|--------------------|-------------------------------------------|
| `--primary` (oklch amber) | `--fu-primary: 262 83% 58%` (`#7c3aed` violet — brand) |
| `--background` / `--foreground` | `--fu-bg: 0 0% 98%` / `--fu-text: 240 6% 10%` |
| `--card` | `--fu-card: 0 0% 100%` |
| `--muted` / `--muted-foreground` | `--fu-muted: 240 5% 96%` |
| `--border` | `--fu-border: 240 6% 90%` |
| `.dark` token swap | `.dark { --fu-* … }` (identical mechanism) |
| DM Sans | Inter (kept from Fusion brand; swap in `--font-sans`) |

The Fusion brand keeps its violet identity; the shadcnblocks *mechanism* (CSS-first
tokens, `.dark` variant, `@utility` composition, `@theme inline` mapping) is fully adopted.
