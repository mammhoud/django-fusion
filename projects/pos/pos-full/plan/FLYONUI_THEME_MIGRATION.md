# POS Full — FlyonUI Integration & Theme Migration Plan

> **Plan file:** `projects/pos/pos-full/plan/FLYONUI_THEME_MIGRATION.md`
> **Created:** 2026-07-25 | **Branch:** `generic`
> **Parent:** `README.md` — Plans #2 + #3

---

## Overview

POS Full currently uses raw Tailwind CSS classes with indigo/purple accent colors
on several pages (Employees, Analytics, Recipes, etc.). This plan covers:

1. **FlyonUI integration** — Add FlyonUI as a Vite-compatible plugin for dropdowns, selects, modals
2. **CTC Teal theme migration** — Replace indigo/purple classes with CTC teal variables

---

## Phase A — FlyonUI Integration

### A.1 Install

```bash
cd projects/pos/pos-full
npm install flyonui
```

### A.2 Vite Configuration

Unlike LMS (Next.js + Tailwind v3), POS uses Vite. Add FlyonUI to `tailwind.config.js`:

```js
// tailwind.config.js
module.exports = {
  content: [
    './src/**/*.{ts,tsx}',
    './node_modules/flyonui/dist/*.js',
  ],
  plugins: [
    require('flyonui'),   // ← FlyonUI Tailwind plugin
  ],
};
```

### A.3 CSS Updates

```css
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* FlyonUI variant CSS */
@import 'flyonui/variants.css';

/* CTC Teal theme variables */
:root {
  --ctc-primary: 0 161 179;
  --ctc-primary-dark: 0 122 136;
  --ctc-accent: 108 99 255;
}
```

### A.4 FlyonUI JS Loader (Vite-specific)

Unlike Next.js (which uses `FlyonuiScript.tsx` + `usePathname`), Vite needs a
simpler approach — load FlyonUI JS once in `main.tsx`:

```tsx
// src/main.tsx
import 'flyonui/flyonui';

// Auto-init on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  if (window.HSStaticMethods?.autoInit) {
    window.HSStaticMethods.autoInit();
  }
});
```

For SPA navigation (React Router), re-init in `App.tsx`:

```tsx
// src/App.tsx — FlyonUI re-init on SPA navigation
import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

export function FlyonUIReinit() {
  const location = useLocation();
  const inited = useRef(false);

  useEffect(() => {
    if (inited.current) {
      setTimeout(() => window.HSStaticMethods?.autoInit(), 100);
    } else {
      inited.current = true;
    }
  }, [location.pathname]);

  return null;
}
```

### A.5 TypeScript Types

```ts
// src/global.d.ts
import { IStaticMethods } from 'flyonui/flyonui';
declare global {
  interface Window {
    HSStaticMethods: IStaticMethods;
  }
}
export {};
```

### A.6 Migrate Components to FlyonUI

| Component | Current | FlyonUI | Priority |
|-----------|---------|---------|:--------:|
| Notification/Status Toast | `StatusToast.tsx` | FlyonUI `notyf` | P1 |
| Dropdown menus | Custom `useState` toggle | `hs-dropdown` | P1 |
| Select inputs (category, type, status filters) | Native `<select>` | `hs-select` | P2 |
| Modals (add/edit forms) | `Modal.tsx` | `hs-modal` | P2 |
| Confirm dialogs | `ConfirmDialog.tsx` | FlyonUI modal + confirm | P2 |
| Tabs (Employees, Inventory, Reports) | Custom `useState` | `hs-tabs` | P3 |
| Sidebar navigation | `SideNav.tsx` | `hs-sidebar` | P3 |

---

## Phase B — CTC Teal Theme Migration

### B.1 Audit: Indigo/Purple Pages

