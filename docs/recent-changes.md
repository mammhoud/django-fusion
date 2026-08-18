# 🔄 Recent Changes — Session Log

> **Related Names:** `changelog`, `recent`, `updates`, `websocket`, `bolt dashboard`, `cloud sync`, `Makefile`, `branding`
> **Tags:** #changelog #recent #updates

Documentation for features and changes added in the most recent development session.

---

## Session 2026-08-18 — Loop-CRM redesign, fusion tables, Redis-free login, Nx/configs wiring

See the [full session changelog](changelogs/session-2026-08-18.md) for the complete
work log, files touched, and commits (`f48c5945f`, `9306ac96c`). Highlights:

- **Industrial-brutalist design system** — tactical telemetry palette across the Loop-CRM frontend shell and Django screens (`DESIGN_SYSTEM.md`).
- **django-fusion tables + forms** — schema-aware `RowGenerator` projections wired into companies/contacts/deals/invoices/payments/revenue screens.
- **Schema-aware API tables** — `GET /bolt/tables/{resource}` + `GET /api/v1/tables/{resource}/` returning header/row JSON contracts; `ResourceTable.tsx` island renders them.
- **Redis-free login** — RESP PING probe replaces the bare TCP check; DEBUG falls back to LocMem cache + in-memory channel layer so login works without Redis.
- **Nx↔Make wiring** — `project.json` Nx targets drive the project Makefiles and `make nx-*` delegates back; backend Makefile gains `i18n`/`makemessages`/`compilemessages`.
- **Env configs package** — dependency-free `projects/loop-crm/configs/` catalog (56 vars) + `make validate-env`.
- **Backend i18n start** — LocaleMiddleware, LANGUAGES (en/ar), LOCALE_PATHS; crm/finance/marketing models use `gettext_lazy`.
- **Docs added** — skills catalog, templates & request flows, Loop-CRM index, pointer pages.

---

## django-fusion — DataToken Sync-Tagging System (v2 — Abstract Base)

### What Changed
Added a lightweight sync-tagging model to `django-fusion` that marks database rows
for ordered synchronisation, now with an abstract base shared by DeviceToken:

- **`AbstractDataToken`** — abstract base with shared fields (`sync_status`, `app_type`,
  `metadata`, `created_at`, `updated_at`) + `Status`/`AppType` enums + base helpers
- **`DataToken(AbstractDataToken)`** — GenericForeignKey tagging for ANY model row
  (supports int, UUID, slug PKs via `CharField` object_id), parent/child tree ordering,
  progress tracking (`retry_count`, `error_message`, `synced_at`)
- **`DataTokenManager`** — sync-aware queryset: `unsynced()`, `for_node()`, `ordered()`,
  `roots()`, `sync_batch()`, `tag_row()` (now with `app_type` param)
- **`DataTokenMixin`** — drop-in mixin for models: `tag_for_sync()`, `mark_synced()`,
  `untag_for_sync()` with cached ContentType
- **Auto-untag signal** — `sync_log_success_handler` (plain function, manual connection)
- **`DeviceToken(AbstractDataToken)`** — all 3 copies (pos-full, pos-solo, pos-cloud) now
  inherit shared fields instead of duplicating `sync_status`/`app_type`/`metadata`
- **DeviceToken ↔ DataToken cascade** — `mark_data_synced()` bulk-updates linked
  DataTokens via `node_id_link`

### Files Changed
| File | Change |
|------|--------|
| `libs/django-fusion/.../datatoken.py` | +AbstractDataToken base, DataToken inherits, +app_type field, +index |
| `libs/django-fusion/.../models/__init__.py` | +AbstractDataToken export |
| `libs/django-fusion/.../ci/models.py` | +AbstractDataToken re-export |
| `libs/django-fusion/.../ci/migrations/0002_*.py` | +app_type field, +[app_type, sync_status] index |
| `pos-full/sidecar/models/token.py` | DeviceToken(AbstractDataToken), removed dup fields |
| `pos-solo/sidecar/models/token.py` | DeviceToken(AbstractDataToken), removed dup fields |
| `pos-cloud/core/models.py` | DeviceToken(AbstractDataToken), removed dup enums/fields |
| `pos-cloud/core/migrations/0003_*.py` | Alter sync_status, app_type, metadata (now inherited) |
| `docs/features/data-token-sync-tagging.md` | Updated with v2 architecture diagram + DeviceToken cascade |

### Benefits
- **Cross-model consistency** — `Status`/`AppType` enums shared, no field duplication
- **Faster sync** — ordered batch queries (indexed) with `app_type` filtering
- **Data integrity** — parent→child tree ensures invoice before items
- **Multi-node** — `node_id` scoping for per-device sync windows
- **Device cascade** — single `mark_data_synced()` propagates to all linked DataTokens

---

## POS Cloud — Bolt Dashboard HTML Page

### What Changed
Added a fully self-contained analytics dashboard HTML page at `/apis/data/`:

- **Dark-themed dashboard** matching Unfold admin (slate bg, emerald green accent)
- **6 KPI cards** — Products, Sales, Inventory Txs, Branches, Organizations, Sync Events — with `data-sync-card` attributes for live WS updates
- **Status indicator** — `sync-status-dot` + `sync-status-label` managed by `bolt-sync-events.js`
- **API endpoint links** — 5 cards linking to bolt data endpoints
- **Quick admin links** — 5 cards linking to Unfold admin sections
- **Auto-refresh** — `fetchStats()` hydrates KPIs on load and every 30s
- **No duplicate WebSocket** — inline WS code removed; `bolt-sync-events.js` (injected by middleware) handles all live updates

