# Community + Client Merge — one edition, two UI modes, three platforms

> Tags: `#formints` `#pos` `#community` `#client` `#vue` `#tauri` `#mobile` — status 🟡 **proposed (awaiting review)**.

**Goal:** fold `formint-client/` (Vue 3 + Pinia + Tauri) into
`formint-community/` as a **build-time selectable UI mode**, sharing one Rust core
and shipping from one edition on **desktop + Android + iOS**. The client's Django
backend, Astro shell, and Python helper scripts are retired — the client UI
becomes offline-first over the shared Rust/Diesel SQLite core.

**Decisions taken (review input):**

| # | Decision |
|---|---|
| 1 | **3 platforms** = Desktop (Win/macOS/Linux) · Android · iOS |
| 2 | **Build-time selector** — React/Astro stays the default; the Vue client builds instead when selected. No runtime UI switching, no duplicate Rust core |
| 3 | **Offline only** — `formint-client/backend/` (Django shop/employee/cms), `formint-client/frontend/` (Astro shell), and the client's Python/Node server helpers are deleted; the Vue UI talks to Rust via `invoke` like the React UI |

## 1. Current state (verified)

| | `formint-community/` | `formint-client/` |
|---|---|---|
| Frontend | Astro 5 static MPA + React 19 islands — `src/pages/*.astro` (24) → `src/app/pages/**` (36) | Vite + Vue 3 + Pinia + vue-router + vue-i18n — 4 views (`Dashboard`, `Menu`, `Orders`, `Settings`), `TitleBar`, `MainLayout`, shadcn-vue `ui/**` |
| Data layer | `invoke()` → Rust (36 files call `invoke`) | `fetch()` → Django `:8075` (`src/api/index.ts`) |
| Rust | `src-tauri/` 8,319 LOC, Diesel/SQLite + migrations, `seed` bin, ESC/POS `print_thermal_receipt`, `get_settings`/`save_settings` | `src-tauri/` **33 LOC** (`greet`, `print_receipt`), plugins log/store/fs/opener |
| Tauri | `Formints Community` · `com.mammhoud.formint-community` · port 1420 · icons from `../../assets/shared/icons` | `Formint Client` · `com.formint.client` · port 1420 · local `icons/` |
| Builds | `build:desktop` / `build:android` / `build:ios` / `build:all` + checksums | `tauri build` only |
| Extra baggage | — | Django `backend/`, Astro `frontend/`, `server*.py`/`server.js`/`keep_alive.py`/`persistent_server.py`/`run_all.py`/`start_*.py`, `next-env.d.ts`, npm `package-lock.json`, `server_pid.txt` |
| i18n | en / fr / ar (react-i18next, `src/i18n/*.json`) | en-US / zh-CN / ar-SA / fr-FR (vue-i18n TS modules) |

Both editions already resolve the shared asset root (`@formints-assets` →
`../assets/shared`) and both bind port **1420** for Tauri.

The Rust surface the Vue UI needs already exists in Community:

| Vue client call | Community command |
|---|---|
| product/menu list | `get_products`, `get_categories` |
| orders / transactions | `get_transactions`, `add_sale`, `update_sale`, `refund_sale` |
| settings store | `get_settings` / `save_settings` |
| receipt print | `print_thermal_receipt` (ESC/POS); client's `print_receipt` merged as the generic fallback |
| dashboard counts | `get_analytics`, `get_user_count` |

## 2. Target layout

