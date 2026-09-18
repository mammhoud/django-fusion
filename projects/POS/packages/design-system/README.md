# @formints/design-system

Shared design system for Formint POS editions — Double-Bezel architecture, compact CRUD widgets, and premium motion choreography.

## Overview

This package provides a unified design language across all Formint editions:

- **Community** (Tauri + React)
- **Standard** (Tauri + React)
- **Formin** (Django + Astro + HTMX)

### Features

- 🎨 **Design Tokens** — Spacing, typography, colors, shadows, motion
- 🧩 **React Components** — BezelCard, BentoGrid, CompactInput, etc.
- 📐 **Double-Bezel Architecture** — Premium nested card system
- ✨ **Motion Choreography** — Custom cubic-bezier easing functions
- 🎬 **Scroll-Triggered Animations** — IntersectionObserver-based reveals

## Installation

```bash
# From the formints root
pnpm add @formints/design-system

# Or with file reference (for monorepo)
pnpm add @formints/design-system@workspace:*
```

## Usage

### CSS Import

```css
/* Import all styles */
@import '@formints/design-system/styles.css';

/* Or import specific parts */
@import '@formints/design-system/css/variables.css';
@import '@formints/design-system/css/bezel.css';
@import '@formints/design-system/css/motion.css';
```

### TypeScript/React Import

```tsx
// Import tokens
import { tokens, spacing, radius, motion } from '@formints/design-system';

// Import components
import { BezelCard, BentoGrid, CompactInput } from '@formints/design-system';

// Import utilities
import { cn, cssVar, staggerDelay } from '@formints/design-system';
```

## CSS Architecture

### Double-Bezel (Doppelrand)

Premium nested card system with outer shell and inner core:

```css
.bezel {
  /* Outer shell */
  background: color-mix(in oklch, var(--color-base-200) 40%, transparent);
  border: 1px solid color-mix(in oklch, var(--color-base-300) 25%, transparent);
  border-radius: 1.5rem;
  box-shadow: 0 0 0 1px ..., 0 1px 3px ...;
  padding: 0.375rem;
}

.bezel-core {
  /* Inner core */
  background: var(--color-base-100);
  border-radius: 1.125rem;
  box-shadow: inset 0 1px 2px ...;
}
```

### Motion Choreography

Premium easing functions for CRUD interactions:

```css
/* Fluid transitions */
.motion-fluid { transition: all 700ms cubic-bezier(0.32, 0.72, 0, 1); }
.motion-snap { transition: all 300ms cubic-bezier(0.32, 0.72, 0, 1); }
.motion-bounce { transition: all 500ms cubic-bezier(0.34, 1.56, 0.64, 1); }

/* CRUD interactions */
.crud-card-hover { /* Card lift on hover */ }
.crud-button-press { /* Physical press feel */ }
.crud-modal-enter { /* Modal scale-up */ }
.crud-row-hover { /* Table row highlight */ }
.crud-field-focus { /* Input focus ring */ }
```

### Scroll-Triggered Animations

IntersectionObserver-based staggered reveals:

```css
.stagger-reveal-item {
  opacity: 0;
  transform: translateY(16px);
  transition: opacity 600ms cubic-bezier(0.32, 0.72, 0, 1),
              transform 600ms cubic-bezier(0.32, 0.72, 0, 1);
}

.stagger-reveal-item.is-visible {
  opacity: 1;
  transform: translateY(0);
}
```

## Design Tokens

### Spacing Scale

```typescript
import { spacing } from '@formints/design-system';

// spacing['1'] = '4px'
// spacing['2'] = '8px'
// spacing['4'] = '16px'
// spacing['8'] = '32px'
```

### Border Radius

```typescript
import { radius } from '@formints/design-system';

// radius.bezelOuter = '1.5rem'  (Double-Bezel outer shell)
// radius.bezelInner = '1.125rem' (Double-Bezel inner core)
// radius.widget = '0.75rem'     (Compact widgets)
// radius.card = '1rem'          (Standard cards)
```

### Motion

```typescript
import { motion } from '@formints/design-system';

// motion.easing.fluid = 'cubic-bezier(0.32, 0.72, 0, 1)'
// motion.easing.bounce = 'cubic-bezier(0.34, 1.56, 0.64, 1)'
// motion.duration.slower = '500ms'
// motion.stagger[3] = '225ms'
```

## Components

### BezelCard

Double-Bezel nested card with premium hover effects.

```tsx
import { BezelCard } from '@formints/design-system';

<BezelCard size="md" accent="primary" hover>
  <h3 className="text-sm font-semibold">Card Title</h3>
  <p className="text-xs text-base-content/60">Card content</p>
</BezelCard>
```

### BentoGrid

Asymmetric bento grid layout for dashboards.

```tsx
import { BentoGrid, BentoItem } from '@formints/design-system';

<BentoGrid variant="asymmetric" gap="md">
  <BentoItem colSpan={8} accent="primary" accentBar>
    {/* Hero content */}
  </BentoItem>
  <BentoItem colSpan={4} accent="success">
    {/* Secondary content */}
  </BentoItem>
</BentoGrid>
```

### CompactInput

Space-efficient form input with integrated label.

```tsx
import { CompactInput } from '@formints/design-system';

<CompactInput
  label="Name"
  value={name}
  onChange={(e) => setName(e.target.value)}
  placeholder="Enter name"
  required
  size="md"
/>
```

## Integration Guide

### Community Edition

```tsx
// src/app/pages/admin/Badges.tsx
import { BezelCard, CompactButton } from '@formints/design-system';

export default function Badges() {
  return (
    <div className="crud-grid">
      {badges.map((badge, idx) => (
        <BezelCard
          key={badge.id}
          size="md"
          accent={badge.tone}
          hover
        >
          {/* Card content */}
        </BezelCard>
      ))}
    </div>
  );
}
```

### Standard Edition

Same as Community — shared components via `@formints/design-system`.

### Formin (Django + Astro)

```astro
---
// Import CSS in Astro layout
import '@formints/design-system/styles.css';
---

<BezelCard size="md" accent="primary">
  <h3>Server-rendered content</h3>
</BezelCard>
```

## Development

```bash
# Install dependencies
pnpm install

# Build package
pnpm build

# Run tests
pnpm test

# Type check
pnpm typecheck
```

## License

AGPL-3.0
