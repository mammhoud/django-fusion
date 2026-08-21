# Guides — Formint

---

## Setup

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | >= 18 | Frontend runtime |
| pnpm | >= 9 | Package manager |
| Rust | >= 1.75 | Backend compilation |
| Tauri CLI | >= 2 | Desktop app build |
| SQLite | >= 3 | Development queries |

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/mammhoud/POS.git
cd projects/formints/formintA

# 2. Install frontend dependencies
pnpm install

# 3. Install Rust dependencies
cd src-tauri && cargo fetch && cd ..

# 4. Create environment file (optional)
echo 'DATABASE_URL=restaurant.db' > .env
echo 'SUPERUSER_EMAIL=admin@pos.local' >> .env
echo 'SUPERUSER_PASSWORD=changeme' >> .env

# 5. Verify installation
make info
```

### Development

```bash
# Start frontend dev server (browser only — http://localhost:1420)
make dev

# Start full Tauri desktop app (with Rust backend)
make dev-desktop
# or: pnpm tauri dev
```

The dev server supports hot-reload for both frontend (Vite HMR) and backend (cargo watch).

### First Run

On first launch, the app:
1. Creates the SQLite database (`restaurant.db`)
2. Runs Diesel migrations (creates all tables + seed data)
3. Shows the Auth page (if authentication is configured)
4. Falls back to the Home dashboard on success

> **Default user:** No default user is created. The first-run setup wizard guides you through creating an admin account.

---

## Database

### Seed Data

The `up.sql` migration includes comprehensive seed data for development:

```bash
# Full seed (all presets merged)
make seed

# Specific preset
make seed PRESET=base      # Restaurant (47 products, 12 employees)
make seed PRESET=gaming    # Gaming lounge
make seed PRESET=coffee    # Coffee shop
```

### Reset

```bash
# Delete + remigrate + reseed
make seed

# Delete database only
make clean-db
```

### Backup

```bash
# Manual backup
cp restaurant.db restaurant.db.backup

# Via Settings UI
# Navigate to Settings → Database → Export Database
```

### Inspecting with SQLite

```bash
sqlite3 restaurant.db
.tables                        # List all tables
.schema products               # Show table schema
SELECT * FROM settings;        # Query settings
SELECT name, price FROM products WHERE category_id = 1;  # Filtered query
```

---

## Building

### Desktop App

```bash
# Production build (Tauri bundle)
make build

# Output:
#   macOS: src-tauri/target/release/bundle/dmg/Formint.dmg
#   Windows: src-tauri/target/release/bundle/msi/Formint.msi
#   Linux: src-tauri/target/release/bundle/appimage/Formint.AppImage

# Build frontend only
make build-frontend
# Output: dist/
```

### Platform-Specific Builds

```bash
make build-android     # Android APK (requires SDK + NDK)
make build-ios         # iOS app (requires macOS + Xcode)
make build-all         # All platforms sequentially
```

### Bundle Configuration

See `src-tauri/tauri.conf.json` for:
- App window dimensions (default: 1200×800)
- Bundle identifier: `com.mammhoud.formint-community`
- Icon paths (icns, ico, png)
- External binaries (server)
- Updater endpoints

---

## Testing

### Frontend Tests (Vitest)

```bash
make test               # Run all tests (verbose)

# Specific test files
pnpm vitest run src/test/pages/Auth.test.tsx
pnpm vitest run src/test/pages/Sale.test.tsx

# With coverage
pnpm test:coverage

# Watch mode
make test-watch
```

### Test Files

```
src/test/
├── setup.ts                     # Vitest setup + Tauri mock
├── invoke.test.ts               # Integration test for all invoke() methods
├── test-utils.tsx               # Custom render with providers
├── pages/
│   ├── Auth.test.tsx            # 21 auth flow tests
│   ├── Sale.test.tsx            # Sale page tests
│   ├── Inventory.test.tsx       # Inventory management tests
│   └── ... (20+ page test files)
├── components/
│   └── ProductCard.test.tsx     # Product card rendering
└── hooks/
    ├── useStatusToast.test.tsx
    └── useDebouncedSearch.test.ts
```

### Rust Tests

```bash
make cargo-test       # Run Rust unit tests
make cargo-check      # Rust compilation check (faster than full build)
make cargo-clippy     # Rust linter
```

### E2E Tests (Playwright)

```bash
make test-e2e          # Run Playwright tests
make test-e2e-ui       # Run with Playwright UI mode
make test-all          # Vitest + Playwright
```

---

## Internationalization

### Adding a New Language

1. Create `src/i18n/{code}.json` (copy `en.json` as template)
2. Translate all values
3. Add language option in:
   - `src/i18n/index.ts` (i18next configuration)
   - `src/components/LanguageToggle.tsx` (language switcher)
   - `src/i18n/en.json` (settings translations)
4. Run validation:
   ```bash
   make i18n-check
   ```

### Translation Keys

Keys are organized by namespace:
```
"namespace": {
  "key": "value",
  "subSection": {
    "subKey": "value"
  }
}
```

Usage in components:
```tsx
const { t } = useTranslation();
t('sale.totalAmount')       // → "Total Amount"
t('productManager.name')    // → "Product Name"
t('common.save')            // → "Save"
```

### Validation

```bash
make i18n-audit        # Generate docs/i18n-gaps.md
make i18n-check        # CI check (exits 1 on missing keys)
```

---

## FlyonUI Component Library

### Installation Status

FlyonUI v2.4.1 is installed and configured as a Tailwind CSS v4 plugin.

### Using FlyonUI Classes

```tsx
// Badge
<span className="badge badge-primary">Active</span>
<span className="badge badge-soft badge-success">Completed</span>
<span className="badge badge-outline badge-warning">Pending</span>

