# Forge POS — Calculations Reference

> All formulas, methods, and fields used across the POS system  
> **Applies to:** forge-pos (Rust/Diesel) — same formulas apply to pos-solo and pos-full via sidecar API

---

## 1. Sales & Cart Calculations

### Subtotal

```typescript
const subtotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
```

| Field | Source | Description |
|-------|--------|-------------|
| `item.price` | `products.price` | Unit price of the product |
| `item.quantity` | Cart state | Quantity being purchased |
| **Result** | Calculated | `price × quantity` per line item, summed across cart |

**Backend equivalent (Rust):**
```rust
let subtotal: f64 = sale_items.iter()
    .map(|item| item.price * item.quantity)
    .sum();
```

### Tax Amount

```typescript
const taxRate = settings.tax_rate ? parseFloat(settings.tax_rate) : 0;
const taxAmount = subtotal * (taxRate / 100);
```

| Field | Source | Description |
|-------|--------|-------------|
| `tax_rate` | `settings` table | Percentage as string (e.g., "8.5" = 8.5%) |
| **Result** | Calculated | `subtotal × tax_rate ÷ 100` |

### Delivery Fee

```typescript
const deliveryFee = orderType === 'delivery' && settings.delivery_fee
  ? settings.delivery_fee
  : 0;
```

**With fee multiplier (if delivery type selected):**
```typescript
const feeMultiplier = deliveryTypes.find(dt => dt.id === deliveryTypeId)?.fee_multiplier ?? 1;
const deliveryFee = settings.delivery_fee * feeMultiplier;
```

| Field | Source | Description |
|-------|--------|-------------|
| `delivery_fee` | `settings` table | Base delivery fee |
| `fee_multiplier` | `delivery_types` table | Multiplier per delivery type |
| `delivery_fee_per_km` | `settings` table | Per-km surcharge |
| **Result** | Calculated | `base_fee × multiplier + (km × per_km_rate)` |

### Total Amount

```typescript
const totalAmount = subtotal + taxAmount + deliveryFee;
```

### Sale Item Subtotal (Rust Backend)

```rust
// In sales.rs — computed when creating sale items
let subtotal = item.price * item.quantity;
// Stored in sale_items.subtotal column
```

---

## 2. Analytics & KPI Calculations

### Summary Metrics

```sql
-- Total orders (count)
SELECT COUNT(*) FROM sales WHERE status = 'completed';

-- Total revenue (sum)
SELECT COALESCE(SUM(total_amount), 0) FROM sales WHERE status = 'completed';

-- Average order value
SELECT COALESCE(SUM(total_amount) / NULLIF(COUNT(*), 0), 0)
FROM sales WHERE status = 'completed';
```

| Metric | Formula | SQL Column |
|--------|---------|------------|
| **Total Orders** | `COUNT(id)` | `sales.count` |
| **Total Revenue** | `SUM(total_amount)` | `sales.total_amount` |
| **Average Order Value** | `SUM(total_amount) / COUNT(id)` | Calculated |
| **Items per Sale** | `COUNT(sale_items.id) / COUNT(DISTINCT sales.id)` | Calculated |

### Daily Revenue

```sql
SELECT date, SUM(total_amount) as revenue, COUNT(*) as orders
FROM sales
WHERE status = 'completed'
  AND date >= date('now', '-30 days')
GROUP BY date
ORDER BY date;
```

### Top Products

```sql
SELECT si.product_name as name,
       SUM(si.quantity) as sales,
       SUM(si.subtotal) as revenue
FROM sale_items si
JOIN sales s ON si.sale_id = s.id
WHERE s.status = 'completed'
  AND s.date >= date('now', '-30 days')
GROUP BY si.product_name
ORDER BY revenue DESC
LIMIT 10;
```

### Product Distribution

```sql
SELECT c.name, COUNT(p.id) as value
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
GROUP BY c.name
ORDER BY value DESC;
```

---

## 3. Inventory Calculations

### Current Stock Level

```typescript
// Calculated from ingredient initial quantity + all transactions
const currentQty = ingredient.current_quantity;
```

### Low Stock Detection

```typescript
const isLowStock = ingredient.current_quantity <= ingredient.reorder_level;
```

### Reorder Quantity

```typescript
const reorderAmount = ingredient.reorder_quantity - ingredient.current_quantity;
```

| Field | Source | Formula |
|-------|--------|---------|
| `current_quantity` | `ingredients` table | Updated by inventory transactions |
| `reorder_level` | `ingredients` table | Threshold; alert triggered when `current ≤ reorder_level` |
| `reorder_quantity` | `ingredients` table | Target stock level |
| **Alert status** | Calculated | `current_quantity ≤ reorder_level` → alert |

### Inventory Transaction Impact

```typescript
// When recording a transaction
const newQuantity = ingredient.current_quantity + quantityChange;
// quantityChange is positive for additions, negative for removals
```

### Cost Calculation

```sql
-- Total ingredient cost for a recipe
SELECT SUM(ri.quantity * i.cost_per_unit) as recipe_cost
FROM recipe_ingredients ri
JOIN ingredients i ON ri.ingredient_id = i.id
WHERE ri.recipe_id = :recipe_id;
```

---

## 4. Payroll Calculations

### Regular Pay

$$regular\_pay = regular\_hours \times \frac{employee.salary}{hours\_per\_period}$$

Default `hours_per_period` = 160 (40h/week × 4 weeks)

### Overtime Pay

$$overtime\_pay = overtime\_hours \times \frac{employee.salary}{hours\_per\_period} \times 1.5$$

Overtime rate = 1.5× (time and a half)

### Total Pay

