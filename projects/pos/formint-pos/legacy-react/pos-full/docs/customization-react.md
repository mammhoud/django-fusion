# POS — React Frontend Customization Guide

> **Path:** `src/` | **Stack:** React 19 + TypeScript 5.8 + Vite 7 + Tailwind CSS 4 + Framer Motion

---

## Customization Overview

The React frontend is designed for easy customization at multiple levels:

| Level | What | Effort | Risk |
|-------|------|--------|------|
| 🟢 **Styles** | Colors, fonts, spacing, dark/light mode | Low | None |
| 🟢 **i18n** | Add/modify translations, add new languages | Low | None |
| 🟡 **Pages** | Modify existing pages, add new routes | Medium | Low |
| 🟡 **Components** | 16 reusable UI components to customize | Medium | Low |
| 🔴 **Core** | Contexts, auth flow, app entry point | High | High |

---

## 🟢 Styling Customization

### CSS Custom Properties (Design Tokens)

All design tokens live in `src/styles/base/_variables.css`:

```css
:root {
  /* Primary palette */
  --pos-primary: #2563eb;       /* Blue */
  --pos-primary-hover: #1d4ed8;
  --pos-secondary: #059669;     /* Green */
  --pos-accent: #f59e0b;        /* Amber */
  --pos-danger: #dc2626;        /* Red */

  /* Surfaces */
  --pos-bg: #f8fafc;            /* Light mode background */
  --pos-surface: #ffffff;       /* Card/surface background */
  --pos-border: #e2e8f0;        /* Border color */

  /* Text */
  --pos-text: #1e293b;          /* Primary text */
  --pos-text-secondary: #64748b; /* Secondary text */

  /* Spacing & shape */
  --pos-radius: 8px;            /* Border radius */
  --pos-font: 'Inter', sans-serif;
}

/* Dark mode override */
.dark {
  --pos-bg: #0f172a;
  --pos-surface: #1e293b;
  --pos-border: #334155;
  --pos-text: #f1f5f9;
  --pos-text-secondary: #94a3b8;
}
```

### Tailwind Configuration

Edit `tailwind.config.js` to extend the theme:

```js
export default {
  content: ['./src/**/*.{ts,tsx}', './index.html'],
  theme: {
    extend: {
      colors: {
        'pos-primary': 'var(--pos-primary)',
        'pos-secondary': 'var(--pos-secondary)',
        // ...
      }
    }
  }
}
```

---

## 🟢 i18n Customization

### Adding a New Language

1. Create a new JSON file in `src/i18n/` (e.g., `es.json`)
2. Register it in `src/i18n/index.ts`:

```typescript
import es from './es.json';

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    fr: { translation: fr },
    ar: { translation: ar },
    es: { translation: es },  // ← New
  },
  // ...
});
```

3. Copy English translations as a template:
```bash
cp src/i18n/en.json src/i18n/es.json
```

4. Translate all values in `es.json`

5. Add language option to `LanguageToggle.tsx`

### Translation Format

```json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "search": "Search..."
  },
  "dashboard": {
    "title": "Dashboard",
    "totalSales": "Total Sales",
    "activeOrders": "Active Orders"
  }
}
```

Usage in components:
```tsx
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();
  return <h1>{t('dashboard.title')}</h1>;
}
```

---

## 🟡 Page Customization

### Modifying an Existing Page

All page components are in `src/pages/`. Each page follows a consistent structure:

```tsx
// src/pages/Home.tsx
import PageLayout from '../components/PageLayout';

function Home() {
  return (
    <PageLayout>
      <h1>Dashboard</h1>
      {/* Page content */}
    </PageLayout>
  );
}

export default Home;
```

To modify a page: edit the component directly. To replace it entirely: create a new component and update the route in `App.tsx`.

### Adding a New Page

1. Create `src/pages/NewPage.tsx`
2. Import it in `src/App.tsx`
3. Add a route:

```tsx
import NewPage from './pages/NewPage';

// In routeOrder:
const routeOrder = {
  // ...existing routes
  '/new-page': 22,  // Next available index
};

// In Routes:
<Route path="/new-page" element={
  <PageWrapper direction={direction} isFirstRender={isFirstRender.current}>
    <NewPage />
  </PageWrapper>
} />
```

4. Add navigation entry in `SideNav.tsx`

---

## 🟡 Component Customization

### Available Components

| Component | File | Customization |
|-----------|------|:---:|
| `PageLayout` | `PageLayout.tsx` | Sidebar width, topbar content, footer |
| `SideNav` | `SideNav.tsx` | Menu items, icons, collapse behavior |
| `DataTable` | `DataTable.tsx` | Column definitions, sort/filter behavior |
| `ProductCard` | `ProductCard.tsx` | Card layout, fields, actions |
| `Modal` | `Modal.tsx` | Size, animation, close behavior |
| `ConfirmDialog` | `ConfirmDialog.tsx` | Title, message, confirm/cancel actions |
| `ChatSupport` | `ChatSupport.tsx` | Chat bubble position, WebSocket config |
| `StatusToast` | `StatusToast.tsx` | Colors, duration, position |
| `Skeleton` | `Skeleton.tsx` | Loading placeholder shapes |
| `Invoice` | `Invoice.tsx` | Invoice layout, fields, print styles |
| `Receipt` | `Receipt.tsx` | Receipt layout, template selection |
| `ThemeToggle` | `ThemeToggle.tsx` | Icons, animation |
| `LanguageToggle` | `LanguageToggle.tsx` | Available languages |

### Extending a Component

Components accept props for customization:

```tsx
<DataTable
  columns={customColumns}
  data={myData}
  onSort={handleSort}
  onFilter={handleFilter}
  pageSize={25}
/>
```

---

## 🔴 Core Customization (Advanced)

### Auth Flow

The auth system lives in `src/contexts/AuthContext.tsx` and `src/pages/Auth.tsx`. The flow:

1. `App.tsx` checks `isAuthRequired` from `AuthContext`
2. If `null` → loading spinner
3. If `true` and not authenticated → show `Auth` page
4. If authenticated → show main app

**To modify auth:** override `AuthContext` methods or extend `Auth.tsx`. **Do not** modify the auth flow order in `App.tsx`.

### Route Transitions

Page transitions use Framer Motion with direction-aware animation. The `routeOrder` map in `App.tsx` determines transition direction (forward/backward). Add new routes to this map to enable transitions.

### Sidecar API Client

The API client is at `src/api/sidecar.ts`. All modules use the shared `request()` wrapper with timeout handling. To add new endpoints:

```typescript
// src/api/data.ts (or create a new module)
import { sidecar } from './sidecar';

export const data = {
  getNewEndpoint: () => sidecar.get<ResponseType>('/api/new-endpoint'),
};
```

---

## Related Docs

- [`START_HERE.md`](START_HERE.md) — Getting started
- [`customization-tauri.md`](customization-tauri.md) — Tauri/Rust backend customization
- [`i18n-conventions.md`](i18n-conventions.md) — Translation workflow
