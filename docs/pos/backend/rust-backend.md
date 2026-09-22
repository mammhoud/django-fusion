# 🦀 Rust — POS Backend

Tauri 2 + Diesel + SQLite backend for the POS desktop application.

## Use Cases

### 1. POS CRUD Operations (`operations/*.rs`)
- **Purpose:** Manage restaurant data — products, sales, categories, inventory, employees, customers, suppliers, recipes, purchase orders, kitchen tickets — via Diesel SQLite queries exposed as Tauri commands
- **Key traits:** 25+ operation modules, each independently testable; most are 🟢 customizable (add fields, change validation); modules follow identical CRUD pattern

### 2. Desktop Authentication (`auth.rs`)
- **Purpose:** Secure the POS app with bcrypt-hashed superuser login or SMTP email-code flow; auto-create superuser from env vars on first launch
- **Key traits:** Auth is 🔴 core — do not modify directly; configurable via `SUPERUSER_EMAIL`/`PASSWORD` env vars; inactivity timeout with warning banner

### 3. Database Lifecycle (`db/mod.rs`)
- **Purpose:** Resolve the SQLite path (env var or platform app-data dir), run pending Diesel migrations automatically on every launch, open connections
- **Key traits:** Auto-migration at startup means zero manual DB setup; path overridable via `DATABASE_URL` env var 🔴 migration system is core infrastructure

### 4. Sidecar Process Management (`sidecar.rs`) — ⛔ removed
- **Purpose (historical):** spawn, monitor, and terminate the Python/Sanic sidecar process.
  The sidecar (Robyn/Sanic) was **removed** — Community and Standard are offline-first
  (Rust/Diesel only); Pro and Cloud serve their APIs from Django. The `sidecar.rs`
  module and `127.0.0.1:8765` port no longer exist in the current editions.

---

## Project Structure

```
src-tauri/src/
├── main.rs                  # Entry point
├── lib.rs                   # Tauri command registration, setup
├── db/
│   ├── mod.rs               # Database connection, migrations, path resolution
│   ├── schema.rs            # Diesel table definitions (auto-generated)
│   └── models.rs            # Rust structs (User, Product, Sale, etc.)
├── operations/
│   ├── mod.rs               # Module declarations
│   ├── auth.rs              # 🔴 Authentication (login, setup, superuser, password)
│   ├── products.rs          # 🟢 CRUD for products
│   ├── sales.rs             # 🟢 CRUD for sales
│   ├── categories.rs        # 🟢 CRUD for categories
│   ├── inventory_transactions.rs  # 🟢 Inventory tracking
│   ├── ingredients.rs       # 🟢 Ingredient management
│   ├── recipes.rs           # 🟢 Recipe management
│   ├── employees.rs         # 🟢 Employee management
│   ├── customers.rs         # 🟢 Customer management
│   ├── suppliers.rs         # 🟢 Supplier management
│   ├── settings.rs          # 🟢 Settings CRUD
│   ├── analytics.rs         # 🟢 Dashboard analytics
│   ├── roles.rs             # 🟢 RBAC roles
│   └── ...                  # (other operations)
├── email.rs                 # 🟢 SMTP email sending
└── bin/
    └── seed.rs              # 🟢 Database seeder binary
```

## Customization Guide

### 🟢 Customizable (safe to modify)
| Module | What you can change |
|--------|-------------------|
| `email.rs` | SMTP server, email templates, recipient addresses |
| `seed.rs` | Seed data presets, branding, menu items |
| `products.rs` | Add new fields, change validation logic |
| `settings.rs` | Add new setting fields |
| `analytics.rs` | Add new report types, metrics |

### 🔴 Not Customizable (framework core)
| Module | Why not |
|--------|---------|
| `auth.rs` | Security-critical: password hashing, session validation |
| `db/mod.rs` | Migration system, connection pooling |
| `db/schema.rs` | Auto-generated from migrations — edit `.sql` files instead |
| `lib.rs` | Tauri command registration, setup orchestration |

### 🟡 Delegate Pattern
| Pattern | Used in |
|---------|---------|
| `Migrate via .sql files` | Add tables/columns in `migrations/` dir |
| `Add Tauri command` | Register in `lib.rs` → implement in `operations/` |
| `Override via env var` | `DATABASE_URL`, `SMTP_*`, `SUPERUSER_*` |

## Key APIs

### Authentication (`auth.rs`)
```rust
// Check if auth is required
check_auth_required(db_path: &PathBuf) -> Result<bool, String>

// Auto-create superuser from env vars
ensure_superuser_exists(db_path: &PathBuf) -> Result<(), String>

// Login with email + password
login(db_path: &PathBuf, email: String, password: String) -> Result<User, String>
```

### Database (`db/mod.rs`)
```rust
// Resolve DB path (env var or app data dir)
get_db_path(app: &AppHandle) -> Result<PathBuf, String>

// Run pending migrations
run_migrations(db_path: &PathBuf) -> Result<(), String>

// Open a connection
open_conn(db_path: &PathBuf) -> Result<SqliteConnection, String>
```

## Tests

```bash
cd projects/formints/formint-community/src-tauri   # or formint-standard/src-tauri
cargo test                          # Run all Rust tests
cargo test auth                     # Run only auth tests
cargo test -- --test-threads=1      # Serial (env var tests)
```

## Environment Variables

| Variable | Module | Purpose |
|----------|--------|---------|
| `SUPERUSER_EMAIL` | `auth.rs` | Superuser login email |
| `SUPERUSER_PASSWORD` | `auth.rs` | Superuser password (auto-created) |
| `SUPERUSER_NAME` | `auth.rs` | Display name (default: "Admin") |
| `SMTP_USERNAME` | `auth.rs`, `email.rs` | Enable email-based auth |
| `DATABASE_URL` | `db/mod.rs` | Override DB path |

---

→ [Back to docs](../README.md)
