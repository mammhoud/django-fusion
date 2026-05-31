// ── Application ───────────────────────────────────────────────
export { Application, createApp, app } from './app.js';

// ── Config ────────────────────────────────────────────────────
export {
    CONFIG,
    ConfigHelpers,
    LAYOUT_TYPES,
    LAYOUT_CONFIG,
    VCARD_SUB_TYPES,
    DEFAULT_LAYOUT,
} from './config.js';

// ── Registry ──────────────────────────────────────────────────
export { RegistryManager, registry } from './registry.js';

// ── Main (side-effects + named helpers) ───────────────────────
export { App, initApp, destroyApp } from './main.js';
