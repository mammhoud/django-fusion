# Architecture — Forge POS

## System Design

Forge POS is a **single-process desktop application** built with Tauri 2. The frontend (React 19 + TypeScript) communicates with the Rust backend through Tauri's `invoke()` IPC mechanism. There is no HTTP server, no API gateway, and no sidecar process.

---

## Data Flow

### Request Lifecycle

```
User Action (click button)
    │
    ▼
React Component (e.g., Sale.tsx)
    │
    ├── Form state managed via useState()
    ├── Validation (client-side)
    │
    ▼
invoke('command_name', { params })
    │
    ├── Tauri IPC bridge (JSON serialization)
    │
    ▼
Rust Command Handler (lib.rs)
    │
    ├── Diesel ORM query
    │
    ▼
SQLite Database (restaurant.db)
    │
    ▼
Diesel result → Rust struct → JSON
    │
    ▼
React Component → setState() → Re-render
    │
    ▼
User sees updated UI
```

### Example: Completing a Sale

```
User clicks "Complete Sale"
    │
    ▼
Sale.tsx: handleSell()
    ├── validate cart (not empty)
    ├── build NewSaleData + NewSaleItemData[]
    │
    ▼
invoke('add_sale', { sale, items })
    │
    ▼
Rust: fn add_sale(invoke, sale, items)
    ├── BEGIN TRANSACTION
    ├── INSERT INTO sales (...)
    ├── FOR EACH item: INSERT INTO sale_items (...)
    ├── COMMIT
    │
    ▼
Return Sale ID
    │
    ▼
React: setReceiptData(...), setShowSuccessDialog(true)
    ├── Receipt component renders
    ├── User can print or download PDF
    │
    ▼
loadData({ quiet: true })  // background refresh
```

---

## FlyonUI Integration

FlyonUI is integrated as a **Tailwind CSS v4 plugin** providing semantic component classes.

### CSS Setup (`src/index.css`)

```css
@import "tailwindcss";
@plugin "flyonui";
@import "../node_modules/flyonui/variants.css";
@source "../node_modules/flyonui/dist/index.js";
@plugin "@iconify/tailwind4";
```

### JS Setup (`src/main.tsx`)

```tsx
import "flyonui/flyonui";
```

### Available FlyonUI Component Classes

| Component | Class Pattern | Usage |
|-----------|---------------|-------|
| **Badge** | `badge`, `badge-primary`, `badge-success`, `badge-warning`, `badge-error`, `badge-info` | Status indicators, labels |
| **Badge Styles** | `badge-soft`, `badge-outline` | Alternate badge appearances |
| **Badge Sizes** | `badge-xs`, `badge-sm`, `badge-md`, `badge-lg`, `badge-xl` | Size variants |
| **Button** | `btn`, `btn-primary`, `btn-secondary`, `btn-accent`, `btn-ghost`, `btn-outline` | All action buttons |
| **Button Styles** | `btn-soft`, `btn-gradient`, `btn-text`, `btn-active`, `btn-disabled` | Button style variants |
| **Button Sizes** | `btn-xs`, `btn-sm`, `btn-md`, `btn-lg`, `btn-xl` | Size variants |
| **Button Modifiers** | `glass`, `btn-wide`, `btn-block`, `btn-circle`, `btn-square` | Shape/layout modifiers |
| **Icons** | `icon-[tabler--icon-name]` | Tabler icons via Iconify |

### Data Attributes (Interactive Components)

FlyonUI provides JavaScript-enhanced components via `data-*` attributes:

| Data Attribute | Component | React Integration |
|---------------|-----------|-------------------|
| `data-toggle="modal"` | Modal dialogs | Via `import "flyonui/flyonui"` |
| `data-hs-overlay` | Overlay/off-canvas | Direct JS import handles DOM events |
| `data-hs-collapse` | Collapse/accordion | Works with JS-managed state |

> **Note:** Forge POS primarily uses **React state** for interactivity rather than FlyonUI's data-attribute-driven JS. FlyonUI's CSS classes (badge, btn) are used via semantic class names, while complex interactive components (modals, toasts) use React components.

---

## Theme System

