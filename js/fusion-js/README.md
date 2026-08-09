# fusion-js

Framework-agnostic, modular **TypeScript/ESM** modules for django-fusion
frontends. Zero runtime dependencies — import from any TS framework
(React, Vue, Svelte, Solid, Astro) via Vite/webpack aliases or npm.

## Modules

| Module | Export | Purpose |
| ------ | ------ | ------- |
| `modules/htmx.ts` | `attachHtmx`, `isHtmxRequest`, `isFragmentRequest`, `bindIndicator`, `onSwap` | Attach + configure an htmx runtime, detect HX requests, global request indicator |
| `modules/sse.ts` | `createSSEClient` | Typed EventSource client with reconnect/backoff + named events |
| `modules/fragments.ts` | `loadFragment`, `refreshFragments` | Fetch + swap `/fragment/...` endpoints into `[data-fusion-fragment]` targets |
| `modules/scroll.ts` | `initScrollReveal`, `initSmoothAnchors` | IntersectionObserver reveals + smooth anchors (reduced-motion aware) |
| `modules/theme.ts` | `createTheme` | FOUC-safe theme bootstrap, toggle, persistence + cross-tab sync |

All modules are strict-TypeScript, dependency-free and tree-shakable.

## Usage

```ts
// Per-module (recommended — keeps bundles small)
import { attachHtmx } from 'fusion-js/modules/htmx';
import { createSSEClient } from 'fusion-js/modules/sse';
import { createTheme } from 'fusion-js/modules/theme';

// Or the barrel
import { initScrollReveal, refreshFragments } from 'fusion-js';

const theme = createTheme({ storageKey: 'fu:theme' });
theme.apply();

attachHtmx(); // uses window.htmx (import htmx.org elsewhere)

initScrollReveal({ staggerMs: 80 });
refreshFragments();

const stream = createSSEClient('/fragment/stream/', {
  events: { 'course-progress': (data) => console.log(data) },
});
```

## Wiring into a Vite/Astro project

```ts
// astro.config.mjs
import { fileURLToPath } from 'node:url';

vite: {
  resolve: {
    alias: {
      '@fusion': fileURLToPath(new URL('../../../libs/django-fusion/js/fusion-js/src', import.meta.url)),
    },
  },
}
```

Then `import { createTheme } from '@fusion/modules/theme';`.

## Standalone build

```bash
npm install        # once (dev-only: typescript)
npm run typecheck  # strict TS check
npm run build      # emits dist/ with .d.ts declarations
```
