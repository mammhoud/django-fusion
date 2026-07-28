# LMS Front-End — Responsive Layout Plan

> **Plan file:** `projects/lms/front-end/plan/RESPONSIVE_LAYOUT_PLAN.md`
> **Created:** 2026-07-25 | **Branch:** `generic`
> **Parent plan:** [`FRONTEND_ENHANCEMENT_MASTER_PLAN.md`](./FRONTEND_ENHANCEMENT_MASTER_PLAN.md) — Phase 5

---

## Overview

The LMS front-end currently uses a monolithic layout (`layout.tsx` → Header + main + Footer)
with minimal responsive breakpoints. This plan defines a mobile-first responsive
architecture with three layout variants, dedicated mobile components, and a
breakpoint strategy that scales from phone to wide desktop.

---

## 1. Breakpoint Strategy

| Breakpoint | Tailwind | Width Range | Target Device | Layout Mode |
|------------|----------|-------------|---------------|-------------|
| **mobile** | default (< `sm`) | 320-639px | Phone (portrait) | `mobile` |
| **mobile-wide** | `sm` | 640-767px | Phone (landscape) / Small tablet | `mobile` |
| **tablet** | `md` | 768-1023px | iPad / Tablet | `tablet` |
| **desktop** | `lg` | 1024-1279px | Laptop | `desktop` |
| **wide** | `xl` `2xl` | ≥ 1280px | Desktop monitor | `desktop` |

### Responsive Hook

```tsx
// src/hooks/useResponsiveVariant.ts
'use client';
import { useState, useEffect } from 'react';

export type LayoutVariant = 'mobile' | 'tablet' | 'desktop';

export function useResponsiveVariant(): LayoutVariant {
  const [variant, setVariant] = useState<LayoutVariant>('desktop');

  useEffect(() => {
    function update() {
      const w = window.innerWidth;
      if (w < 768) setVariant('mobile');
      else if (w < 1024) setVariant('tablet');
      else setVariant('desktop');
    }
    update();
    window.addEventListener('resize', update);
    return () => window.removeEventListener('resize', update);
  }, []);

  return variant;
}
```

---

## 2. Layout Architecture

### 2.1 Layout Components

```
src/components/layouts/
  PublicLayout.tsx       # Header + content + Footer (public pages)
  DashboardLayout.tsx    # Sidebar + content (authenticated pages)
  AuthLayout.tsx         # Centered card + animated background (login/register)
```

### 2.2 PublicLayout

```tsx
interface PublicLayoutProps {
  variant: LayoutVariant;
  children: React.ReactNode;
}

export default function PublicLayout({ variant, children }: PublicLayoutProps) {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Header adapts based on variant */}
      <Header variant={variant} />

      <main className="flex-1">
        {children}
      </main>

      <Footer />

      {/* Mobile-only bottom navigation */}
      {variant === 'mobile' && <MobileBottomNav />}
    </div>
  );
}
```

### 2.3 DashboardLayout

```tsx
interface DashboardLayoutProps {
  variant: LayoutVariant;
  role: 'student' | 'instructor' | 'admin';
  children: React.ReactNode;
}

export default function DashboardLayout({ variant, role, children }: DashboardLayoutProps) {
  const links = role === 'admin' ? adminLinks : role === 'instructor' ? instructorLinks : studentLinks;

  // Mobile: sidebar is a slide-out drawer triggered by hamburger
  if (variant === 'mobile') {
    return (
      <div className="flex flex-col min-h-screen">
        <DashboardMobileHeader role={role} />
        <MobileSidebar links={links} />
        <main className="flex-1 px-4 py-6">{children}</main>
        <MobileBottomNav />
      </div>
    );
  }

  // Tablet: collapsible sidebar with icons only when collapsed
  if (variant === 'tablet') {
    return (
      <div className="flex min-h-screen">
        <CollapsibleSidebar links={links} defaultCollapsed />
        <main className="flex-1 px-6 py-8">{children}</main>
      </div>
    );
  }

  // Desktop: full sidebar with labels
  return (
    <div className="flex min-h-screen">
      <DesktopSidebar links={links} />
      <main className="flex-1 px-8 py-10">{children}</main>
    </div>
  );
}
```

---

## 3. Mobile-Specific Components

