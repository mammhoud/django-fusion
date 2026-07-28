# Forge POS — Styling & UI Package Reference

> **Last updated:** July 2026  
> **Stack:** Tailwind CSS v4 + FlyonUI v2.4.1 + Framer Motion v12 + Iconify

---

## Overview

The Forge POS UI is built on **Tailwind CSS v4** with **FlyonUI** as the semantic component layer, **Iconify** for icons, and **Framer Motion** for animations. This document covers every styling package, how they integrate, and how to use them.

---

## Package Catalog

| Package | Version | Purpose | Bundle Impact |
|---------|---------|---------|---------------|
| `tailwindcss` | ^4.0.0 | Utility-first CSS framework | ~10KB (PostCSS plugin) |
| `@tailwindcss/postcss` | ^4.0.0 | Tailwind v4 PostCSS integration | Build-time only |
| `flyonui` | ^2.4.1 | Semantic component classes (badge, btn) | ~270KB JS + CSS |
| `@iconify/tailwind4` | ^1.2.3 | Tailwind v4 plugin for Iconify icons | Build-time only |
| `@iconify-json/tabler` | ^1.2.37 | Tabler icon set (2000+ icons) | Dynamically loaded |
| `framer-motion` | ^12.0.5 | Page transitions, micro-interactions | ~160KB |
| `react-icons` | ^5.4.0 | Fallback icon components | ~30KB (tree-shaken) |

---

## Tailwind CSS v4 Configuration

### CSS-First Configuration

Forge POS uses Tailwind v4's new **CSS-first configuration** model. Theme variants are defined directly in `src/index.css` using FlyonUI's `@plugin "flyonui/theme"` blocks — no separate `themes.css` or `theme-overrides.css` files:

```css
@import "tailwindcss";
@import "../node_modules/flyonui/variants.css";
@import "./styles/base/_variables.css";
@import "./styles/base/_reset.css";

@plugin "flyonui" {
  themes: light --default, dark --prefersdark,
          corporate-light, corporate-dark,
          luxury-light, luxury-dark,
          pastel-light, pastel-dark,
          cyberpunk-light, cyberpunk;
}

@plugin "flyonui/theme" { name: "corporate-light"; ... }
@plugin "flyonui/theme" { name: "corporate-dark"; ... }
/* ... 8 more theme blocks ... */

@source "../node_modules/flyonui/dist/index.js";
@plugin "@iconify/tailwind4";

@custom-variant dark (&:where(.dark, .dark *));
@custom-variant rtl (&:where([dir="rtl"] &));
```

### Key Directives

| Directive | Purpose |
|-----------|---------|
| `@import "tailwindcss"` | Loads Tailwind v4 base |
| `@import "../node_modules/flyonui/variants.css"` | FlyonUI variant utilities |
| `@plugin "flyonui"` | Registers FlyonUI's component classes + theme list |
| `@plugin "flyonui/theme"` | Defines a single theme variant's OKLCH color tokens |
| `@source "../node_modules/flyonui/dist/index.js"` | Tells Tailwind's JIT to scan FlyonUI JS for class usage |
| `@plugin "@iconify/tailwind4"` | Enables `icon-[tabler--name]` syntax |
| `@custom-variant dark` | Tailwind's dark: variant (via `.dark` class) |
| `@custom-variant rtl` | Custom RTL variant |

### PostCSS Configuration

```js
// postcss.config.js
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
```

---

## FlyonUI Component Library

### What is FlyonUI?

FlyonUI is a free, open-source Tailwind CSS component library by ThemeSelection. It provides **semantic CSS classes** (like `badge`, `btn`, `card`) that compile down to Tailwind utility classes. Version 2.4.1 supports Tailwind v4 with CSS-first configuration.

### Installed Components

FlyonUI is installed at `node_modules/flyonui/` with:

```
node_modules/flyonui/
├── flyonui.js          # 270KB — bundled JS for interactive components
├── flyonui.css         # Compiled CSS
├── variants.css        # Variant utilities (badge-soft, btn-outline, etc.)
├── dist/               # Per-component JS modules
│   ├── accordion.js
│   ├── carousel.js
│   ├── collapse.js
│   ├── dropdown.js
│   ├── modal.js
│   └── ...
├── index.js            # Main entry (exports all)
└── package.json        # v2.4.1
```

### Available CSS Classes

#### Badges
```tsx
<span className="badge">Default</span>
<span className="badge badge-primary">Primary</span>
<span className="badge badge-secondary">Secondary</span>
<span className="badge badge-success">Success</span>
<span className="badge badge-warning">Warning</span>
<span className="badge badge-error">Error</span>
<span className="badge badge-info">Info</span>

<span className="badge badge-soft badge-primary">Soft Primary</span>
<span className="badge badge-outline badge-success">Outline Success</span>

<span className="badge badge-xs">XS</span>
<span className="badge badge-sm">SM</span>
<span className="badge badge-md">MD</span>
<span className="badge badge-lg">LG</span>
<span className="badge badge-xl">XL</span>
```

