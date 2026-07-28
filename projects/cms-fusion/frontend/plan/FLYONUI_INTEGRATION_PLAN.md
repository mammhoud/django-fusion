# LMS Front-End — FlyonUI Integration Plan

> **Plan file:** `projects/lms/front-end/plan/FLYONUI_INTEGRATION_PLAN.md`
> **Created:** 2026-07-25 | **Branch:** `generic`
> **Parent plan:** [`FRONTEND_ENHANCEMENT_MASTER_PLAN.md`](./FRONTEND_ENHANCEMENT_MASTER_PLAN.md) — Phase 2

---

## Overview

FlyonUI is a free, open-source Tailwind CSS component library that provides
80+ prebuilt components with semantic class names, JavaScript interactions,
and built-in accessibility. This plan covers integrating FlyonUI into the
LMS front-end (Next.js 14 + Tailwind CSS 3) and migrating existing dropdown
and select components.

**Reference:** https://flyonui.com/docs/framework-integrations/nextjs/

---

## Step-by-Step Integration

### Step 1 — Install FlyonUI

```bash
cd projects/lms/front-end
npm install flyonui
```

**Verification:**
```bash
node -e "console.log(require('flyonui/package.json').version)"
# Expected: 1.x.x
```

---

### Step 2 — Update `globals.css`

**Current state:** `src/app/globals.css` uses Tailwind CSS v3 directives
(`@tailwind base`, `@tailwind components`, `@tailwind utilities`).

**After FlyonUI:** Must add `@plugin "flyonui"` and variant imports.

```css
/* src/app/globals.css — AFTER FlyonUI integration */

/* ── Tailwind CSS v3 base directives (KEPT for backward compat) ── */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* ── FlyonUI plugin (v3-compatible) ── */
/* NOTE: With Tailwind v3, FlyonUI is added as a plugin in tailwind.config.js,
   NOT via @plugin directive (that's Tailwind v4 syntax). */

/* ── FlyonUI variant CSS ── */
@import "flyonui/variants.css";

/* ── FlyonUI JS source scanning ── */
/* (Tailwind v3 uses content: in tailwind.config.js for this) */

/* ── Fusion CMS custom theme (KEPT — all existing layers) ── */
@layer base {
  :root {
    --ctc-primary: 0 161 179;
    --ctc-primary-dark: 0 122 136;
    --ctc-primary-light: 26 127 212;
    --ctc-secondary: 0 128 128;
    --ctc-accent: 108 99 255;
    --ctc-accent-alt: 255 107 139;
  }
  /* ... rest of existing styles ... */
}
```

**⚠️ IMPORTANT — Tailwind v3 vs v4:**
The FlyonUI Next.js docs show Tailwind v4 syntax (`@plugin "flyonui"`,
`@import "tailwindcss"`). The LMS project uses **Tailwind v3** (`@tailwind`
directives, `tailwind.config.js`). For v3, FlyonUI is added as a **plugin**
in `tailwind.config.js`, not via `@plugin` in CSS.

---

