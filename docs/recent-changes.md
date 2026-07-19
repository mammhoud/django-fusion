# 🔄 Recent Changes — Session Log

> **Related Names:** `changelog`, `recent`, `updates`, `infrastructure restructuring`, `auth tests`, `profile button`, `sidecar API`, `scripts reorganization`, `documentation`
> **Tags:** #changelog #recent #updates

Documentation for features and changes added in the most recent development session.

---

## 🏗️ Infrastructure Restructuring — `core/` → `projects/` + `libs/` Move

### What Changed
The entire monorepo layout was restructured for clarity and standard conventions:

| Before | After | Reason |
|--------|-------|--------|
| `core/` | `projects/` | Clearer monorepo project root |
| `core/libs/django-fusion` | `libs/django-fusion` | Libraries now at repo root (standard submodule convention) |
| `core/libs/ceptor-ai` | `libs/ceptor-ai` | Libraries now at repo root |
| `core/lms-demo/` | `projects/lms/` | Shorter, canonical name |
| `core/VResume/` | `projects/portfolio/` | Descriptive project name |
| `core/tinker/` | `projects/cypercloud/` | New brand name for AI customizer |
| `core/configs/` | `projects/configs/` | Configs stay with projects |
| `core/assets/` | `projects/assets/` | Shared assets stay with projects |
| `core/www/` | `projects/www/` | Shared core stays with projects |

### Files Updated
- `AGENTS.md` — all path references updated
- `CHANGELOG.md` — path references updated
- `Makefile` — CUSTOMIZER_DIR → CYPERCLOUD_DIR, lms-demo → lms, vresume → portfolio
- `.dockerignore` — all paths updated for new layout
- `.gitignore` — libs patterns updated
- `.gitmodules` — submodule paths updated
- `.env.example` — comment references updated
- All GitHub Actions workflows — path triggers updated
- `INFRASTRUCTURE.md` — container names and paths updated

### Migration Notes
- All `core/` references in code and config replaced with `projects/`
- `core/libs/` submodule paths moved to `libs/` at repo root
- No database schema changes — only directory names
- Docker volume mounts updated for new paths

---

## POS — Auth System (Rust)

### Files Changed
- `projects/pos/src-tauri/src/operations/auth.rs`

### What Changed
Added comprehensive unit tests (23 tests) covering `check_auth_required`, `ensure_superuser_exists`, and `get_superuser_email`.

### Key Functions Tested

| Function | Tests | Scenarios |
|----------|-------|-----------|
| `get_superuser_email` | 6 | Both set, none set, partial, both empty, password empty |
| `check_auth_required` | 8 | No env vars, superuser set, partial, SMTP with/without manager email, superuser priority, no DB needed |
| `ensure_superuser_exists` | 9 | No env vars, email/password empty, creates user, custom name, idempotent, password update, name preservation |

> 💡 **Tip:** Run with `cargo test -- --test-threads=1` — env var tests require serial execution due to global state.

---

## POS — Profile/Logout Button (TypeScript)

### Files Changed
- `projects/pos/src/components/PageLayout.tsx`

### What Changed
Added profile/logout button to the top bar showing logged-in user email.

### Features
- **Avatar circle** (first letter of name) + email on tablet/desktop
- **Dropdown** with full user info (name, email) + red Sign Out button
- **Outside click** to close
- **Inactivity warning** toast with "Stay" button
- Only visible when `isAuthRequired && user` (auth enabled + logged in)

> ⚠️ **Warning:** The dropdown is duplicated in two layout branches (showNav and !showNav). Both use the same `ProfileDropdown` local component to avoid code duplication.

---

## POS — Sidecar API Expansion (Python)

### Files Changed
- `projects/pos/sidecar/server.py`

### New Endpoints Added

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/sales` | GET | List all sales with line items |
| `/api/sales/<id>` | GET | Get single sale with items |
| `/api/products` | GET | List products |
| `/api/settings` | GET | Get app settings |
| `/invoice/render/<id>` | GET | Render printable invoice HTML |
| `/api/support/ticket` | POST | Create support ticket |
| `/api/support/tickets` | GET | List support tickets |
| `/api/support/ticket/<id>` | PATCH | Update ticket status |
| `/ws/chat/<room>` | WS | WebSocket chat endpoint |

### Invoice Rendering
- `GET /invoice/render/<id>?type=commercial&design=modern`
- Designs: `modern` (teal), `classic` (blue), `minimal` (dark)
- Types: `tax`, `commercial`, `proforma`, `credit`, `receipt`

---

## POS — TypeScript API Layer (TypeScript)

### New Files
- `projects/pos/src/api/sidecar.ts` — Base HTTP client with `get`/`post`/`patch`
- `projects/pos/src/api/chat.ts` — Chat REST + persistent WebSocket (`createChatWs`)
- `projects/pos/src/api/tickets.ts` — Support ticket CRUD
- `projects/pos/src/api/data.ts` — Sales, products, settings, invoice URL
- `projects/pos/src/api/index.ts` — Barrel exports

### Key Change
**Fixed WebSocket bug**: Previously, `ChatSupport.tsx` created a new WebSocket connection for every message. Now uses `createChatWs` for a persistent connection with auto-reconnect.

```typescript
// New pattern:
const conn = createChatWs({ room: 'support', onMessage });
conn.send({ type: 'message', text: 'Hello!', sender: 'user' });
conn.close();
```

---

## POS — Scripts Reorganization

### What Changed
Moved scripts to organized directories:

```
scripts/
├── check-i18n.cjs              ← translation audit
├── fill-fr-translations.cjs    ← auto-fill translations
├── generate-checksums.cjs      ← checksums
├── i18n-merge-ar.cjs           ← Arabic merge
├── verify-checksum.cjs         ← checksum verify
├── dev/                        ← 7 dev scripts
│   ├── kill-port.cjs
│   ├── update-year.cjs
│   ├── ensure-db.cjs
│   ├── capture-screenshots.sh
│   ├── build-sidecar.cjs
│   ├── build-all.cjs
│   └── generate-android-keystore.sh
└── github/                     ← 2 CI/CD scripts
    ├── diff-i18n.cjs
    └── encode-keystore-for-github.sh
```

### References Updated
- `package.json` — `prebuild`, `predev`, `build:all`, `build:sidecar`
- `Makefile` — `build-sidecar`, `screenshots`, `port-kill`
- `.github/workflows/i18n.yml` — `diff-i18n.cjs` path
- Internal `__dirname`/`SCRIPT_DIR` paths fixed (`..` → `../..`)

---

## POS — Environment Documentation

### Files Changed
- `projects/pos/.env.example` — Updated with `SUPERUSER_EMAIL`, `SUPERUSER_PASSWORD`, `SUPERUSER_NAME` docs

---

→ [Back to docs](./) | [Auth Guide](./guides/02-auth.md) | [POS Dev Guide](./guides/03-dev.md)