// Button
<button className="btn btn-primary">Save</button>
<button className="btn btn-soft btn-secondary">Cancel</button>
<button className="btn btn-outline btn-error">Delete</button>
<button className="btn btn-block btn-gradient btn-primary">Full Width</button>

// Tabler Icons (via Iconify)
<span className="icon-[tabler--settings]"></span>
<span className="icon-[tabler--user]"></span>
<span className="icon-[tabler--shopping-cart]"></span>
```

### Interactive Components

FlyonUI's JavaScript handles interactive components like modals, dropdowns, toggles. The JS is imported in `src/main.tsx`:

```tsx
import "flyonui/flyonui";
```

---

## Theme Customization

### Adding a New Theme Variant

1. Add CSS custom properties in `src/styles/themes.css`:
```css
[data-theme="ocean"] {
  --theme-primary: #0891b2;
  --theme-primary-hover: #0e7490;
  /* ... all other --theme-* variables */
}
.dark[data-theme="ocean"] { /* dark variant */ }
```

2. Add Tailwind color overrides in `src/styles/theme-overrides.css`:
```css
[data-theme="ocean"] {
  --color-teal-500: #0891b2;
  /* ... override teal, slate, and other color tokens */
}
```

3. Add to theme options in `Settings.tsx` appearance tab.

### Available Variants

| Variant | Light Primary | Dark Primary | data-theme value |
|---------|--------------|--------------|-----------------|
| Default | #6366f1 (Indigo) | #6366f1 | (none) |
| Corporate | #2563eb (Blue) | #3b82f6 | `corporate` |
| Luxury | #ca8a04 (Gold) | #eab308 | `luxury` |
| Pastel | #db2777 (Pink) | #f472b6 | `pastel` |
| Perplexity | Teal | Teal | `perplexity` |

---

## Calculations

### Sale Total
```
subtotal = Σ(price × quantity)
total = subtotal + delivery_fee + tax
tax = subtotal × (tax_rate / 100)
```

### Delivery Fee
```
delivery_fee = flat_fee + (distance_km × per_km_fee)
```

### Recipe Cost
```
total_ingredient_cost = Σ(ingredient_quantity × ingredient_cost_per_unit)
cost_per_serving = total_ingredient_cost / yield_quantity
profit_margin = ((product_price - cost_per_serving) / product_price) × 100
```

### Payroll
```
total_pay = regular_hours × hourly_rate + overtime_hours × hourly_rate × 1.5
```

### Loyalty Points
```
points_earned = floor(total_amount / point_rate)
```

See [calculations.md](calculations.md) for full formula reference.

---

## Deployment

### Production Build

```bash
# Full desktop app bundle
make build

# The output will be in:
# macOS:   src-tauri/target/release/bundle/dmg/
# Windows: src-tauri/target/release/bundle/msi/
# Linux:   src-tauri/target/release/bundle/appimage/
```

### Environment Variables

```env
# Database
DATABASE_URL=restaurant.db

# Authentication
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PASSWORD=securepassword123

# SMTP (for support emails)
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=user@example.com
SMTP_PASSWORD=password
SMTP_RECIPIENT=support@example.com
SMTP_FROM_NAME=Formint
SMTP_FROM_EMAIL=no-reply@example.com
```

### Data Directory

The database and config files are stored in the app's data directory:
- **macOS:** `~/Library/Application Support/com.mammhoud.formint-community/`
- **Windows:** `%APPDATA%/com.mammhoud.formint-community/`
- **Linux:** `~/.local/share/com.mammhoud.formint-community/`

### Auto-Update

Tauri's built-in updater is configured but requires:
1. A public key in `tauri.conf.json`
2. An update endpoint URL
3. A release artifacts server

---

## Troubleshooting

### Port Conflict

```bash
make port-kill         # Kill process on port 1420
lsof -i :1420          # Find what's using the port
```

### Database Issues

```bash
make seed              # Reset database completely
sqlite3 restaurant.db "PRAGMA integrity_check;"  # Check integrity
sqlite3 restaurant.db "VACUUM;"                  # Optimize
```

### Build Errors

```bash
make clean             # Remove all build artifacts
just install           # Reinstall dependencies
make build             # Rebuild
```

### CSS/Badge Errors

If you see `Cannot apply unknown utility class 'badge'`:

```bash
# Ensure FlyonUI is properly configured in src/index.css:
@plugin "flyonui";
@import "../node_modules/flyonui/variants.css";
@source "../node_modules/flyonui/dist/index.js";

# Verify _forms.css was removed (it uses @apply which conflicts with v4):
ls src/styles/components/_forms.css  # Should say "No such file"
```
