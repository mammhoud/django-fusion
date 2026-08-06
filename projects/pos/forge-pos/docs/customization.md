# Formint — Customization Guide

> **Applies to:** forge-pos (Tauri + React + Rust/Diesel)  
> **Adapt for:** formint-pos (merged package — use the Robyn sidecar / Django Ninja API instead of Tauri invoke)

---

## Table of Contents

1. [Theme Customization](#1-theme-customization)
2. [Product Card Colors & Border System](#2-product-card-colors--border-system)
3. [Receipt & Invoice Templates](#3-receipt--invoice-templates)
4. [i18n & Translations](#4-i18n--translations)
5. [Tax Calculation Methods](#5-tax-calculation-methods)
6. [Delivery Fee Calculation](#6-delivery-fee-calculation)
7. [Loyalty Points System](#7-loyalty-points-system)
8. [Payroll Calculations](#8-payroll-calculations)
9. [Database Seeding Presets](#9-database-seeding-presets)
10. [Adding New Fields to Products](#10-adding-new-fields-to-products)

---

## 1. Theme Customization

### Theme Variants

The POS ships with 5 theme variants defined in `src/contexts/ThemeContext.tsx`:

| Variant | ID | Primary Color | Surface | Mood |
|---------|-----|--------------|---------|------|
| Default | `default` | Teal/Indigo `#14b8a6` | Slate | Clean, modern |
| Corporate | `corporate` | Blue `#3b82f6` | Neutral | Professional |
| Luxury | `luxury` | Gold `#eab308` | Warm stone | Premium |
| Pastel | `pastel` | Pink `#ec4899` | Light purple | Playful |
| Perplexity | `perplexity` | Teal | Neutral | Minimal |

**How to customize:**

```css
/* src/styles/theme-overrides.css */
[data-theme="ocean"] {
  --color-teal-50:  #ecfeff;
  --color-teal-500: #06b6d4;
  --color-teal-600: #0891b2;
  /* Add all Tailwind color scale values */
}
```

Then register in `ThemeContext.tsx`:
```typescript
THEME_VARIANTS = [
  { id: 'ocean', label: 'Ocean', icon: '🌊', description: 'Deep blue waters' },
  // ... existing variants
]
```

### Dark/Light Mode

Toggled via `ThemeToggle.tsx` component. Mode is persisted to localStorage and applies `.dark` class to `<html>`.

---

## 2. Product Card Colors & Border System

### How It Works

Products can have a custom `border_color` field stored in the database. When set, the `ProductCard` component applies it as an inline style:

```typescript
// src/components/ProductCard.tsx
const borderHex = product.border_color;
const hasCustomColor = !!borderHex && !isSelected;

// Uses inline borderColor + hexToRgba() background
const customBorderStyle = {
  borderColor: borderHex,
  backgroundColor: hexToRgba(borderHex, 0.06)
};
```

### Color Assignment Logic

1. **Custom color** (`product.border_color` set): Uses inline styles with the hex value
2. **Selected state**: Uses `selectedClassName` (teal highlight)
3. **Default**: Cycles through `PRODUCT_CARD_COLORS` array by index:

```typescript
const color = PRODUCT_CARD_COLORS[index % PRODUCT_CARD_COLORS.length];
```

### Adding New Default Colors

Edit `PRODUCT_CARD_COLORS` in `ProductCard.tsx`:
```typescript
export const PRODUCT_CARD_COLORS: ProductCardColor[] = [
  { bg, border, initial, badge, icon }, // Rose
  { bg, border, initial, badge, icon }, // Sky
  // Add your own:
  { bg: 'bg-cyan-100/70 dark:bg-cyan-900/20',
    border: 'border-cyan-300 dark:border-cyan-700/50',
    initial: 'text-cyan-500 dark:text-cyan-300',
    badge: 'bg-cyan-500', icon: 'text-cyan-400' },
];
```

### Color Picker UI (ProductManager)

The product editor includes:
- Native `<input type="color">` picker
- Hex text field with validation (`pattern="^#[0-9a-fA-F]{6}$"`)
- 6 preset color swatches: Indigo, Pink, Teal, Amber, Red, Green
- Preview shows the color applied to the product image border

### Use Cases

| Use Case | How | Example |
|----------|-----|---------|
| **Category color-coding** | Set `border_color` on import/bulk edit | Red for Pizzas, Green for Salads |
| **Promotional items** | Manually set bright color | Gold border for specials |
| **Inventory status** | Integration with low-stock alerts | Orange for low-stock items |
| **Seasonal menus** | Batch update colors by season | Pastel pink for spring |

---

## 3. Receipt & Invoice Templates

### Receipt Templates

Defined in the `receipt_templates` table. Customize via `ReceiptTemplates.tsx`:

| Field | Type | Description |
|-------|------|-------------|
| `name` | Text | Template name |
| `template_body` | Text | HTML template |
| `category` | Text | Category grouping |
| `is_default` | Boolean | Default template flag |

### Invoice Types

7 invoice types supported via `INVOICE_TYPE_LABELS`:

| Type | Label | Use Case |
|------|-------|----------|
| `tax` | TAX INVOICE | Standard tax invoice |
| `commercial` | COMMERCIAL INVOICE | Business-to-business |
| `proforma` | PROFORMA INVOICE | Quote / estimate |
| `credit` | CREDIT NOTE | Refund / credit |
| `receipt` | RECEIPT | Simple receipt |
| `selling` | SELLING INVOICE | Retail selling |
| `goods_transfer` | GOODS TRANSFER | Inventory transfer |

### Invoice PDF Customization

Edit `src/utils/invoicePdf.ts` to customize:
- Layout dimensions (default: 80×297mm)
- Font sizes and styles
- Header/footer content
- Currency formatting

---

## 4. i18n & Translations

### Supported Languages

| Language | Code | File | RTL |
|----------|------|------|:---:|
| English | `en` | `src/i18n/en.json` | No |
| French | `fr` | `src/i18n/fr.json` | No |
| Arabic | `ar` | `src/i18n/ar.json` | Yes |

### Adding a New Language

```bash
# 1. Create translation file
cp src/i18n/en.json src/i18n/de.json

# 2. Edit src/i18n/index.ts
import de from './de.json';
resources: { de: { translation: de } }

# 3. Add RTL support if needed (Arabic, Hebrew, etc.)
# In src/styles/utilities/_rtl.css — add [dir="rtl"] overrides

# 4. Run audit
make i18n-audit
```

### i18n Commands

| Command | Description |
|---------|-------------|
| `make i18n-audit` | Generate gap report |
| `make i18n-check` | CI check (exits non-zero on gaps) |
| `make i18n-fix` | Auto-merge Arabic + regenerate |
| `make i18n-fix-check` | Full pipeline |

---

## 5. Tax Calculation Methods

Tax is calculated per sale based on `settings.tax_rate`:

### Method: Percentage-Based

```typescript
// Sale.tsx — tax applied to subtotal
const subtotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
const taxRate = settings.tax_rate ? parseFloat(settings.tax_rate) : 0;
const taxAmount = subtotal * (taxRate / 100);
const finalTotal = subtotal + taxAmount;
```

| Field | Source | Formula |
|-------|--------|---------|
| `tax_rate` | `settings` table | Percentage (e.g., 8.5 = 8.5%) |
| Tax amount | Calculated | `subtotal × tax_rate / 100` |
| Final total | Calculated | `subtotal + tax_amount + delivery_fee` |

### Customization

To change tax calculation (e.g., inclusive tax, tiered rates):
1. Modify the calculation logic in `Sale.tsx` and `Transactions.tsx`
2. Add new fields to `settings` table for tax tiers
3. Update the frontend tax display

---

## 6. Delivery Fee Calculation

### Delivery Fee Model

```sql
settings {
  delivery_fee: Decimal,         -- Base delivery fee
  delivery_fee_per_km: Decimal,  -- Per-kilometer surcharge
}

delivery_types {
  fee_multiplier: Double,        -- Multiplier for base fee (e.g., 1.5 = 50% extra)
}
```

### Formula

```
delivery_fee = settings.delivery_fee × delivery_type.fee_multiplier
                + (distance_km × settings.delivery_fee_per_km)

total_with_delivery = subtotal + tax + delivery_fee
```

### Display in POS

Delivery fee is calculated during checkout when `orderType === 'delivery'`:
```typescript
const deliveryFee = orderType === 'delivery' && settings.delivery_fee
  ? settings.delivery_fee * selectedDeliveryType.fee_multiplier
  : 0;
```

### Use Cases

| Scenario | settings.delivery_fee | fee_multiplier | Per km | Total Fee |
|----------|:--------------------:|:--------------:|:------:|:---------:|
| Standard delivery | 5.00 | 1.0 | 0 | 5.00 |
| Express (1.5× fee) | 5.00 | 1.5 | 0 | 7.50 |
| Long distance (5km) | 5.00 | 1.0 | 1.50 | 12.50 |
| Free delivery promo | 0 | 1.0 | 0 | 0 |

---

## 7. Loyalty Points System

### Points Calculation

```typescript
// customers.ts — points earned per sale
const POINTS_PER_CURRENCY_UNIT = 10; // 10 points per $1 spent
const points = Math.floor(saleTotal) * POINTS_PER_CURRENCY_UNIT;
```

| Method | Formula | Example |
|--------|---------|---------|
| Earned per sale | `floor(total_amount) × 10` | $45.50 → 450 points |
| Points to discount | `points × 0.01` | 450 → $4.50 discount |
| Redemption | Deducted from total | Customer uses points at checkout |

### Loyalty Transaction History

Each points change is recorded in `loyalty_transactions`:
```sql
loyalty_transactions {
  customer_id, sale_id, points_change, reason
}
```

### Use Cases

| Action | points_change | reason |
|--------|:------------:|--------|
| Purchase | +450 | points earned on sale #123 |
| Redeem | -200 | points redeemed for discount |
| Bonus | +100 | birthday bonus |
| Adjustment | -50 | correction |

---

## 8. Payroll Calculations

### Payroll Model Fields

```sql
payrolls {
  employee_id, period_start, period_end,
  regular_hours: Decimal,
  overtime_hours: Decimal,
  total_pay: Decimal,
  status: String
}
```

### Calculation Methods

| Method | Formula | Example |
|--------|---------|---------|
| Regular pay | `regular_hours × employee.salary / (hours_per_period)` | 160h × $3,200 / 160h = $3,200 |
| Overtime pay | `overtime_hours × (employee.salary / hours_per_period) × 1.5` | 10h × ($20/h × 1.5) = $300 |
| **Total pay** | `regular_pay + overtime_pay` | $3,200 + $300 = **$3,500** |

### Payroll Statuses

| Status | Description |
|--------|-------------|
| `draft` | Being calculated, not finalized |
| `approved` | Manager approved |
| `paid` | Payment issued |
| `cancelled` | Voided |

### Use Cases

| Scenario | Calculation |
|----------|------------|
| Salaried employee (monthly) | `salary × (hours_worked / expected_hours)` |
| Hourly employee | `hours × hourly_rate + overtime × rate × 1.5` |

---

## 9. Database Seeding Presets

### Available Presets

| Preset | `make seed PRESET=` | Items | Brand |
|--------|:------------------:|:-----:|-------|
| All | `all` (default) | 100+ | Level Up Gaming Center |
| Base restaurant | `base` | 30 | POS KO |
| Gaming center | `gaming` | 60+ | Level Up Gaming Center |
| Coffee shop | `coffee` | 40+ | The Daily Grind |

### Seed Data Structure

Each preset seeds:
- `settings` — restaurant name, currency, tax rate
- `categories` — product groupings
- `products` — menu items with prices, units, categories
- `ingredients` — stock items
- `recipes` — product→ingredient mappings
- `recipe_ingredients` — quantities per recipe
- `employees` — staff records
- `customers` — customer records

### Adding a New Preset

```bash
# 1. Create migration folder
src-tauri/migrations/2026-08-01-000000_my_preset_seed/
├── up.sql    # INSERT statements
└── down.sql  # DELETE statements

# 2. Add preset to seed.rs
fn is_valid_preset(p) -> matches!("my_preset", ...)
fn seed_with_preset(preset) -> handle "my_preset" case
```

---

## 10. Adding New Fields to Products

### Full Stack Change Checklist

Making changes to the product schema requires updates at every layer:

| Layer | File | Change |
|-------|------|--------|
| **Frontend types** | `src/types.ts` | Add field to `Product`, `NewProduct`, `UpdateProductPayload` |
| **Rust DB model** | `src-tauri/src/db/models.rs` | Add field to `Product`, `NewProduct`, `UpdateProduct` |
| **Diesel schema** | `src-tauri/src/db/schema.rs` | Add column (re-generate or hand-edit) |
| **SQL migration** | `src-tauri/migrations/*/up.sql` | `ALTER TABLE products ADD COLUMN ...` |
| **Tauri command** | `src-tauri/src/lib.rs` | Update if needed (usually auto-passes through) |
| **UI component** | e.g., `ProductManager.tsx` | Add form field, validation, display |
| **Product card** | `ProductCard.tsx` | Render new field if visible on card |

### Example: Adding `weight` Field

```typescript
// 1. types.ts
export interface Product {
  weight?: number | null;  // grams
}
```

```rust
// 2. models.rs — Product
pub weight: Option<f64>,
// NewProduct
pub weight: Option<f64>,
// UpdateProduct
pub weight: Option<Option<f64>>,
```

```sql
-- 3. up.sql
ALTER TABLE products ADD COLUMN weight REAL;
```

```typescript
// 4. ProductManager.tsx — form
<input type="number" value={weight} onChange={...} step="0.1" />
```

```typescript
// 5. ProductCard.tsx — display
{product.weight && <span>{product.weight}g</span>}
```
