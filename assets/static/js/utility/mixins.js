/**
 * @file theme/mixins.js
 * Reusable class-factory mixins for theme, pages, and components.
 *
 * Pattern:  const MyClass = SomeMixin(AnotherMixin(BaseClass));
 *
 * Mixins provided:
 *   - EventEmitterMixin   – on/off/emit (DOM-backed custom events)
 *   - LifecycleMixin      – init/destroy/refresh pattern
 *   - ObserverMixin       – IntersectionObserver + ResizeObserver helpers
 *   - ScrollMixin         – scroll position tracking with direction
 *   - AnimationMixin      – AOS / CSS class animation triggers
 *   - ThemeVendorMixin    – lazy-load a named vendor from vendor-packages
 */

import { debounce, throttle } from './helpers.js';

// ─────────────────────────────────────────────────────────────────────────────
// 1. EventEmitterMixin
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Adds on/off/emit to any class.
 * Events are also dispatched as DOM CustomEvents on `document`.
 */
export const EventEmitterMixin = (Base) => class EventEmitter extends Base {
  constructor(...args) {
    super(...args);
    this._emitterHandlers = new Map();
  }

  on(event, handler) {
    if (!this._emitterHandlers.has(event)) this._emitterHandlers.set(event, new Set());
    this._emitterHandlers.get(event).add(handler);
    return () => this.off(event, handler);
  }

  off(event, handler) {
    this._emitterHandlers.get(event)?.delete(handler);
    return this;
  }

  emit(event, detail = {}) {
    this._emitterHandlers.get(event)?.forEach((fn) => {
      try { fn(detail); } catch (e) { console.error(`[EventEmitter] ${event}`, e); }
    });
    document.dispatchEvent(new CustomEvent(event, { detail, bubbles: true }));
    return this;
  }
};

// ─────────────────────────────────────────────────────────────────────────────
// 2. LifecycleMixin
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Enforces init / destroy / refresh lifecycle.
 * Subclasses implement _onInit / _onDestroy / _onRefresh.
 */
export const LifecycleMixin = (Base) => class Lifecycle extends Base {
  constructor(...args) {
    super(...args);
    this._initialized = false;
    this._destroyed   = false;
    this._cleanups    = [];
  }

  async init() {
    if (this._initialized || this._destroyed) return this;
    await this._onInit?.();
    this._initialized = true;
    return this;
  }

  async destroy() {
    if (this._destroyed) return;
    this._cleanups.forEach((fn) => { try { fn(); } catch (_) {} });
    this._cleanups = [];
    await this._onDestroy?.();
    this._initialized = false;
    this._destroyed   = true;
  }

  async refresh() {
    await this.destroy();
    this._destroyed = false;
    await this.init();
    await this._onRefresh?.();
    return this;
  }

  /** Register a cleanup function that runs on destroy */
  _addCleanup(fn) { this._cleanups.push(fn); }
};

// ─────────────────────────────────────────────────────────────────────────────
// 3. ObserverMixin
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Helpers for IntersectionObserver and ResizeObserver.
 */
export const ObserverMixin = (Base) => class Observer extends Base {
  constructor(...args) {
    super(...args);
    this._observers = [];
  }

  /**
   * Watch element entering viewport.
   * @param {Element}  el
   * @param {Function} callback  – receives IntersectionObserverEntry
   * @param {Object}   [opts]
   * @param {boolean}  [once=true]
   */
  onVisible(el, callback, opts = {}, once = true) {
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        callback(entry);
        if (once) obs.unobserve(entry.target);
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -5% 0px', ...opts });

    observer.observe(el);
    this._observers.push(observer);

    if (this._addCleanup) this._addCleanup(() => observer.disconnect());
    return observer;
  }

  /**
   * Watch element resizing.
   * @param {Element}  el
   * @param {Function} callback – receives ResizeObserverEntry[]
   */
  onResize(el, callback) {
    const observer = new ResizeObserver(callback);
    observer.observe(el);
    this._observers.push(observer);

    if (this._addCleanup) this._addCleanup(() => observer.disconnect());
    return observer;
  }

  _disconnectObservers() {
    this._observers.forEach((o) => o.disconnect());
    this._observers = [];
  }
};