| Page | Indigo Usage | Status |
|------|:-----------:|:------:|
| **Employees** | Heavy (`bg-indigo-500`, `text-indigo-500`, etc.) | ❌ |
| **Analytics** | Background gradient (`via-purple-100`) | ❌ |
| **Recipes** | Summary cards, buttons | ❌ |
| **Inventory** | Tab buttons, stats | ❌ |
| **Reports** | Tab buttons | ❌ |
| **Roles** | Cards, form elements | ❌ |
| **Payroll** | Header, button | ❌ |
| **Settings** | Save button (`bg-teal-500` — already CTC!) | ✅ |
| **Customers** | `bg-teal-500` buttons — already CTC! | ✅ |
| **Suppliers** | `bg-teal-500` buttons — already CTC! | ✅ |
| **Sale** | `bg-teal-500` — already CTC! | ✅ |

### B.2 Replacement Map

```css
/* ── Indigo → Teal ── */
bg-indigo-500 → bg-[rgb(var(--ctc-primary))]
text-indigo-500 → text-[rgb(var(--ctc-primary))]
hover:bg-indigo-600 → hover:bg-[rgb(var(--ctc-primary-dark))]
border-indigo-500 → border-[rgb(var(--ctc-primary))]
bg-indigo-500/10 → bg-[rgb(var(--ctc-primary))]/10
bg-indigo-100 → bg-[rgb(var(--ctc-primary))]/10
text-indigo-600 → text-[rgb(var(--ctc-primary-dark))]

/* ── Purple → Accent (optional — keep as accent or convert to teal) ── */
bg-purple-500 → bg-[rgb(var(--ctc-accent))]
via-purple-100 → via-[rgb(var(--ctc-primary))]/10
text-purple-500 → text-[rgb(var(--ctc-accent))]
bg-purple-500/20 → bg-[rgb(var(--ctc-accent))]/20
```

### B.3 Migration Order (By Page Complexity)

| # | Page | Lines | Indigo/Purple Refs | Priority |
|---|------|:-----:|:------------------:|:--------:|
| 1 | Employees | 650+ | ~25 | P0 (most references) |
| 2 | Analytics | 330+ | ~15 | P0 (background gradient) |
| 3 | Inventory | 770+ | ~20 | P1 |
| 4 | Recipes | 640+ | ~15 | P1 |
| 5 | Reports | 2400+ | ~20 | P1 |
| 6 | Roles | 200+ | ~10 | P2 |
| 7 | Payroll | 116+ | ~8 | P2 |
| 8 | KitchenDisplay | 169+ | ~5 | P3 |
| 9 | EmployeeSchedule | 112+ | ~8 | P3 |
| 10 | Transactions | 1600+ | ~10 | P3 |

### B.4 Verification

```bash
# After each page migration, verify no indigo/purple remains:
rg 'indigo-|purple-' src/pages/employees/ --no-filename

# Full audit:
rg 'indigo-|purple-' src/ --no-filename | wc -l
# Expected: 0 after completion
```

### B.5 E2E Theme Regression

Add visual regression test using the existing POMs:

```typescript
// ../pos-e2e/tests/visual/theme-regression.spec.ts
test('POS Full — CTC Teal Theme', async ({ page }) => {
  const pages = [
    '/employees', '/analytics', '/inventory', '/recipes',
    '/reports', '/roles', '/payroll', '/kitchen', '/schedule', '/transactions',
  ];

  for (const route of pages) {
    await page.goto(route);
    // Verify no indigo or purple classes in DOM
    const hasIndigo = await page.locator('[class*="indigo-"]').count();
    const hasPurple = await page.locator('[class*="purple-"]').count();
    expect(hasIndigo).toBe(0);
    expect(hasPurple).toBe(0);
  }
});
```

---

## Progress

| Phase | Step | Status | Effort |
|-------|------|:------:|:------:|
| A | Install FlyonUI | ⬜ | 0.5h |
| A | Configure Vite + Tailwind | ⬜ | 0.5h |
| A | CSS updates | ⬜ | 0.5h |
| A | JS loader in main.tsx + App.tsx | ⬜ | 0.5h |
| A | TypeScript types | ⬜ | 0.25h |
| A | Migrate components to FlyonUI | ⬜ | 4h |
| B | Audit pages | ⬜ | 0.5h |
| B | Migrate indigo→teal (10 pages) | ⬜ | 6h |
| B | Verification | ⬜ | 0.5h |
| B | E2E theme regression test | ⬜ | 1h |

**Total:** ~14 hours
