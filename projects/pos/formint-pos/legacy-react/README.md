# legacy-react — Archived React POS UIs

The `pos-full` and `pos-solo` React desktop UIs were **merged into the
formint-pos package** and their directories deleted. This folder preserves
their complete **source-only** archives (React + Vite + Tauri shell source,
no `node_modules` / `dist` / sidecar / databases) as a reference for the
Astro shell and for porting React screens into `frontend/`.

## Contents

| Directory | Edition | Notes |
|---|---|---|
| [`pos-full/`](pos-full/) | Cloud master manager | 23 pages, Redux store, i18n (5 langs), DataTable/Modal components, Tauri shell |
| [`pos-solo/`](pos-solo/) | Branch device | Same React app with device-oriented config, `src/config/` |

## What was merged where

| pos-full/pos-solo capability | New home in formint-pos |
|---|---|
| Django + Robyn sidecar (server, routes, models, streams, ws_client, sync signals, scheduler, middleware, tests) | [`../sidecar/`](../sidecar/) |
| Django + Ninja backend, Unfold admin, fusion render-mode | [`../backend/`](../backend/) |
| React UI source (this folder) | [`../legacy-react/`](./) — preserved reference |
| Astro + HTMX shell (primary frontend) | [`../frontend/`](../frontend/) |

## Running the archived UIs (optional reference)

The archives are source-only; install and run them exactly as before, but
from the archive path:

```bash
cd projects/pos/formint-pos/legacy-react/pos-full
pnpm install        # or npm install
pnpm dev            # Vite dev server (frontend only; sidecar APIs are in ../sidecar)
```

> The Robyn sidecar server they talked to now lives at `../sidecar/`
> (`python3 server.py --port 8766`). The `src-tauri/` shell inside each
> archive is unchanged source.

## Tests

The archived React tests (`src/test/`) are collected by the unified vitest
config: `tests/js/vitest.config.ts` includes
`legacy-react/pos-full/src/test/**` (run from the repo root). Known issues
(React tests needing context providers) are documented in `tests/README.md`.
