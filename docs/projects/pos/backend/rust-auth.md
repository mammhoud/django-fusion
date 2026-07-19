# 🔴 Auth — `src-tauri/src/operations/auth.rs`

Authentication module for POS. Handles login, account setup, password management, and superuser auto-creation.

> **Customization level**: 🔴 Not Customizable — security-critical code. Modify only if you understand the implications.

## Public API

| Function | Returns | Purpose |
|----------|---------|---------|
| `check_auth_required(db_path)` | `Result<bool, String>` | Is auth required? (env vars or SMTP) |
| `ensure_superuser_exists(db_path)` | `Result<(), String>` | Auto-create/update superuser from env vars |
| `get_superuser_email()` | `Option<String>` | Get configured superuser email |
| `has_users(db_path)` | `Result<bool, String>` | Are there any users in the DB? |
| `verify_user(db_path, email)` | `Result<User, String>` | Verify a user exists (session check) |
| `login(db_path, email, password)` | `Result<User, String>` | Login with bcrypt password check |
| `setup_account(db_path, email, code, pw, name)` | `Result<User, String>` | Create account with email code |
| `change_password(db_path, email, old, new)` | `Result<(), String>` | Change password |
| `send_confirmation_code(email)` | `Result<(), String>` | Send email verification code |

## Auth Flow

```
App Launch
    │
    ├── SUPERUSER_EMAIL + SUPERUSER_PASSWORD set?
    │   ├── YES → Auth required → Show login screen
    │   │         └── ensure_superuser_exists() → creates user if new
    │   │         └── User enters SUPERUSER_EMAIL + SUPERUSER_PASSWORD → login()
    │   │
    │   └── NO → Check SMTP
    │       ├── SMTP configured + manager email? → Auth required
    │       └── No → Skip auth, open Home directly
```

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `SUPERUSER_EMAIL` | For superuser auth | — | Login email |
| `SUPERUSER_PASSWORD` | For superuser auth | — | Login password |
| `SUPERUSER_NAME` | No | `"Admin"` | Display name |
| `SMTP_USERNAME` | For SMTP auth | — | SMTP server username |

## Quick Usage

```rust
use operations::auth;

// Check if auth is needed
let required = auth::check_auth_required(&db_path)?;

// Create superuser at startup
auth::ensure_superuser_exists(&db_path)?;

// Login
let user = auth::login(&db_path, "admin@test.com".into(), "password".into())?;
```

## Tests

23 unit tests covering all auth functions. See bottom of `auth.rs`.

```bash
cargo test auth -- --test-threads=1
```

---

→ [Back to Rust docs](README.md)
