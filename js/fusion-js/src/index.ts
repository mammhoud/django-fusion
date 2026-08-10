/**
 * fusion-js — modular, framework-agnostic TS/ESM modules for
 * django-fusion frontends. Import individual modules for tree-shaking,
 * or use this barrel for convenience.
 *
 * ```ts
 * import { createTheme, initScrollReveal } from 'fusion-js';
 * ```
 */

export * from './modules/htmx';
export * from './modules/sse';
export * from './modules/fragments';
export * from './modules/scroll';
export * from './modules/theme';
export * from './skeleton';
export * from './component-loader';
export * from './perf';

export { default } from './modules/index';
