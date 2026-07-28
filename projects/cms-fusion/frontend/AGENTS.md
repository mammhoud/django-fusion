# LMS Front-End — AI Agent Instructions

> **Project:** `projects/lms/front-end/`  
> **Type:** Next.js 14 web application  
> **Stack:** React 18 + TypeScript + Next.js 14 + Tailwind CSS + RTK Query + Framer Motion

---

## Project Overview

The LMS front-end is a Next.js 14 application serving the Fusion CMS
learning management system. It provides:
- **Public pages:** Homepage, courses, about, contact, FAQ, blog, shop
- **Auth pages:** Login, registration
- **Dashboard pages:** Role-based (student, instructor, admin) with sidebar navigation
- **Fragment rendering:** CMS-backed pages via django-fusion FusionPage/FusionProxy

---

## Directory Structure

```
front-end/
├── src/
│   ├── app/                      # Next.js App Router pages
│   │   ├── page.tsx              # Homepage (authenticated → /dashboard redirect)
│   │   ├── layout.tsx            # Root layout (Providers + Header + Footer)
│   │   ├── login/                # Login page
│   │   ├── registration/         # Registration page
│   │   ├── dashboard/            # Dashboard (role-based sidebar + content)
│   │   │   ├── layout.tsx        # Dashboard layout (sidebar + main)
│   │   │   └── page.tsx          # Dashboard home (student/instructor/admin dispatch)
│   │   ├── courses/              # Public courses listing
│   │   ├── about-us/             # About page
│   │   ├── contact/              # Contact page
│   │   ├── faq/                  # FAQ page
│   │   ├── blog/                 # Blog listing
│   │   ├── shop/                 # Shop listing
│   │   └── ...                   # Other public pages
│   ├── components/               # Shared React components
│   │   ├── backgrounds/          # ⬜ PLANNED (Phase 4) — Animated backgrounds
│   │   ├── dashboard/            # ✅ Dashboard-specific components (charts)
│   │   ├── layouts/              # ⬜ PLANNED (Phase 5) — Layout components
│   │   │   ├── PublicLayout.tsx
│   │   │   ├── DashboardLayout.tsx
│   │   │   └── AuthLayout.tsx
│   │   ├── pages/                # ⬜ PLANNED (Phase 6) — Page-level composition components
│   │   │   ├── home/
│   │   │   ├── auth/
│   │   │   ├── courses/
│   │   │   ├── dashboard/
│   │   │   └── shared/
│   │   └── ui/                   # ✅ UI primitives (LoadingSkeleton, ErrorState, EmptyState)
│   ├── store/                    # Redux Toolkit + RTK Query
│   │   ├── index.ts              # Store configuration
│   │   ├── hooks.ts              # Typed hooks
│   │   ├── session/              # Session slice
│   │   └── api/
│   │       ├── baseApi.ts        # Base API configuration
│   │       └── endpoints/        # API endpoint definitions
│   ├── lib/                      # Core libraries
│   │   ├── fusion-decoder.ts     # Fusion codec decoder
│   │   ├── fusion-types.ts       # Shared TypeScript types
│   │   └── api-errors.ts         # Error extraction utility
│   ├── hooks/                    # Custom React hooks
│   │   └── useResponsiveVariant.ts # ⬜ PLANNED — Breakpoint detection
│   └── test/                     # ✅ Vitest tests (mirrors src/ structure)
├── tests/
│   └── e2e/                      # Playwright E2E tests
│       ├── dashboard-core-flows.spec.ts
│       ├── dashboard-ctc-theme.spec.ts
│       ├── withdrawal-flow.spec.ts
│       └── public-pages.spec.ts
├── docs/                         # Project documentation
│   ├── typescript/               # TypeScript/React docs
│   ├── css/                      # Tailwind/CSS theme docs
│   └── testing/                  # Test strategy docs
├── plan/                         # Implementation plans
│   ├── FRONTEND_ENHANCEMENT_MASTER_PLAN.md
│   ├── FLYONUI_INTEGRATION_PLAN.md
│   ├── RESPONSIVE_LAYOUT_PLAN.md
│   └── COMPONENT_PAGES_PLAN.md
└── public/                       # Static assets (fonts, images)
```

