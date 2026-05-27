# JS Asset Plan (VResume model)

Goal: standardize site JS assets, bundle notification system, and ensure HTMX + SSE integration builds cleanly with existing frontend pipelines (webpack/npm).

Overview
- Use a single `webpack`/`npm` build per site that exposes a `notifications` entry.
- Place source modules under `websites/www/static_src/js/` (or existing `assets/js`) and compile to `static/bundles/`.
- Export small, ESM-friendly modules (`SSEHandler`, `NotificationSystem`, `HTMXNotificationHandler`) so they can be imported by site pages or lazy-loaded.

Key steps
1. Add `notifications` webpack entry that imports `./notifications/index.js` (from `.js.plans`).
2. Ensure `NotificationSystem` registers global helpers (`window.showNotification`, etc.) only after DOM ready.
3. For HTMX: ensure `htmx` is loaded before `HTMXNotificationHandler`; listen on `htmx:afterSwap` and `htmx:beforeOnLoad` for headers.
4. Build output: `bundles/notifications.[contenthash].js` and include via template tag or `webpack-loader` config.

Tests & Verification
- Dev: run `npm run build:<site>` and open pages that use notifications; trigger server-side HX-Trigger with `showNotification` payload.
- Smoke: open browser console and execute `window.NotificationSystem.test()` and `window.SSEManager.getStatus()`.

Packaging notes
- Keep `.js.plans` as a design-time source reference; copy or move modules into `websites/www/static_src/js/notifications/` when integrating into the main build.
- Avoid bundling HTMX twice; mark `htmx` as external if using a CDN.

Next actions
- Move `.js.plans` modules into site `static_src` and add `notifications` entry to `websites/package.json` and `webpack` config. Create a small CI smoke-runner that builds and runs basic node/static checks.