#### Buttons
```tsx
<button className="btn btn-primary">Primary</button>
<button className="btn btn-secondary">Secondary</button>
<button className="btn btn-accent">Accent</button>
<button className="btn btn-ghost">Ghost</button>
<button className="btn btn-outline">Outline</button>
<button className="btn btn-soft">Soft</button>
<button className="btn btn-gradient">Gradient</button>

<button className="btn btn-primary btn-sm">Small</button>
<button className="btn btn-primary btn-lg">Large</button>
<button className="btn btn-primary btn-block">Full Width</button>
<button className="btn btn-primary btn-circle">⏺</button>
<button className="btn btn-primary glass">Glass</button>
```

### React JS Integration

FlyonUI is imported once in `src/main.tsx`:
```tsx
import "flyonui/flyonui";
```

And re-initialized after route changes in `src/App.tsx`:
```tsx
async function reinitFlyonUI() {
  await import('flyonui/flyonui');
  setTimeout(() => window.HSStaticMethods?.autoInit(), 100);
}
```

> **Note:** Forge POS primarily uses React state for interactivity. FlyonUI's CSS classes (`badge`, `btn`) are used via semantic class names, while complex interactive components (modals, toasts) use React components.

---

## Icon System (Iconify + Tabler Icons)

### Usage

Icons use the `icon-[tabler--name]` utility class syntax:

```tsx
<span className="icon-[tabler--settings]" />
<span className="icon-[tabler--user]" />
<span className="icon-[tabler--shopping-cart]" />
<span className="icon-[tabler--home]" />
<span className="icon-[tabler--database]" />
```

### Available Icons

