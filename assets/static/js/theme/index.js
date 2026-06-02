/**
 * @file theme/index.js
 * Unified theme registry.
 *
 * Exports (in dependency order):
 *   1. Helpers & mixins  — registerUsecase, compose, EventEmitterMixin …
 *   2. Vendors           — loadThemeVendorPackages, loadThemeVendor …
 *   3. Usecases          — initAnimationsUsecase, initLandingUsecase …
 *   4. Plugins           — PluginManager, pluginManager, initializePlugins …
 */

// ── 1. Helpers & Mixins ──────────────────────────────────────────────────────
export {
  registerUsecase,
  getUsecase,
  getUsecaseNames,
  reinitUsecases,
} from './helpers.js';

export {
  EventEmitterMixin,
  LifecycleMixin,
  ObserverMixin,
  ScrollMixin,
  AnimationMixin,
  ThemeVendorMixin,
  compose,
} from './mixins.js';

// ── 2. Vendor Packages ───────────────────────────────────────────────────────
export {
  loadThemeVendorPackages,
  loadThemeVendor,
  isThemeVendorLoaded,
  getLoadedThemeVendors,
} from './vendor-packages.js';

// ── 3. Usecases ──────────────────────────────────────────────────────────────
export { initAnimationsUsecase } from './animations/index.js';
export { initLandingUsecase }    from './landing/index.js';
export { initLmsUsecase }        from './lms/index.js';
export { initCrmUsecase }        from './crm/index.js';
export { initFormsUsecase }      from './forms/index.js';
export { initModalUsecase }      from './modal/index.js';
export { initSpaUsecase }        from './spa/index.js';

// ── 4. Layouts ───────────────────────────────────────────────────────────────
export {
  BaseLayout,
  PagesManager,
  LayoutManager,
  pagesManager,
  layoutManager,
  AppLayout,
  AuthLayout,
  LandingLayout,
  NotificationsLayout,
  ProfileLayout,
} from './layouts/index.js';

// ── 5. Plugins ───────────────────────────────────────────────────────────────
export {
  PluginManager,
  pluginManager,
  initializePlugins,
  getPlugin,
  registerPlugin,
} from '../plugins/index.js';
