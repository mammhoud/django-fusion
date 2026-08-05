# 🦀 Rust — Seed Data & Presets

> **Related Names:** `seed`, `seeder`, `demo data`, `presets`, `gaming`, `coffee`, `restaurant`, `database seeding`, `initial data`
> **Tags:** #rust #seed #database #presets #demo

How the POS database seeder works and how to customize demo data presets.

---

## Overview

The seed binary (`projects/pos/src-tauri/src/bin/seed.rs`) populates the SQLite database with demo data. It supports 4 presets, each producing a different restaurant brand.

### Presets

| Preset | Brand | Description |
|--------|-------|-------------|
| `all` (default) | Level Up Gaming Center | Gaming center with coffee shop menu |
| `base` | POS KO | Basic restaurant (strips gaming + coffee) |
| `gaming` | Level Up Gaming Center | Gaming center only (strips coffee) |
| `coffee` | The Daily Grind | Coffee shop only (strips gaming) |

> 💡 **Tip:** The default `all` preset is the richest demo — use it for development and demonstrations.

---

## How It Works

```
seed binary starts
  └── Read PRESET env var (default: "all")
       ├── Delete existing restaurant.db (fresh start)
       ├── Run ALL migrations (base + gaming + coffee)
       ├── Strip unwanted presets via down.sql
       │    ├── base → strip gaming + coffee
       │    ├── gaming → strip coffee
       │    └── coffee → strip gaming
       └── Force settings.restaurant_name to preset brand
```

> ⚠️ **Warning:** The seeder **deletes** the existing `restaurant.db` before seeding. Don't run it on a production database.

---

## Running the Seeder

### Via Make (Recommended)

```bash
cd POS

make seed                        # preset=all (default)
make seed PRESET=coffee          # coffee-only
make seed PRESET=gaming          # gaming-only
make seed PRESET=base            # restaurant-only
```

### Via pnpm

```bash
PRESET=coffee pnpm db:reset
```

### Via Cargo Directly

```bash
PRESET=coffee cargo run --manifest-path src-tauri/Cargo.toml --bin seed
```

---

## Migration Layering

```
Migrations (applied in order):
  2026-01-01-000000_create_initial       ← Base tables (always)
  2026-01-02-000000_create_users         ← Auth tables (always)
  2026-07-15-000000_add_product_image    ← Product images (always)
  2026-07-16-000000_add_enterprise_features ← Enterprise tables (always)
  2026-07-17-000000_gaming_center_seed   ← Gaming demo data (may be stripped)
  2026-08-01-000000_coffee_shop_seed     ← Coffee demo data (may be stripped)
```

> 💡 **Tip:** The coffee_shop_seed migration may not exist in all branches. The seed binary gracefully skips missing presets with a warning (not an error).

Each migration has:
- `up.sql` — INSERT demo data
- `down.sql` — DELETE demo data (used for stripping)

> 💡 **Tip:** The down.sql uses narrow `IN (...)` lists — stripping one preset doesn't affect another.

---

## Force-Brand Logic

After stripping, `seed_with_preset()` forces `settings.restaurant_name`:

```rust
let brand = match preset {
    "all"    => "Level Up Gaming Center",
    "base"   => "POS",
    "gaming" => "Level Up Gaming Center",
    "coffee" => "The Daily Grind",
    _ => unreachable!(),
};
sql_query("UPDATE settings SET restaurant_name='{brand}' WHERE id=1;")
    .execute(&mut conn)?;
```

This ensures the top bar shows the correct brand regardless of migration order.

---

## Adding a New Preset (🟢 Customizable)

### Step 1: Create Migration

```bash
cd projects/pos/src-tauri
diesel migration generate my_preset_seed
```

### Step 2: Write `up.sql`

```sql
-- migrations/<timestamp>_my_preset_seed/up.sql
INSERT INTO settings (id, restaurant_name, currency)
VALUES (99, 'My Restaurant', 'USD')
ON CONFLICT(id) DO NOTHING;

INSERT INTO products (id, name, price, unit)
VALUES (1001, 'My Special Item', 19.99, 'piece');
```

### Step 3: Write `down.sql`

```sql
-- migrations/<timestamp>_my_preset_seed/down.sql
DELETE FROM settings WHERE id = 99;
DELETE FROM products WHERE id IN (1001);
```

### Step 4: Add Preset to Seeder

In `seed.rs`:

```rust
fn is_valid_preset(p: &str) -> bool {
    matches!(p, "all" | "base" | "gaming" | "coffee" | "my_preset")
}

// In seed_with_preset:
let brand = match preset {
    // ... existing presets ...
    "my_preset" => "My Restaurant",
    _ => unreachable!(),
};

// Add strip logic if needed
let to_strip: &[&str] = match preset {
    // Strip my_preset when using other presets that layer on top
    // ...
};
```

### Step 5: Test

```bash
make seed PRESET=my_preset
```

---

## Programmatic Usage

The seeder functions can be used from tests:

```rust
use pos_ko_lib::db;

// Create a fresh test database
let db_path = PathBuf::from("/tmp/test.db");
db::run_migrations(&db_path)?;

// Or use the full seed pipeline
pos_ko_lib::bin::seed::seed_with_preset(&db_path, "base")?;
```

---

## Customization Guide

### 🟢 Customizable
| What | How |
|------|-----|
| Add a preset | Create migration → add to `seed_with_preset()` |
| Change demo data | Edit migration `up.sql` files |
| Change brand name | Edit the `brand` match in `seed_with_preset()` |
| Add products/categories | Add INSERTs to preset migration |

### 🔴 Not Customizable
| What | Why not |
|------|---------|
| Strip logic | Complex layering — must preserve other presets' data |
| Migration ordering | Diesel tracks applied versions — reordering breaks |
| Force-brand UPDATE | `settings.restaurant_name` must match preset |

### ⚪ Config Only
| Setting | Where |
|---------|-------|
| Preset selection | `PRESET` env var |
| Database path | `DATABASE_URL` env var |

---

→ [Back to Rust docs](README.md) | [Database Layer](../backend/rust-database.md) | [POS Dev Guide](../../../guides/03-dev.md)
