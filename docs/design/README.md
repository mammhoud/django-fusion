# 🎨 Design System

> UI/UX design conventions, component styling, and visual guidelines across all Structa Cloud projects — Django sites and POS desktop apps.

---

## Design Principles

| Principle | Description |
|-----------|-------------|
| **Clarity** | Every interface element communicates its purpose without ambiguity |
| **Consistency** | Same patterns, components, and behaviors across all projects |
| **Accessibility** | WCAG AA minimum — semantic HTML, proper ARIA, keyboard navigation |
| **Performance** | Minimal CSS/JS bundles, lazy-loaded components, efficient re-renders |
| **Mobile-first** | Responsive layouts that work on any screen size |

---

## Visual Language

### Color Palette

#### Primary Colors

| Token | Hex | Usage |
|-------|:---:|-------|
| `--color-primary` | `#2563EB` | Buttons, links, active states, brand elements |
| `--color-primary-dark` | `#1D4ED8` | Hover states, active pressed states |
| `--color-primary-light` | `#DBEAFE` | Subtle backgrounds, badges, highlights |

#### Neutral Colors

| Token | Hex | Usage |
|-------|:---:|-------|
| `--color-bg` | `#FFFFFF` | Page backgrounds |
| `--color-bg-subtle` | `#F9FAFB` | Card backgrounds, section alternates |
| `--color-border` | `#E5E7EB` | Borders, dividers, form controls |
| `--color-text` | `#111827` | Primary body text |
| `--color-text-muted` | `#6B7280` | Secondary text, placeholders, metadata |

#### Semantic Colors

| Token | Hex | Usage |
|-------|:---:|-------|
| `--color-success` | `#10B981` | Success states, confirmations |
| `--color-warning` | `#F59E0B` | Warnings, pending states |
| `--color-error` | `#EF4444` | Errors, destructive actions |
| `--color-info` | `#3B82F6` | Informational banners, tooltips |

### Typography

| Element | Font | Size | Weight | Line Height |
|---------|------|:----:|:------:|:-----------:|
| Body | System UI | 16px | 400 | 1.5 |
| Heading 1 | System UI | 32px | 700 | 1.2 |
| Heading 2 | System UI | 24px | 600 | 1.3 |
| Heading 3 | System UI | 20px | 600 | 1.4 |
| Small | System UI | 14px | 400 | 1.5 |
| Caption | System UI | 12px | 400 | 1.4 |

### Spacing Scale

```css
:root {
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
  --space-3xl: 64px;
}
```

### Border Radius

```css
:root {
  --radius-sm: 4px;   /* Small elements, badges */
  --radius-md: 8px;   /* Cards, modals, buttons */
  --radius-lg: 12px;  /* Large containers, dialogs */
  --radius-full: 9999px; /* Pills, avatars */
}
```

---

## Component Design Patterns

### Django Templates (BEM Methodology)

All Django templates use BEM-style CSS naming:

```html
<div class="card card--featured">
  <h3 class="card__title">Featured Item</h3>
  <p class="card__description">Description text</p>
  <div class="card__actions">
    <button class="button button--primary">Learn More</button>
  </div>
</div>
```

### SCSS Organization

```
assets/static/styles/
├── base/              # Variables, reset, typography
│   ├── _variables.scss
│   ├── _reset.scss
│   └── _typography.scss
├── components/        # BEM component styles
│   ├── _card.scss
│   ├── _button.scss
│   ├── _modal.scss
│   └── _form.scss
├── layouts/           # Layout-specific styles
│   ├── _landing.scss
│   ├── _admin.scss
│   └── _auth.scss
├── utilities/         # Utility classes
│   └── _helpers.scss
└── main.scss          # Entry point — imports all partials
```

### POS Desktop (TailwindCSS)

The POS app uses TailwindCSS utility classes:

```tsx
<button className="
  px-4 py-2 rounded-lg font-medium
  bg-blue-600 text-white
  hover:bg-blue-700
  focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
  disabled:opacity-50 disabled:cursor-not-allowed
  transition-colors duration-150
">
  Save Changes
</button>
```

---

## Responsive Breakpoints

| Breakpoint | Width | Target |
|-----------|:-----:|--------|
| `sm` | 640px | Mobile landscape |
| `md` | 768px | Tablet |
| `lg` | 1024px | Desktop |
| `xl` | 1280px | Large desktop |
| `2xl` | 1536px | Extra large |

---

## Accessibility Guidelines

- All interactive elements must be keyboard accessible
- Color is never the sole indicator of state or meaning
- Forms have proper `<label>` associations with `for` attributes
- Images have descriptive `alt` text
- ARIA landmarks used for page structure: `<nav>`, `<main>`, `<aside>`
- Focus indicators visible (minimum 2:1 contrast ratio)
- Minimum touch target size: 44×44px on mobile

---

## Dark Mode

Django sites support dark mode via CSS custom properties:

```css
:root {
  --color-bg: #FFFFFF;
  --color-text: #111827;
}

[data-theme="dark"] {
  --color-bg: #1F2937;
  --color-text: #F3F4F6;
}
```

The POS app uses Tailwind's `dark:` variant:

```tsx
<div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
```

---

## Design Per Project

| Project | Design Notes |
|---------|--------------|
| **LMS** | Learning-focused UI with course cards, progress bars, video player |
| **Portfolio** | Minimal, clean layout with tab navigation, centered content |
| **Cypercloud** | AI chat interface with streaming response rendering, Monaco editor |
| **CTC Research** | Research portal with publication listings, clean typography |
| **POS** | Dark-themed, high-contrast UI for fast-paced retail, large touch targets, barcode scanner support |

---

## Related

| Resource | Path |
|----------|------|
| SCSS architecture | `projects/assets/static/js/ARCHITECTURE.md` |
| JS component design | `docs/dev/technical/components/design/js_structure.md` |
| Customization methods | `docs/customization/customization-methods.md` |
| django-fusion components | `libs/django-fusion/src/django_fusion/comp/templates/components/` |
| POS frontend docs | `docs/projects/pos/frontend/` |
