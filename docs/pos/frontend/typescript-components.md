# 🔵 Components — `src/components/`

Reusable React components for POS. Use TailwindCSS + Framer Motion.

> **Customization level**: 🟢 Most are customizable — see per-component tags below.

## Component Index

| Component | Level | File | Purpose |
|-----------|-------|------|---------|
| `ChatSupport` | 🟢 | `ChatSupport.tsx` | Floating WebSocket chat widget |
| `DataTable` | 🟢 | `DataTable.tsx` | Sortable/filterable data table |
| `Invoice` | 🟢 | `Invoice.tsx` | A4 invoice preview |
| `Modal` | 🟢 | `Modal.tsx` | Generic modal dialog |
| `PageLayout` | 🔵 | `PageLayout.tsx` | Page wrapper with top bar + profile |
| `SideNav` | 🟢 | `SideNav.tsx` | Slide-out navigation panel |
| `Skeleton` | 🟢 | `Skeleton.tsx` | Loading placeholders |
| `StatusToast` | 🟢 | `StatusToast.tsx` | Toast notifications |
| `ProductCard` | 🟢 | `ProductCard.tsx` | Product display card |
| `DatePicker` | 🟢 | `DatePicker.tsx` | Date input component |
| `ConfirmDialog` | 🟢 | `ConfirmDialog.tsx` | Confirmation modal |
| `BackButton` | 🟢 | `BackButton.tsx` | Navigation back button |
| `LanguageToggle` | 🟢 | `LanguageToggle.tsx` | Language switcher |
| `ThemeToggle` | 🟢 | `ThemeToggle.tsx` | Dark/light mode toggle |
| `Receipt` | 🟢 | `Receipt.tsx` | Receipt preview |
| `KeyboardShortcutsModal` | 🟢 | `KeyboardShortcutsModal.tsx` | Keyboard shortcuts help |

## Usage Patterns

### PageLayout (Top Bar + Profile)

```tsx
import PageLayout from '../components/PageLayout';

<PageLayout
  title="My Page"
  showNav={true}          // Show hamburger menu + back button
  background="bg-slate-100 dark:bg-slate-900"
>
  {/* Page content */}
</PageLayout>
```

The top bar automatically shows:
- 🟢 Hamburger menu → opens SideNav
- 🟢 Back button → navigates to Home
- 🔵 Logo + page title
- 🔴 Profile button (only when auth is enabled + user logged in)

### ChatSupport

```tsx
<ChatSupport
  room="support-page"     // WebSocket room ID
  showTrigger={false}     // Hide floating button
  defaultOpen={true}      // Start expanded
/>
```

### DataTable

```tsx
<DataTable
  columns={[
    { key: 'name', label: 'Name', sortable: true },
    { key: 'price', label: 'Price', sortable: true },
  ]}
  data={products}
  searchPlaceholder="Search..."
  onSearch={(q) => filter(q)}
/>
```

## Adding a New Component

1. Create `src/components/MyComponent.tsx`
2. Follow existing conventions:
   - Use TailwindCSS classes (no inline styles)
   - Use Framer Motion for animations
   - Export as default
   - Add ARIA labels for accessibility
3. Import and use in pages

## Design Conventions

- **Hover**: Simple y-axis translation only (`whileHover={{ y: -4 }}`)
- **Colors**: TailwindCSS palette (teal-500 for primary, slate for neutral)
- **RTL**: Use `u-rtl-flip` class for icons that need mirroring
- **Dark mode**: Always provide both `dark:` variants
- **No IDs for styling**: Use BEM-like class names only

---

→ [Back to TypeScript docs](README.md)