---

## Code Style & Standards

### TypeScript / React
- **Component naming:** `PascalCase` for components, `camelCase` for hooks/utils
- **File naming:** `PascalCase.tsx` for components, `camelCase.ts` for utilities
- **Page components:** Each `app/` route is a thin composer — delegates to `components/pages/`
- **Props interfaces:** Named `ComponentNameProps`, colocated in the same file
- **State management:** Redux Toolkit + RTK Query for server state
- **Styling:** Tailwind CSS with CTC teal CSS variables (`rgb(var(--ctc-*))`)
- **Animation:** Framer Motion for page transitions and micro-interactions
- **Testing:** Vitest (unit) + Playwright (E2E)

### Four-State Convention
Every data-driven component MUST handle:
1. **Loading** → `<LoadingSkeleton variant="..." />`
2. **Error** → `<ErrorState message={...} onRetry={...} />`
3. **Empty** → `<EmptyState icon="..." />`
4. **Normal** → Render data

## Project Metadata

- **Dev server port:** `3457` (configured in `playwright.config.ts`)
- **Next.js output:** `standalone` (configured in `next.config.js`)
- **Node version:** 20+
- **Package manager:** npm

```css
:root {
  --ctc-primary: 0 161 179;        /* #00a1b3 */
  --ctc-primary-dark: 0 122 136;   /* #007a88 */
  --ctc-primary-light: 26 127 212; /* #1a7fd4 */
  --ctc-secondary: 0 128 128;      /* #008080 */
  --ctc-accent: 108 99 255;        /* #6C63FF */
  --ctc-accent-alt: 255 107 139;   /* #FF6B8B */
}
```

Usage: `text-[rgb(var(--ctc-primary))]`, `bg-[rgb(var(--ctc-primary))]/10`

---

## Key Components

| Component | Purpose | State |
|-----------|---------|:-----:|
| `FusionPage` | CMS-backed page wrapper (two modes: fragment + data) | ✅ |
| `FusionProxy` | HTML fragment fetcher/renderer | ✅ |
| `FusionMiddleware` | Fragment-vs-data mode context provider | ✅ |
| `AuthGuard` | Protected route wrapper (redirects to /login) | ✅ |
| `DashboardRedirect` | Client-side redirect with loading state | ✅ |
| `Header` | Site header with nav + auth + notifications | ✅ |
| `Footer` | Site footer with link groups | ✅ |
| `NotificationBell` | Notification bell with unread count | ✅ |
| `NotificationDropdown` | Notification dropdown panel | ✅ |
| `LoadingSkeleton` | 6 loading variants (card, list, table, detail, profile, text) | ✅ |
| `ErrorState` | Error display with retry button | ✅ |
| `EmptyState` | Empty state with icon + action link | ✅ |

---

## Testing

```bash
# Unit tests (Vitest)
npm run test          # 354 tests passing

# E2E tests (Playwright)
npm run test:e2e
npm run test:e2e:ui           # Interactive mode
npm run test:e2e:report       # Show HTML report

# TypeScript typecheck
npx tsc --noEmit

# Build
npm run build
```

---

## Documentation References

| Topic | File |
|-------|------|
| Enhancement master plan | `./plan/FRONTEND_ENHANCEMENT_MASTER_PLAN.md` |
| FlyonUI integration plan | `./plan/FLYONUI_INTEGRATION_PLAN.md` |
| Responsive layout plan | `./plan/RESPONSIVE_LAYOUT_PLAN.md` |
| Component/pages plan | `./plan/COMPONENT_PAGES_PLAN.md` |
| E2E testing guide | `./docs/e2e-testing.md` |
| Visual regression guide | `./docs/visual-regression-testing.md` |
| Improvements plan | `./docs/IMPROVEMENTS_PLAN.md` |
| Fragment/Redux integration | `../../docs/FRAGMENT_REDUX_INTEGRATION_PLAN.md` |
| Prompt variations | `./PROMPTS.md` |