### 3.1 MobileBottomNav

A fixed bottom navigation bar with 5 icon tabs, visible only on mobile.

```tsx
// src/components/layouts/MobileBottomNav.tsx
'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { HiHome, HiBookOpen, HiUser, HiBell, HiMenu } from 'react-icons/hi';

const MOBILE_NAV_ITEMS = [
  { href: '/', icon: HiHome, label: 'Home' },
  { href: '/courses', icon: HiBookOpen, label: 'Courses' },
  { href: '/dashboard', icon: HiUser, label: 'Dashboard' },
  { href: '/dashboard/notifications', icon: HiBell, label: 'Alerts' },
  // 5th tap opens slide-out menu
];

export default function MobileBottomNav() {
  const pathname = usePathname();

  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200
                    safe-area-bottom">
      <div className="flex items-center justify-around h-14">
        {MOBILE_NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href as any}
              className={`flex flex-col items-center justify-center flex-1 h-full
                ${isActive ? 'text-[rgb(var(--ctc-primary))]' : 'text-gray-400'}`}
            >
              <item.icon className="w-5 h-5" />
              <span className="text-[10px] mt-0.5">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
```

### 3.2 MobileSidebar

A slide-out drawer triggered from MobileBottomNav or a hamburger button.

```tsx
// Uses FlyonUI hs-drawer (Phase 3) or custom framer-motion
```

### 3.3 MobileUtility Classes

```css
/* Safe area insets for notched phones */
.safe-area-top { padding-top: env(safe-area-inset-top); }
.safe-area-bottom { padding-bottom: env(safe-area-inset-bottom); }

/* Smooth scrolling for iOS */
body { -webkit-overflow-scrolling: touch; }

/* Prevent text size adjustment on orientation change */
html { -webkit-text-size-adjust: 100%; }
```

---

## 4. Responsive Grid System

### 4.1 Standard Grids

| Context | Mobile | Tablet | Desktop |
|---------|--------|--------|---------|
| Course cards | 1 col | 2 col | 3 col |
| Instructor cards | 1 col | 2 col | 4 col |
| Blog posts | 1 col | 2 col | 3 col |
| Dashboard stats | 2 col | 2 col | 4 col |
| Form fields | 1 col | 2 col | 2 col |
| Shop products | 2 col | 3 col | 4 col |

### 4.2 Grid Component

```tsx
// src/components/ui/ResponsiveGrid.tsx
interface ResponsiveGridProps {
  cols?: { mobile?: number; tablet?: number; desktop?: number };
  gap?: number;
  children: React.ReactNode;
}

export default function ResponsiveGrid({
  cols = { mobile: 1, tablet: 2, desktop: 3 },
  gap = 6,
  children,
}: ResponsiveGridProps) {
  const mobile = cols.mobile ?? 1;
  const tablet = cols.tablet ?? 2;
  const desktop = cols.desktop ?? 3;

  return (
    <div
      className={`grid gap-${gap}`}
      style={{
        gridTemplateColumns: `repeat(${mobile}, 1fr)`,
      }}
      // Tailwind responsive:
      // grid-cols-{mobile} md:grid-cols-{tablet} lg:grid-cols-{desktop}
    >
      {children}
    </div>
  );
}
```

---

## 5. Page-Level Variant Composition

Each page accepts the variant and renders different sub-components:

```tsx
// src/app/courses/page.tsx — example
'use client';
import { useResponsiveVariant } from '@/hooks/useResponsiveVariant';
import PublicLayout from '@/components/layouts/PublicLayout';
import CourseGrid from '@/components/pages/courses/CourseGrid';
import CourseFilters from '@/components/pages/courses/CourseFilters';
import MobileFilter from '@/components/layouts/MobileFilter';

export default function CoursesPage() {
  const variant = useResponsiveVariant();

  return (
    <PublicLayout variant={variant}>
      <div className="max-w-7xl mx-auto px-4 py-10">
        {/* Desktop/Tablet: filters in sidebar */}
        {variant !== 'mobile' && <CourseFilters />}

        {/* Mobile: filters as bottom sheet */}
        {variant === 'mobile' && <MobileFilter><CourseFilters /></MobileFilter>}

        <CourseGrid variant={variant} />
      </div>
    </PublicLayout>
  );
}
```