### Files Changed
| File | Change |
|------|--------|
| `projects/pos/pos-cloud/configs/urls.py` | Updated — `DASHBOARD_HTML` constant + `_bolt_dispatch` now serves HTML when `route` is empty |

### Dashboard Verification
- All 6 API endpoints verified: 200 OK (stats, products, sales, inventory, branches, sync-logs)
- WebSocket broadcasts: 3/3 entity types received live (products, sales, inventory)
- pos-full scheduler: 752 syncs, 0 errors, running with 10s interval
- Sync log viewer panel: appears at bottom-right, 50-entry ring buffer

---

## POS Cloud — WebSocket Sync Events + Real-Time Dashboard

### What Changed
Added real-time WebSocket sync event pipeline to the POS Cloud Django server:

- **Django Channels ASGI server** with `daphne` replacing WSGI-only gunicorn
- **WebSocket endpoint** at `/ws/sync-events/` — `SyncEventConsumer` broadcasts live events
- **Channel layer** (in-memory for dev, Redis-ready for prod) connecting sync receivers → WebSocket
- **4 sync receivers** (`products`, `sales`, `inventory`, `heartbeat`) broadcast events on every push
- **BoltAPI catch-all bridge** at `/apis/data/*` — bridges Django URL dispatcher to `django_bolt` internal routing
- **Path rename**: `/bolt/` → `/apis/`, `/bolt-api/` → `/apis/data/`

### Dashboard Enhancements
- **Sync event log viewer** — fixed-position panel (bottom-right) showing last 50 live events with colored badges, relative timestamps, collapse toggle, clear button, and reconnect indicator (pulsing amber dot)
- **Admin dashboard badges** — live sync activity counters (Products, Sales, Inventory, Heartbeat) with delta badges (+N pulse), WS status dot (green/amber/gray), and server-rendered initial values
- **BoltSyncEventsMiddleware** — injects JS script into `/apis/` and `/admin/` page responses

### Sync Enhancements
- **`/sync/scheduler/interval`** endpoint — change sync interval at runtime (PATCH, validated ≥5s)
- **Inventory transaction_type mapping** — `in/out` → `addition/removal` for pos-cloud compatibility
- **Scheduled sync** — `BranchSyncScheduler` with `_refresh_interval()` for persisted config

### Branding
- **pos-crest.svg** — animated SVG crest logo deployed to all 3 POS editions (`src/assets/`, `src-tauri/icons/`, `sidecar/static/`) and pos-cloud (`core/static/`)
- Updated Unfold admin settings (`SITE_ICON`, `SITE_LOGO`) and sidecar admin templates

### Files Changed
| File | Change |
|------|--------|
| `projects/pos/pos-cloud/configs/asgi.py` | New — ASGI app with ProtocolTypeRouter |
| `projects/pos/pos-cloud/core/consumers.py` | New — SyncEventConsumer (AsyncWebsocketConsumer) |
| `projects/pos/pos-cloud/core/static/js/bolt-sync-events.js` | New — WebSocket client + log viewer + badge updater |
| `projects/pos/pos-cloud/core/middleware.py` | New — JS injection middleware |
| `projects/pos/pos-cloud/core/sync_api.py` | Updated — `_broadcast_sync_event()` in all 4 receivers |
| `projects/pos/pos-cloud/configs/__init__.py` | Updated — daphne, channels, ASGI, CHANNEL_LAYERS, SITE_ICON/LOGO |
| `projects/pos/pos-cloud/configs/urls.py` | Updated — BoltAPI catch-all bridge, path renames |
| `projects/pos/pos-cloud/templates/admin/dashboard.html` | Updated — live sync activity badges |
| `projects/pos/pos-cloud/configs/dashboard.py` | Updated — sync stats context |
| `projects/pos/pos-cloud/pyproject.toml` | Updated — channels, daphne deps |
| `projects/pos/pos-cloud/.env` | New — Django superuser + DB config |

---

## POS — Makefile Cloud Targets

### What Changed
Added 6 new `cloud-*` targets to `projects/pos/Makefile`:

| Target | Purpose |
|--------|---------|
| `make cloud-install` | Install dependencies + migrate |
| `make cloud-run` | Start daphne ASGI server on :8082 |
| `make cloud-dev` | Start with `--reload` for development |
| `make cloud-check` | Validate Django imports |
| `make cloud-test` | Run cloud test suite |
| `make cloud-clean` | Remove database + bytecode cache |

---

## POS — .env Files for All Editions

### What Changed
Created `.env` files with sensible defaults for all 4 editions:

| Edition | File | Key Config |
|---------|------|------------|
| pos-mini | `.env` (28 lines) | SUPERUSER + DATABASE_URL + PRESET |
| pos-solo | `.env` (34 lines) | + SIDECAR_HOST/PORT + POS_NODE_ID |
| pos-full | `.env` (50 lines) | + CLOUD_CRM_URL + SYNC_INTERVAL + Django admin |
| pos-cloud | `.env` (43 lines) | + DJANGO_SUPERUSER + DB config + SERVER_PORT |

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
