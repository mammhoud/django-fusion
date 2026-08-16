# Formint Cloud Frontend — AI Agent Instructions

**Path:** `projects/formints/formint-cloud/frontend/`
**Product:** Formint Cloud frontend
**Stack:** Astro + React 19 + TypeScript + Tailwind/Alpine utilities

Read `projects/formints/AGENTS.md` and `projects/formints/formint-cloud/README.md`
first. This is not the Community desktop project; do not copy its
Tauri/Rust guidance into this folder.

## Structure

```text
frontend/
├── src/
│   ├── pages/                # Cloud operations/admin-facing routes
│   ├── layouts/              # Astro document/application shells
│   ├── components/           # App shell and reusable UI
│   ├── hooks/                # API, status, navigation, search, sync hooks
│   ├── contexts/             # Auth, theme, language, currency state
│   ├── api/                  # Django API, dashboard, data, sync-event clients
│   ├── utils/                # exports, transitions, preload, domain helpers
│   ├── i18n/                 # en/fr/de/es/ar translations
│   ├── lib/                  # icons, router shims, shared utilities
│   ├── test/                 # Vitest setup and tests
│   └── types.ts              # Frontend API/domain contracts
├── scripts/                  # dev/build/i18n utilities
├── docs/                     # frontend and architecture documentation
├── astro.config.mjs          # API/admin proxy configuration
├── package.json
├── pnpm-workspace.yaml
└── vitest.config.ts
```

## Backend contract

The frontend talks to the Django cloud master in `../backend/`. Formint Cloud
serves the former server-compatible API directly from Django; the
`SERVER_BASE`/`VITE_SERVER_URL` naming is compatibility vocabulary, not proof
that a Robyn process exists.

Keep these contracts synchronized with backend tests and README documentation:

- CRUD/data API paths
- `/fusion/*` render-mode, navigation, session, and asset endpoints
- dashboard and sync APIs
- `/ws/sync-events/` WebSocket frames and reconnect behavior
- auth/session and error response shapes

When changing a client type or API helper, search the corresponding backend
route and parity test before editing only the frontend.

## Frontend conventions

- Keep pages thin; put reusable behavior in hooks, API modules, contexts, or
  components according to the existing boundaries.
- Preserve loading, empty, error, and disconnected-WebSocket states.
- Keep translations complete for all supported locales when adding visible
  strings.
- Use existing theme tokens and component patterns; do not introduce a second
  design system in one page.
- Do not hard-code the backend port in multiple modules; use the existing
  Astro/env proxy configuration.

## Commands

```bash
cd projects/formints/formint-cloud/frontend
pnpm install
pnpm dev
pnpm check
pnpm build
pnpm test
pnpm exec vitest run
```

Use the parent `formint-cloud/Makefile` for coordinated backend/frontend startup
and stack verification. Browser tests may require the Django backend and
WebSocket endpoint to be running first.
