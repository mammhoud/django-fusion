# ARCHIVED — COMPLETED (as of 2026-08-02)

> This plan has been fully implemented (see forge-pos CHANGELOG).
> Moved from `docs/plans/pos/` on 2026-08-02. Kept for historical reference only.

---

# Forge POS — UI Enhancement Master Plan
> **Tags:** #pos #forge-pos #ui #tauri

> **Generated:** 2026-07-30 | **Scope:** Frontend (React/TypeScript/Tailwind v4/FlyonUI)

---

## 1. Unified Theme Color System

### 1.1 CSS Variable Architecture
**What:** Replace all hardcoded Tailwind color classes (`bg-rose-100`, `text-amber-500`, etc.) with FlyonUI semantic CSS variables (`--color-primary`, `--color-secondary`, etc.) tied to the active theme variant.

**Why:** Currently, components like `ProductCard` and menu items use 10 separate hardcoded color presets per component. These don't adapt when the user switches theme variants (corporate/luxury/pastel/cyberpunk). The theme variants already define these semantic colors in `index.css` — we need to use them.

**Files affected:**
- `src/components/ProductCard.tsx` — Replace `PRODUCT_CARD_COLORS` array using fixed Tailwind classes with theme-adaptive classes using `bg-primary/10`, `border-primary/30`, `text-primary`
- `src/components/SideNav.tsx` — Replace hardcoded gradient classes on nav items with semantic color classes
- `src/pages/Home.tsx` — Replace hardcoded gradient classes on MENU_ITEMS with semantic color classes
- `src/components/StatCard.tsx` — Already uses semantic mapping, verify coverage
- `src/components/Card.tsx` — Already uses `bg-base-100`, verify border color consistency
- `src/styles/base/_variables.css` — Add `--color-border`, `--color-button-text`, `--color-category-title` variables
- `src/styles/pos-theme.css` — Update to reference FlyonUI CSS variables

**Implementation:**
```css
/* Add to _variables.css */
:root {
  --color-border: oklch(var(--bc) / 0.15);
  --color-button-primary-text: var(--color-primary-content);
  --color-button-secondary-text: var(--color-secondary-content);
  --color-category-title: oklch(var(--bc) / 0.6);
}

/* Update ProductCard colors to be theme-adaptive */
const PRODUCT_CARD_THEME_COLORS = [
  'primary', 'secondary', 'info', 'success', 'warning', 'error', 'neutral'
];
```

