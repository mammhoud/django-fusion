/**
 * @file utility/index.js
 * Unified shared utilities for all workspace sites.
 * Import from '@utility' or '@base'.
 */

// ── DOM ──────────────────────────────────────────────────────────────────────
export { DOM }        from './dom.js';
export { default as _DOM } from './dom.js';

// ── State ────────────────────────────────────────────────────────────────────
export { AppState }   from './state.js';

// ── Helpers ──────────────────────────────────────────────────────────────────
export {
  Utils, createLogger,
  debounce, throttle, batchUpdates, sleep,
  isString, isNumber, isBoolean, isFunction, isObject, isArray, isElement, isDate, isPromise,
  capitalize, capitalizeAll, camelCase, kebabCase, truncate,
  escapeHtml, unescapeHtml, stripHtml,
  deepClone, merge, pick, omit,
  unique, chunk, flatten, groupBy, sortBy, shuffle, randomItem,
  random, randomFloat, uuid, generateId,
  isValidEmail, isValidUrl, isValidPhone,
  formatBytes, formatTime, formatDate,
  safeParseJSON, safeStringifyJSON,
  getQueryParam, getUrlParams, createUrl,
  isMobile, isTouchDevice, isOnline, getScrollbarWidth, getScrollParent,
  copyToClipboard, clamp, lerp, round,
  trigger, storage, measure,
} from './helpers.js';

// ── URL / History ────────────────────────────────────────────────────────────
export { URLTrackerMixin } from './url.js';

// ── Base Manager (used by all manager classes) ────────────────────────────────
export { BaseManager } from './base.manager.js';

// ── Mixins ───────────────────────────────────────────────────────────────────
export {
  EventEmitterMixin,
  LifecycleMixin,
  ObserverMixin,
  ScrollMixin,
  AnimationMixin,
  ThemeVendorMixin,
  compose,
} from './mixins.js';

// ── Config Helpers ───────────────────────────────────────────────────────────
export {
  ConfigHelpers,
  LAYOUT_TYPES,
  DEFAULT_LAYOUT,
  PAGE_TYPE_MAPPINGS,
  APP_SUB_TYPES,
} from './config.helpers.js';

// ── Metrics ───────────────────────────────────────────────────────────────────
export { MetricsCollector } from './app.metrics.js';

// ── Bootbox shim ─────────────────────────────────────────────────────────────
export { default as bootbox } from './bootbox-shim.js';

// ── Site helpers (used by every app entry point) ─────────────────────────────
export function ready(callback) {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', callback, { once: true });
    return;
  }
  callback();
}

export function siteName(defaultName = 'workspace') {
  return document.documentElement?.dataset?.site || window?.STRUCTA_SITE || defaultName;
}
