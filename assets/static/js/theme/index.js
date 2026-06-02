/**
 * @file theme/index.js
 * Unified theme barrel — single import point for the entire theme system.
 *
 * Exports (in dependency order):
 *   1. Usecases + registration engine  (registerUsecase, USECASES, init*)
 *   2. Vendor packages                 (loadThemeVendorPackages, …)
 *   3. Layouts                         (BaseLayout, AppLayout, …)
 *   4. Plugins                         (PluginManager, pluginManager, …)
 *   5. Mixins re-exported from utility (EventEmitterMixin, compose, …)
 */

// ── 1. Usecases ──────────────────────────────────────────────────────────────
// helpers + all 7 usecases live in usecases.js
export {
  registerUsecase,
  getUsecase,
  getUsecaseNames,
  reinitUsecases,
  initAnimationsUsecase,
  initLandingUsecase,
  initLmsUsecase,
  initCrmUsecase,
  initFormsUsecase,
  initModalUsecase,
  initSpaUsecase,
  initAllUsecases,
  initUsecase,
  USECASES,
} from './usecases.js';

// ── 2. Vendor Packages ───────────────────────────────────────────────────────
export {
  loadThemeVendorPackages,
  loadThemeVendor,
  isThemeVendorLoaded,
  getLoadedThemeVendors,
} from './vendor-packages.js';

// ── 3. Layouts ───────────────────────────────────────────────────────────────
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

// ── 4. Plugins ───────────────────────────────────────────────────────────────
export {
  PluginManager,
  pluginManager,
  initializePlugins,
  getPlugin,
  registerPlugin,
} from '../plugins/index.js';

// ── 5. Mixins (forwarded from utility) ──────────────────────────────────────
export {
  EventEmitterMixin,
  LifecycleMixin,
  ObserverMixin,
  ScrollMixin,
  AnimationMixin,
  ThemeVendorMixin,
  compose,
} from '../utility/mixins.js';