### 1.2 Border Colors Unification
**What:** All borders use `border-base-300/50` (theme's base-300 at 50% opacity) consistently across all components.

**Files affected:** All page components, Card.tsx, Modal.tsx, ProductCard.tsx, DataTable.tsx

### 1.3 Button Colors Unification
**What:** All buttons reference semantic theme colors:
- Primary action buttons → `bg-primary text-primary-content`
- Secondary/danger → `bg-error text-error-content`
- Ghost buttons → `bg-transparent border border-base-300 text-base-content`
- Category/tab buttons → `bg-base-200 text-base-content`

**Files affected:** Every page component (`Recipes.tsx`, `Inventory.tsx`, `ProductManager.tsx`, `Settings.tsx`, etc.)

---

## 2. Component Text Alignment & Layout

### 2.1 Card Component (Dashboard)
**What:** Ensure all dashboard cards have consistent text alignment:
- Title: `text-sm font-semibold text-base-content/80`
- Value: `text-2xl font-bold text-base-content`
- Description/delta: `text-xs text-base-content/50`
- Icons: 24px, aligned top-right in stat-figure area
- Use Iconify icons via `<span className="icon-[tabler--{name}] w-6 h-6" />` pattern

**Files affected:**
- `src/pages/Home.tsx` — All KPI stat cards
- `src/components/StatCard.tsx` — Verify stat-title, stat-value, stat-desc spacing
- `src/pages/Analytics.tsx` — Analytics stat cards

### 2.2 All Components Text Alignment Audit
**What:** Systematically verify text alignment in:
- Product cards (name centered, price aligned)
- Recipe cards (cost analysis grid alignment)
- Transaction table (column alignment)
- Employee cards
- Settings form labels
- Modal form layouts

---

## 3. Theme Toggle → Select Box

### 3.1 Replace Current Toggle
**What:** Replace the current `ThemeToggle.tsx` (3-position sliding knob: light/dark/system) with a clean select dropdown.

**Design:**
- Compact select box showing current mode icon + label
- Dropdown with 3 options: ☀️ Light, 🌙 Dark, 🖥️ System
- Matches the `LanguageToggle.tsx` dropdown pattern
- Uses FlyonUI select styling with theme-adaptive colors

**File:** `src/components/ThemeToggle.tsx` (rewrite)
**Update:** `src/components/SideNav.tsx` (import unchanged, component interface stays same)

### 3.2 Theme Variant Selector
**What:** Add a compact theme variant picker next to the theme mode selector:
- Dropdown: Default, Corporate, Luxury, Pastel, Cyberpunk
- Shows color preview swatch next to each option
- Persists to localStorage

**File:** New component `src/components/ThemeVariantSelect.tsx`
**Update:** `src/contexts/ThemeContext.tsx` — already supports variants

---

## 4. Image Container → Circle

### 4.1 ProductCard Image
**What:** Change product image container from `rounded-lg` to `rounded-full` (circle).

**File:** `src/components/ProductCard.tsx`
```diff
- <div className="w-12 h-12 mb-1.5 rounded-lg overflow-hidden ...">
+ <div className="w-12 h-12 mb-1.5 rounded-full overflow-hidden ...">
```

### 4.2 Settings Logo
**What:** Change restaurant logo preview to circle.

**File:** `src/pages/Settings.tsx`
```diff
- <div className="w-20 h-20 rounded-lg overflow-hidden ...">
+ <div className="w-20 h-20 rounded-full overflow-hidden ...">
```

### 4.3 All Avatar/Image Containers
**What:** Find and update all image containers:
- Employee avatars → circle
- Customer avatars → circle  
- Product images in Sale page → circle
- Dashboard logo → circle

---

## 5. Product Grid — More Columns

### 5.1 ProductManager Grid
**What:** Increase product grid density from 4-5 columns to 6-8 columns on wide screens.

**File:** `src/pages/ProductManager.tsx`
```diff
- grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6
+ grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-7 2xl:grid-cols-8
```

### 5.2 Sale Page Product Grid
**File:** `src/pages/Sale.tsx`
```diff
- grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5
+ grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-7
```

### 5.3 Recipe Cards Grid
**File:** `src/pages/Recipes.tsx`
```diff
- grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 3xl:grid-cols-5
+ grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 3xl:grid-cols-6
```

---

## 6. Recipes Page → Notes Page Enhancement

### 6.1 Add Notes Field
**What:** Add a `notes` section to each recipe that persists with the recipe data. Each note has:
- Title
- Content (text area)
- Category (dropdown from predefined categories)
- Created/updated timestamps
- Template support (reuse note templates)

**Backend (Rust):**
- Add `notes` table to SQLite schema: `id, recipe_id, title, content, category, created_at, updated_at`
- Add `notes` field to Recipe struct
- Add Tauri commands: `add_recipe_note`, `update_recipe_note`, `delete_recipe_note`, `get_recipe_notes`

**Frontend:**
- Add Notes tab/section to the recipe detail view
- Note templates: "Preparation Steps", "Chef Tips", "Allergen Info", "Plating Guide"
- Category color coding matching the theme

**Files affected:**
- `src-tauri/migrations/` — New migration for notes table
- `src-tauri/src/db/models.rs` — Notes model
- `src-tauri/src/db/schema.rs` — Schema update
- `src-tauri/src/lib.rs` — New commands
- `src/pages/Recipes.tsx` — Add Notes UI section
- `src/types.ts` — New RecipeNote type

---

## 7. RTL Support Enhancement

### 7.1 Current State
The project already has:
- `LanguageContext` that sets `dir="rtl"` on `<html>` for Arabic
- `rtl:` Tailwind variant defined in `index.css`
- Complete Arabic translations in `ar.json`
- `LanguageToggle` component

### 7.2 Enhancements Needed
**What:** Ensure every component is RTL-aware:

| Component | Issue | Fix |
|-----------|-------|-----|
| `SideNav.tsx` | Left border should become right border in RTL | Add `rtl:left-auto rtl:right-0 rtl:border-l rtl:border-r-0` |
| `ProductCard.tsx` | Icons, padding, text alignment | Add `rtl:` variants for flex direction and text alignment |
| `StatCard.tsx` | Stat figure position, border-left | `rtl:border-l-0 rtl:border-r-4` |
| `DataTable.tsx` | Column alignment | Add `rtl:text-right` to table cells |
| `Modal.tsx` | Close button position | Ensure close button stays top-right |
| `DatePicker.tsx` | Calendar layout | RTL calendar grid layout |
| All input fields | Text direction | Add `rtl:text-right` to inputs when in RTL mode |
| `Home.tsx` | Menu card layout | Ensure flex direction adapts |

### 7.3 STR (String) Support
**What:** Ensure all user-facing strings are wrapped in `t()` calls and have translations in all 5 language files.

**Verification:** Run `grep -r '"' src/pages/ src/components/ | grep -v 't(' | grep -v 'className' | grep -v '//'` to find untranslated strings.

---

## 8. Stats Card Enhancements

### 8.1 Current State
`StatCard` already supports:
- Semantic colors mapped from gradient names
- Sparkline charts via Recharts
- Animated entrance

### 8.2 Enhancements Needed
- **More color variants**: Add `accent`, `neutral` as valid semantic colors
- **Icon size consistency**: All icons should be `w-6 h-6` (currently varies)
- **Loading skeleton**: Add `StatCardSkeleton` for loading states
- **Compact mode**: Add `size="compact"` for grid views with smaller padding
- **Border-left color fix**: Use proper CSS variable instead of Tailwind class

**File:** `src/components/StatCard.tsx`

---

## 9. Dashboard Card Enhancements

### 9.1 Quick Access Cards
**What:** Enhance the 4 merged quick-access cards on the Home page:
- Use Iconify icons consistently (already using icon-[tabler--*])
- Ensure text layout: icon (36px) → title → description → arrow
- Add hover gradient animation
- Make cards fully clickable (pointer cursor, keyboard accessible)

**File:** `src/pages/Home.tsx`

### 9.2 KPI Stats Row
**What:** The top stats row should:
- Use 4-5 StatCards in a responsive grid
- Each with sparkline data
- Proper text hierarchy: label → value → delta → sparkline

---

## 10. Translations Completion

### 10.1 Audit Current Coverage
**What:** Check all 5 language files (en, ar, fr, de, es) and ensure all translation keys exist in all files.

**Missing translations to add:**
| Key | Status |
|-----|--------|
| `nav.notes` (new) | Add to all 5 files |
| `notes.*` (new section) | Add to all 5 files |
| `settings.appearanceTab.themeDropdown` | Add if not exists |
| `theme.variant.*` labels | Verify in all files |

### 10.2 Currency Translation
**What:** Current `common.currency` is hardcoded to "USD"/"دولار". Make it dynamic:
- Read currency from Settings
- Display currency symbol (not name) in transaction/sale contexts
- Display currency name in settings selector

---

## 11. Default Currency & Currency Selection

### 11.1 Currency Initialization
**What:** The Settings page already has a currency selector. Ensure:
- Default currency reads from Settings model on app init
- Currency symbol (`$`, `€`, `£`, etc.) is used in all price displays
- Currency is passed via context to all components

**Files affected:**
- `src/pages/Settings.tsx` — Already has currency selector, verify it persists
- `src/types.ts` — Settings has `currency?` field
- `src/contexts/AuthContext.tsx` — Add currency to user context or create CurrencyContext
- All pages displaying prices — Use `currency` from settings

### 11.2 Currency Context
**What:** Create a `CurrencyContext` that provides:
- `currency: string` — The active currency code
- `currencySymbol: string` — The currency symbol
- Reads from Settings on mount

**File:** New `src/contexts/CurrencyContext.tsx`

---

## 12. Iconify Complete Integration

### 12.1 Current State
The project already uses:
- `@iconify/tailwind4` plugin in `index.css`
- Tabler icons via `icon-[tabler--{name}]` utility classes
- An `Ic()` helper function for creating icon components

### 12.2 Complete Integration
**What:** Ensure ALL icons use the Iconify pattern consistently:
- Replace any remaining emoji icons (like 🎨, 💼 in ThemeContext) with Iconify equivalents
- Replace any SVG-file-based icons with Iconify inline icons
- Add icon size consistency: `w-4 h-4` for inline, `w-5 h-5` for nav, `w-6 h-6` for stat cards

**Files to update:**
- `src/contexts/ThemeContext.tsx` — Replace emoji icons in THEME_VARIANTS
- `src/pages/Home.tsx` — Verify MENU_CATEGORIES icons use Iconify
- `src/components/SideNav.tsx` — Already uses Iconify ✅
- `src/pages/ThemeStudio.tsx` — Check for emoji icons
- `src/pages/Settings.tsx` — Check appearance tab icons

### 12.3 Icon Mapping Reference
Based on [flyonui.com/docs/customization/icons/](https://flyonui.com/docs/customization/icons/), the standard pattern is:
```tsx
<span className="icon-[tabler--{icon-name}] w-5 h-5" />
```

Theme variant emoji → Iconify replacements:
| Emoji | Iconify |
|-------|---------|
| 🎨 | `icon-[tabler--palette]` |
| 💼 | `icon-[tabler--briefcase]` |
| 👑 | `icon-[tabler--crown]` |
| 🌸 | `icon-[tabler--flower]` |
| ⚡ | `icon-[tabler--bolt]` |

---

## Implementation Order (Priority)

### Phase 1 — Quick Wins (1-2 hours)
1. Image containers → circles (Section 4)
2. Product grid → more columns (Section 5)
3. Theme variant emoji → Iconify icons (Section 12.3)
4. ThemeToggle → select box (Section 3.1)

### Phase 2 — Theme Integration (2-3 hours)
5. Unified theme color system (Section 1)
6. Border/button colors unification (Sections 1.2-1.3)
7. Stats card enhancements (Section 8)

### Phase 3 — Layout & Text (2-3 hours)
8. Dashboard card enhancements (Section 9)
9. Component text alignment audit (Section 2)
10. Translation completion (Section 10)

### Phase 4 — New Features (3-5 hours)
11. Recipes → Notes page enhancement (Section 6)
12. Currency context & initialization (Section 11)
13. RTL support enhancement (Section 7)

### Phase 5 — Polish (1-2 hours)
14. Iconify complete integration pass (Section 12)
15. Full visual regression test with all 5 themes × 2 modes (light/dark)

---

## Testing Strategy

### Per-phase validation:
```bash
# TypeScript check
cd projects/pos/forge-pos && npx tsc --noEmit

# Vitest unit tests
cd projects/pos/forge-pos && npx vitest run

# Lint
cd projects/pos/forge-pos && npx eslint src/ --ext .ts,.tsx

# Build check
cd projects/pos/forge-pos && npm run build
```

### Visual testing:
- Visit each page in light + dark mode
- Switch through all 5 theme variants
- Test RTL by switching to Arabic
- Verify mobile responsiveness

---

## Files Summary

| File | Changes Needed |
|------|---------------|
| `src/index.css` | Add CSS variables for unified colors |
| `src/styles/base/_variables.css` | Add border/button/category CSS variables |
| `src/styles/pos-theme.css` | Reference FlyonUI variables |
| `src/components/ThemeToggle.tsx` | Rewrite as select dropdown |
| `src/components/ThemeVariantSelect.tsx` | New component |
| `src/components/ProductCard.tsx` | Circle images, theme-adaptive colors, more columns |
| `src/components/StatCard.tsx` | Compact mode, skeleton, color variants |
| `src/components/Card.tsx` | Verify consistency |
| `src/components/SideNav.tsx` | RTL fixes, theme-adaptive colors |
| `src/pages/Home.tsx` | RTL fixes, theme-adaptive colors, card layout |
| `src/pages/Recipes.tsx` | Notes section, more columns |
| `src/pages/ProductManager.tsx` | More columns |
| `src/pages/Sale.tsx` | Circle images, more columns |
| `src/pages/Settings.tsx` | Circle logo, verify currency |
| `src/contexts/ThemeContext.tsx` | Iconify icons for variants |
| `src/contexts/CurrencyContext.tsx` | New context |
| `src/i18n/en.json` | Notes translations, theme variant translations |
| `src/i18n/ar.json` | Notes translations, theme variant translations |
| `src/i18n/fr.json` | Notes translations, theme variant translations |
| `src/i18n/de.json` | Notes translations, theme variant translations |
| `src/i18n/es.json` | Notes translations, theme variant translations |
| `src/types.ts` | RecipeNote type, CurrencyContext type |
| `src-tauri/migrations/` | New notes table migration |
| `src-tauri/src/db/models.rs` | Notes model |
| `src-tauri/src/lib.rs` | Notes Tauri commands |

---

## 13. Settings Enhancements (from prompt)

### 13.1 Add Theme Section Navigation
**What:** Add dedicated theme section in Settings with navigation to sub-sections:
- Appearance (current theme mode, variant selector, customization)
- Theme Studio (preview mode)

**File:** `src/pages/Settings.tsx`

### 13.2 Merge Theme Showcase with Theme Studio
**What:** Merge `ThemeShowcase.tsx` into `ThemeStudio.tsx` as a modal preview.
- Add "Preview" button that opens a modal showing theme applied to sample components
- Remove standalone `ThemeShowcase` page
- The modal preview shows: buttons, cards, product grid, nav — all themed

**Files:**
- Merge `ThemeShowcase.tsx` → `ThemeStudio.tsx` (as modal)
- Delete standalone `ThemeShowcase.tsx` component

---

## 14. Receipt Templates → Optional Notes

### 14.1 Merge Receipt Templates with Notes
**What:** Receipt templates become optional note templates under the Notes system.
- Each receipt template is a note with `category: "receipt"`
- Users can create/edit/delete receipt templates as notes
- The receipt printing system reads from notes with category `receipt`

**Files:**
- `src/pages/Recipes.tsx` — Add receipt category to notes
- `src/pages/Settings.tsx` — Remove standalone receipt templates section
- `src/types.ts` — Add `"receipt"` to note categories

---

## 15. Support Chat (Email-Based)

### 15.1 Architecture
**What:** Support chat that sends emails — no APIs or MCP services needed.
- Reads `SUPPORT_EMAIL` from environment variable
- If `SUPPORT_EMAIL` is set AND MCP settings are NOT configured: show chat button
- If MCP settings are configured: use MCP (future enhancement)
- If neither is set: hide support chat entirely

**Trigger logic:**
```typescript
const showSupportChat = (
  Boolean(process.env.SUPPORT_EMAIL) && 
  !settings.mcp_enabled
);
```

**Files:**
- New `src/components/SupportChat.tsx` — Chat widget UI
- New `src/lib/supportEmail.ts` — Email sending via Tauri shell command to sendmail
- `src/pages/Settings.tsx` — Add MCP settings toggle
- `.env.example` — Add `SUPPORT_EMAIL=`

---

## 16. Dashboard Enhancements (from prompt)

### 16.1 Dashboard Buttons & Pinned Buttons
**What:** Enhance dashboard quick-access buttons:
- 4-card grid layout per page section
- Cards use dimmed colors matching the card's theme color
- Icons positioned correctly with consistent sizing
- Text at correct position with proper hierarchy

### 16.2 Stats Cards at Each Page
**What:** Each page gets its own stats row:
- Home → Sales/Revenue/Customers/Orders (existing)
- Inventory → Stock/Value/Low Stock/Suppliers
- Recipes → Total Recipes/Active/Cost/Margin
- Transactions → Today/Week/Month/Outstanding
- Analytics → Custom KPI cards

### 16.3 Card Design Fix
**What:** Fix icon placement and text colors:
- Icons: `w-6 h-6` consistently, aligned top-right or left depending on layout
- Text: more dimmed (`text-base-content/60` instead of `text-base-content/80`)
- Description: match card background color (`bg-primary/5 text-primary/70`)

---

## 17. Files & Assets Reorganization (from prompt)

### 17.1 Move POS Assets
**What:** Move POS assets from shared `projects/pos/assets/` to each edition's main project dir.
- `forge-pos/src/styles/` (rename from `css/`)
- `pos-solo/src/styles/`
- `pos-full/src/styles/`

### 17.2 Rename CSS → Styles
**What:** Rename all `css/` directories to `styles/` and update imports.
- `src/css/` → `src/styles/`
- Update all `import '../css/` references
- Update `index.css` path references

### 17.3 Organize Pages & Components by Category
**What:** Reorganize file structure:
```
src/pages/
  pos/        → Sale, ProductManager, Transactions
  kitchen/    → Recipes, Inventory
  admin/      → Settings, Employees, Roles
  analytics/  → Analytics, Reports
  auth/       → Login, Register

src/components/
  pos/        → ProductCard, CartSummary, PaymentModal
  kitchen/    → RecipeCard, InventoryTable
  ui/         → Modal, Skeleton, DataTable, StatCard
  layout/     → PageLayout, SideNav, Header
```

**Status:** ⬜ Not Started | **Effort:** 2-3 hours

---

## Files Summary (updated)