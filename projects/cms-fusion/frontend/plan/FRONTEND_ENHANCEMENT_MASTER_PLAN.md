# LMS Front-End — Enhancement Master Plan

> **Plan file:** `projects/lms/front-end/plan/FRONTEND_ENHANCEMENT_MASTER_PLAN.md`
> **Created:** 2026-07-25 | **Branch:** `generic`
> **Scope:** FlyonUI integration, dropdown/select redesign, animated background, responsive layouts, conditional homepage, component/pages architecture, documentation

---

## Executive Summary

This plan covers the complete enhancement of the LMS front-end (Next.js 14 + React 18 + Tailwind CSS 3) with:

1. **FlyonUI integration** — Replace raw Tailwind dropdowns/selects with FlyonUI's prebuilt, accessible, animated components
2. **Animated background** — Solid teal background with subtle corner animations
3. **Responsive layout foundation** — Mobile-first design with desktop/web variants
4. **Conditional homepage** — Redirect authenticated users from `/` → `/dashboard`
5. **Component/pages architecture** — Standardized `components/pages/` directory with layout variants
6. **Build targets** — Windows, macOS, mobile PWA documentation
7. **Documentation** — Extendable pages, benefits, developer guides

---

## Phase 1 — Conditional Homepage (Quick Win)

### Status: ⬜ Not Started | Effort: Low | Priority: High

**Goal:** When a signed-in user visits `/`, redirect them to `/dashboard`. Unauthenticated users see the public landing page.

### Implementation

Modify `src/app/page.tsx`:

```tsx
// Add auth check at top of HomePage component
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();
  const hasToken = typeof window !== 'undefined' && Boolean(localStorage.getItem('lms_token'));

  if (hasToken) {
    router.replace('/dashboard' as never);
    return null; // or a loading spinner
  }

  return <FusionPage slug="home">...</FusionPage>;
}
```

**Alternative — Next.js Middleware (future enhancement):**

```ts
// middleware.ts (root of front-end)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('lms_token')?.value;
  if (request.nextUrl.pathname === '/' && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
}

export const config = { matcher: ['/'] };
```

### Deliverables

- [ ] Modified `src/app/page.tsx` with auth redirect
- [ ] Loading state during redirect check
- [ ] `middleware.ts` as future enhancement (commented out)

---

## Phase 2 — FlyonUI Integration

### Status: ⬜ Not Started | Effort: Medium | Priority: High

See detailed sub-plan: [`FLYONUI_INTEGRATION_PLAN.md`](./FLYONUI_INTEGRATION_PLAN.md)

### Summary

| Step | Task | Details |
|:----:|------|---------|
| 2.1 | Install `flyonui` | `npm install flyonui` |
| 2.2 | Update `globals.css` | Add `@plugin "flyonui"`, `@import "flyonui/variants.css"`, `@source` directives |
| 2.3 | Create `FlyonuiScript.tsx` | Client-side loader with `HSStaticMethods.autoInit()` on route change |
| 2.4 | Wire in `layout.tsx` | Add `<FlyonuiScript />` to root layout |
| 2.5 | Add `global.d.ts` | Type definitions for `HSStaticMethods` |
| 2.6 | Update `tailwind.config.js` | Add FlyonUI to `content` paths |

### Post-Integration Checklist

- [ ] Verify Tailwind compiles without errors (`npm run build`)
- [ ] Verify FlyonUI CSS loads (inspect DevTools for FlyonUI classes)
- [ ] Verify `HSStaticMethods.autoInit()` fires on page navigation
- [ ] Run existing E2E tests — no regressions
- [ ] Run existing Vitest tests — no regressions

---

## Phase 3 — Dropdown & Select Redesign

### Status: ⬜ Not Started | Effort: High | Priority: High

### 3.1 Current State Audit

| Component | Current Implementation | Issues |
|-----------|----------------------|--------|
| **Header mobile menu** | Simple `useState` toggle + conditional render | No animation, no FlyonUI, no focus trap |
| **NotificationBell** | Custom `useRef` + `mousedown` listener | No FlyonUI dropdown, no keyboard nav |
| **NotificationDropdown** | Plain `<div>` positioned absolutely | No animation, no accessibility |
| **Dashboard sidebar** | Static `<aside>` with links | No FlyonUI, no collapse on mobile |
| **Registration role selector** | Two `<button>` toggles | Not a proper select, no FlyonUI styling |
| **LanguageSwitcher** | Fixed position `<div>` | No dropdown animation |
| **Course filter** (courses page) | N/A — not yet built | Needs FlyonUI select/combo-box |