```text
formint-community/
├── src/                      # React UI (default mode) — unchanged
├── src/pages/*.astro          # Astro MPA shell (default mode) — unchanged
├── astro.config.mjs           # default-mode builds
├── package.json               # root scripts: dev / build / build:desktop|android|ios (+ :client variants)
├── pnpm-workspace.yaml        # packages: ['', 'client']
├── client/                    # ◀ NEW — the Vue client as a UI mode
│   ├── src/                   # moved from formint-client/src (Vue app)
│   ├── index.html
│   ├── vite.config.ts         # @formints-assets → ../../assets/shared
│   ├── tsconfig.json          # @formints-assets/* alias
│   ├── package.json           # vue, pinia, vue-router, vue-i18n, reka-ui, daisyui, oxlint, vue-tsc
│   └── project.json           # nx: build/check/test/dev targets (stack:tauri+vue)
├── src-tauri/                 # single shared Rust core + Tauri configs
│   ├── tauri.conf.json        # base (React mode): beforeBuildCommand → pnpm build
│   ├── tauri.client.conf.json # ◀ NEW overlay: Vue mode
│   └── capabilities/
├── assets/ · e2e/ · docs/
└── Makefile                   # UI=react|client switch
```

**`formint-client/` is removed** (git history is the archive), consistent with
the `pos-full`/`pos-solo` → `formint-pro` merge precedent and the root rule
against duplicate source trees.

## 3. Selector mechanics

One env var, one Tauri config overlay, no branching inside app code.

```bash
# default (React) — unchanged commands
make dev-desktop           # or: pnpm dev:desktop
make build-android

# Vue client mode
make dev-desktop  UI=client
make build-desktop UI=client
make build-android UI=client
make build-ios     UI=client
```

- `UI=client` exports `FORMINTS_UI=client`; npm scripts append
  `--config src-tauri/tauri.client.conf.json` to `tauri dev/build/android/ios`.
- `src-tauri/tauri.client.conf.json` overrides only:
  `productName: "Formint Client"`, `identifier: "com.formint.client"`,
  `build.beforeDevCommand: "pnpm -C client dev"`,
  `build.beforeBuildCommand: "pnpm -C client build"`,
  `build.frontendDist: "../client/dist"`.
- Post-build steps (`generate-checksums.cjs`, `build-all.cjs`,
  `community-bundle.cjs`) take the mode flag so artifacts are labelled
  `*-client-*` and mobile bundles are signed with the client identifier.
- Both modes use port **1420** — they are never built or run simultaneously;
  `make` targets call `port-kill` first (existing `scripts/dev/kill-port.cjs`).

## 4. Phases

Each phase is independently verifiable and leaves the tree green.

### Phase 1 — Scaffold the UI mode (no behaviour change)

1. `git mv formint-client/src formint-community/client/src` and
   `formint-client/index.html`, `vite.config.ts`, `tsconfig.json`,
   `.oxlintrc.json`, `.prettierrc` into `formint-community/client/`.
2. Add `formint-community/client/package.json` with the current client deps
   (vue, pinia, vue-router, vue-i18n, reka-ui, @heroicons/vue, daisyui,
   @tauri-apps/api, tailwindcss v4, oxlint, vue-tsc) and scripts
   `dev` / `build` / `check` / `test`.
3. Add `client` to `formint-community/pnpm-workspace.yaml`; run one
   `pnpm install` at the community root and commit the single lockfile.
4. Repoint `client/vite.config.ts` + `client/tsconfig.json` at
   `../../assets/shared` (keeping the `@formints-assets` alias and
   `fs: { allow: [SHARED_ASSETS] }` contract).
5. Add `src-tauri/tauri.client.conf.json` and the `:client` npm scripts +
   `UI=client` Make targets + `client/project.json` (nx).
6. Extend `scripts/publish/build-all.cjs` / `generate-checksums.cjs` to accept
   the mode.
7. Remove the client's stale extras: `next-env.d.ts`, `package-lock.json`,
   `server_pid.txt`, `public/`.

**Verify:** `cd formint-community && pnpm install && make check && make test`
(React path unchanged) **and** `UI=client make check-client` (Vue typecheck).
Optionally `UI=client make dev-desktop`.

### Phase 2 — Rewire the Vue UI onto the shared Rust core, drop the server