### Step 3 — Update `tailwind.config.js`

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{ts,tsx}',
    './node_modules/flyonui/dist/*.js',  // ← FlyonUI JS components
  ],
  theme: {
    extend: {
      colors: {
        ctc: {
          primary: '#00a1b3',
          'primary-dark': '#007a88',
          'primary-light': '#1a7fd4',
          secondary: '#008080',
          accent: '#6C63FF',
          'accent-alt': '#FF6B8B',
        },
      },
      fontFamily: {
        heading: ['Urbanist', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('flyonui'),  // ← FlyonUI Tailwind v3 plugin
  ],
};
```

---

### Step 4 — Create `FlyonuiScript.tsx`

**Path:** `src/components/FlyonuiScript.tsx`

```tsx
'use client';

import { usePathname } from 'next/navigation';
import { useEffect } from 'react';

/**
 * FlyonUI JavaScript loader.
 *
 * Dynamically imports flyonui/flyonui.js on first render, then calls
 * HSStaticMethods.autoInit() on every route change to re-initialize
 * FlyonUI components (dropdowns, selects, etc.) on newly rendered pages.
 *
 * FlyonUI requires this because its components use data-* attributes
 * that need JavaScript initialization (e.g., hs-dropdown, hs-select).
 */
async function loadFlyonUI() {
  return import('flyonui/flyonui');
}

export default function FlyonuiScript() {
  const path = usePathname();

  useEffect(() => {
    const initFlyonUI = async () => {
      await loadFlyonUI();
    };
    initFlyonUI();
  }, []);

  useEffect(() => {
    setTimeout(() => {
      if (
        window.HSStaticMethods &&
        typeof window.HSStaticMethods.autoInit === 'function'
      ) {
        window.HSStaticMethods.autoInit();
      }
    }, 100);
  }, [path]);

  return null;
}
```

**Note on specific components (optimization):**
For production, import only the needed JS modules to reduce bundle size:

```tsx
// Instead of: import('flyonui/flyonui')
// Import only what you need:
async function loadFlyonUI() {
  await import('flyonui/dist/dropdown.js');
  await import('flyonui/dist/select.js');
  // add more as needed...
}
```

---

### Step 5 — Create `global.d.ts`

**Path:** `global.d.ts` (project root)

```ts
// global.d.ts
import { IStaticMethods } from 'flyonui/flyonui';

declare global {
  interface Window {
    HSStaticMethods: IStaticMethods;
  }
}

export {};
```

---

### Step 6 — Wire in `layout.tsx`

Add `<FlyonuiScript />` to the root layout's `<body>`:

```tsx
// src/app/layout.tsx
import FlyonuiScript from '@/components/FlyonuiScript';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <ErrorBoundary>
            <div className="flex flex-col min-h-screen">
              <Header />
              <main className="flex-1">{children}</main>
              <Footer />
            </div>
          </ErrorBoundary>
        </Providers>
        <FlyonuiScript />
      </body>
    </html>
  );
}
```

---

## Post-Integration Verification Checklist

- [ ] `npm run dev` starts without errors
- [ ] `npm run build` completes successfully
- [ ] Browser DevTools → Network tab: `flyonui.js` loads (or specific component JS)
- [ ] Browser DevTools → Elements: FlyonUI CSS classes visible (e.g., `hs-dropdown`)
- [ ] No console errors related to `HSStaticMethods`
- [ ] Existing E2E tests pass: `npm run test:e2e`
- [ ] Existing Vitest tests pass: `npm run test`
- [ ] No visual regressions — compare screenshots before/after
- [ ] Tailwind purge didn't strip FlyonUI classes (`content:` paths correct)

---

## Component Migration Order

| Order | Component | FlyonUI Primitive | Effort |
|:-----:|-----------|-------------------|:------:|
| 1 | `NotificationBell.tsx` | `hs-dropdown` | Low |
| 2 | `NotificationDropdown.tsx` | `hs-dropdown-menu` items | Low |
| 3 | `Header.tsx` mobile menu | `hs-drawer` (offcanvas) | Medium |
| 4 | `RegistrationPage` role buttons | `hs-select` | Low |
| 5 | `LanguageSwitcher.tsx` | `hs-dropdown` | Low |
| 6 | Dashboard sidebar | `hs-sidebar` | High |
| 7 | Course filters (new) | `hs-advanced-select` | Medium |
| 8 | Course search (new) | `hs-combo-box` | Medium |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Tailwind v3 vs FlyonUI v4 docs | Build errors if using v4 `@plugin` syntax | Use v3 `tailwind.config.js` plugin approach |
| CTC theme CSS conflicts | FlyonUI may override custom classes | Add `!important` or increase specificity on CTC classes |
| Bundle size increase | Slower page load | Use per-component JS imports (Step 4 optimization) |
| FlyonUI JS not initializing on SPA nav | Dropdowns broken after client-side navigation | `useEffect([path])` + `autoInit()` handles this |
| Existing E2E tests break | Selectors may change with FlyonUI markup | Update Playwright selectors after migration |

---

## Progress

| Step | Status | Notes |
|:----:|:------:|-------|
| 1 — Install npm package | ⬜ | `npm install flyonui` |
| 2 — Update globals.css | ⬜ | Add variant import |
| 3 — Update tailwind.config.js | ⬜ | Add plugin + content paths |
| 4 — Create FlyonuiScript.tsx | ⬜ | Client-side loader |
| 5 — Create global.d.ts | ⬜ | TypeScript types |
| 6 — Wire in layout.tsx | ⬜ | Add `<FlyonuiScript />` |
| Verification checklist | ⬜ | Build + test + visual check |
| Component migration | ⬜ | 8 components in order |

---

*Refer to [FlyonUI Next.js docs](https://flyonui.com/docs/framework-integrations/nextjs/) for the latest integration guide.*