$$total\_pay = regular\_pay + overtime\_pay$$

### Payroll Fields

| Field | Source | Description |
|-------|--------|-------------|
| `regular_hours` | `payrolls` table | Hours worked at regular rate |
| `overtime_hours` | `payrolls` table | Hours at overtime rate (×1.5) |
| `total_pay` | `payrolls` table | Calculated: `regular + overtime` |
| `salary` | `employees` table | Employee's base salary |

---

## 5. Employee Schedule Calculations

### Shift Duration

```typescript
const shiftStart = new Date(schedule.shift_start);
const shiftEnd = new Date(schedule.shift_end);
const durationHours = (shiftEnd.getTime() - shiftStart.getTime()) / (1000 * 60 * 60);
```

### Weekly Hours Total

```sql
SELECT employee_id,
       SUM(julianday(shift_end) - julianday(shift_start)) * 24 as total_hours
FROM employee_schedules
WHERE status = 'scheduled'
  AND shift_start >= :week_start
  AND shift_end <= :week_end
GROUP BY employee_id;
```

---

## 6. Loyalty Points Calculations

### Points Earned

```typescript
const POINTS_PER_CURRENCY_UNIT = 10;
const points = Math.floor(saleTotal) * POINTS_PER_CURRENCY_UNIT;
```

| Field | Formula | Example ($45.50) |
|-------|---------|:-----------------:|
| Points earned | `floor(total) × 10` | 450 points |
| Discount value | `points × 0.01` | $4.50 |

### Points Redemption

```typescript
// When customer redeems points
const redeemedPoints = request.points_to_redeem;
const discountAmount = redeemedPoints * 0.01; // $0.01 per point
const adjustedTotal = saleTotal - discountAmount;
```

### Current Points Balance

```sql
SELECT customer_id,
       SUM(points_change) as balance
FROM loyalty_transactions
GROUP BY customer_id;
```

---

## 7. Tax Report Calculations

### Period Totals

```sql
SELECT
  COUNT(*) as transaction_count,
  COALESCE(SUM(total_amount), 0) as total_sales,
  COALESCE(SUM(total_amount * :tax_rate / 100), 0) as total_tax
FROM sales
WHERE status = 'completed'
  AND date >= :period_start
  AND date <= :period_end;
```

### Tax Report Fields

| Field | Source | Description |
|-------|--------|-------------|
| `period_start` | User input | Start date |
| `period_end` | User input | End date |
| `total_sales` | Calculated | Sum of completed sales in period |
| `total_tax` | Calculated | `total_sales × tax_rate / 100` |
| `transaction_count` | Calculated | Count of completed sales |

---

## 8. Currency & Formatting

### Currency Symbol Resolution

```typescript
// From settings table
const currencySymbol = settings.currency || 'USD';

// Display format
`${currencySymbol} ${amount.toFixed(2)}`
// e.g., "USD 45.50" or with symbol: "$45.50"
```

### Supported Currencies

Set in `settings.currency`. Default: `USD`. Displayed as-is from the settings value.

---

## 9. Recipe Cost Calculations

### Per-Unit Cost

```sql
-- Cost per unit of a recipe
SELECT
  r.product_id,
  SUM(ri.quantity * i.cost_per_unit) / r.yield_quantity as cost_per_unit
FROM recipes r
JOIN recipe_ingredients ri ON ri.recipe_id = r.id
JOIN ingredients i ON ri.ingredient_id = i.id
GROUP BY r.product_id, r.yield_quantity;
```

### Profit Margin

$$profit\_margin = \frac{product.price - recipe\_cost}{product.price} \times 100$$

---

## 10. Discount Calculations

### Manual Discount (Future Feature)

$$discounted\_price = original\_price \times (1 - \frac{discount\_percent}{100})$$

### Bulk Discount (Quantity-Based)

```typescript
// Example: 10% off when buying 5+ of the same item
const DISCOUNT_THRESHOLD = 5;
const DISCOUNT_PERCENT = 10;

let unitPrice = product.price;
if (item.quantity >= DISCOUNT_THRESHOLD) {
  unitPrice = product.price * (1 - DISCOUNT_PERCENT / 100);
}
```

---

## Complete Formula Reference Table

| Calculation | Formula | Module | Affected Tables |
|------------|---------|--------|-----------------|
| Line item total | `price × quantity` | Sale | `sale_items.subtotal` |
| Cart subtotal | `Σ(price × quantity)` | Sale | — |
| Tax amount | `subtotal × tax_rate / 100` | Sale | — |
| Delivery fee | `base × multiplier + km × per_km` | Sale | — |
| Sale total | `subtotal + tax + delivery_fee` | Sale | `sales.total_amount` |
| Revenue | `Σ(total_amount)` | Analytics | — |
| Avg order value | `Σ(total_amount) / COUNT(sales)` | Analytics | — |
| Low stock alert | `current_qty ≤ reorder_level` | Inventory | `inventory_alerts` |
| Reorder amount | `reorder_qty - current_qty` | Inventory | — |
| Regular pay | `hours × (salary / 160)` | Payroll | `payrolls.regular_hours` |
| Overtime pay | `hours × (salary / 160) × 1.5` | Payroll | `payrolls.overtime_hours` |
| Total pay | `regular + overtime` | Payroll | `payrolls.total_pay` |
| Loyalty points | `floor(total) × 10` | Customers | `loyalty_transactions` |
| Points→Discount | `points × 0.01` | Customers | — |
| Recipe cost | `Σ(ingredient_qty × cost)` | Recipes | — |
| Profit margin | `(price - cost) / price × 100` | Analytics | — |
