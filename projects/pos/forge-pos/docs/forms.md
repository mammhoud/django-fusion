# Forge POS — Forms & Inputs Reference

> **Stack:** Tailwind v4 + FlyonUI semantic classes + BEM `.field` wrapper

---

## Overview

Every form control in Forge POS is wrapped in a **BEM `.field` block** that provides the label, control, helper text and error/success states in one consistent structure. The markup and styles live in `assets/styles/base/_reset.css` (`.field` block) and reuse FlyonUI classes (`input`, `select`, `textarea`, `checkbox`) for the control itself.

```
.field                    ── block (column: label → control → helper)
├── .label-text           ── element (label)
├── .input / .select      ── FlyonUI control element
├── .helper-text          ── element (hint)
└── .field--error         ── modifier (error state)
    └── .field--success   ── modifier (success state)
```

---

## Field Block

### Basic field

```tsx
<div className="field">
  <label className="label-text">{t('productManager.productName')}</label>
  <input
    type="text"
    value={value}
    onChange={…}
    className="input w-full"
    placeholder={…}
  />
</div>
```

### With helper text

```tsx
<div className="field">
  <label className="label-text">SKU / Barcode</label>
  <input type="text" className="input w-full" placeholder="e.g. 8901234567890" />
  <p className="helper-text">Optional — used for fast search</p>
</div>
```

### Error state

```tsx
<div className={`field ${errors.name ? 'field--error' : ''}`}>
  <label className="label-text">Product name</label>
  <input type="text" className="input w-full" data-testid="pm-name-input" />
  {errors.name && <p className="helper-text">{errors.name}</p>}
</div>
```

Error + success states tint the control border, label and helper text using the semantic tokens (`--color__semantic--error` / `--color__semantic--success`).

---

## Modifiers

| Modifier | Purpose |
|----------|---------|
| `.field--error` | Error border + red label/helper |
| `.field--success` | Success border + green helper |
| `.field--sm` | Compact height (`--input__height--sm`) — used in filter bars |
| `.field--lg` | Large height (`--input__height--lg`) |
| `.field--ghost` | Borderless minimal style |
| `.field__icon` | Leading icon inside the control |

### Compact field (filter bars)

```tsx
<div className="field field--sm">
  <select value={sortKey} onChange={…} className="select" aria-label="Sort by">
    <option value="newest">Newest</option>
  </select>
</div>
```

---

## Controls

### Text / number input

```tsx
<input type="number" step="0.01" min="0" className="input w-full h-9 text-sm" placeholder="0.00" />
```

### Select

```tsx
<select className="select w-full" value={categoryId} onChange={…}>
  <option value="">— No category —</option>
  {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
</select>
```

> **Accessibility:** always set `aria-label` on selects that have no visible `<label>`.

### Textarea

```tsx
<textarea className="textarea w-full text-sm resize-none" rows={2} placeholder="Notes…" />
```

### Checkbox (FlyonUI)

```tsx
<input type="checkbox" className="checkbox checkbox-sm checkbox-primary" />
```

---

## Form Layout Patterns

### Two-column row

```tsx
<div className="grid grid-cols-2 gap-3">
  <div className="field">…Price…</div>
  <div className="field">…Unit…</div>
</div>
```

### Choice tiles (button groups)

```tsx
<div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
  {OPTIONS.map(opt => (
    <button
      type="button"
      onClick={() => setValue(opt.value)}
      className={`flex flex-col items-center gap-1.5 p-3 rounded-xl border-2 transition-all
        ${selected === opt.value
          ? 'border-primary bg-primary/5 text-primary'
          : 'border-base-300/50 bg-base-100/50 hover:border-primary/50'}`}
    >
      <span className={iconClass(opt.icon, 'w-5 h-5')} />
      <span className="text-xs font-semibold">{opt.label}</span>
    </button>
  ))}
</div>
```

Used for Product Type (`product`, `service`, `combo`, `addon`) and Available Order Types.

---

## Validation

Validation lives in the page component (no form library):

```tsx
const validateForm = (): boolean => {
  const newErrors: FormErrors = {};
  if (!name.trim()) newErrors.name = t('productManager.validationName');
  else if (duplicateExists) newErrors.name = t('productManager.validationDuplicate');
  setErrors(newErrors);
  return Object.keys(newErrors).length === 0;
};
```

- **Submit disabled** while `isSubmitting` to prevent double-sends.
- Errors are cleared per-field as the user types (`handleInputChange` clears the field's error).
- Success/error feedback uses the `alert` toast pattern (ProductManager) or the shared `useStatusToast` hook (Sale).

---

## References

- `assets/styles/base/_reset.css` — `.field` block styles + input states
- `assets/styles/base/_variables.css` — `--input__*` and `--color__semantic--*` tokens
- [`docs/tables-grid.md`](tables-grid.md) — tables & grid layout patterns
- Example pages: `ProductManager.tsx` (product + category forms), `Settings.tsx` (BEM labels), `Sale.tsx` (inline note inputs)
