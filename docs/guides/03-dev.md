# 03 — POS Development Guide

> **Related:** `rust/`, `typescript/`, `server/`, `databases/`, `tests/`
> **Tags:** #development #pos #tauri #react #rust #sidecar #workflow

How to develop, build, and debug the POS desktop application.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────┐
│                 POS Desktop App                │
│                                                  │
│  ┌──────────────────┐    ┌──────────────────────┐│
│  │  React (Vite)    │    │  Rust/Tauri Backend   ││
│  │  src/pages/*.tsx  │◄──►│  src-tauri/src/       ││
│  │  src/components/  │    │  operations/*.rs     ││
│  └────────┬─────────┘    └──────────┬───────────┘│
│           │                         │             │
│           │  HTTP/WS                │  Diesel ORM │
│           ▼                         ▼             │
│  ┌──────────────────┐    ┌──────────────────────┐│
│  │  Sidecar (Sanic) │◄──►│  SQLite (restaurant.db)││
│  │  sidecar/server.py│   │                      ││
│  └──────────────────┘    └──────────────────────┘│
└──────────────────────────────────────────────────┘
```

> 💡 **Tip:** The sidecar is a Python/Sanic process spawned by Rust. It provides chat, tickets, and data APIs that the frontend consumes via HTTP/WebSocket.

---

## Dev Workflow

### 1. Start Development

```bash
cd projects/pos

# Terminal 1: Vite dev server
pnpm dev

# Terminal 2: Tauri dev (builds Rust + opens app window)
pnpm tauri dev
```

### 2. TypeScript Typecheck

```bash
npx tsc --noEmit
```

### 3. Rust Build Check

```bash
cd src-tauri
cargo check
```

### 4. Run Tests

```bash
# Frontend
pnpm vitest run

# Backend (serial — env var tests need this)
cd src-tauri && cargo test -- --test-threads=1
```

> ⚠️ **Warning:** Rust env var tests require `--test-threads=1` because they modify global environment. Running in parallel will cause race conditions.

---

## Project Anatomy

### Frontend (`src/`)

| Directory | Purpose | Customizable? |
|-----------|---------|:---:|
| `api/` | Sidecar HTTP + WebSocket client | 🟡 extend |
| `components/` | Reusable UI components | 🟢 yes |
| `contexts/` | Auth, Theme, Language providers | 🔴 no |
| `hooks/` | Custom React hooks | 🟢 yes |
| `i18n/` | Translation JSON files (en/fr/ar) | 🟢 yes |
| `pages/` | Route-level page components | 🟢 yes |
| `styles/` | SCSS (base, components, utilities) | 🟢 yes |
| `utils/` | PDF export, CSV export | 🟢 yes |

### Backend (`src-tauri/src/`)

| Module | Covers | Customizable? |
|--------|--------|:---:|
| `db/mod.rs` | Connection, migrations, path resolution | 🔴 no |
| `db/models.rs` | All Rust structs (50+ types) | 🔴 no |
| `db/schema.rs` | Diesel table definitions | 🔴 no (auto-generated) |
| `operations/auth.rs` | Login, superuser, password hashing | 🔴 no |
| `operations/products.rs` | Product CRUD | 🟢 yes |
| `operations/sales.rs` | Sales + line items CRUD | 🟢 yes |
| `operations/categories.rs` | Category CRUD | 🟢 yes |
| `operations/inventory_transactions.rs` | Stock movements | 🟢 yes |
| `operations/ingredients.rs` | Ingredient CRUD | 🟢 yes |
| `operations/recipes.rs` | Recipe + ingredients CRUD | 🟢 yes |
| `operations/employees.rs` | Employee CRUD | 🟢 yes |
| `operations/customers.rs` | Customer + loyalty CRUD | 🟢 yes |
| `operations/suppliers.rs` | Supplier CRUD | 🟢 yes |
| `operations/analytics.rs` | Dashboard analytics | 🟢 yes |
| `operations/sidecar.rs` | Sidecar process lifecycle | 🔴 no |
| `operations/settings.rs` | Settings CRUD | 🟢 yes |
| `operations/roles.rs` | RBAC roles | 🟢 yes |
| `operations/transactions.rs` | Financial transactions | 🟢 yes |
| `operations/tax_reports.rs` | Tax reporting | 🟢 yes |
| `operations/payrolls.rs` | Payroll management | 🟢 yes |
| `operations/employee_schedules.rs` | Shift scheduling | 🟢 yes |
| `operations/kitchen_tickets.rs` | Kitchen display tickets | 🟢 yes |
| `operations/purchase_orders.rs` | Purchase orders + items | 🟢 yes |
| `operations/receipt_templates.rs` | Receipt template CRUD | 🟢 yes |
| `operations/reports.rs` | Report metadata | 🟢 yes |
| `operations/dump.rs` | Data export (JSON dump) | 🟢 yes |
| `email.rs` | SMTP email sending | 🟢 yes |
| `bin/seed.rs` | Database seeder | 🟢 yes |

---

## Sidecar Development

```bash
cd projects/pos/sidecar
pip install -r requirements.txt

# Run standalone with DB access
python server.py --db ../restaurant.db --port 8765

# Test endpoints
curl http://127.0.0.1:8765/health
curl http://127.0.0.1:8765/api/sales
```

> 💡 **Tip:** When adding a new API endpoint to the sidecar, also add the corresponding TypeScript client in `src/api/`.

---

## Scripts (Build/Dev)

```bash
# scripts/dev/ — development utilities
node scripts/dev/kill-port.cjs         # Kill port 1420
node scripts/dev/update-year.cjs       # Update copyright year
node scripts/dev/ensure-db.cjs         # Ensure DB exists
node scripts/dev/build-sidecar.cjs     # Build sidecar binary
bash scripts/dev/capture-screenshots.sh # Capture screenshots

# scripts/ — i18n + checksums
node scripts/check-i18n.cjs            # Translation audit
node scripts/fill-fr-translations.cjs  # Auto-fill French translations
node scripts/generate-checksums.cjs    # Build checksums
```

---

## Adding a New Feature

### 1. Rust Operation

```rust
// projects/pos/src-tauri/src/operations/my_feature.rs
pub fn my_operation(db_path: &PathBuf) -> Result<MyType, String> {
    let conn = &mut open_conn(db_path)?;
    // ... Diesel query ...
}
```

### 2. Tauri Command

```rust
// projects/pos/src-tauri/src/lib.rs
#[tauri::command]
fn my_command(state: tauri::State<AppState>) -> Result<MyType, String> {
    let db_path = &state.db_path;
    operations::my_feature::my_operation(db_path)
}
```

### 3. TypeScript Page

```tsx
// projects/pos/src/pages/MyFeature.tsx
import { invoke } from '@tauri-apps/api/core';

export default function MyFeature() {
  const data = await invoke<MyType>('my_command');
  // ... render ...
}
```

> 💡 **Tip:** Follow the pattern: Rust operation → Tauri command → TypeScript page. Each layer is independently testable.

---

→ [Back to Guides](README.md) | [Rust Docs](../rust/) | [TypeScript Docs](../typescript/) | [Server Docs](../server/)