// ─────────────────────────────────────────────────────────────────────────────
// 4. ScrollMixin
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Tracks scroll position, direction, and percentage.
 */
export const ScrollMixin = (Base) => class Scroll extends Base {
  constructor(...args) {
    super(...args);
    this._scroll = { position: 0, direction: 'down', percent: 0, last: 0 };
  }

  initScrollTracking(throttleMs = 100) {
    const handler = throttle(() => this._onScrollUpdate(), throttleMs);
    window.addEventListener('scroll', handler, { passive: true });
    if (this._addCleanup) this._addCleanup(() => window.removeEventListener('scroll', handler));
    this._onScrollUpdate(); // seed values
  }

  _onScrollUpdate() {
    const pos   = window.scrollY;
    const total = document.documentElement.scrollHeight - window.innerHeight;
    const dir   = pos > this._scroll.last ? 'down' : 'up';

    this._scroll = {
      position:  pos,
      direction: dir,
      percent:   total > 0 ? Math.round((pos / total) * 100) : 0,
      last:      pos,
    };

    this.onScrollChange?.(this._scroll);
  }

  get scrollPosition()  { return this._scroll.position; }
  get scrollDirection() { return this._scroll.direction; }
  get scrollPercent()   { return this._scroll.percent; }
};

// ─────────────────────────────────────────────────────────────────────────────
// 5. AnimationMixin
// ─────────────────────────────────────────────────────────────────────────────

/**
 * AOS / CSS animation helpers.
 */
export const AnimationMixin = (Base) => class Animation extends Base {
  initAOS(options = {}) {
    if (typeof AOS !== 'undefined') {
      AOS.init({
        duration: 800,
        easing: 'ease-out-cubic',
        once: true,
        offset: 50,
        ...options,
      });
    }
    return this;
  }

  /**
   * Stagger-animate children of `parent`.
   * @param {Element} parent
   * @param {string}  [childSelector='[data-animate], .animate']
   * @param {number}  [stepMs=100]
   * @param {string}  [cls='animate-in']
   */
  staggerAnimate(parent, childSelector = '[data-animate]', stepMs = 100, cls = 'animate-in') {
    parent.querySelectorAll(childSelector).forEach((el, i) => {
      setTimeout(() => el.classList.add(cls), i * stepMs);
    });
  }

  /** Add `cls` to `el` after an optional delay */
  animateIn(el, cls = 'animate-in', delayMs = 0) {
    setTimeout(() => el?.classList.add(cls), delayMs);
  }

  animateOut(el, cls = 'animate-in') { el?.classList.remove(cls); }
};

// ─────────────────────────────────────────────────────────────────────────────
// 6. ThemeVendorMixin
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Lazy-loads a named vendor from theme/vendor-packages.js.
 */
export const ThemeVendorMixin = (Base) => class ThemeVendor extends Base {
  /**
   * @param {string} vendorName  – key in vendorLoaders (e.g. 'swiper', 'aos')
   * @returns {Promise<any>}
   */
  async loadVendor(vendorName) {
    const { loadThemeVendor } = await import('./vendor-packages.js');
    return loadThemeVendor(vendorName);
  }

  async loadVendors(names = []) {
    const { loadThemeVendorPackages } = await import('./vendor-packages.js');
    const all = await loadThemeVendorPackages();
    return names.length === 0 ? all : Object.fromEntries(names.map((n) => [n, all.get(n)]));
  }
};

// ─────────────────────────────────────────────────────────────────────────────
// Convenience composer – apply mixins left-to-right
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Compose multiple mixins onto a base class.
 *
 * @example
 *   class MyComponent extends compose(BaseClass, EventEmitterMixin, LifecycleMixin, ScrollMixin) {}
 *
 * @param {Function}    Base
 * @param {...Function} mixins
 */
export function compose(Base, ...mixins) {
  return mixins.reduce((cls, mixin) => mixin(cls), Base);
}