The `@iconify-json/tabler` package provides **2000+ Tabler icons**. All are available at runtime via the Iconify API or locally via the Tailwind plugin. Browse available icons at [tabler.io/icons](https://tabler.io/icons).

### Helper Component

In pages, icons are wrapped in a helper function for cleaner JSX:

```tsx
function Ic(name: string): React.ComponentType<{ className?: string }> {
  return ({ className = '' }) => 
    <span className={`icon-[tabler--${name}] ${className}`} />;
}

// Usage:
const GlobeIcon = Ic('globe');
const BriefcaseIcon = Ic('briefcase');

<GlobeIcon className="w-5 h-5" />
```

### Common Icons Used

| Icon Name | Usage |
|-----------|-------|
| `tabler--home` | Home/dashboard |
| `tabler--shopping-cart` | Point of Sale |
| `tabler--package` | Product manager |
| `tabler--users` | Employees |
| `tabler--settings` | Settings |
| `tabler--chart-bar` | Analytics |
| `tabler--database` | Database/Inventory |
| `tabler--truck` | Delivery settings |
| `tabler--tools-kitchen-2` | Dining/Kitchen |
| `tabler--moon` / `tabler--sun` | Dark/Light mode |
| `tabler--check` | Success indicators |
| `tabler--alert-triangle` | Errors/warnings |
| `tabler--x` | Close/delete |
| `tabler--chevron-down` | Dropdown indicators |

---

## Animation System (Framer Motion)

### Package

**framer-motion v12** provides:

### Page Transitions

All 22 routes use spring-based sliding transitions:

```tsx
<motion.div
  variants={{
    initial: (dir) => ({ opacity: 0, x: dir > 0 ? 40 : -40, scale: 0.97 }),
    animate: { opacity: 1, x: 0, scale: 1 },
    exit: (dir) => ({ opacity: 0, x: dir > 0 ? -40 : 40, scale: 0.97 }),
  }}
  transition={{
    x: { type: 'spring', stiffness: 300, damping: 30 },
    opacity: { duration: 0.25 },
    scale: { duration: 0.25 },
  }}
>
```

### Micro-interactions

Buttons and interactive elements use `whileHover` and `whileTap`:

```tsx
<motion.button
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
>
  Save
</motion.button>
```

### Loading States

Spinners use Framer Motion's `animate` prop:

```tsx
<motion.div
  animate={{ rotate: 360 }}
  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
  className="w-8 h-8 border-2 border-teal-400 border-t-transparent rounded-full"
/>
```

---

## Theme System

### Architecture

Forge POS uses **FlyonUI's native theme system**. Each theme variant is defined via `@plugin "flyonui/theme"` blocks in `src/index.css`. Light and dark mode for each variant are separate themes (e.g., `corporate-light`, `corporate-dark`), avoiding the dual-theme conflict that existed with the prior custom `themes.css` + `theme-overrides.css` approach.

```
ThemeContext (variant + mode)
    ↓
THEME_MAP → "corporate-light" | "corporate-dark" | "luxury-light" | ...
    ↓
data-theme attribute on <html>
    ↓
FlyonUI CSS resolves semantic tokens (--color-primary, --color-base-100)
    ↓
FlyonUI component classes (badge-primary, btn-primary) apply correctly
```

### Theme Variants

| Variant | Light Theme ID | Dark Theme ID | Light Primary | Dark Primary | Best For |
|---------|---------------|---------------|--------------|--------------|----------|
| **Default** | `light` | `dark` | Indigo (#6366f1) | Indigo | General use |
| **Corporate** | `corporate-light` | `corporate-dark` | Blue #2563eb | Royal Blue #3b82f6 | Business |
| **Luxury** | `luxury-light` | `luxury-dark` | Gold #ca8a04 | Amber #eab308 | Premium restaurants |
| **Pastel** | `pastel-light` | `pastel-dark` | Pink #db2777 | Light Pink #f472b6 | Cafes, bakeries |
| **Cyberpunk** | `cyberpunk-light` | `cyberpunk` | Magenta #cc00cc | Neon Pink #ff00ff | Gaming centers |

### Theme Context

The `ThemeContext` provides:
```tsx
const { mode, variant, followSystem, resolvedTheme, setVariant, setMode, setFollowSystem } = useTheme();
// mode = 'light' | 'dark'
// variant = 'default' | 'corporate' | 'luxury' | 'pastel' | 'cyberpunk'
// resolvedTheme = 'light' | 'dark' | 'corporate-light' | 'corporate-dark' | ...
```

Applied to `<html>` element:
```html
<html data-theme="corporate-dark" class="dark"> ... </html>
```

The `data-theme` attribute controls FlyonUI's semantic component colors. The `.dark` class controls Tailwind's `dark:` utility variant.

### Theme Token Reference

Each FlyonUI theme block defines these OKLCH tokens:

| Token | Role |
|-------|------|
| `--color-base-100` | Main surface background |
| `--color-base-200` | Slightly darker surface (cards, dropdowns) |
| `--color-base-300` | Deepest surface (borders, hover) |
| `--color-base-content` | Text/icon on base backgrounds |
| `--color-primary` | Brand/action color |
| `--color-primary-content` | Text/icon on primary |
| `--color-secondary` | Complementary accent |
| `--color-accent` | Highlight color |
| `--color-neutral` | Neutral gray surface |
| `--color-info/success/warning/error` | Semantic state colors |
| `--radius-selector/field/box` | Border radius scale |
| `--border` | Default border width |
| `--depth` | Toggle dynamic shadow effects |
| `--noise` | Toggle background noise |

---

## Dark/Light Mode

Toggle via `ThemeToggle.tsx` component. Mode is persisted to `localStorage`.

- **Light mode:** No class on `<html>` (default)
- **Dark mode:** `.dark` class on `<html>`
- **System follow:** Reads `prefers-color-scheme` media query

Flash prevention script in `index.html`:
```html
<script>
  (function() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme || (prefersDark ? 'dark' : 'light');
    document.documentElement.classList.add(theme);
  })();
</script>
```

---

## Static Assets

### Logo Files

```
public/
├── Logo.svg          # 1.1KB — SVG favicon
├── Logo.png          # 28KB — PNG favicon
└── Logo.png.placeholder.svg  # 1.1KB — Placeholder

src/assets/
├── CompanyLogo.png   # 60KB — Invoice/receipt logo
├── logo-img.png      # 60KB — UI logo variant
└── pos-crest.svg     # 2.8KB — POS crest icon
```

Referenced in `index.html`:
```html
<link rel="icon" type="image/svg+xml" href="/Logo.svg" />
<link rel="alternate icon" type="image/png" href="/Logo.png" />
```

---

## CSS File Architecture

```
src/
├── index.css                         # Main entry — imports + 10 FlyonUI theme blocks
└── styles/
    ├── base/
    │   ├── _variables.css            # Base CSS variables & design tokens
    │   └── _reset.css                # CSS reset & initial dark/light setup
    └── README.md                     # Styles documentation
```

> **Note:** The old `themes.css` and `theme-overrides.css` were removed in favor of FlyonUI-native `@plugin "flyonui/theme"` blocks in `index.css`. This eliminates the dual-theme conflict where both FlyonUI's built-in themes and custom CSS were fighting for control of `data-theme` selectors.

---

## Bundle Size Analysis

| Asset | Size (uncompressed) | Size (gzip) |
|-------|---------------------|-------------|
| CSS (Tailwind + FlyonUI) | 326 KB | 41 KB |
| Main JS (React + app) | 2,458 KB | 670 KB |
| html2canvas | 202 KB | 48 KB |
| recharts + dependencies | 160 KB | 53 KB |

> **Note:** The main JS bundle is large due to recharts, jspdf, and html2canvas. These could be code-split for future optimization.

---

## Adding a New Styling Package

1. Install the package:
   ```bash
   pnpm add <package-name>
   ```

2. For Tailwind v4 CSS plugins, add to `src/index.css`:
   ```css
   @plugin "<package-name>";
   ```

3. For JS-only packages, import in the component or `main.tsx`:
   ```tsx
   import 'package-name';
   ```

4. For PostCSS plugins, add to `postcss.config.js`:
   ```js
   export default {
     plugins: {
       '@tailwindcss/postcss': {},
       'new-plugin': {},
     },
   }
   ```
