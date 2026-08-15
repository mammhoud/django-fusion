# FormintA Community/Mini POS — AI Agent Instructions

**Path:** `projects/formints/formintA/`
**Product identity:** Formint Community / `formint-pos`
**Stack:** Tauri 2 + React 19 + TypeScript + Vite + Rust + SQLite/Diesel

Read `projects/formints/AGENTS.md` and the repository root first. This edition
is the lightweight offline desktop product.

## Structure

```text
formintA/
├── src/                      # React frontend
│   ├── pages/                # Product route pages
│   ├── components/           # Shared application shell/components
│   ├── layouts/              # Layout wrappers
│   ├── hooks/                # Data/UI hooks
│   ├── contexts/             # Auth, theme, currency, language contexts
│   ├── api/                  # Tauri/API wrappers and data clients
│   ├── utils/                # Export, invoice, navigation, UI helpers
│   ├── i18n/                 # JSON/TypeScript translations
│   ├── lib/                  # Icons and shared helpers
│   ├── test/                 # Vitest setup and tests
│   └── types.ts              # Frontend contracts
├── src-tauri/                # Rust/Tauri native layer
│   ├── src/                  # Commands, native integration, app entry
│   ├── capabilities/         # Tauri permissions
│   ├── icons/                # Desktop icons
│   ├── Cargo.toml            # Rust dependencies
│   └── tauri.conf.json       # Desktop packaging/configuration
├── assets/                   # CSS and product assets
├── e2e/                      # Playwright auth/visual flows
├── docs/                     # Product architecture and customization docs
├── scripts/                  # Local/release helpers
├── package.json
├── Makefile
└── vite/astro configuration files
```

The exact page/component inventory can evolve. Treat `src/types.ts`, the API
wrappers, and Rust command signatures as the integration boundary.

## Architecture constraints

- There is **no Python server**, Django ORM, or server-rendered Fusion route in
  this edition.
- Data flow is `React → Tauri invoke → Rust → SQLite`.
- Keep TypeScript invoke wrappers, Rust command arguments/results, and database
  migrations synchronized.
- Native filesystem, dialog, store, and platform behavior belongs in Rust or a
  narrow `src/api` wrapper, not scattered through pages.
- Keep translations and theme behavior in the existing contexts/i18n modules.
- Do not copy Formint Professional or Cloud server code into this edition.

## Commands

```bash
cd projects/formints/formintA
pnpm install
pnpm dev
pnpm tauri dev
pnpm test
npx tsc --noEmit
cargo check --manifest-path src-tauri/Cargo.toml
pnpm build
```

Use the repository's actual package manager lockfile and scripts; do not add a
second package manager or regenerate lockfiles unnecessarily.

## Testing

- Add Vitest coverage for utility/hooks/data transformations.
- Add Playwright coverage for visible flows and authentication behavior.
- Add Rust tests for native/database behavior where the command is non-trivial.
- Run the smallest affected suite before an edition-level build.

Never commit local SQLite databases, generated installers, secrets, or signing
keys. Read the product-level POS guidance before changing shared contracts.
