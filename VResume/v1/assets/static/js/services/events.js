import { debounce, throttle } from '../lib/helpers.js';

export class EventManagerHandler {
  constructor() {
    /** @type {Map<string, Function>} */
    this._listeners = new Map();
    /** @type {Map<string, Set<Function>>} */
    this._subscribers = new Map();
  }

  // ── Lifecycle ────────────────────────────────────────────────

  setup() {
    this._register('resize', debounce((e) => this._emit('resize', e), 250), window);
    this._register('scroll', throttle((e) => this._emit('scroll', e), 100), window);
  }

  cleanup() {
    this._listeners.forEach((handler, key) => {
      const [target, event] = key.split(':');
      (target === 'document' ? document : window).removeEventListener(event, handler);
    });
    this._listeners.clear();
    this._subscribers.clear();
  }

  // ── Pub/Sub ──────────────────────────────────────────────────

  /**
   * Subscribe to a managed event.
   * @param {'resize'|'scroll'} event
   * @param {Function} callback
   * @returns {() => void} unsubscribe function
   */
  on(event, callback) {
    if (!this._subscribers.has(event)) this._subscribers.set(event, new Set());
    this._subscribers.get(event).add(callback);
    return () => this.off(event, callback);
  }

  /**
   * @param {'resize'|'scroll'} event
   * @param {Function} callback
   */
  off(event, callback) {
    this._subscribers.get(event)?.delete(callback);
  }

  // ── Private ──────────────────────────────────────────────────

  _register(event, handler, target = window) {
    const key = `${target === document ? 'document' : 'window'}:${event}`;
    this._listeners.set(key, handler);
    target.addEventListener(event, handler, { passive: true });
  }

  _emit(event, payload) {
    this._subscribers.get(event)?.forEach(cb => {
      try { cb(payload); } catch (e) { console.error(`[EventManagerHandler] ${event} subscriber error:`, e); }
    });
  }
}
