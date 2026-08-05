# POS — i18n Conventions

> **Library:** i18next (react-i18next) | **Locales:** en, fr, ar | **RTL:** Arabic

---

## Translation Architecture

```
src/i18n/
├── index.ts             # i18next initialization
├── en.json              # English (source of truth — 500+ keys)
├── fr.json              # French translations
└── ar.json              # Arabic translations (RTL)
```

### Initialization

```typescript
// src/i18n/index.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './en.json';
import ar from './ar.json';
import fr from './fr.json';

const savedLang = localStorage.getItem('language') || 'en';

i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, ar: { translation: ar }, fr: { translation: fr } },
  lng: savedLang,
  fallbackLng: 'en',
  interpolation: { escapeValue: false, prefix: '{', suffix: '}' },
  react: { useSuspense: false },
});

export default i18n;
```

**Important:** The `prefix: '{'` and `suffix: '}'` interpolation pattern prevents conflicts with JSX `{}` syntax and ICU message format.

---

## Key Structure Convention

Keys use **dot notation** organized by feature area:

```
common        → Shared UI strings (save, cancel, delete, search...)
dashboard     → Home dashboard widgets
pos           → Point of Sale terminal
inventory     → Inventory management
employees     → Employee management
products      → Product/category management
sales         → Sales & transactions
analytics     → Analytics & reports
settings      → Settings & configuration
customers     → Customer management
suppliers     → Supplier management
kitchen       → Kitchen display
recipes       → Recipe management
payroll       → Payroll processing
schedule      → Employee scheduling
tax           → Tax reporting
roles         → Roles & permissions
chat          → Support chat
auth          → Authentication
about         → App info
```

### Example Key Structure

```json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit",
    "add": "Add",
    "search": "Search...",
    "loading": "Loading...",
    "noResults": "No results found",
    "confirm": "Confirm",
    "back": "Back"
  },
  "pos": {
    "title": "Point of Sale",
    "cart": "Cart",
    "checkout": "Checkout",
    "subtotal": "Subtotal",
    "tax": "Tax",
    "total": "Total",
    "addToCart": "Add to Cart",
    "emptyCart": "Cart is empty"
  }
}
```

---

## Using Translations in Components

### Basic Usage

```tsx
import { useTranslation } from 'react-i18next';

function MyPage() {
  const { t } = useTranslation();
  return (
    <div>
      <h1>{t('pos.title')}</h1>
      <button>{t('common.save')}</button>
    </div>
  );
}
```

### With Interpolation

```json
{
  "inventory": {
    "lowStockWarning": "Only {count} units remaining for {product}",
    "itemCount": "{count} items"
  }
}
```

```tsx
<p>{t('inventory.lowStockWarning', { count: 5, product: 'Espresso' })}</p>
// → "Only 5 units remaining for Espresso"
```

### Plurals

```json
{
  "sales": {
    "items_one": "{{count}} item",
    "items_other": "{{count}} items"
  }
}
```

```tsx
<p>{t('sales.items', { count: items.length })}</p>
// → "3 items" or "1 item"
```

---

## Adding a New Language

1. **Create the translation file:**
```bash
cp src/i18n/en.json src/i18n/es.json
```

2. **Translate all values** in `es.json` (keep keys identical to `en.json`)

3. **Register in `src/i18n/index.ts`:**
```typescript
import es from './es.json';

i18n.init({
  resources: {
    en: { translation: en },
    fr: { translation: fr },
    ar: { translation: ar },
    es: { translation: es },  // ← new locale
  },
});
```

4. **Add RTL support** (if needed) in `src/main.tsx`:
```typescript
if (savedLang === 'es' || savedLang === 'ar') {
  document.documentElement.dir = 'rtl';
} else {
  document.documentElement.dir = 'ltr';
}
```

5. **Add to language switcher** in `LanguageToggle.tsx`

---

## RTL (Right-to-Left) Conventions

Arabic uses the `src/styles/utilities/_rtl.css` stylesheet:

```css
[dir="rtl"] .sidebar {
  left: auto;
  right: 0;
}

[dir="rtl"] .ml-auto {
  margin-left: unset;
  margin-right: auto;
}
```

### RTL Checklist for New Locales

- [ ] Set `document.documentElement.dir = 'rtl'`
- [ ] Mirror sidebar position (right instead of left)
- [ ] Mirror margin/padding utilities
- [ ] Flip directional icons (arrows, chevrons)
- [ ] Verify table column alignment
- [ ] Test date/number formatting

---

## Translation Workflow

### Audit for Gaps

```bash
make i18n-audit
```

Generates `docs/i18n-gaps.md` showing which keys are missing in French or Arabic.

### Apply Arabic Translations

```bash
make i18n-fix
```

Runs `scripts/dev/i18n-merge-ar.cjs` to auto-merge Arabic translations from a reference source.

### CI Check

```bash
make i18n-check
```

Exits non-zero if any locale has missing keys — used in GitHub Actions `i18n.yml`.

### Full Pipeline

```bash
make i18n-fix-check
```

Runs `i18n-fix` then `i18n-check` — the recommended pre-commit check.

---

## MSA (Modern Standard Arabic) Register Rules

All Arabic translations follow these conventions:

| Rule | Example |
|------|---------|
| Use MSA (فصحى), not dialect | "مرحباً" not "أهلاً" |
| Tashkeel on critical words only | "إدارة المخزون" |
| Consistent terminology | "منتج" always for "product" |
| Respect i18next interpolation | `{count}` not `{{count}}` |
| Mirror technical terms | "API" stays "API" |

---

## Related Docs

- [i18next Documentation](https://www.i18next.com/)
- [react-i18next Guide](https://react.i18next.com/)
- [`customization-react.md`](customization-react.md) — Frontend customization
- [`commands.md`](commands.md) — Full CLI reference
