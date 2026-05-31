// ── Core (side-effects: jQuery, Bootstrap, HTMX, theme) ───────
export * from './core/index.js';

// ── Utilities & Managers ──────────────────────────────────────
export * from './lib/index.js';

// ── Services (side-effects: cookies auto-init) ────────────────
export * from './services/index.js';

// ── Navigation ────────────────────────────────────────────────
export * from './navigation/index.js';

// ── Components ────────────────────────────────────────────────
export * from './components/index.js';

// ── Global debug namespace ────────────────────────────────────
if (typeof window !== 'undefined') {
    window.VResume = {
        version: '1.0.0',
        modules: {},
        components: {},
        services: {},
        utils: {},
    };
}