---

## 6. Responsive Typography

```css
/* Fluid type scale */
h1 { font-size: clamp(1.75rem, 4vw, 3.75rem); }   /* 28px → 60px */
h2 { font-size: clamp(1.5rem, 3vw, 2.25rem); }     /* 24px → 36px */
h3 { font-size: clamp(1.25rem, 2vw, 1.5rem); }      /* 20px → 24px */
body { font-size: clamp(0.875rem, 1.5vw, 1rem); }   /* 14px → 16px */
```

---

## 7. Responsive Tables

Tables on mobile become stacked cards:

```tsx
// src/components/ui/ResponsiveTable.tsx
export default function ResponsiveTable({ columns, data }: ResponsiveTableProps) {
  const variant = useResponsiveVariant();

  if (variant === 'mobile') {
    // Render as card list
    return (
      <div className="space-y-4">
        {data.map((row) => (
          <MobileTableCard key={row.id} columns={columns} row={row} />
        ))}
      </div>
    );
  }

  // Render as full table
  return (
    <div className="overflow-x-auto">
      <table className="w-full">...</table>
    </div>
  );
}
```

---

## 8. Image Optimization

- Use `<Image>` from `next/image` for all images
- Provide `sizes` prop for responsive loading
- Use WebP format with fallback

```tsx
<Image
  src="/hero-bg.jpg"
  alt="Fusion CMS"
  width={1920}
  height={600}
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  priority // for above-the-fold images
/>
```

---

## 9. Touch Targets (Mobile)

WCAG 2.1 minimum touch target: **44×44px** (AA) / **48×48px** (AAA).

```css
/* All interactive elements on mobile */
@media (max-width: 767px) {
  button, a, input, select, textarea, [role="button"] {
    min-height: 44px;
    min-width: 44px;
  }
}
```

---

## 10. Desktop/Mobile Component Swap Strategy

| Page Section | Desktop | Tablet | Mobile |
|-------------|---------|--------|--------|
| Header nav | Horizontal links | Horizontal links (fewer) | Hamburger → drawer |
| Sidebar | Full sidebar with labels | Collapsible (icons only) | Slide-out drawer |
| Filters | Sticky sidebar | Inline dropdowns | Bottom sheet |
| Tables | Full `<table>` | Horizontal scroll `<table>` | Stacked cards |
| Stats | 4-column grid | 2-column grid | 2-column grid |
| Footer | 4-column | 2-column | 1-column (stacked) |
| Charts | Recharts (full size) | Recharts (compact) | Simple numbers (no chart) |

---

## 11. Build & Test Targets

| Target | Command | Expected Behavior |
|--------|---------|-------------------|
| Mobile Firefox | `npm run dev` → open `localhost:3457` in responsive mode (375px) | MobileBottomNav visible, cards 1-col |
| Tablet Safari | `npm run dev` → responsive mode (768px) | Collapsible sidebar, 2-col grids |
| Desktop Chrome | `npm run dev` → 1440px | Full sidebar, 3-4 col grids, charts |
| Mobile PWA | `npm run build && npm start` → Add to Home Screen | Works offline, full-screen mode |

---

## Progress

| Task | Status | Notes |
|------|:------:|-------|
| `useResponsiveVariant` hook | ⬜ | Create `src/hooks/` |
| `PublicLayout` component | ⬜ | Header variant + MobileBottomNav |
| `DashboardLayout` component | ⬜ | Sidebar variants |
| `AuthLayout` component | ⬜ | Centered card + bg |
| `MobileBottomNav` component | ⬜ | 5-tab bottom nav |
| `MobileSidebar` component | ⬜ | Slide-out drawer |
| `ResponsiveGrid` component | ⬜ | Auto cols based on variant |
| `ResponsiveTable` component | ⬜ | Table → cards on mobile |
| Safe area CSS | ⬜ | `safe-area-inset-*` |
| Touch targets | ⬜ | 44px min on mobile |
| Fluid typography | ⬜ | `clamp()` values |
| Image optimization | ⬜ | `next/image` + `sizes` |

---

*Refer to [FlyonUI Responsive docs](https://flyonui.com/docs/) and [Next.js Image docs](https://nextjs.org/docs/app/api-reference/components/image) for implementation details.*