1. Replace `client/src/api/index.ts` HTTP fetch calls with a thin `invoke`
   adapter (`client/src/api/tauri.ts`) mapping to the Community commands listed
   in §1; delete the Django portal URL + `/api/catalog`, `/api/orders`, `/fusion/*`
   calls and the `portalUrl` setting.
2. Point `client/src/utils/settings.ts` at `get_settings`/`save_settings`
   instead of `@tauri-apps/plugin-store`; drop `pinia-plugin`-free disk store
   code and the `plugin-store`/`plugin-log` plugins from the Vue mode.
3. Merge the client's `print_receipt` (`WebviewWindow::print`) into
   `src-tauri/src/lib.rs` as the generic print command, keeping
   `print_thermal_receipt` for ESC/POS; gate the webview print path to desktop
   targets (`#[cfg(desktop)]`) with an ESC/POS fallback on mobile.
4. Delete `formint-client/backend/` (Django shop/employee/cms), `frontend/`
   (Astro), all `*.py` server helpers, `server.js`/`start-server.js`, and
   `client/scripts/dev-stack.sh` + `scripts/e2e.sh` that boot them.
5. Confirm no capability additions are needed (Community already grants
   `core:default`, `opener`, `dialog`, `fs`); add the Vue mode to
   `capabilities/default.json` if the client's window/label differs.

**Verify:** `UI=client make check-client`; Rust `cargo check` + `cargo test`;
grep shows zero `localhost:8075` / `fetch(` server calls left in `client/`.

### Phase 3 — i18n, theming, and parity with the React mode

1. Align the Vue mode's locales with the edition's i18n contract: keep
   `client/src/locales/*.ts` (en-US/fr-FR/ar-SA/zh-CN), and extend
   `scripts/dev/check-i18n.cjs` (or add a client-scoped audit) so the Vue
   locales are checked for key parity alongside `src/i18n/*.json`.
2. Adopt the edition's design tokens/BEM classes for shared surfaces, keeping
   the Vue app's daisyUI/Tailwind config scoped inside `client/` (no CSS
   leakage into `assets/styles/index.css`).
3. Keep the shared-asset registry honest: update
   `configs/assets.yml` → `client: { frontend: vite-vue, backend: tauri-rust }`.
4. Feature parity note: the Vue mode is a **client/register** UI, not a
   replacement for the React mode's 23 pages/36 views — document the mode's
   scope explicitly so "same edition" is not read as "feature identical".

**Verify:** `UI=client make test-client` (Vitest) + `make i18n-check`.

### Phase 4 — Mobile enablement (Android + iOS)

1. Responsive/viewport pass on the Vue views: safe-area insets, touch targets,
   portrait layouts, and the mobile `TitleBar`/`MainLayout` (currently
   desktop-sized 800×600).
2. Add mobile capability entries (`mobile-schema.json`) and verify
   `tauri android init` / `tauri ios init` generate `src-tauri/gen/` for the
   `client` mode without touching the React mode's generated files.
3. Mobile icons/splash: reuse `assets/shared/icons` and the existing
   `generate-android-keystore.sh`; add the client-mode identifiers to the
   signing/publish docs.
4. Verify `UI=client make build-android` (and iOS on macOS) produce bundles with
   the client product name/identifier.

**Verify:** Android APK build (or `cargo check` for the mobile targets where the
SDK/NDK is unavailable, as the environment allows) + a device/emulator smoke of
sale → receipt.

### Phase 5 — Tests, tooling, and CI parity

1. `tests/pos-e2e/playwright.config.ts` — retarget the `formint-client` project
   to `cd ../../formint-community/client`, keep/rename the project (proposed:
   `formint-community-client`, keeping `test:e2e:client` as an alias).
2. `tests/test_asset_contracts.py` — repoint the `client` entries at
   `formint-community/client/vite.config.ts` + `client/tsconfig.json` (relative
   root `../../assets/shared`), drop the `formint-client/backend/settings.py`
   entry from the Django-static test, and drop/replace the client
   `tauri.conf.json` bundle-icon entry.