### Architecture

```
data-theme="default|corporate|luxury|pastel|cyberpunk"
    │
    ▼
themes.css ───> CSS custom properties (--theme-primary, etc.)
    │
    ▼
theme-overrides.css ───> Tailwind color token overrides (--color-teal-*, etc.)
    │
    ▼
All components using Tailwind classes (bg-teal-500, text-slate-900)
automatically pick up the variant's palette
```

### Theme Context (React)

```tsx
// ThemeContext provides:
{ theme, setTheme, mode, toggleMode }
// theme = 'default' | 'corporate' | 'luxury' | 'pastel' | 'cyberpunk'
// mode = 'light' | 'dark'

// Applied to <html>:
<html data-theme="corporate" class="dark"> ... </html>
```

### Theme Variants

| Variant | Light Primary | Dark Primary | Best For |
|---------|--------------|--------------|----------|
| **Default** | Indigo (#6366f1) | Indigo | General use |
| **Corporate** | Blue (#2563eb) | Royal Blue | Business environments |
| **Luxury** | Gold (#ca8a04) | Amber (#eab308) | Premium restaurants |
| **Pastel** | Pink (#db2777) | Light Pink (#f472b6) | Cafes, bakeries |
| **Cyberpunk** | Magenta (#cc00cc) | Neon Pink (#ff00ff) | Gaming centers, tech spots |

---

## Component Architecture

### Page → Component Hierarchy

```
Page Layout (PageLayout)
├── SideNav (navigation + shortcuts)
├── Page Content (route-specific)
│   ├── DataTable (reusable table)
│   ├── Modal (dialogs)
│   ├── ConfirmDialog (delete confirmations)
│   ├── StatusToast (notifications)
│   └── Form elements (FlyonUI-inspired)
└── ChatSupport (floating widget)
```

### Context Providers (wrapping order in main.tsx)

```
<ThemeProvider>
  <LanguageProvider>
    <AuthProvider>
      <App />
    </AuthProvider>
  </LanguageProvider>
</ThemeProvider>
```

### Routing Structure

```
<Router>
  <AnimatedRoutes>
    /              → Home
    /manager       → ProductManager
    /sale          → Sale
    /analytics     → Analytics
    /transactions  → Transactions
    /inventory     → Inventory
    /employees     → Employees
    /recipes       → Recipes
    /reports       → Reports
    /settings      → Settings
    /about         → About
    /customers     → Customers
    /suppliers     → Suppliers
    /kitchen       → KitchenDisplay
    /schedule      → EmployeeSchedule
    /payroll       → Payroll
    /receipt-templates → ReceiptTemplates
    /tax-reports   → TaxReports
    /roles         → Roles
    /support-chat  → SupportChat
    /invoice       → InvoicePage
```

### Page Transitions

All routes are wrapped in `AnimatePresence` with `popLayout` mode for smooth spring-based sliding transitions. Direction is determined by the route's position in the ordering map (`src/App.tsx`).

---

## State Management

Forge POS uses **React useState/useEffect** for component-local state. There is no global state store (Zustand libraries are installed but unused in this edition).

### Data Flow Patterns

| Pattern | Usage | Example |
|---------|-------|---------|
| **useState + useEffect** | Page-level data loading | `loadData()` in Sale.tsx |
| **Context** | Global shared state | Theme, Auth, Language |
| **Custom Hooks** | Reusable logic | `useDebouncedSearch`, `useStatusToast` |

---

## Internationalization (i18n)

- **Library:** react-i18next + i18next
- **Languages:** English (en), Arabic (ar), French (fr), German (de), Spanish (es)
- **RTL Support:** Automatic direction switching via `[dir="rtl"]` on `<html>`
- **Key Structure:** `namespace.key.subkey` — e.g., `t('sale.totalAmount')`
- **Validation:** CI workflow checks all locale files match `en.json` keys

### Locale Files

```
src/i18n/
├── en.json    (reference — 926 keys)
├── ar.json    (Arabic — RTL)
├── fr.json    (French)
├── de.json    (German)
├── es.json    (Spanish)
└── index.ts   (i18next configuration)
```