### 3.2 FlyonUI Dropdown Components

FlyonUI provides these dropdown variants (from [FlyonUI docs](https://flyonui.com/docs/component/)):

| Component | Use Case | Current LMS Equivalent |
|-----------|----------|----------------------|
| `dropdown` | Header nav menus, user menus, action menus | NotificationBell, mobile menu |
| `select` | Form selects, filter dropdowns | Registration role toggle |
| `advanced-select` | Searchable selects, multi-select | Course category filter (future) |
| `combo-box` | Autocomplete inputs | Course search (future) |
| `menu` | Context menus, sidebar navigation | Dashboard sidebar (future) |
| `context-menu` | Right-click actions | Data tables (future) |

### 3.3 Migration Plan

| Priority | Component | FlyonUI Replacement | Effort |
|:--------:|-----------|---------------------|:------:|
| **P0** | NotificationBell → FlyonUI dropdown | `data-flyonui-dropdown` + `hs-dropdown` | Medium |
| **P0** | NotificationDropdown content | FlyonUI dropdown menu items | Low |
| **P1** | Header mobile menu → FlyonUI offcanvas/drawer | `data-flyonui-drawer` | Medium |
| **P1** | Registration role → FlyonUI select | `data-flyonui-select` | Low |
| **P2** | Dashboard sidebar → FlyonUI sidebar | `hs-sidebar` with collapse | High |
| **P2** | LanguageSwitcher → FlyonUI dropdown | `data-flyonui-dropdown` | Low |
| **P3** | Course filters → FlyonUI advanced-select | `data-flyonui-advanced-select` | Medium |
| **P3** | Course search → FlyonUI combo-box | `data-flyonui-combo-box` | Medium |

### 3.4 FlyonUI Dropdown Pattern (Example)

```tsx
// NotificationBell with FlyonUI dropdown
'use client';
import { useEffect, useRef } from 'react';

export default function NotificationBell() {
  const dropdownRef = useRef<HTMLDivElement>(null);

  return (
    <div className="hs-dropdown relative inline-flex">
      <button
        type="button"
        className="hs-dropdown-toggle relative p-2 text-white/80 hover:text-white"
        aria-label="Notifications"
      >
        <HiBell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-bold text-white bg-red-500 rounded-full">
            {unreadCount}
          </span>
        )}
      </button>

      <div
        className="hs-dropdown-menu hidden opacity-0 transition-[opacity,margin] duration-200
                   absolute right-0 mt-2 min-w-[380px] bg-white rounded-xl shadow-xl border border-gray-200
                   [&.hs-dropdown-open]:opacity-100 [&.hs-dropdown-open]:block"
        role="menu"
      >
        <NotificationDropdown onClose={() => {/* close dropdown */}} />
      </div>
    </div>
  );
}
```

### 3.5 FlyonUI Select Pattern (Example)

```tsx
// Registration role selector as FlyonUI select
<div className="relative">
  <select
    data-flyonui-select='{"placeholder": "Select role..."}'
    className="w-full"
    value={form.role}
    onChange={(e) => setForm({...form, role: e.target.value as 'student' | 'instructor'})}
  >
    <option value="student">Learn as Student</option>
    <option value="instructor">Teach as Instructor</option>
  </select>
</div>
```

### 3.6 Accessibility Requirements

Each FlyonUI component must include:
- [ ] `aria-label` on toggle buttons
- [ ] `role="menu"` / `role="listbox"` on dropdown containers
- [ ] `role="menuitem"` / `role="option"` on dropdown items
- [ ] Keyboard navigation: `Tab`, `Enter`, `Escape`, `Arrow Keys`
- [ ] Focus trap within open dropdowns
- [ ] `aria-expanded` on toggle buttons
- [ ] Screen-reader announcements for dynamic content

---

## Phase 4 — Animated Background

### Status: ⬜ Not Started | Effort: Medium | Priority: Medium

### 4.1 Design Specification

The homepage hero section and auth pages (login, registration) should have:
- **Solid teal gradient background** (already exists: `section-hero` class)
- **Animated small images/floating elements** in corners — geometric shapes, dots, or research-themed icons
- **Subtle parallax or float animation** using `framer-motion`

### 4.2 Implementation — AnimatedHeroBackground Component

```tsx
// src/components/backgrounds/AnimatedHeroBackground.tsx
'use client';
import { motion } from 'framer-motion';

interface FloatingElement {
  icon: React.ReactNode;
  x: number; // % from left
  y: number; // % from top
  size: number; // px
  duration: number; // seconds
  delay: number; // seconds
}

const FLOATING_ELEMENTS: FloatingElement[] = [
  { icon: <HiBeaker />, x: 5, y: 10, size: 40, duration: 20, delay: 0 },
  { icon: <HiClipboard />, x: 90, y: 15, size: 32, duration: 25, delay: 2 },
  { icon: <HiGlobeAlt />, x: 85, y: 75, size: 48, duration: 22, delay: 1 },
  { icon: <HiUserGroup />, x: 10, y: 80, size: 36, duration: 18, delay: 3 },
];

export default function AnimatedHeroBackground() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
      {FLOATING_ELEMENTS.map((el, i) => (
        <motion.div
          key={i}
          className="absolute text-white/10"
          style={{
            left: `${el.x}%`,
            top: `${el.y}%`,
            width: el.size,
            height: el.size,
          }}
          animate={{
            y: [0, -20, 0, 20, 0],
            x: [0, 10, 0, -10, 0],
            rotate: [0, 5, 0, -5, 0],
          }}
          transition={{
            duration: el.duration,
            delay: el.delay,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          {el.icon}
        </motion.div>
      ))}
    </div>
  );
}
```

### 4.3 Integration Points

| Page | Section | Integration |
|------|---------|-------------|
| Homepage `/` | Hero `<section className="section-hero">` | Add `<AnimatedHeroBackground />` as first child |
| Login `/login` | Page background | Wrap in `<section className="section-hero relative overflow-hidden">` |
| Registration `/registration` | Page background | Same as login |
| About `/about-us` | Hero section | Optional — based on design review |

### 4.4 Visual Variants

| Variant | Use Case | Config |
|---------|----------|--------|
| `hero` | Full-page hero sections | Large icons, slow float (18-25s) |
| `auth` | Login/registration pages | Small icons, fast float (12-18s) |
| `subtle` | Page section backgrounds | Tiny dots, very slow (30s+) |

---

## Phase 5 — Responsive Layout Foundation

### Status: ⬜ Not Started | Effort: High | Priority: High

See detailed sub-plan: [`RESPONSIVE_LAYOUT_PLAN.md`](./RESPONSIVE_LAYOUT_PLAN.md)

### 5.1 Breakpoint Strategy

| Breakpoint | Width | Target | Layout |
|------------|-------|--------|--------|
| **mobile** | < 640px (`sm`) | Phone (portrait) | Single column, hamburger menu, bottom nav |
| **mobile-wide** | 640-768px (`md`) | Phone (landscape) / Small tablet | 2-column grid, collapsible sidebar |
| **tablet** | 768-1024px (`lg`) | iPad / Tablet | Sidebar + content, 3-column grid |
| **desktop** | 1024-1280px (`xl`) | Laptop | Full sidebar, 4-column grid, advanced charts |
| **wide** | > 1280px (`2xl`) | Desktop monitor | Max-width container, extra whitespace |

### 5.2 Mobile-First Layout Architecture

```
src/
  components/
    layouts/
      PublicLayout.tsx          # Public pages (header + content + footer)
      DashboardLayout.tsx       # Dashboard pages (sidebar + content)
      AuthLayout.tsx           # Auth pages (centered card, animated bg)
      MobileBottomNav.tsx      # Bottom navigation bar (mobile only)
      MobileSidebar.tsx        # Slide-out sidebar (mobile only)
    pages/                      # NEW — page-level composition components
      HomePage.tsx              # Public homepage (pulled from app/page.tsx)
      LoginPage.tsx            # Auth login (pulled from app/login/page.tsx)
      RegistrationPage.tsx     # Auth registration
      CoursesPage.tsx          # Public courses listing
      DashboardHomePage.tsx    # Dashboard overview
      ...
```

### 5.3 Layout Variant System

Each layout accepts a `variant` prop:

```tsx
interface LayoutProps {
  variant: 'mobile' | 'tablet' | 'desktop';
  children: React.ReactNode;
}

// Usage in pages:
export default function HomePage() {
  const { variant } = useResponsiveVariant();
  return (
    <PublicLayout variant={variant}>
      <HomePageContent variant={variant} />
    </PublicLayout>
  );
}
```

### 5.4 Mobile-Specific Components

| Component | Purpose | Priority |
|-----------|---------|:--------:|
| `MobileBottomNav` | 4-5 icon tabs at screen bottom | P0 |
| `MobileSidebar` | Slide-out navigation drawer | P0 |
| `MobileCard` | Responsive card that stacks on mobile | P1 |
| `MobileTable` | Responsive table → card list on mobile | P1 |
| `MobileFilter` | Bottom-sheet filter panel | P2 |
| `MobileSwipeAction` | Swipe-to-reveal actions (edit/delete) | P2 |

---

## Phase 6 — Component / Pages Architecture

### Status: ⬜ Not Started | Effort: High | Priority: Medium

See detailed sub-plan: [`COMPONENT_PAGES_PLAN.md`](./COMPONENT_PAGES_PLAN.md)

### 6.1 Directory Structure

```
src/
  components/
    backgrounds/
      AnimatedHeroBackground.tsx    # Phase 4
    layouts/
      PublicLayout.tsx              # Phase 5
      DashboardLayout.tsx           # Phase 5
      AuthLayout.tsx                # Phase 5
      MobileBottomNav.tsx           # Phase 5
    pages/                          # NEW — Phase 6
      home/
        HomeHero.tsx
        HomeStats.tsx
        HomeFeaturedCourses.tsx
        HomeCTA.tsx
        HomeInstructors.tsx
      auth/
        LoginForm.tsx
        RegistrationForm.tsx
        PasswordResetForm.tsx
      courses/
        CourseCard.tsx
        CourseGrid.tsx
        CourseFilters.tsx
        CourseSearch.tsx
      dashboard/
        instructor/
          InstructorStats.tsx
          InstructorCharts.tsx
          InstructorCourses.tsx
        student/
          StudentStats.tsx
          StudentEnrollments.tsx
          StudentProgress.tsx
        admin/
          AdminWithdrawals.tsx
      shared/
        StatCard.tsx
        FeatureCard.tsx
        TestimonialCard.tsx
```

### 6.2 Component Interface Standard

All page components follow a consistent interface:

```tsx
interface PageComponentProps {
  variant?: 'mobile' | 'tablet' | 'desktop';  // Responsive variant
  data?: PageData;                              // CMS/API data
  isLoading?: boolean;                          // Loading state
  error?: unknown;                              // Error state
  className?: string;                           // CSS overrides
  children?: React.ReactNode;                   // Slot content
}
```

### 6.3 Loading / Error / Empty State Convention

Every data-driven component must handle all four states:

```tsx
function CourseGrid({ data, isLoading, error }: PageComponentProps) {
  if (isLoading) return <LoadingSkeleton variant="card" count={6} />;
  if (error) return <ErrorState message={extractErrorMessage(error)} onRetry={refetch} />;
  if (!data?.courses?.length) return <EmptyState icon="courses" />;
  return <div className="grid grid-cols-1 md:grid-cols-3 gap-6">...</div>;
}
```

---

## Phase 7 — Build Targets & Platform Documentation

### Status: ⬜ Not Started | Effort: Low | Priority: Low

### 7.1 Build Commands

| Target | Command | Output | Notes |
|--------|---------|--------|-------|
| **Web (dev)** | `npm run dev` | `http://localhost:3457` | Hot reload enabled |
| **Web (prod)** | `npm run build && npm start` | `http://localhost:3457` | Optimized build |
| **Static export** | `next build && next export` | `out/` | For CDN hosting |
| **PWA** | `next build` + service worker | `.next/` | Requires `next-pwa` |
| **Docker** | `docker build -t lms-frontend .` | Container | Linux target |
| **Windows** | `npm run build` (native Node) | `.next/` | No WSL needed |
| **macOS** | `npm run build` (native Node) | `.next/` | No Rosetta needed |

### 7.2 Platform-Specific Notes

| Platform | Considerations |
|----------|---------------|
| **Windows** | Use Node 20+ native; no WSL needed. Paths use `\` — next.config.js handles this. |
| **macOS** | Native ARM builds (Apple Silicon). No special config needed. |
| **Linux** | Production target. Docker-based deployment. |
| **Mobile (PWA)** | Install via "Add to Home Screen." Works offline with service worker. |
| **Tablet** | Responsive layout handles 768-1024px natively. |
| **iOS Safari** | `-webkit-overflow-scrolling: touch` for smooth scroll. Safe area insets for notch. |
| **Android Chrome** | Material You theme-color meta tag. |

### 7.3 PWA Checklist

- [ ] `manifest.json` with CTC teal theme color
- [ ] Service worker (`next-pwa` or custom)
- [ ] Offline fallback page
- [ ] Install prompt
- [ ] Push notifications (tied to NotificationBell)

---

## Phase 8 — Documentation

### Status: ⬜ Not Started | Effort: Medium | Priority: Medium

### 8.1 Documents to Create

| Document | Path | Content |
|----------|------|---------|
| **Component Catalog** | `front-end/docs/COMPONENT_CATALOG.md` | Every component with props, variants, usage examples |
| **Page Extension Guide** | `front-end/docs/PAGE_EXTENSION_GUIDE.md` | How to add new pages, layouts, API endpoints |
| **Theme Guide** | `front-end/docs/THEME_GUIDE.md` | CTC teal variables, FlyonUI theming, responsive breakpoints |
| **Build Guide** | `front-end/docs/BUILD_GUIDE.md` | Build targets, platform notes, Docker, PWA |
| **Testing Guide** | `front-end/docs/TESTING_GUIDE.md` | Vitest + Playwright conventions, CI pipeline |

### 8.2 Extendable Pages — Benefits Summary

The new `components/pages/` architecture enables:

| Benefit | Description |
|---------|-------------|
| **Reusability** | Page sections (Hero, Stats, CTA) are standalone components usable across multiple pages |
| **Testability** | Each component has isolated unit tests — no page-level coupling |
| **CMS Integration** | Components accept `data` prop from CMS, API, or static content |
| **Responsive Variants** | Each component renders differently based on `variant` prop |
| **Lazy Loading** | Page sections can be `dynamic(() => import(...))` for code splitting |
| **Storybook-Ready** | Flat prop interfaces → easy to document in Storybook |
| **A/B Testing** | Swap components at the page level without touching page logic |

---

## Timeline & Dependencies

```
Phase 1: Conditional Homepage ────────── 1 hour ── ✅ (quick win)
    │
Phase 2: FlyonUI Integration ──────────── 2-3 hours ──── depends on Phase 1
    │
Phase 3: Dropdown/Select Redesign ─────── 4-6 hours ──── depends on Phase 2
    │
Phase 4: Animated Background ──────────── 2-3 hours ──── parallel with Phase 3
    │
Phase 5: Responsive Layout ────────────── 6-8 hours ──── depends on Phase 3
    │
Phase 6: Component/Pages Architecture ─── 8-12 hours ─── depends on Phase 5
    │
Phase 7: Build Targets ───────────────── 1-2 hours ──── parallel with Phase 6
    │
Phase 8: Documentation ───────────────── 3-4 hours ──── parallel with Phase 6-7
```

**Total estimated effort:** 27-39 hours (1-2 weeks for a solo developer)

---

## Progress Tracking

| Phase | Status | Started | Completed | PR |
|-------|:------:|:-------:|:---------:|:--:|
| 1 — Conditional Homepage | ⬜ | — | — | — |
| 2 — FlyonUI Integration | ⬜ | — | — | — |
| 3 — Dropdown/Select Redesign | ⬜ | — | — | — |
| 4 — Animated Background | ⬜ | — | — | — |
| 5 — Responsive Layout | ⬜ | — | — | — |
| 6 — Component/Pages Arch | ⬜ | — | — | — |
| 7 — Build Targets | ⬜ | — | — | — |
| 8 — Documentation | ⬜ | — | — | — |

---

*This plan is a living document. Update progress tracking as each phase is completed.*