3. Add Vitest setup for the Vue mode (mirroring the React mode's
   `src/test/setup.ts` patterns) and a smoke suite for the mode selector.
4. Extend the mode matrix into the root/`just`/nx wiring:
   `formints/Makefile` `client-*` targets become **compatibility aliases**
   forwarding to `$(MAKE) -C formint-community ... UI=client`.
5. Standalone Community bundle: `scripts/publish/community-bundle.cjs` copies
   all of `formint-community/` into the public free-repo bundle — **decide**
   whether the public bundle ships the Vue client UI (bigger, more deps) or
   excludes `client/` (recommended, keeps the free tier React-only).

**Verify:** `make check` + `npx playwright test --project=formint-community-client`;
`uv run pytest tests/test_asset_contracts.py`.

### Phase 6 — Remove `formint-client/` and sync the docs

1. `git rm -r formint-client/` (history is the archive; no stub tree, no
   symlink — per root AGENTS §4/§5).
2. Update the guidance hierarchy: root `AGENTS.md` (§2 tree + edition tables),
   `projects/formints/AGENTS.md` (edition map, commands, testing matrix),
   `formint-community/AGENTS.md` (new "UI modes" section), and delete
   `formint-client/AGENTS.md` + `CLAUDE.md` (content folded into
   `client/AGENTS.md` if a scoped file is still wanted).
3. Update user-facing docs: `projects/formints/README.md`,
   `projects/formints/CHANGELOG.md`, `projects/formints/Makefile` header/menu,
   `docs/architecture/editions.md`, `docs/README.md`, `docs/GETTING_STARTED.md`,
   `docs/THEME_SYSTEM.md`, `docs/legacy/README.md`, `docs/scss-migration-plan.md`
   references, and this plans index — plus `docs/plans/editions/05-pos-client.md`
   (superseded) and the status board in `README.md` of this directory.
4. New ADR `projects/formints/docs/adr/0002-client-as-community-ui-mode.md`
   recording: client merged as a UI mode, Django shop backend + Astro shell
   retired, build-time selector rationale, three-platform target, and the
   public-bundle decision from Phase 5.

**Verify:** `grep -rn "formint-client" projects/ docs/ tests/` returns only
intentional compatibility aliases and historical mentions; `uv run pytest`
(workspace tests) + `nx run-many check --all`.

## 5. Open decisions for review

1. **Selector name/shape** — `UI=client` (env + Make var, recommended) vs a
   `--ui` flag on the Tauri CLI vs separate `tauri.client.conf.json` only
   (requiring raw `tauri --config` invocations).
2. **Public Community bundle** — ship the Vue client in the standalone
   `github.com/mammhoud/formint-community` bundle, or keep it React-only
   (recommended) and reserve the client UI for the in-repo edition?
3. **i18n strategy** — keep the Vue mode's own locale modules (fast, 4 locales,
   some key drift) vs migrate to one shared locale source for both modes
   (cleaner, larger rewrite)?
4. **Theme strategy** — keep daisyUI inside `client/` (fast) vs port the Vue
   views onto the edition's `fu-*` tokens/BEM (consistent, larger job)?
5. **Playwright project name** — rename to `formint-community-client` (honest,
   touches the `test:e2e:client` script + docs) vs keep `formint-client` (no
   churn, stale name)?
6. **The client's 4th locale** — zh-CN exists only in the client (React mode has
   en/fr/ar). Add zh-CN to the React mode for parity, or leave the modes
   divergent?

## 6. Out of scope

- No cloud/sync capability is added to the client mode (no Channels, no Django).
- No change to Standard / Pro / Cloud editions.
- No signing-key, keystore, or store-publishing work — release packaging stays
  an operator action.
- No migration of the React mode's pages to Vue (or vice versa).
